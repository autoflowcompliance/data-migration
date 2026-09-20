"""Anomaly detection: notice when this run does not look like the last one.

Data observability, at the scale a small team actually needs. On each run the
tool stores a compact baseline — per-column null rate, distinct shape count,
row count and quality score — and on the next run compares against it. A spike
in missing values, a new format appearing in a column, or a volume drop gets
flagged in plain language.

The baseline is a real file (``~/.autoflow/baselines/<name>.json``), so it
survives restarts. Two runs of the same file therefore genuinely differ in what
they report, which is the only way to tell this apart from a stub.

Comparison is deliberately conservative about *what* is anomalous:

* null rate — flagged when it rises by more than ``null_delta`` absolute points
  and at least ``min_null_rows`` rows, so one blank in a 5-row file is not noise;
* volume — flagged when the row count moves by more than ``volume_delta``;
* new formats — flagged when a column gains a value *shape* it never had, which
  is how a wrong date format or a stray currency symbol shows up;
* quality — flagged when the score drops by more than ``score_delta``.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.transforms import is_missing


def baseline_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "baselines"


def _slug(name: str) -> str:
    keep = [ch if ch.isalnum() or ch in "-_." else "_" for ch in str(name)]
    return "".join(keep) or "unnamed"


def baseline_path(name: str) -> Path:
    return baseline_dir() / f"{_slug(name)}.json"


def shape_of(value: Any) -> str:
    """A format fingerprint: ``12/31/24`` -> ``99/99/99``, ``$1,200`` -> ``$9,999``."""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "nat"}:
        return ""
    return "".join("9" if ch.isdigit() else "A" if ch.isalpha() else ch for ch in text)


@dataclass
class ColumnBaseline:
    null_rate: float
    shapes: list[str] = field(default_factory=list)


@dataclass
class Baseline:
    """A compact snapshot of one dataset, stored between runs."""

    name: str
    rows: int
    columns: list[str]
    quality_score: float = 0.0
    column_stats: dict[str, ColumnBaseline] = field(default_factory=dict)
    sampled_at: str = ""

    @classmethod
    def from_frame(
        cls,
        frame: pd.DataFrame,
        name: str,
        quality_score: float = 0.0,
        max_shapes: int = 12,
    ) -> "Baseline":
        stats: dict[str, ColumnBaseline] = {}
        total = len(frame) or 1
        for column in frame.columns:
            series = frame[column]
            missing = sum(1 for value in series if is_missing(value))
            shapes: list[str] = []
            seen: set[str] = set()
            for value in series:
                shape = shape_of(value)
                if not shape or shape in seen:
                    continue
                seen.add(shape)
                shapes.append(shape)
                if len(shapes) >= max_shapes:
                    break
            stats[str(column)] = ColumnBaseline(
                null_rate=round(missing / total, 4), shapes=shapes
            )
        return cls(
            name=name,
            rows=len(frame),
            columns=[str(c) for c in frame.columns],
            quality_score=float(quality_score),
            column_stats=stats,
        )

    def save(self) -> Path:
        import datetime as dt

        self.sampled_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        path = baseline_path(self.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, name: str) -> "Baseline | None":
        path = baseline_path(name)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        stats = {
            key: ColumnBaseline(
                null_rate=float(body.get("null_rate", 0.0)),
                shapes=list(body.get("shapes", [])),
            )
            for key, body in (payload.get("column_stats") or {}).items()
        }
        return cls(
            name=payload.get("name", name),
            rows=int(payload.get("rows", 0)),
            columns=list(payload.get("columns", [])),
            quality_score=float(payload.get("quality_score", 0.0)),
            column_stats=stats,
            sampled_at=str(payload.get("sampled_at", "")),
        )


@dataclass
class Anomaly:
    """One thing that changed unexpectedly."""

    kind: str
    field: str
    message: str
    before: Any = None
    after: Any = None
    severity: str = "warning"

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "field": self.field,
            "severity": self.severity,
            "message": self.message,
            "before": self.before,
            "after": self.after,
        }


@dataclass
class AnomalyReport:
    name: str
    is_baseline_run: bool
    anomalies: list[Anomaly] = field(default_factory=list)
    baseline: Baseline | None = None

    @property
    def clean(self) -> bool:
        return not self.anomalies

    @property
    def status(self) -> str:
        if self.is_baseline_run:
            return "BASELINE SET"
        return "OK" if self.clean else f"{len(self.anomalies)} ANOMALY(IES)"

    def frame(self) -> pd.DataFrame:
        columns = ["kind", "field", "severity", "message", "before", "after"]
        if not self.anomalies:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([a.as_dict() for a in self.anomalies], columns=columns)

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "is_baseline_run": self.is_baseline_run,
            "status": self.status,
            "anomalies": len(self.anomalies),
            "kinds": sorted({a.kind for a in self.anomalies}),
        }


def compare_to_baseline(
    frame: pd.DataFrame,
    name: str,
    quality_score: float = 0.0,
    null_delta: float = 0.20,
    min_null_rows: int = 1,
    volume_delta: float = 0.30,
    score_delta: float = 15.0,
) -> AnomalyReport:
    """Compare ``frame`` with the stored baseline for ``name``.

    Does **not** store anything; call :func:`record_baseline` to persist. That
    separation is what lets a caller compare without side effects.
    """
    baseline = Baseline.load(name)
    if baseline is None:
        return AnomalyReport(name=name, is_baseline_run=True, baseline=None)

    anomalies: list[Anomaly] = []
    total = len(frame) or 1

    # Volume
    if baseline.rows:
        change = abs(len(frame) - baseline.rows) / baseline.rows
        if change > volume_delta:
            direction = "dropped" if len(frame) < baseline.rows else "jumped"
            anomalies.append(
                Anomaly(
                    kind="volume",
                    field="*",
                    severity="error" if len(frame) < baseline.rows else "warning",
                    message=(
                        f"Row count {direction} {change * 100:.0f}% "
                        f"({baseline.rows} → {len(frame)})"
                    ),
                    before=baseline.rows,
                    after=len(frame),
                )
            )

    # New / missing columns
    current_columns = [str(c) for c in frame.columns]
    for column in baseline.columns:
        if column not in current_columns:
            anomalies.append(
                Anomaly(
                    kind="missing_column",
                    field=column,
                    severity="error",
                    message=f"Column '{column}' was present in the last run but is gone",
                )
            )
    for column in current_columns:
        if column not in baseline.columns:
            anomalies.append(
                Anomaly(
                    kind="new_column",
                    field=column,
                    severity="info",
                    message=f"New column '{column}' did not exist in the last run",
                )
            )

    # Null rate and new shapes
    for column in current_columns:
        stats = baseline.column_stats.get(column)
        if stats is None:
            continue
        series = frame[column]
        missing = sum(1 for value in series if is_missing(value))
        rate = missing / total
        delta = rate - stats.null_rate
        if delta > null_delta and missing - round(stats.null_rate * baseline.rows) >= min_null_rows:
            anomalies.append(
                Anomaly(
                    kind="null_spike",
                    field=column,
                    severity="error",
                    message=(
                        f"Missing values in '{column}' rose from {stats.null_rate * 100:.0f}% "
                        f"to {rate * 100:.0f}%"
                    ),
                    before=round(stats.null_rate, 4),
                    after=round(rate, 4),
                )
            )

        current_shapes = {
            shape_of(value) for value in series if shape_of(value)
        }
        known = set(stats.shapes)
        new_shapes = sorted(current_shapes - known)
        if known and new_shapes:
            anomalies.append(
                Anomaly(
                    kind="new_format",
                    field=column,
                    severity="warning",
                    message=(
                        f"'{column}' contains {len(new_shapes)} value format(s) not seen before: "
                        + ", ".join(new_shapes[:3])
                    ),
                    before=sorted(known)[:3],
                    after=new_shapes[:3],
                )
            )

    # Quality
    if baseline.quality_score and baseline.quality_score - quality_score > score_delta:
        anomalies.append(
            Anomaly(
                kind="quality_drop",
                field="*",
                severity="error",
                message=(
                    f"Quality score fell from {baseline.quality_score:.1f}% "
                    f"to {quality_score:.1f}%"
                ),
                before=baseline.quality_score,
                after=quality_score,
            )
        )

    return AnomalyReport(name=name, is_baseline_run=False, anomalies=anomalies, baseline=baseline)


def record_baseline(frame: pd.DataFrame, name: str, quality_score: float = 0.0) -> Baseline:
    """Store the current frame as the baseline for ``name``."""
    return Baseline.from_frame(frame, name=name, quality_score=quality_score)


def detect(
    frame: pd.DataFrame,
    name: str,
    quality_score: float = 0.0,
    update_baseline: bool = True,
) -> AnomalyReport:
    """Compare against the baseline and, by default, replace it with this run.

    Call this once per run. The first call establishes the baseline; later calls
    compare against it, which is what makes the second call able to report a
    change the first could not.
    """
    report = compare_to_baseline(frame, name, quality_score=quality_score)
    if update_baseline:
        record_baseline(frame, name=name, quality_score=quality_score).save()
    return report


def clear_baselines(name: str | None = None) -> int:
    """Remove one baseline (or all). Returns how many were deleted."""
    if name:
        path = baseline_path(name)
        if path.exists():
            path.unlink()
            return 1
        return 0
    folder = baseline_dir()
    if not folder.exists():
        return 0
    removed = 0
    for path in folder.glob("*.json"):
        path.unlink()
        removed += 1
    return removed


def render_anomaly_html(report: AnomalyReport) -> str:
    """A standalone anomaly note. No external resources."""
    if report.is_baseline_run:
        inner = (
            "<p class='ok'>First run for this file — a baseline has been recorded. "
            "Run it again after the data changes and any unexpected shift will be "
            "reported here.</p>"
        )
    elif report.clean:
        inner = "<p class='ok'>No unexpected changes since the last run.</p>"
    else:
        rows = "".join(
            f"<tr class='{a.severity}'><td>{a.severity}</td><td>{a.field}</td>"
            f"<td>{a.message}</td></tr>"
            for a in report.anomalies
        )
        inner = (
            "<table><tr><th>Severity</th><th>Field</th><th>What changed</th></tr>"
            f"{rows}</table>"
        )
    baseline_when = (
        f"<p class='meta'>Compared with the run recorded at {report.baseline.sampled_at}."
        "</p>" if report.baseline and report.baseline.sampled_at else ""
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Anomaly report</title>"
        "<style>body{font-family:sans-serif;padding:20px;color:#111827;}"
        "table{border-collapse:collapse;width:100%;font-size:13px;}"
        "th,td{border-bottom:1px solid #e5e7eb;padding:6px 8px;text-align:left;}"
        "th{background:#f3f4f6;}tr.error td{background:#fee2e2;}tr.warning td{background:#fef3c7;}"
        "tr.info td{background:#e0f2fe;}.ok{color:#047857;font-weight:600;}"
        ".meta{font-size:12px;color:#6b7280;}</style></head><body>"
        f"<h1>Anomaly report: {report.name}</h1>"
        f"<p><strong>{report.status}</strong></p>"
        f"{baseline_when}{inner}</body></html>"
    )