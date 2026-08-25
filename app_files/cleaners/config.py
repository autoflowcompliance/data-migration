"""Configuration objects for the cleaning pipeline.

The cleaning pipeline is configuration driven: no column names are hardcoded.
Column roles (email/phone/date/numeric/text) are detected from the data unless
they are declared explicitly in the configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CleaningConfig:
    remove_duplicates: bool = True
    trim_whitespace: bool = True
    collapse_internal_whitespace: bool = True
    lowercase_emails: bool = True
    standardize_dates: bool = True
    date_format: str = "%Y-%m-%d"
    date_first: bool = False
    standardize_phones: bool = True
    default_region: str = "US"
    fix_scientific_notation: bool = True
    normalize_unicode: bool = False
    missing_value_strategy: str = "flag"
    """One of ``flag`` (leave empty, report), ``auto`` (median/mode) or ``drop``."""
    missing_value_tokens: tuple[str, ...] = (
        "",
        "-",
        "n/a",
        "na",
        "null",
        "none",
        "nan",
        "#n/a",
        "unknown",
    )
    email_columns: list[str] = field(default_factory=list)
    phone_columns: list[str] = field(default_factory=list)
    date_columns: list[str] = field(default_factory=list)
    id_columns: list[str] = field(default_factory=list)
    """Columns that must keep their literal value (SKUs, account numbers)."""
    duplicate_subset: list[str] = field(default_factory=list)
    """Columns used to detect duplicates; empty means every column."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CleaningConfig:
        pipeline = data.get("pipeline", data)
        cleaning = pipeline.get("cleaning", pipeline)
        known = set(cls.__dataclass_fields__)
        kwargs = {key: value for key, value in cleaning.items() if key in known}
        return cls(**kwargs)


def load_cleaning_config(path: str | Path | None) -> CleaningConfig:
    if path is None:
        return CleaningConfig()
    with open(path, encoding="utf-8") as handle:
        return CleaningConfig.from_dict(yaml.safe_load(handle) or {})
