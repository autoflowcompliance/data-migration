"""Prometheus-compatible metrics.

A small registry in the exposition format Prometheus scrapes: counters, gauges
and histograms, each with labels. No client library and no network, so a scrape
endpoint is the only thing an operator has to add.

Runs emit through :func:`record_run`, which keeps the naming in one place. The
names are the contract: a dashboard written against them should not have to
change when the pipeline changes underneath.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

RUNS_TOTAL = "dataflow_runs_total"
RUN_DURATION_SECONDS = "dataflow_run_duration_seconds"
RUN_FAILURES_TOTAL = "dataflow_run_failures_total"
QUALITY_SCORE = "dataflow_quality_score"
ROWS_PROCESSED = "dataflow_rows_processed_total"


def _escape(value: Any) -> str:
    text = str(value)
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _labels(pairs: Mapping[str, Any]) -> str:
    if not pairs:
        return ""
    inside = ",".join(f'{key}="{_escape(value)}"' for key, value in sorted(pairs.items()))
    return "{" + inside + "}"


def _key(labels: Mapping[str, Any] | None) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in (labels or {}).items()))


@dataclass
class Counter:
    """A number that only goes up, per label set."""

    name: str
    help: str = ""
    values: dict[tuple[tuple[str, str], ...], float] = field(default_factory=dict)

    def inc(self, amount: float = 1.0, labels: Mapping[str, Any] | None = None) -> None:
        if amount < 0:
            raise ValueError("A counter cannot decrease")
        key = _key(labels)
        self.values[key] = self.values.get(key, 0.0) + amount

    def value(self, labels: Mapping[str, Any] | None = None) -> float:
        return self.values.get(_key(labels), 0.0)

    def samples(self) -> Iterator[tuple[str, dict[str, str], float]]:
        for key, value in sorted(self.values.items()):
            yield self.name, dict(key), value

    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} counter"]
        for name, labels, value in self.samples():
            lines.append(f"{name}{_labels(labels)} {value}")
        return "\n".join(lines)


@dataclass
class Gauge:
    """A number that goes up and down, per label set."""

    name: str
    help: str = ""
    values: dict[tuple[tuple[str, str], ...], float] = field(default_factory=dict)

    def set(self, value: float, labels: Mapping[str, Any] | None = None) -> None:
        self.values[_key(labels)] = float(value)

    def inc(self, amount: float = 1.0, labels: Mapping[str, Any] | None = None) -> None:
        key = _key(labels)
        self.values[key] = self.values.get(key, 0.0) + amount

    def value(self, labels: Mapping[str, Any] | None = None) -> float:
        return self.values.get(_key(labels), 0.0)

    def samples(self) -> Iterator[tuple[str, dict[str, str], float]]:
        for key, value in sorted(self.values.items()):
            yield self.name, dict(key), value

    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} gauge"]
        for name, labels, value in self.samples():
            lines.append(f"{name}{_labels(labels)} {value}")
        return "\n".join(lines)


@dataclass
class Histogram:
    """Observations bucketed into cumulative ranges.

    ``count`` and ``sum`` are exposed alongside the buckets, which is what an
    averaging query needs. The default buckets suit run durations in seconds.
    """

    name: str
    help: str = ""
    buckets: tuple[float, ...] = (0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 300.0)
    observations: dict[tuple[tuple[str, str], ...], list[float]] = field(default_factory=dict)

    def observe(self, value: float, labels: Mapping[str, Any] | None = None) -> None:
        self.observations.setdefault(_key(labels), []).append(float(value))

    def count(self, labels: Mapping[str, Any] | None = None) -> int:
        return len(self.observations.get(_key(labels), []))

    def total(self, labels: Mapping[str, Any] | None = None) -> float:
        return float(sum(self.observations.get(_key(labels), [])))

    def bucket_counts(self, key: tuple[tuple[str, str], ...]) -> list[int]:
        values = self.observations.get(key, [])
        return [sum(1 for value in values if value <= bound) for bound in self.buckets]

    def samples(self) -> Iterator[tuple[str, dict[str, str], float]]:
        for key, values in sorted(self.observations.items()):
            labels = dict(key)
            cumulative = self.bucket_counts(key)
            for bound, count in zip(self.buckets, cumulative, strict=True):
                yield f"{self.name}_bucket", {**labels, "le": repr(bound)}, float(count)
            yield f"{self.name}_bucket", {**labels, "le": "+Inf"}, float(len(values))
            yield f"{self.name}_count", labels, float(len(values))
            yield f"{self.name}_sum", labels, float(sum(values))

    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} histogram"]
        for name, labels, value in self.samples():
            lines.append(f"{name}{_labels(labels)} {value}")
        return "\n".join(lines)


class MetricsRegistry:
    """Holds the metrics an operator can scrape."""

    def __init__(self) -> None:
        self._metrics: dict[str, Counter | Gauge | Histogram] = {}
        self._declare_defaults()

    def _declare_defaults(self) -> None:
        self.counter(RUNS_TOTAL, "Runs started, by source and status")
        self.histogram(RUN_DURATION_SECONDS, "Run duration in seconds, by source")
        self.counter(RUN_FAILURES_TOTAL, "Runs that failed, by source and reason")
        self.gauge(QUALITY_SCORE, "Most recent quality score, by source")
        self.counter(ROWS_PROCESSED, "Rows processed, by source")

    def counter(self, name: str, help: str = "") -> Counter:
        existing = self._metric(name)
        if isinstance(existing, Counter):
            return existing
        metric = Counter(name, help)
        self._metrics[name] = metric
        return metric

    def gauge(self, name: str, help: str = "") -> Gauge:
        existing = self._metric(name)
        if isinstance(existing, Gauge):
            return existing
        metric = Gauge(name, help)
        self._metrics[name] = metric
        return metric

    def histogram(
        self, name: str, help: str = "", buckets: Iterable[float] | None = None
    ) -> Histogram:
        existing = self._metric(name)
        if isinstance(existing, Histogram):
            return existing
        kwargs: dict[str, Any] = {}
        if buckets is not None:
            kwargs["buckets"] = tuple(buckets)
        metric = Histogram(name, help, **kwargs)
        self._metrics[name] = metric
        return metric

    def _metric(self, name: str) -> Counter | Gauge | Histogram | None:
        return self._metrics.get(name)

    def register(self, metric: Counter | Gauge | Histogram) -> None:
        self._metrics[metric.name] = metric

    @property
    def names(self) -> list[str]:
        return sorted(self._metrics)

    def render(self) -> str:
        blocks = [metric.render() for metric in (self._metrics[name] for name in self.names)]
        return "\n".join(blocks) + "\n"


_DEFAULT = MetricsRegistry()


def default_registry() -> MetricsRegistry:
    return _DEFAULT


def record_run(
    source: str,
    status: str,
    duration_seconds: float,
    quality_score: float | None = None,
    rows: int = 0,
    reason: str | None = None,
    registry: MetricsRegistry | None = None,
) -> None:
    """Record one pipeline run. Never raises, so it cannot fail a run."""
    target = registry or _DEFAULT
    labels = {"source": source}
    target.counter(RUNS_TOTAL, "Runs started, by source and status").inc(
        1.0, {**labels, "status": status}
    )
    target.histogram(RUN_DURATION_SECONDS, "Run duration in seconds, by source").observe(
        duration_seconds, labels
    )
    if rows:
        target.counter(ROWS_PROCESSED, "Rows processed, by source").inc(
            float(rows), labels
        )
    if quality_score is not None:
        target.gauge(QUALITY_SCORE, "Most recent quality score, by source").set(
            float(quality_score), labels
        )
    if status == "failed":
        target.counter(RUN_FAILURES_TOTAL, "Runs that failed, by source and reason").inc(
            1.0, {**labels, "reason": reason or "unknown"}
        )


def render_prometheus(registry: MetricsRegistry | None = None) -> str:
    return (registry or _DEFAULT).render()


__all__ = [
    "QUALITY_SCORE",
    "ROWS_PROCESSED",
    "RUNS_TOTAL",
    "RUN_DURATION_SECONDS",
    "RUN_FAILURES_TOTAL",
    "Counter",
    "Gauge",
    "Histogram",
    "MetricsRegistry",
    "default_registry",
    "record_run",
    "render_prometheus",
]
