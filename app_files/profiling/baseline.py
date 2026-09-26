"""Baseline comparison: is this run worse than the run we accepted?

A trend shows drift over many runs. This compares one run against a pinned
baseline and raises an alert when a dimension falls past a threshold, so a
regression is caught on the run it happens rather than three runs later.

    store = TrendStore()
    store.set_baseline("salesforce", store.record("salesforce", first_profile))
    comparison = compare_to_baseline(current_profile, store.baseline("salesforce"))
    if comparison.alerting:
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app_files.profiling.profiler import DIMENSION_NAMES, Profile
from app_files.profiling.trends import QualityPoint

#: A dimension must fall at least this many points below baseline to alert.
DEFAULT_DROP_THRESHOLD = 5.0


@dataclass(frozen=True)
class DimensionDrift:
    dimension: str
    baseline: float
    current: float

    @property
    def delta(self) -> float:
        return round(self.current - self.baseline, 1)

    @property
    def dropped(self) -> bool:
        return self.delta < 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "baseline": self.baseline,
            "current": self.current,
            "delta": self.delta,
        }


@dataclass
class BaselineComparison:
    source: str
    baseline_at: str
    overall_baseline: float
    overall_current: float
    drifts: list[DimensionDrift] = field(default_factory=list)
    threshold: float = DEFAULT_DROP_THRESHOLD

    @property
    def overall_delta(self) -> float:
        return round(self.overall_current - self.overall_baseline, 1)

    @property
    def regressed_dimensions(self) -> list[str]:
        return [
            drift.dimension
            for drift in self.drifts
            if drift.delta <= -self.threshold
        ]

    @property
    def alerting(self) -> bool:
        """True when any dimension fell past the threshold."""
        return bool(self.regressed_dimensions)

    def summary(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "baseline_at": self.baseline_at,
            "overall_baseline": self.overall_baseline,
            "overall_current": self.overall_current,
            "overall_delta": self.overall_delta,
            "alerting": self.alerting,
            "regressed_dimensions": self.regressed_dimensions,
            "drifts": [drift.as_dict() for drift in self.drifts],
        }

    def render_html(self) -> str:
        if not self.alerting:
            return (
                "<div class='baseline'>"
                f"<p>Within baseline. Overall {self.overall_baseline:.1f} \u2192 "
                f"{self.overall_current:.1f}.</p></div>"
            )
        rows = "".join(
            f"<tr><td>{drift.dimension}</td><td>{drift.baseline:.1f}</td>"
            f"<td>{drift.current:.1f}</td><td>{drift.delta:+.1f}</td></tr>"
            for drift in self.drifts
            if drift.dimension in self.regressed_dimensions
        )
        return (
            "<div class='baseline alert'>"
            f"<p>Regression against baseline: {', '.join(self.regressed_dimensions)}.</p>"
            "<table><thead><tr><th>Dimension</th><th>Baseline</th><th>Now</th>"
            f"<th>Change</th></tr></thead><tbody>{rows}</tbody></table></div>"
        )


def _baseline_scores(baseline: Profile | QualityPoint) -> dict[str, float]:
    if isinstance(baseline, QualityPoint):
        return dict(baseline.dimensions)
    return {name: float(baseline.scores.get(name, 0.0)) for name in DIMENSION_NAMES}


def _baseline_overall(baseline: Profile | QualityPoint) -> float:
    return float(baseline.overall)


def _baseline_time(baseline: Profile | QualityPoint) -> str:
    return baseline.recorded_at if isinstance(baseline, QualityPoint) else ""


def compare_to_baseline(
    current: Profile,
    baseline: Profile | QualityPoint,
    source: str = "unnamed",
    threshold: float = DEFAULT_DROP_THRESHOLD,
) -> BaselineComparison:
    """Compare one run's profile against a pinned baseline."""
    baseline_scores = _baseline_scores(baseline)
    drifts = []
    for dimension in DIMENSION_NAMES:
        before = baseline_scores.get(dimension)
        if before is None:
            continue
        after = float(current.scores.get(dimension, 0.0))
        drifts.append(DimensionDrift(dimension, round(before, 1), round(after, 1)))
    return BaselineComparison(
        source=source,
        baseline_at=_baseline_time(baseline),
        overall_baseline=round(_baseline_overall(baseline), 1),
        overall_current=round(current.overall, 1),
        drifts=drifts,
        threshold=threshold,
    )


def compare_to_stored_baseline(
    source: str,
    current: Profile,
    store,
    threshold: float = DEFAULT_DROP_THRESHOLD,
) -> BaselineComparison | None:
    """Compare against the baseline pinned in ``store``, or ``None`` if unset."""
    baseline = store.baseline(source)
    if baseline is None:
        return None
    return compare_to_baseline(current, baseline, source=source, threshold=threshold)
