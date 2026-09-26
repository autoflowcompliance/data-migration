"""Column-level statistics: the shape of each column, not just its score.

Layer 5 answers "how good is this column" with a 0-100 score. This answers
"what is in it" — count, distinct, missing, centre, spread, and for text the
length range. A score without a shape is hard to act on: 60% complete does not
tell you whether one column is empty or every column is 40% empty.

Deliberately a sibling of ``dimensions.py``, not a change to it. The dimension
scores are frozen and their tests pin them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.transforms import is_missing

# A column is treated as numeric only when every non-blank value parses as a
# number. The inverse bug — typing a column of names as numeric because a few
# values look numeric — is worse than the false negative, so the check is
# "all", not "most".
_NUMERIC_SAMPLE_LIMIT = 10_000


@dataclass
class ColumnStats:
    """The statistics for one column."""

    name: str
    kind: str = "text"  # numeric | categorical | text
    count: int = 0  # non-missing values
    missing: int = 0
    missing_pct: float = 0.0
    distinct: int = 0
    minimum: float | None = None
    maximum: float | None = None
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    p25: float | None = None
    p75: float | None = None
    iqr: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    mean_length: float | None = None
    top_values: list[tuple[Any, int]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """JSON-safe view. ``top_values`` becomes a list of ``[value, count]``."""
        return {
            "name": self.name,
            "kind": self.kind,
            "count": self.count,
            "missing": self.missing,
            "missing_pct": self.missing_pct,
            "distinct": self.distinct,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": self.mean,
            "median": self.median,
            "std": self.std,
            "p25": self.p25,
            "p75": self.p75,
            "iqr": self.iqr,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "mean_length": self.mean_length,
            "top_values": [[value, count] for value, count in self.top_values],
        }


def _present(series: pd.Series) -> pd.Series:
    """The non-missing values, as the layer's own notion of missing."""
    mask = ~series.map(is_missing)
    return series[mask]


def _numeric(series: pd.Series) -> pd.Series | None:
    """``series`` as floats, or ``None`` when it is not wholly numeric.

    Booleans are excluded on purpose: ``True`` coerces to ``1`` and would make
    a flag column report a mean of 0.6, which is a true statement about
    nothing.
    """
    if series.map(lambda value: isinstance(value, bool)).any():
        return None
    coerced = pd.to_numeric(series, errors="coerce")
    if coerced.isna().any():
        return None
    return coerced.astype(float)


def _round(value: Any) -> float | None:
    if value is None:
        return None
    number = float(value)
    if number != number:  # NaN
        return None
    return round(number, 6)


def summarize_column(
    frame: pd.DataFrame,
    column: str,
    *,
    top_values: int = 5,
    numeric_sample_limit: int = _NUMERIC_SAMPLE_LIMIT,
) -> ColumnStats:
    """Summarise one column of ``frame``.

    Args:
        top_values: how many most-common values to keep for a categorical.
        numeric_sample_limit: sample size for the numeric test, so a very wide
            column does not pay a full-parse cost on every call.
    """
    if column not in frame.columns:
        raise KeyError(f"No column {column!r} in the frame")

    series = frame[column]
    stats = ColumnStats(name=str(column))
    total = len(series)
    present = _present(series)
    stats.count = int(len(present))
    stats.missing = int(total - stats.count)
    stats.missing_pct = round(stats.missing / total * 100, 6) if total else 0.0

    if stats.count == 0:
        # Nothing to describe. Reporting zeros rather than crashing keeps a
        # fully-blank column in the report, where an operator can see it.
        stats.kind = "text"
        return stats

    stats.distinct = int(present.nunique(dropna=True))

    sample = present
    if len(sample) > numeric_sample_limit:
        sample = sample.head(numeric_sample_limit)
    numeric = _numeric(sample)

    if numeric is not None:
        full = _numeric(present)
        if full is not None:
            stats.kind = "numeric"
            stats.minimum = _round(full.min())
            stats.maximum = _round(full.max())
            stats.mean = _round(full.mean())
            stats.median = _round(full.median())
            stats.std = _round(full.std(ddof=0))
            stats.p25 = _round(full.quantile(0.25))
            stats.p75 = _round(full.quantile(0.75))
            if stats.p25 is not None and stats.p75 is not None:
                stats.iqr = _round(stats.p75 - stats.p25)
            return stats

    # Categorical vs text: a column with any repetition is a category column;
    # one where every value is unique is free text. Repetition, not a ratio —
    # a 5-row column with 3 cities is categorical even though distinct is most
    # of the column, and a name column where two people share a surname is not
    # free text either.
    stats.kind = "categorical" if stats.distinct < stats.count else "text"

    lengths = present.astype(str).str.len()
    stats.min_length = int(lengths.min())
    stats.max_length = int(lengths.max())
    stats.mean_length = _round(lengths.mean())

    if top_values:
        counts = present.astype(str).value_counts().head(top_values)
        stats.top_values = [(str(value), int(count)) for value, count in counts.items()]

    return stats


def column_statistics(
    frame: pd.DataFrame,
    *,
    columns: list[str] | None = None,
    top_values: int = 5,
) -> list[ColumnStats]:
    """Summarise every column of ``frame`` (or the named subset), in order."""
    if frame is None or frame.empty or frame.columns.empty:
        return []
    target = columns if columns is not None else list(frame.columns)
    return [summarize_column(frame, str(name), top_values=top_values) for name in target]
