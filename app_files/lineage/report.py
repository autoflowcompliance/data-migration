"""Write a lineage log to ``lineage_report.csv`` (and a short text summary)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app_files.lineage.tracker import LineageTracker


def write_lineage_report(
    tracker: LineageTracker, path: str | Path = "lineage_report.csv"
) -> Path:
    """Write the tracker's events to ``path`` and return the path written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tracker.to_frame().to_csv(path, index=False)
    return path


def lineage_summary(tracker: LineageTracker) -> dict[str, Any]:
    """Counts describing the log, for embedding in a QA report or the UI."""
    frame = tracker.to_frame()
    return {
        "total_events": tracker.total_events,
        "rows_touched": int(frame["source_row"].nunique()) if not frame.empty else 0,
        "actions": tracker.actions(),
    }


def render_lineage_html(tracker: LineageTracker, limit: int = 200) -> str:
    """A small standalone HTML view of the lineage log."""
    frame = tracker.to_frame()
    summary = lineage_summary(tracker)
    rows = "".join(
        "<tr>"
        + "".join(f"<td>{'' if pd.isna(v) else v}</td>" for v in row)
        + "</tr>"
        for row in frame.head(limit).itertuples(index=False)
    )
    header = "".join(f"<th>{column}</th>" for column in frame.columns)
    actions = ", ".join(f"{name}: {count}" for name, count in summary["actions"].items())
    return (
        "<html><head><meta charset='utf-8'><title>Lineage report</title>"
        "<style>body{font-family:sans-serif;padding:24px;color:#111827;}"
        "table{border-collapse:collapse;width:100%;font-size:13px;}"
        "th,td{border-bottom:1px solid #e5e7eb;padding:6px 8px;text-align:left;}"
        "th{background:#f3f4f6;}</style></head><body>"
        "<h1>Transformation lineage</h1>"
        f"<p>{summary['total_events']} events across {summary['rows_touched']} source rows."
        f"{(' Actions &mdash; ' + actions) if actions else ''}</p>"
        f"<table><tr>{header}</tr>{rows}</table>"
        "</body></html>"
    )