"""The five data-quality dimensions, each scored 0-100.

Kept separate from ``profiler.py`` so each dimension can be unit-tested in
isolation and reasoned about on its own, the way the project brief describes.

Every function takes a DataFrame plus optional hints and returns a float
between 0.0 and 100.0. An empty frame scores 0 for real-data dimensions
(completeness etc.) rather than 100 — a file with no rows is not "perfect",
it is unusable, and silently reporting 100 would be misleading.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from app_files.transforms import (
    is_missing,
    is_valid_email,
    is_valid_phone,
)

# Column-name hints used when the caller supplies no explicit column lists.
_EMAIL_HINT = "email"
_PHONE_HINT = "phone"
_DATE_HINT = "date"


def _columns(frame: pd.DataFrame, hints: tuple[str, ...]) -> list[str]:
    return [name for name in frame.columns if any(hint in str(name).lower() for hint in hints)]


def _score(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(passed / total * 100, 1)


def completeness(frame: pd.DataFrame, columns: list[str] | None = None) -> float:
    """Percentage of cells that are non-null across the given (or all) columns."""
    if frame.empty or frame.size == 0:
        return 0.0
    target = columns or list(frame.columns)
    total = 0
    filled = 0
    for column in target:
        if column not in frame.columns:
            continue
        series = frame[column]
        total += len(series)
        filled += int((~series.map(is_missing)).sum())
    return _score(filled, total)


def uniqueness(frame: pd.DataFrame, subset: list[str] | None = None) -> float:
    """Percentage of rows that are unique (i.e. 100 = no duplicate rows)."""
    total = len(frame)
    if total == 0:
        return 0.0
    columns = [c for c in (subset or list(frame.columns)) if c in frame.columns]
    unique = len(frame.drop_duplicates(subset=columns or None))
    return _score(unique, total)


def validity(
    frame: pd.DataFrame,
    email_columns: list[str] | None = None,
    phone_columns: list[str] | None = None,
) -> float:
    """Percentage of non-empty format-checkable values that pass their format.

    Only email and phone values are format-checkable without extra config; a
    frame with neither scores 100, because there is nothing to fail.
    """
    emails = email_columns if email_columns is not None else _columns(frame, (_EMAIL_HINT,))
    phones = phone_columns if phone_columns is not None else _columns(frame, (_PHONE_HINT,))
    passed = 0
    total = 0
    for column in emails:
        for value in frame.get(column, pd.Series(dtype=object)):
            if is_missing(value):
                continue
            total += 1
            passed += int(is_valid_email(value))
    for column in phones:
        for value in frame.get(column, pd.Series(dtype=object)):
            if is_missing(value):
                continue
            total += 1
            passed += int(is_valid_phone(value))
    if total == 0:
        return 100.0
    return _score(passed, total)


def _dominant_case(values: list[str]) -> str:
    """Return the casing most values in a column already use."""
    votes = {"lower": 0, "upper": 0, "title": 0}
    for value in values:
        if value != value.strip():
            continue
        if value == value.lower():
            votes["lower"] += 1
        elif value == value.upper():
            votes["upper"] += 1
        elif value == value.title():
            votes["title"] += 1
    return max(votes, key=lambda key: votes[key])


def _matches_case(value: str, convention: str) -> bool:
    if convention == "lower":
        return value == value.lower()
    if convention == "upper":
        return value == value.upper()
    if convention == "title":
        return value == value.title()
    return True


def _is_canonical_date(text: str, expected: str) -> bool:
    try:
        datetime.strptime(text, expected)
    except (ValueError, TypeError):
        return False
    return True


def consistency(
    frame: pd.DataFrame,
    date_columns: list[str] | None = None,
    text_columns: list[str] | None = None,
    date_format: str = "%Y-%m-%d",
) -> float:
    """Percentage of values already matching the expected formatting convention.

    Two conventions are measured, over whichever columns apply:

    * **date format** — is the stored text already canonical ``YYYY-MM-DD``?
      A date written ``12/31/24`` is a real, parseable date but *inconsistent*
      with the convention the rest of the pipeline emits.
    * **text case** — does the value match the casing the column predominantly
      uses? A column with 90 lower-case emails and 10 shouted ones is at 90%
      consistency, which is the signal a reviewer wants.
    """
    dates = date_columns if date_columns is not None else _columns(frame, (_DATE_HINT,))
    passed = 0
    total = 0

    for column in dates:
        for value in frame.get(column, pd.Series(dtype=object)):
            if is_missing(value):
                continue
            total += 1
            text = (
                value.strftime(date_format)
                if isinstance(value, (datetime, date, pd.Timestamp))
                else str(value).strip()
            )
            passed += int(_is_canonical_date(text, date_format))

    candidates = (
        text_columns
        if text_columns is not None
        else [c for c in frame.columns if c not in set(dates)]
    )
    for column in candidates:
        pairs = [
            (index, str(value).strip())
            for index, value in frame.get(column, pd.Series(dtype=object)).items()
            if not is_missing(value)
        ]
        if not pairs:
            continue
        values = [text for _, text in pairs]
        # Only judge casing when the values actually look like free text —
        # pure digits, amounts and codes have no meaningful "case".
        if not any(char.isalpha() for text in values for char in text):
            continue
        convention = _dominant_case(values)
        for _, text in pairs:
            total += 1
            passed += int(_matches_case(text, convention))

    if total == 0:
        return 100.0
    return _score(passed, total)


def timeliness(
    frame: pd.DataFrame,
    date_columns: list[str] | None = None,
    start: Any = None,
    end: Any = None,
) -> float:
    """Percentage of dates falling inside the expected [start, end] window.

    When no window is supplied, the window is derived from the data itself
    (min..max of the parseable dates). That makes the dimension meaningful on
    an arbitrary file: it measures how tightly clustered the dates are around
    the range they define — a single severe outlier drops the score, which is
    exactly the signal worth surfacing.
    """
    dates = date_columns if date_columns is not None else _columns(frame, (_DATE_HINT,))
    parsed: list[pd.Timestamp] = []
    for column in dates:
        for value in frame.get(column, pd.Series(dtype=object)):
            if is_missing(value):
                continue
            timestamp = pd.to_datetime(value, errors="coerce")
            if timestamp is not pd.NaT and not pd.isna(timestamp):
                parsed.append(timestamp)
    if not parsed:
        return 100.0

    if start is None:
        start = min(parsed)
    if end is None:
        end = max(parsed)
    start_ts = pd.to_datetime(start, errors="coerce")
    end_ts = pd.to_datetime(end, errors="coerce")
    if pd.isna(start_ts) or pd.isna(end_ts):
        return 100.0
    inside = sum(1 for value in parsed if start_ts <= value <= end_ts)
    return _score(inside, len(parsed))


DIMENSIONS = {
    "completeness": completeness,
    "uniqueness": uniqueness,
    "validity": validity,
    "consistency": consistency,
    "timeliness": timeliness,
}