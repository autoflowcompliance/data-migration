"""Observability: Prometheus metrics, alert rules, health checks, trends.

Four things a buyer needs to prove the system is working, and to let an
orchestrator manage it:

* **Metrics** — a counter, a gauge and a histogram, rendered in the Prometheus
  text exposition format. Run counts, durations, failures and the latest quality
  score, with the labels a dashboard needs. No client library: the format is
  small and writing it here keeps the dependency list honest.

* **Alert rules** — declarative rules over a run summary: alert on failure, on
  a quality drop below a threshold, or on a duration over an SLA. Each rule
  produces a routed alert (email, Slack, Teams, webhook), and the routing is
  data, so adding a channel is a mapping entry.

* **Health checks** — liveness and readiness. Liveness says "the process is up";
  readiness says "it can actually work", checking that the configs load and the
  output directory is writable. Kubernetes treats the two differently, so they
  are separate signals, not one endpoint pretending to be both.

* **Quality trend** — the run history as a time series, with the delta and a
  simple direction, so "is quality getting better or worse" has an answer.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ------------------------------------------------------------------- metrics
def _escape_label(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _labels(pairs: dict[str, str]) -> str:
    if not pairs:
        return ""
    inner = ",".join(f'{k}="{_escape_label(v)}"' for k, v in sorted(pairs.items()))
    return "{" + inner + "}"


@dataclass
class Counter:
    name: str
    help: str
    values: dict[tuple, float] = field(default_factory=dict)

    def inc(self, amount: float = 1.0, **labels: str) -> None:
        key = tuple(sorted(labels.items()))
        self.values[key] = self.values.get(key, 0.0) + amount

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} counter"]
        if not self.values:
            lines.append(f"{self.name} 0")
        for key, value in sorted(self.values.items()):
            lines.append(f"{self.name}{_labels(dict(key))} {_format(value)}")
        return lines


@dataclass
class Gauge:
    name: str
    help: str
    values: dict[tuple, float] = field(default_factory=dict)

    def set(self, value: float, **labels: str) -> None:
        key = tuple(sorted(labels.items()))
        self.values[key] = value

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} gauge"]
        for key, value in sorted(self.values.items()):
            lines.append(f"{self.name}{_labels(dict(key))} {_format(value)}")
        return lines


@dataclass
class Histogram:
    name: str
    help: str
    buckets: tuple[float, ...] = (0.1, 0.5, 1, 5, 15, 60, float("inf"))
    counts: dict[tuple, list[float]] = field(default_factory=dict)
    totals: dict[tuple, float] = field(default_factory=dict)

    def observe(self, value: float, **labels: str) -> None:
        key = tuple(sorted(labels.items()))
        counts = self.counts.setdefault(key, [0.0] * len(self.buckets))
        for index, bound in enumerate(self.buckets):
            if value <= bound:
                counts[index] += 1
        self.totals[key] = self.totals.get(key, 0.0) + value

    def render(self) -> list[str]:
        lines = [f"# HELP {self.name} {self.help}", f"# TYPE {self.name} histogram"]
        for key, counts in sorted(self.counts.items()):
            label_dict = dict(key)
            for bound, count in zip(self.buckets, counts):
                le = "+Inf" if bound == float("inf") else _format(bound)
                lines.append(f"{self.name}_bucket{_labels({**label_dict, 'le': le})} {_format(count)}")
            lines.append(f"{self.name}_sum{_labels(label_dict)} {_format(self.totals.get(key, 0.0))}")
            lines.append(f"{self.name}_count{_labels(label_dict)} {_format(counts[-1])}")
        return lines


def _format(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else repr(float(value))


class MetricsRegistry:
    """The metrics a DataFlow deployment exposes."""

    def __init__(self) -> None:
        self.runs_total = Counter("dataflow_runs_total", "Migration runs started or finished.")
        self.failures_total = Counter("dataflow_failures_total", "Failed runs.")
        self.rows_total = Counter("dataflow_rows_processed_total", "Rows processed.")
        self.quality_score = Gauge("dataflow_quality_score", "Latest run quality score.")
        self.run_duration = Histogram(
            "dataflow_run_duration_seconds", "Run duration in seconds."
        )
        self.losses = Counter("dataflow_losses", "Failures/errors.")

    def record_run(
        self,
        *,
        status: str,
        rows: int = 0,
        quality: float = 0.0,
        duration: float = 0.0,
        config: str = "",
        tenant: str = "",
    ) -> None:
        labels = {"config": config, "tenant": tenant}
        self.runs_total.inc(1, status=status, **labels)
        if status == "failed":
            self.failures_total.inc(1, **labels)
        if rows:
            self.rows_total.inc(rows, **labels)
        if quality:
            self.quality_score.set(quality, **labels)
        if duration:
            self.run_duration.observe(duration, **labels)

    def render(self) -> str:
        lines: list[str] = []
        for metric in (
            self.runs_total,
            self.failures_total,
            self.rows_total,
            self.quality_score,
            self.run_duration,
        ):
            lines.extend(metric.render())
        return "\n".join(lines) + "\n"


# ------------------------------------------------------------------- alerting
@dataclass
class AlertRule:
    """One condition over a run summary that raises an alert."""

    name: str
    kind: str  # "failure" | "quality_below" | "duration_above"
    threshold: float = 0.0
    channels: list[str] = field(default_factory=list)
    severity: str = "warning"

    def evaluate(self, summary: dict[str, Any]) -> "Alert | None":
        if self.kind == "failure":
            if summary.get("status") == "failed":
                return self._alert(summary, f"Run failed: {summary.get('error', 'unknown error')}")
        elif self.kind == "quality_below":
            score = summary.get("quality_score")
            if score is not None and float(score) < self.threshold:
                return self._alert(
                    summary,
                    f"Quality {score} is below the {self.threshold} threshold.",
                )
        elif self.kind == "duration_above":
            duration = summary.get("duration")
            if duration is not None and float(duration) > self.threshold:
                return self._alert(
                    summary,
                    f"Run took {duration}s, over the {self.threshold}s SLA.",
                )
        else:
            raise ValueError(f"Unknown alert kind {self.kind!r}.")
        return None

    def _alert(self, summary: dict[str, Any], message: str) -> "Alert":
        return Alert(
            rule=self.name,
            severity=self.severity,
            message=message,
            channels=list(self.channels),
            config=str(summary.get("config", "")),
            tenant=str(summary.get("tenant", "")),
        )


@dataclass
class Alert:
    rule: str
    severity: str
    message: str
    channels: list[str] = field(default_factory=list)
    config: str = ""
    tenant: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "channels": self.channels,
            "config": self.config,
            "tenant": self.tenant,
        }


def evaluate_alerts(rules: list[AlertRule], summary: dict[str, Any]) -> list[Alert]:
    alerts = []
    for rule in rules:
        alert = rule.evaluate(summary)
        if alert is not None:
            alerts.append(alert)
    return alerts


DEFAULT_CHANNEL_ROUTING = {
    "critical": ["email", "slack", "teams", "webhook"],
    "warning": ["slack"],
    "info": [],
}


def route_channels(alert: Alert, routing: dict[str, list[str]] | None = None) -> list[str]:
    """Which channels an alert goes to: the rule's own, else the severity default."""
    if alert.channels:
        return list(alert.channels)
    table = routing or DEFAULT_CHANNEL_ROUTING
    return list(table.get(alert.severity, []))


