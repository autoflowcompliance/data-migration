"""Profiling engine: five quality scores (0-100) for any DataFrame.

``profile`` is the single entry point. It returns a :class:`Profile` carrying
the five dimension scores, an overall score, and a per-column breakdown, so
both the HTML scorecard and the web UI can use one object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.profiling import dimensions

DIMENSION_NAMES = (
    "completeness",
    "uniqueness",
    "validity",
    "consistency",
    "timeliness",
)

# Weighting for the overall score. Completeness and validity carry the most
# weight because a record that is missing or malformed is unusable, whereas an
# inconsistent casing convention is cosmetic and easily fixed in bulk.
_WEIGHTS = {
    "completeness": 0.30,
    "validity": 0.30,
    "uniqueness": 0.15,
    "consistency": 0.15,
    "timeliness": 0.10,
}


@dataclass
class Profile:
    """The five scores plus supporting detail."""

    scores: dict[str, float] = field(default_factory=dict)
    row_count: int = 0
    column_count: int = 0
    column_scores: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    applicable: set[str] = field(default_factory=set)

    @property
    def overall(self) -> float:
        """Weighted overall score, 0-100.

        Only dimensions that had something to evaluate are counted. A score of
        100 for "no invalid emails" on a frame with no emails is true but
        vacuous, and averaging it in would let an unusable frame look
        respectable — a frame of blank cells scores ~60 that way. Dimensions
        with no input are dropped from the average instead.
        """
        if not self.scores:
            return 0.0
        counted = self.applicable or set(self.scores)
        total_weight = sum(_WEIGHTS.get(name, 0) for name in counted) or 0.0
        if total_weight == 0:
            return 0.0
        weighted = sum(
            self.scores.get(name, 0.0) * _WEIGHTS.get(name, 0) for name in counted
        )
        return round(weighted / total_weight, 1)

    def as_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "row_count": self.row_count,
            "column_count": self.column_count,
            **{name: self.scores.get(name, 0.0) for name in DIMENSION_NAMES},
        }

    def worst(self, count: int = 2) -> list[tuple[str, float]]:
        """The lowest-scoring dimensions, for a short natural-language summary."""
        ordered = sorted(self.scores.items(), key=lambda item: item[1])
        return ordered[:count]


def _column_completeness(frame: pd.DataFrame) -> dict[str, float]:
    from app_files.transforms import is_missing

    scores: dict[str, float] = {}
    for column in frame.columns:
        series = frame[column]
        if not len(series):
            continue
        filled = int((~series.map(is_missing)).sum())
        scores[str(column)] = round(filled / len(series) * 100, 1)
    return scores


def profile(
    frame: pd.DataFrame,
    email_columns: list[str] | None = None,
    phone_columns: list[str] | None = None,
    date_columns: list[str] | None = None,
    date_format: str = "%Y-%m-%d",
    timeliness_window: tuple[Any, Any] | None = None,
    today: Any = None,
) -> Profile:
    """Compute all five quality scores for ``frame``.

    Args:
        frame: any DataFrame (raw or cleaned).
        email_columns / phone_columns / date_columns: override auto-detection.
        date_format: the canonical date format consistency is measured against.
        timeliness_window: optional ``(start, end)``. When omitted, timeliness
            scores each date for freshness against a rolling 24-month window.
        today: reference date for that rolling window; defaults to the real
            current date. Injectable so results are reproducible in tests.
    """
    if frame is None or frame.empty:
        return Profile(
            scores=dict.fromkeys(DIMENSION_NAMES, 0.0),
            row_count=0,
            column_count=0,
            column_scores={},
            notes=["The frame is empty, so every dimension scores 0."],
        )

    start, end = timeliness_window if timeliness_window else (None, None)
    scores = {
        "completeness": dimensions.completeness(frame),
        "uniqueness": dimensions.uniqueness(frame),
        "validity": dimensions.validity(frame, email_columns, phone_columns),
        "consistency": dimensions.consistency(frame, date_columns, None, date_format),
        "timeliness": dimensions.timeliness(frame, date_columns, start, end, today),
    }

    notes: list[str] = []
    if scores["uniqueness"] < 100:
        duplicates = frame.shape[0] - frame.drop_duplicates().shape[0]
        notes.append(f"{duplicates} duplicate row(s) detected.")
    if scores["completeness"] < 100:
        worst = sorted(_column_completeness(frame).items(), key=lambda item: item[1])[:3]
        listed = ", ".join(f"{name} ({value}%)" for name, value in worst)
        notes.append(f"Least complete columns: {listed}.")

    return Profile(
        scores=scores,
        row_count=len(frame),
        column_count=len(frame.columns),
        column_scores=_column_completeness(frame),
        notes=notes,
        applicable=dimensions.evaluable_dimensions(
            frame, email_columns, phone_columns, date_columns
        ),
    )


def scorecard_rows(profile_result: Profile) -> list[dict[str, Any]]:
    """Rows for rendering a 5-bar scorecard (name, score, label)."""
    rows = []
    for name in DIMENSION_NAMES:
        score = profile_result.scores.get(name, 0.0)
        rows.append(
            {
                "dimension": name.title(),
                "score": score,
                "band": "ok" if score >= 90 else "warn" if score >= 70 else "bad",
            }
        )
    return rows