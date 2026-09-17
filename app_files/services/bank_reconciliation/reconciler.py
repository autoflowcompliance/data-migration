"""Bank reconciliation core logic — no UI framework, fully tested standalone.

Positioned as PREP WORK for a bookkeeper/accountant to review and finalize —
this cleans and matches transactions, it does not categorize them or make
accounting judgments. That distinction should stay explicit in any
client-facing copy: this tool finds discrepancies, a qualified bookkeeper
resolves them.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd


def clean_currency_amount(value: Any) -> float | None:
    """Parse messy accounting-style amounts into a signed float.
    Handles '$1,234.56', '(150.00)' as negative, '1,200.00 CR/DR' suffixes,
    plain negatives, and stray whitespace. Returns None if unparseable."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    text = text.replace("$", "").replace(",", "").strip()

    if text.upper().endswith("CR"):
        text = text[:-2].strip()
    elif text.upper().endswith("DR"):
        negative = True
        text = text[:-2].strip()

    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None

    return float(-amount if negative else amount)


class UnreadableStatementError(ValueError):
    """Raised when an uploaded statement cannot be parsed as a CSV table.

    A distinct type lets the UI show a plain-language reason instead of a raw
    pandas ``EmptyDataError``.
    """


def _read_statement(raw: bytes, label: str) -> pd.DataFrame:
    """Read an uploaded statement, turning an empty file into a clear error."""
    import io

    if not raw or not raw.strip():
        raise UnreadableStatementError(
            f"The {label} file is empty. Upload a CSV with a header row, for example: Date,Amount"
        )
    try:
        return pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError as exc:
        raise UnreadableStatementError(
            f"The {label} file has no header row, so no columns could be read. "
            f"Expected a CSV beginning with a header such as: Date,Amount"
        ) from exc
    except pd.errors.ParserError as exc:
        raise UnreadableStatementError(
            f"The {label} file could not be parsed as CSV: {exc}"
        ) from exc


def _numeric_or_none(value: Any) -> float | None:
    """Return ``value`` as a float if it is a usable number, else ``None``.

    Amounts arrive as ``None`` from ``clean_currency_amount`` when unparseable,
    and as ``NaN``/``NaT`` from pandas' coercion.
    """
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        parsed = clean_currency_amount(value)
        return parsed
    return None if number != number else number


def _date_or_none(value: Any) -> Any:
    """Return ``value`` as a Timestamp if it is a usable date, else ``None``."""
    if value is None or value is pd.NaT:
        return None
    try:
        stamp = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(stamp) else stamp


def reconcile_transactions(
    bank_df: pd.DataFrame,
    ledger_df: pd.DataFrame,
    bank_date_col: str,
    bank_amount_col: str,
    ledger_date_col: str,
    ledger_amount_col: str,
    date_tolerance_days: int = 2,
) -> dict[str, Any]:
    """Match bank transactions against ledger entries.

    Matches on amount (exact, to the cent) + date (within tolerance, since
    bank clearing dates often differ slightly from ledger entry dates).
    Returns matched pairs, bank-only (missing from the client's books), and
    ledger-only (recorded but never actually cleared the bank).
    """
    bank = bank_df.copy().reset_index(drop=True)
    ledger = ledger_df.copy().reset_index(drop=True)
    bank["_matched"] = False
    ledger["_matched"] = False

    matches = []
    for i, brow in bank.iterrows():
        bank_amount = _numeric_or_none(brow[bank_amount_col])
        bank_date = _date_or_none(brow[bank_date_col])
        if bank_amount is None or bank_date is None:
            # Unparseable amount or date: the row cannot be compared, so it
            # stays unmatched and surfaces in bank_only for a human to look at
            # rather than crashing the whole run.
            continue
        for j, lrow in ledger.iterrows():
            if ledger.at[j, "_matched"]:
                continue
            ledger_amount = _numeric_or_none(lrow[ledger_amount_col])
            ledger_date = _date_or_none(lrow[ledger_date_col])
            if ledger_amount is None or ledger_date is None:
                continue
            same_amount = abs(bank_amount - ledger_amount) < 0.01
            date_diff = abs((bank_date - ledger_date).days)
            if same_amount and date_diff <= date_tolerance_days:
                matches.append({
                    "bank_row": i, "ledger_row": j,
                    "amount": bank_amount, "date_diff_days": date_diff,
                })
                bank.at[i, "_matched"] = True
                ledger.at[j, "_matched"] = True
                break

    bank_only = bank[~bank["_matched"]].drop(columns=["_matched"])
    ledger_only = ledger[~ledger["_matched"]].drop(columns=["_matched"])
    return {
        "matches": matches, "bank_only": bank_only, "ledger_only": ledger_only,
        "bank_total": len(bank), "ledger_total": len(ledger),
    }


def run_reconciliation(
    bank_bytes: bytes,
    ledger_bytes: bytes,
    bank_date_col: str, bank_amount_col: str,
    ledger_date_col: str, ledger_amount_col: str,
    date_tolerance_days: int = 2,
) -> dict[str, Any]:
    """Full pipeline from raw uploaded file bytes to a reconciliation result.
    Returns cleaned frames, match results, and a summary dict."""
    import io
    bank_df = _read_statement(bank_bytes, "bank statement")
    ledger_df = _read_statement(ledger_bytes, "ledger")

    bank_df[bank_amount_col] = bank_df[bank_amount_col].map(clean_currency_amount)
    ledger_df[ledger_amount_col] = ledger_df[ledger_amount_col].map(clean_currency_amount)
    bank_df[bank_date_col] = pd.to_datetime(bank_df[bank_date_col], errors="coerce")
    ledger_df[ledger_date_col] = pd.to_datetime(ledger_df[ledger_date_col], errors="coerce")

    before_bank, before_ledger = len(bank_df), len(ledger_df)
    bank_df = bank_df.drop_duplicates()
    ledger_df = ledger_df.drop_duplicates()

    result = reconcile_transactions(
        bank_df, ledger_df, bank_date_col, bank_amount_col, ledger_date_col, ledger_amount_col,
        date_tolerance_days,
    )

    summary = {
        "bank_transactions": result["bank_total"],
        "ledger_transactions": result["ledger_total"],
        "bank_duplicates_removed": before_bank - len(bank_df),
        "ledger_duplicates_removed": before_ledger - len(ledger_df),
        "matched": len(result["matches"]),
        "missing_from_books": len(result["bank_only"]),
        "recorded_but_never_cleared": len(result["ledger_only"]),
    }
    return {**result, "summary": summary}