def deliver_alerts(alerts: list[Alert], sender: Any, routing: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    """Push each alert to each routed channel via ``sender(channel, alert)``.

    A channel failure is reported per-channel rather than raised, so one dead
    webhook does not stop the email going out.
    """
    results = []
    for alert in alerts:
        for channel in route_channels(alert, routing):
            try:
                sender(channel, alert)
                results.append({"channel": channel, "rule": alert.rule, "delivered": True})
            except Exception as exc:  # noqa: BLE001 - one channel must not sink the rest
                results.append(
                    {"channel": channel, "rule": alert.rule, "delivered": False, "error": str(exc)}
                )
    return results


# --------------------------------------------------------------- health checks
def health_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path(__file__).resolve().parent.parent.parent
    return base / "health"


@dataclass
class HealthStatus:
    name: str
    ok: bool
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def liveness() -> HealthStatus:
    """The process is up. Cheap enough for a probe every few seconds."""
    return HealthStatus(name="liveness", ok=True, detail="process is running")


def readiness(output_dir: str | Path | None = None, configs_dir: str | Path | None = None) -> HealthStatus:
    """Can the service actually work: configs load and output is writable."""
    from app_files.mappers.schema import load_mapping_config

    problems: list[str] = []

    configs = Path(configs_dir) if configs_dir else _default_configs_dir()
    if not configs.is_dir():
        problems.append(f"configs directory {configs} is missing")
    else:
        yaml_files = sorted(configs.glob("*.yaml"))
        if not yaml_files:
            problems.append(f"no target configs found in {configs}")
        for path in yaml_files:
            try:
                load_mapping_config(path)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"config {path.name} does not load: {exc}")

    destination = Path(output_dir) if output_dir else health_dir() / "probe"
    try:
        destination.mkdir(parents=True, exist_ok=True)
        probe = destination / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        problems.append(f"output directory {destination} is not writable: {exc}")

    if problems:
        return HealthStatus(name="readiness", ok=False, detail="; ".join(problems))
    return HealthStatus(name="readiness", ok=True, detail="configs load and output is writable")


