"""Configuration driven cleaning of a raw CRM export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.transforms import (
    email_lowercase,
    expand_scientific_notation,
    is_missing,
    is_valid_email,
    normalize_unicode,
    phone_e164,
    to_iso_date,
    trim_whitespace,
)
from app_files.cleaners.config import CleaningConfig

DATE_HINT = re.compile(r"date|dob|birth|created|updated|closed|renewal", re.I)
PHONE_HINT = re.compile(r"phone|mobile|cell|tel|fax", re.I)
EMAIL_HINT = re.compile(r"e-?mail", re.I)
ID_HINT = re.compile(r"\b(id|sku|zip|postcode|postal|account number)\b", re.I)


@dataclass
class CleaningResult:
    frame: pd.DataFrame
    actions: list[dict[str, Any]] = field(default_factory=list)
    column_roles: dict[str, str] = field(default_factory=dict)
    duplicates_removed: int = 0
    rows_in: int = 0

    @property
    def rows_out(self) -> int:
        return len(self.frame)

    def log(self, column: str, action: str, count: int, detail: str = "") -> None:
        if count:
            self.actions.append(
                {"column": column, "action": action, "records": count, "detail": detail}
            )

    def actions_frame(self) -> pd.DataFrame:
        columns = ["column", "action", "records", "detail"]
        if not self.actions:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(self.actions, columns=columns)


def _series_role(name: str, series: pd.Series, config: CleaningConfig) -> str:
    if name in config.email_columns:
        return "email"
    if name in config.phone_columns:
        return "phone"
    if name in config.date_columns:
        return "date"
    if name in config.id_columns:
        return "identifier"

    sample = [str(v).strip() for v in series.dropna().head(200) if not is_missing(v)]
    if not sample:
        return "text"
    if EMAIL_HINT.search(name) or sum(is_valid_email(v) for v in sample) > len(sample) * 0.6:
        return "email"
    if ID_HINT.search(name):
        return "identifier"
    if PHONE_HINT.search(name):
        return "phone"
    if DATE_HINT.search(name):
        return "date"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    return "text"


def detect_column_roles(frame: pd.DataFrame, config: CleaningConfig) -> dict[str, str]:
    return {name: _series_role(name, frame[name], config) for name in frame.columns}


def _apply(
    result: CleaningResult, column: str, func: Any, action: str, detail: str = ""
) -> None:
    original = result.frame[column]
    updated = original.map(func)
    changed = int((original.astype("string") != updated.astype("string")).fillna(False).sum())
    result.frame[column] = updated
    result.log(column, action, changed, detail)


def _fill_missing(result: CleaningResult, column: str, role: str) -> None:
    series = result.frame[column]
    blanks = series.map(is_missing)
    if not blanks.any():
        return
    if role == "numeric":
        numeric = pd.to_numeric(series, errors="coerce")
        fill: Any = numeric.median()
    else:
        modes = series[~blanks].mode()
        fill = modes.iloc[0] if not modes.empty else None
    if fill is None or (isinstance(fill, float) and pd.isna(fill)):
        return
    result.frame.loc[blanks, column] = fill
    result.log(column, "filled_missing", int(blanks.sum()), f"filled with {fill!r}")


def clean_data(
    source: pd.DataFrame, config: CleaningConfig | None = None
) -> CleaningResult:
    """Clean ``source`` and return the cleaned frame plus an audit trail."""
    config = config or CleaningConfig()
    frame = source.copy()
    frame.columns = [str(name).strip() for name in frame.columns]
    result = CleaningResult(frame=frame, rows_in=len(frame))
    result.column_roles = detect_column_roles(frame, config)

    for column, role in result.column_roles.items():
        if config.trim_whitespace:
            _apply(
                result,
                column,
                lambda v: trim_whitespace(v, config.collapse_internal_whitespace),
                "trimmed_whitespace",
            )
        if config.fix_scientific_notation and role in {"identifier", "text", "numeric"}:
            _apply(result, column, expand_scientific_notation, "expanded_scientific_notation")
        if config.normalize_unicode and role in {"text", "email"}:
            _apply(result, column, normalize_unicode, "normalized_unicode")
        if config.lowercase_emails and role == "email":
            _apply(result, column, email_lowercase, "lowercased_email")
        if config.standardize_phones and role == "phone":
            _apply(
                result,
                column,
                lambda v: phone_e164(v, config.default_region),
                "standardized_phone",
                "E.164",
            )
        if config.standardize_dates and role == "date":
            _apply(
                result,
                column,
                lambda v: to_iso_date(v, config.date_format, config.date_first),
                "standardized_date",
                config.date_format,
            )

    if config.missing_value_strategy == "auto":
        for column, role in result.column_roles.items():
            _fill_missing(result, column, role)
    elif config.missing_value_strategy == "drop":
        before = len(result.frame)
        blank_rows = result.frame.map(is_missing).all(axis=1)
        result.frame = result.frame[~blank_rows]
        result.log("*", "dropped_empty_rows", before - len(result.frame))

    if config.remove_duplicates:
        subset = [c for c in config.duplicate_subset if c in result.frame.columns] or None
        before = len(result.frame)
        result.frame = result.frame.drop_duplicates(subset=subset, keep="first")
        result.duplicates_removed = before - len(result.frame)
        result.log("*", "removed_duplicates", result.duplicates_removed)

    result.frame = result.frame.reset_index(drop=True)
    return result
