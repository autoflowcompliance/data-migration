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

# Rolling window used by ``timeliness`` when the caller names no window.
_DEFAULT_WINDOW_MONTHS = 24
_DAYS_PER_YEAR = 365.0


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


def _freshness(value: pd.Timestamp, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> float:
    """How fresh a single date is against the rolling window, as 0.0-1.0.

    A date inside the window is fully fresh. A date before the window loses
    points in proportion to how far it has aged — something just outside the
    window is nearly fresh, a five-year-old date is not. A future date loses
    points in proportion to how far ahead it sits, reaching zero a year out.
    """
    if start_ts <= value <= end_ts:
        return 1.0
    if value > end_ts:
        ahead_days = (value - end_ts).days
        return max(0.0, 1.0 - ahead_days / _DAYS_PER_YEAR)
    window_days = max((end_ts - start_ts).days, 1)
    stale_days = (start_ts - value).days
    return max(0.0, 1.0 - stale_days / window_days)


def timeliness(
    frame: pd.DataFrame,
    date_columns: list[str] | None = None,
    start: Any = None,
    end: Any = None,
    today: Any = None,
) -> float:
    """How recent the dates in ``frame`` are, 0-100.

    Two modes, and the difference matters:

    * An explicit ``start``/``end`` window is a statement of intent — "these
      dates are acceptable, those are not" — so the score is the plain
      percentage of dates inside it.
    * With no window, the window is a rolling 24 months ending ``today``
      (injectable so tests are not clock-dependent) and each date is scored on
      its freshness, so an old date degrades the score gradually rather than
      falling off a cliff.

    The earlier default compared the data against its own min/max, which meant
    every date was inside the window by construction and the score could never
    move off 100. A frame with no parseable dates scores 100: there is nothing
    to be stale.
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

    if start is not None or end is not None:
        start_ts = pd.to_datetime(start, errors="coerce") if start is not None else min(parsed)
        end_ts = pd.to_datetime(end, errors="coerce") if end is not None else max(parsed)
        if pd.isna(start_ts) or pd.isna(end_ts):
            return 100.0
        inside = sum(1 for value in parsed if start_ts <= value <= end_ts)
        return _score(inside, len(parsed))

    reference = pd.Timestamp(today) if today is not None else pd.Timestamp(date.today())
    if pd.isna(reference):
        return 100.0
    end_ts = reference
    start_ts = reference - pd.DateOffset(months=_DEFAULT_WINDOW_MONTHS)
    freshness = sum(_freshness(value, start_ts, end_ts) for value in parsed)
    return round(freshness / len(parsed) * 100, 1)


def evaluable_dimensions(
    frame: pd.DataFrame,
    email_columns: list[str] | None = None,
    phone_columns: list[str] | None = None,
    date_columns: list[str] | None = None,
) -> set[str]:
    """Which of the five dimensions had actual input to score.

    A dimension with no input returns 100 ("nothing failed"), which is true but
    vacuous. ``Profile.overall`` excludes those so an empty or blank frame
    cannot score well by absence of evidence.
    """
    applicable: set[str] = set()
    if frame is None or frame.empty or frame.size == 0:
        return applicable

    applicable.add("completeness")
    if len(frame) > 0:
        applicable.add("uniqueness")

    emails = email_columns if email_columns is not None else _columns(frame, (_EMAIL_HINT,))
    phones = phone_columns if phone_columns is not None else _columns(frame, (_PHONE_HINT,))
    format_cells = sum(
        1
        for column in [*emails, *phones]
        for value in frame.get(column, pd.Series(dtype=object))
        if not is_missing(value)
    )
    if format_cells:
        applicable.add("validity")

    dates = date_columns if date_columns is not None else _columns(frame, (_DATE_HINT,))
    date_set = set(dates)
    parseable_dates = sum(
        1
        for column in dates
        for value in frame.get(column, pd.Series(dtype=object))
        if not is_missing(value) and not pd.isna(pd.to_datetime(value, errors="coerce"))
    )
    if parseable_dates:
        applicable.add("timeliness")

    # Mirrors ``consistency``: every non-date column with free text is judged,
    # plus the date columns themselves.
    checkable_text = 0
    for column in [c for c in frame.columns if c not in date_set]:
        for value in frame.get(column, pd.Series(dtype=object)):
            if is_missing(value):
                continue
            if any(char.isalpha() for char in str(value)):
                checkable_text += 1
    if checkable_text or parseable_dates:
        applicable.add("consistency")

    return applicable


DIMENSIONS = {
    "completeness": completeness,
    "uniqueness": uniqueness,
    "validity": validity,
    "consistency": consistency,
    "timeliness": timeliness,
}