def _default_configs_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "configs"


def full_health(output_dir: str | Path | None = None) -> dict[str, Any]:
    checks = [liveness(), readiness(output_dir)]
    return {
        "ok": all(check.ok for check in checks),
        "checks": [check.as_dict() for check in checks],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


# --------------------------------------------------------------- quality trend
def trend_path(tenant: str = "") -> Path:
    base = health_dir()
    base.mkdir(parents=True, exist_ok=True)
    return base / (f"trend_{tenant}.jsonl" if tenant else "trend.jsonl")


@dataclass
class TrendEntry:
    timestamp: str
    quality_score: float
    rows_in: int
    rows_out: int
    config: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "quality_score": self.quality_score,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "config": self.config,
        }


def record_trend(
    quality_score: float,
    *,
    rows_in: int = 0,
    rows_out: int = 0,
    config: str = "",
    tenant: str = "",
) -> TrendEntry:
    entry = TrendEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        quality_score=float(quality_score),
        rows_in=int(rows_in),
        rows_out=int(rows_out),
        config=config,
    )
    path = trend_path(tenant)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.as_dict()) + "\n")
    return entry


def read_trend(tenant: str = "") -> list[dict[str, Any]]:
    path = trend_path(tenant)
    if not path.exists():
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                entries.append(json.loads(line))
    return entries


@dataclass
class TrendSummary:
    entries: int
    latest: float | None
    previous: float | None
    delta: float | None
    direction: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "entries": self.entries,
            "latest": self.latest,
            "previous": self.previous,
            "delta": self.delta,
            "direction": self.direction,
        }


def summarise_trend(entries: list[dict[str, Any]]) -> TrendSummary:
    """The latest score, the delta from the one before, and a direction."""
    scores = [float(e["quality_score"]) for e in entries if "quality_score" in e]
    if not scores:
        return TrendSummary(0, None, None, None, "no data")
    latest = scores[-1]
    previous = scores[-2] if len(scores) > 1 else None
    delta = None if previous is None else round(latest - previous, 2)
    if delta is None:
        direction = "baseline"
    elif delta > 0:
        direction = "improving"
    elif delta < 0:
        direction = "declining"
    else:
        direction = "flat"
    return TrendSummary(len(scores), latest, previous, delta, direction)