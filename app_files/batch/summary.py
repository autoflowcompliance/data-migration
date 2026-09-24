"""One CSV row per processed file, for sorting and filtering in a spreadsheet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app_files.batch.runner import BatchResult

COLUMNS = [
    "file",
    "status",
    "rows_in",
    "rows_out",
    "score",
    "errors",
    "warnings",
    "rule_failures",
    "rules_run",
    "privacy_masked",
    "addresses_normalised",
    "amounts_converted",
    "duplicates_removed",
    "error",
    "output_dir",
]


def summary_frame(result: BatchResult) -> pd.DataFrame:
    """The batch outcome as a frame, with a stable column order."""
    return pd.DataFrame([item.as_dict() for item in result.items], columns=COLUMNS)


def write_summary(result: BatchResult, path: str | Path) -> Path:
    """Write ``summary.csv`` and return its path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    summary_frame(result).to_csv(target, index=False)
    return target