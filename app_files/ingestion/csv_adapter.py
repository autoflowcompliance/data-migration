"""CSV adapter: the existing chardet-backed CSV read, behind the Adapter API."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from app_files.ingestion.base import Adapter

# Encodings to try when chardet is unavailable or returns something unusable.
_FALLBACK_ENCODINGS = ("utf-8-sig", "utf-8", "latin-1", "cp1252")


def detect_encoding(raw: bytes) -> str:
    """Best-effort encoding detection, with a chardet-free fallback chain.

    Mirrors the logic already used by ``app_files.cli`` so CSV behaviour stays
    bit-for-bit identical to the existing tool.
    """
    try:
        import chardet

        result = chardet.detect(raw)
        detected = result.get("encoding") if result else None
        if detected:
            return detected
    except ImportError:
        pass
    for encoding in _FALLBACK_ENCODINGS:
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "utf-8"


class CSVAdapter(Adapter):
    name = "csv"
    extensions = (".csv", ".txt", ".tsv")

    def read(self, source: str | Path | BinaryIO | bytes) -> pd.DataFrame:
        raw = self._as_bytes(source)
        if not raw.strip():
            return pd.DataFrame()
        encoding = detect_encoding(raw)
        separator = "\t" if Path(str(source)).suffix.lower() == ".tsv" else ","
        try:
            frame = pd.read_csv(
                io.BytesIO(raw),
                dtype=str,
                keep_default_na=False,
                encoding=encoding,
                sep=separator,
            )
        except (UnicodeDecodeError, pd.errors.ParserError):
            frame = pd.read_csv(
                io.BytesIO(raw),
                dtype=str,
                keep_default_na=False,
                encoding=encoding,
                sep=separator,
                engine="python",
                on_bad_lines="skip",
            )
        return self._stringify(frame)