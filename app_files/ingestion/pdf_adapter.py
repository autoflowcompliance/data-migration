"""PDF adapter: extract transaction tables from bank statement PDFs.

Bank statement layouts vary a lot between regions, so the adapter normalises
them to one canonical shape — ``Date``, ``Description``, ``Amount`` (signed) —
which is what makes "a PDF and a CSV of the same data produce identical
cleaned output" possible.

Layouts handled:

* **US** — ``Date | Description | Amount`` and
  ``Date | Description | Debit | Credit | Balance``
* **UK** — ``Date | Type | Details | Paid out | Paid in | Balance``
* **ZA** — ``Date | Description | Debit | Credit | Balance`` and
  ``Date | Description | Money out | Money in`` with trailing ``DR``/``CR``

Debit/credit pairs are collapsed into a single signed amount (debits
negative). Multi-page statements are handled by carrying the header mapping
forward when a continuation page repeats no header, and by skipping any row
that is itself a repeated header. If a page has no extractable table at all,
the adapter falls back to parsing text lines that look like
``<date> <description> <amount>``.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd

from app_files.ingestion.base import Adapter, UnsupportedFormatError

# Canonical output columns.
DATE, DESCRIPTION, AMOUNT = "Date", "Description", "Amount"

_HEADER_SYNONYMS: dict[str, set[str]] = {
    DATE: {
        "date", "transaction date", "trans date", "posting date", "posted date",
        "value date", "txn date", "date posted", "effective date",
    },
    DESCRIPTION: {
        "description", "details", "narrative", "memo", "particulars", "reference",
        "transaction", "transaction description", "transaction details", "payee",
    },
    "type": {"type", "transaction type", "txn type", "method", "channel"},
    AMOUNT: {"amount", "value", "transaction amount", "amt", "amount (usd)", "amount (zar)"},
    "debit": {
        "debit", "debits", "withdrawal", "withdrawals", "paid out", "paid out (£)",
        "money out", "outflow", "debit amount", "dr", "amount debited",
    },
    "credit": {
        "credit", "credits", "deposit", "deposits", "paid in", "paid in (£)",
        "money in", "inflow", "credit amount", "cr", "amount credited",
    },
    "balance": {"balance", "running balance", "closing balance", "balance (usd)", "bal"},
}

_DEBIT_INDICATOR = "debit"
_CREDIT_INDICATOR = "credit"

# A row whose first cell parses as a date starts a transaction.
_DATE_LIKE = re.compile(
    r"^\s*(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}|"
    r"[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4})\s*$"
)
_AMOUNT_LIKE = re.compile(r"^[\s(]*-?[$£€R]?\s?-?[\d,]+\.?\d*\s?(?:CR|DR)?[\s)]*$", re.I)


def _normalise_header(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower()).strip(":")


def _canonical(header: str) -> str | None:
    """Map a raw header cell to a canonical role, or None if unrecognised."""
    key = _normalise_header(header)
    if not key:
        return None
    for role, synonyms in _HEADER_SYNONYMS.items():
        if key in synonyms:
            return role
    # Loose containment for decorated headers e.g. "Debit Amount (ZAR)".
    for role, synonyms in _HEADER_SYNONYMS.items():
        if any(synonym in key for synonym in synonyms):
            return role
    return None


def _looks_like_header(cells: list[Any]) -> bool:
    roles = [_canonical(cell) for cell in cells]
    return sum(role is not None for role in roles) >= 2


def _header_map(cells: list[Any]) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for index, cell in enumerate(cells):
        role = _canonical(cell)
        if role and role not in mapping.values():
            mapping[index] = role
    return mapping


def _is_date(value: Any) -> bool:
    return bool(_DATE_LIKE.match(str(value or "")))


def _parse_amount(value: Any) -> float | None:
    """Parse a statement amount, honouring parentheses, CR/DR and signs."""
    text = str(value or "").strip()
    if not text or not _AMOUNT_LIKE.match(text):
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    upper = text.upper()
    if upper.endswith("DR"):
        negative = True
        text = text[:-2]
    elif upper.endswith("CR"):
        negative = False
        text = text[:-2]
    text = re.sub(r"[^0-9.\-]", "", text)
    if not text or text in {"-", ".", "-."}:
        return None
    try:
        amount = float(text)
    except ValueError:
        return None
    return -amount if negative else amount


class PDFAdapter(Adapter):
    name = "pdf"
    extensions = (".pdf",)

    def read(
        self, source: str | Path | BinaryIO | bytes, extension: str | None = None
    ) -> pd.DataFrame:
        raw = self._as_bytes(source)
        if not raw.strip():
            return pd.DataFrame()
        try:
            import pdfplumber
        except ImportError as exc:  # pragma: no cover - dependency is pinned
            raise UnsupportedFormatError(
                "Reading PDF statements needs pdfplumber. Install it with: pip install pdfplumber"
            ) from exc

        records: list[dict[str, Any]] = []
        carry_map: dict[int, str] | None = None
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables() or []
                page_records, carry_map = self._records_from_tables(tables, carry_map)
                if page_records:
                    records.extend(page_records)
                    continue
                # No usable table on this page — fall back to text lines.
                records.extend(self._records_from_text(page.extract_text() or ""))

        if not records:
            raise UnsupportedFormatError(
                "No transaction table could be extracted from this PDF. If it is a "
                "scanned image the text layer is missing — export a CSV from your "
                "bank instead, or run OCR on it first."
            )
        return self._stringify(pd.DataFrame(records, columns=[DATE, DESCRIPTION, AMOUNT]))

    # -- table strategy ---------------------------------------------------

    def _records_from_tables(
        self, tables: list[list[list[Any]]], carry_map: dict[int, str] | None
    ) -> tuple[list[dict[str, Any]], dict[int, str] | None]:
        records: list[dict[str, Any]] = []
        header_map = carry_map
        for table in tables:
            for cells in table:
                if cells is None:
                    continue
                cells = [cell for cell in cells]
                if _looks_like_header(cells):
                    header_map = _header_map(cells)
                    continue
                if not header_map:
                    continue
                row = self._row_from_cells(cells, header_map)
                if row:
                    records.append(row)
        return records, header_map

    @staticmethod
    def _cell(cells: list[Any], header_map: dict[int, str], role: str) -> str:
        for index, mapped in header_map.items():
            if mapped == role and index < len(cells):
                value = cells[index]
                if value not in (None, ""):
                    return str(value)
        return ""

    def _row_from_cells(
        self, cells: list[Any], header_map: dict[int, str]
    ) -> dict[str, Any] | None:
        cells = [" " if cell is None else str(cell) for cell in cells]
        date_value = self._cell(cells, header_map, DATE)
        # A transaction row must begin with a recognisable date in its date cell.
        if not _is_date(date_value):
            return None

        description = " ".join(
            part
            for part in (
                self._cell(cells, header_map, "type"),
                self._cell(cells, header_map, DESCRIPTION),
            )
            if part.strip()
        )
        amount: float | None = None
        if AMOUNT in header_map.values():
            amount = _parse_amount(self._cell(cells, header_map, AMOUNT))
        if amount is None:
            debit = _parse_amount(self._cell(cells, header_map, _DEBIT_INDICATOR))
            credit = _parse_amount(self._cell(cells, header_map, _CREDIT_INDICATOR))
            # Debits are money leaving the account, so they are negative.
            if debit is not None and debit != 0:
                amount = -abs(debit)
            elif credit is not None:
                amount = abs(credit)
        if amount is None:
            return None
        return {
            DATE: date_value.strip(),
            DESCRIPTION: description.strip(),
            AMOUNT: f"{amount:.2f}",
        }

    # -- text fallback ----------------------------------------------------

    @staticmethod
    def _records_from_text(text: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(
                r"^(?P<date>\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}|"
                r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4})"
                r"\s+(?P<body>.+)$",
                stripped,
            )
            if not match:
                continue
            body = match.group("body").strip()
            # The amount is the last money-looking token on the line.
            tokens = body.split()
            amount_index = None
            for index in range(len(tokens) - 1, -1, -1):
                if _AMOUNT_LIKE.match(tokens[index]) and any(
                    char.isdigit() for char in tokens[index]
                ):
                    amount_index = index
                    break
            if amount_index is None:
                continue
            amount = _parse_amount(tokens[amount_index])
            if amount is None:
                continue
            description = " ".join(tokens[:amount_index]).strip()
            records.append(
                {
                    DATE: match.group("date").strip(),
                    DESCRIPTION: description,
                    AMOUNT: f"{amount:.2f}",
                }
            )
        return records