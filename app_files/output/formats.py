"""Format registry: which writers exist, and how to normalise a format name.

Lives in its own module so both the package ``__init__`` and
``inmemory.py`` can use it without importing each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from app_files.output.csv_writer import write as write_csv
from app_files.output.excel_writer import write as write_excel
from app_files.output.json_writer import write as write_json
from app_files.output.sql_writer import write as write_sql


@dataclass(frozen=True)
class Format:
    name: str
    extension: str
    writer: Callable[..., Path]


FORMATS: dict[str, Format] = {
    "csv": Format("csv", ".csv", write_csv),
    "excel": Format("excel", ".xlsx", write_excel),
    "json": Format("json", ".json", write_json),
    "sql": Format("sql", ".sql", write_sql),
}

# Friendly aliases so a user typing "xlsx" or "insert" still works.
_ALIASES = {
    "xlsx": "excel",
    "xls": "excel",
    "excel": "excel",
    "csv": "csv",
    "tsv": "csv",
    "json": "json",
    "sql": "sql",
    "insert": "sql",
}


def normalise_format(name: str) -> str:
    """Resolve a user-supplied format name (or alias) to a canonical name."""
    key = str(name or "csv").strip().lower()
    try:
        return _ALIASES[key]
    except KeyError:
        raise ValueError(
            f"Unknown output format {name!r}. Choose one of: {', '.join(sorted(FORMATS))}"
        ) from None


def output_filename(base: str, output_format: str) -> str:
    """``clean_data`` + ``excel`` -> ``clean_data.xlsx``."""
    canonical = normalise_format(output_format)
    stem = base
    for extension in {fmt.extension for fmt in FORMATS.values()}:
        if stem.lower().endswith(extension):
            stem = stem[: -len(extension)]
    return f"{stem}{FORMATS[canonical].extension}"


def write_any(
    df: pd.DataFrame, path: str | Path, output_format: str = "csv", **kwargs
) -> Path:
    """Write ``df`` in the requested format, choosing the writer and suffix.

    Args:
        df: the frame to write.
        path: destination. Its suffix is corrected to match the format.
        output_format: ``csv``/``excel``/``json``/``sql`` (aliases accepted).
        kwargs: forwarded to the specific writer (e.g. ``table=`` for SQL).
    """
    canonical = normalise_format(output_format)
    path = Path(path)
    if path.suffix.lower() != FORMATS[canonical].extension:
        path = path.with_suffix(FORMATS[canonical].extension)
    return FORMATS[canonical].writer(df, path, **kwargs)