"""Bind the quality trend store and baseline comparison into a run.

Layer 5 already produces a five-dimension scorecard for one run, and
``profiling/trends.py`` and ``profiling/baseline.py`` already store that score
over time and compare a run against a pinned baseline. Neither had a caller
outside the profiling package: a run produced a score and forgot it, so "is
this source improving or rotting" and "is this run worse than the one we
accepted" were unanswerable without importing the package by hand.

This is the same additive binding as privacy, normalization and dedupe: a run
records its score (always, because history is the whole point) and compares
against the source's pinned baseline (only once one has been set). Nothing
about the pipeline changes.

State lives under ``AUTOFLOW_HOME`` via ``TrendStore``, so a run against a
fresh home starts a new history rather than reading the repo's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app_files.profiling.baseline import (
    DEFAULT_DROP_THRESHOLD,
    BaselineComparison,
    compare_to_stored_baseline,
)
from app_files.profiling.profiler import Profile
from app_files.profiling.trends import QualityPoint, TrendStore, trend_direction


def source_key(source: str | Path) -> str:
    """The name a source is remembered under: its filename stem, stable across runs."""
    name = Path(str(source)).name
    return Path(name).stem or name


@dataclass
class QualityHistory:
    """What one recorded run learned about its source's history."""

    source: str
    run_id: int
    recorded: QualityPoint
    history: list[QualityPoint] = field(default_factory=list)
    comparison: BaselineComparison | None = None

    @property
    def trend(self) -> str:
        return trend_direction(self.history)

    @property
    def alerting(self) -> bool:
        return self.comparison is not None and self.comparison.alerting

    def summary(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "run_id": self.run_id,
            "score": round(self.recorded.overall, 1),
            "runs_recorded": len(self.history),
            "trend": self.trend,
            "baseline_set": self.comparison is not None,
            "regressed": list(self.comparison.regressed_dimensions)
            if self.comparison is not None
            else [],
        }


def record_quality(
    source: str | Path,
    profile_result: Profile,
    store: TrendStore | None = None,
    threshold: float = DEFAULT_DROP_THRESHOLD,
) -> QualityHistory:
    """Record this run's score and compare it against the source's baseline.

    Recording happens first, so the run just made is part of the history the
    trend is read from. The comparison uses the baseline that was pinned before
    this run, so a run cannot become its own baseline.
    """
    store = store if store is not None else TrendStore()
    key = source_key(source)
    comparison = compare_to_stored_baseline(key, profile_result, store, threshold=threshold)
    run_id = store.record(key, profile_result)
    return QualityHistory(
        source=key,
        run_id=run_id,
        recorded=store.latest(key) or _point_from(run_id, key, profile_result),
        history=store.trend(key),
        comparison=comparison,
    )


def _point_from(run_id: int, source: str, profile_result: Profile) -> QualityPoint:
    """A QualityPoint for a just-recorded run, for when the read-back is empty."""
    from datetime import datetime, timezone

    return QualityPoint(
        id=run_id,
        source=source,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        overall=float(profile_result.overall),
        row_count=int(profile_result.row_count),
        column_count=int(profile_result.column_count),
        dimensions={name: float(value) for name, value in profile_result.scores.items()},
    )


def pin_baseline(
    source: str | Path,
    profile_result: Profile,
    store: TrendStore | None = None,
) -> QualityPoint:
    """Record a run and pin it as the source's baseline in one step."""
    store = store if store is not None else TrendStore()
    key = source_key(source)
    run_id = store.record(key, profile_result)
    store.set_baseline(key, run_id)
    point = store.latest(key)
    if point is None:  # pragma: no cover - read-back of a just-written row
        point = _point_from(run_id, key, profile_result)
    return point