"""Excel adapter built on openpyxl.

Note on ``.xls``: openpyxl only reads the OOXML formats (.xlsx/.xlsm). The
legacy binary ``.xls`` (BIFF) format is a completely different container that
openpyxl cannot open — attempting it raises ``InvalidFileException``. Rather
than fail with an opaque error, ``.xls`` is routed to ``xlrd`` when it is
installed (xlrd>=2 reads .xls only) and otherwise raises a clear, actionable
message telling the user to re-save as .xlsx.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from app_files.ingestion.base import Adapter, UnsupportedFormatError


class ExcelAdapter(Adapter):
    name = "excel"
    extensions = (".xlsx", ".xlsm", ".xls")

    def read(
        self, source: str | Path | BinaryIO | bytes, sheet: str | int | None = None
    ) -> pd.DataFrame:
        raw = self._as_bytes(source)
        if not raw.strip():
            return pd.DataFrame()
        suffix = Path(str(source)).suffix.lower()
        if suffix == ".xls":
            return self._read_legacy_xls(raw, sheet)
        return self._read_openpyxl(raw, sheet)

    def _read_openpyxl(self, raw: bytes, sheet: str | int | None) -> pd.DataFrame:
        try:
            import openpyxl  # noqa: F401
        except ImportError as exc:  # pragma: no cover - dependency is pinned
            raise UnsupportedFormatError(
                "Reading Excel files needs openpyxl. Install it with: pip install openpyxl"
            ) from exc
        try:
            frame = pd.read_excel(io.BytesIO(raw), sheet_name=sheet or 0, dtype=str, engine="openpyxl")
        except Exception as exc:
            raise UnsupportedFormatError(f"Could not read Excel file: {exc}") from exc
        return self._stringify(frame)

    def _read_legacy_xls(self, raw: bytes, sheet: str | int | None) -> pd.DataFrame:
        try:
            import xlrd  # noqa: F401
        except ImportError as exc:
            raise UnsupportedFormatError(
                "The legacy .xls format cannot be read by openpyxl. Either re-save the "
                "file as .xlsx, or install the optional reader: pip install xlrd"
            ) from exc
        try:
            frame = pd.read_excel(io.BytesIO(raw), sheet_name=sheet or 0, dtype=str, engine="xlrd")
        except Exception as exc:
            raise UnsupportedFormatError(f"Could not read .xls file: {exc}") from exc
        return self._stringify(frame)

    def sheet_names(self, source: str | Path | BinaryIO | bytes) -> list[str]:
        """List worksheets in an .xlsx workbook (empty for legacy .xls)."""
        raw = self._as_bytes(source)
        if Path(str(source)).suffix.lower() == ".xls":
            try:
                import xlrd

                book = xlrd.open_workbook(file_contents=raw)
                return list(book.sheet_names())
            except Exception:
                return []
        try:
            import openpyxl

            book = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
            try:
                return list(book.sheetnames)
            finally:
                book.close()
        except Exception:
            return []