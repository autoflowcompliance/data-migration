"""Anomaly detection over learned quality-dimension ranges.

The column-shape detector in ``app_files.intelligence.anomaly`` notices a column
that suddenly fills with nulls. It cannot notice that a source's *validity*
score has drifted outside anything it normally produces, because it has no
memory of previous scores.

This learns a normal range per dimension from the recorded history and flags a
run that falls outside it, so an anomaly surfaces without anyone writing a rule
for it. Needs enough history to be meaningful: below the minimum sample count it
reports ``learning`` rather than guessing.

    store = TrendStore()
    report = detect_dimension_anomalies("salesforce", current_profile, store)
    report.anomalies          # dimensions outside the learned range
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from app_files.profiling.profiler import DIMENSION_NAMES, Profile
from app_files.profiling.trends import QualityPoint, TrendStore

#: Runs needed before a range is trusted.
MIN_SAMPLES = 5
#: How many recent runs to learn from.
LEARNING_WINDOW = 30
#: A dimension is anomalous outside mean +/- this many standard deviations.
SIGMA = 3.0
#: Floor on the spread, so a perfectly stable source does not flag every
#: one-point wobble as a three-sigma event.
MIN_STDDEV = 1.0


@dataclass(frozen=True)
class DimensionRange:
    dimension: str
    mean: float
    stddev: float
    low: float
    high: float
    samples: int

    def contains(self, value: float) -> bool:
        return self.low <= value <= self.high

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "mean": round(self.mean, 2),
            "stddev": round(self.stddev, 2),
            "low": round(self.low, 2),
            "high": round(self.high, 2),
            "samples": self.samples,
        }


@dataclass
class DimensionAnomaly:
    dimension: str
    value: float
    expected_low: float
    expected_high: float
    mean: float

    @property
    def direction(self) -> str:
        return "below" if self.value < self.expected_low else "above"

    @property
    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "value": round(self.value, 1),
            "expected_low": round(self.expected_low, 1),
            "expected_high": round(self.expected_high, 1),
            "mean": round(self.mean, 1),
            "direction": self.direction,
        }


@dataclass
class DimensionAnomalyReport:
    source: str
    learning: bool
    samples: int
    anomalies: list[DimensionAnomaly] = field(default_factory=list)
    ranges: dict[str, DimensionRange] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return not self.anomalies

    @property
    def status(self) -> str:
        if self.learning:
            return f"LEARNING ({self.samples} runs)"
        return "OK" if self.clean else f"{len(self.anomalies)} ANOMALY(IES)"

    def summary(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "learning": self.learning,
            "samples": self.samples,
            "status": self.status,
            "anomalies": [anomaly.as_dict for anomaly in self.anomalies],
            "ranges": {name: rng.as_dict() for name, rng in self.ranges.items()},
        }

    def render_html(self) -> str:
        if self.learning:
            return (
                "<div class='dimension-anomaly'><p>"
                f"Learning normal ranges for {self.source} "
                f"({self.samples} of {MIN_SAMPLES} runs so far).</p></div>"
            )
        if self.clean:
            return (
                "<div class='dimension-anomaly'><p>"
                f"No anomalies for {self.source}.</p></div>"
            )
        rows = "".join(
            f"<tr><td>{anomaly.dimension}</td><td>{anomaly.value:.1f}</td>"
            f"<td>{anomaly.expected_low:.1f}\u2013{anomaly.expected_high:.1f}</td>"
            f"<td>{anomaly.direction}</td></tr>"
            for anomaly in self.anomalies
        )
        return (
            "<div class='dimension-anomaly alert'>"
            f"<p>{len(self.anomalies)} dimension(s) outside the learned range "
            f"for {self.source}.</p>"
            "<table><thead><tr><th>Dimension</th><th>Value</th><th>Expected</th>"
            f"<th>Direction</th></tr></thead><tbody>{rows}</tbody></table></div>"
        )


def learn_ranges(
    points: list[QualityPoint], sigma: float = SIGMA
) -> dict[str, DimensionRange]:
    """Mean and sigma bounds per dimension from recorded history."""
    ranges: dict[str, DimensionRange] = {}
    for dimension in DIMENSION_NAMES:
        values = [
            point.dimensions[dimension]
            for point in points
            if dimension in point.dimensions
        ]
        if not values:
            continue
        mean = statistics.fmean(values)
        stddev = statistics.pstdev(values) if len(values) > 1 else 0.0
        spread = max(stddev * sigma, MIN_STDDEV)
        ranges[dimension] = DimensionRange(
            dimension=dimension,
            mean=mean,
            stddev=stddev,
            low=max(0.0, mean - spread),
            high=min(100.0, mean + spread),
            samples=len(values),
        )
    return ranges


def detect_dimension_anomalies(
    source: str,
    current: Profile,
    store: TrendStore,
    *,
    sigma: float = SIGMA,
    min_samples: int = MIN_SAMPLES,
    window: int = LEARNING_WINDOW,
) -> DimensionAnomalyReport:
    """Flag dimensions of ``current`` outside the range learned for ``source``.

    The history is read *before* the current run is recorded by the caller, so a
    run is never part of the range it is judged against.
    """
    history = store.recent(source, limit=window)
    if len(history) < min_samples:
        return DimensionAnomalyReport(
            source=source, learning=True, samples=len(history)
        )
    ranges = learn_ranges(history, sigma=sigma)
    anomalies = []
    for dimension, rng in ranges.items():
        value = float(current.scores.get(dimension, 0.0))
        if not rng.contains(value):
            anomalies.append(
                DimensionAnomaly(
                    dimension=dimension,
                    value=value,
                    expected_low=rng.low,
                    expected_high=rng.high,
                    mean=rng.mean,
                )
            )
    anomalies.sort(key=lambda anomaly: anomaly.dimension)
    return DimensionAnomalyReport(
        source=source,
        learning=False,
        samples=len(history),
        anomalies=anomalies,
        ranges=ranges,
    )
