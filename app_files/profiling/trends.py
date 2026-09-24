"""Quality trend tracking: a score per run in a local SQLite database.

The profiler already produces a five-dimension scorecard for one run. That
answers "how good is this file". It cannot answer "is this source getting
better or worse", because nothing remembers yesterday's score.

This stores one row per run per source and reads them back as a trend. SQLite
is used rather than a JSON file because the access pattern is additive and
partial: append a run, then read one source's recent history without loading
every other source's.

State lives under ``AUTOFLOW_HOME`` (falling back to ``~/.autoflow``) so a
deployment can point it at a writable volume.

    store = TrendStore()
    store.record("salesforce", profile)
    store.trend("salesforce")          # oldest first
    store.latest("salesforce")
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app_files.profiling.profiler import DIMENSION_NAMES, Profile

SCHEMA = """
CREATE TABLE IF NOT EXISTS quality_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    overall REAL NOT NULL,
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    dimensions TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_quality_source_time
    ON quality_runs (source, recorded_at);
CREATE TABLE IF NOT EXISTS baselines (
    source TEXT PRIMARY KEY,
    run_id INTEGER NOT NULL,
    set_at TEXT NOT NULL
);
"""


def trend_dir() -> Path:
    """Where the trend database lives. ``AUTOFLOW_HOME`` overrides for portability."""
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "trends"


def trend_db_path() -> Path:
    return trend_dir() / "quality.db"


@dataclass(frozen=True)
class QualityPoint:
    """One recorded run's score for one source."""

    id: int
    source: str
    recorded_at: str
    overall: float
    row_count: int
    column_count: int
    dimensions: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "recorded_at": self.recorded_at,
            "overall": self.overall,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "dimensions": self.dimensions,
        }


@dataclass
class TrendStore:
    """Append-only quality history, one row per run per source."""

    path: Path = field(default_factory=trend_db_path)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        try:
            connection.executescript(SCHEMA)
            yield connection
            connection.commit()
        finally:
            connection.close()

    def record(
        self,
        source: str,
        profile_result: Profile,
        recorded_at: datetime | None = None,
    ) -> int:
        """Append one run. Returns the new row's id."""
        import json

        moment = (recorded_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        dimensions = {
            name: float(profile_result.scores.get(name, 0.0)) for name in DIMENSION_NAMES
        }
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO quality_runs "
                "(source, recorded_at, overall, row_count, column_count, dimensions) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(source),
                    moment.isoformat(),
                    float(profile_result.overall),
                    int(profile_result.row_count),
                    int(profile_result.column_count),
                    json.dumps(dimensions),
                ),
            )
            return int(cursor.lastrowid or 0)

    def trend(self, source: str, limit: int | None = None) -> list[QualityPoint]:
        """That source's runs, oldest first."""
        return self._read(source, limit=limit, newest_first=False)

    def recent(self, source: str, limit: int = 10) -> list[QualityPoint]:
        """That source's newest runs, newest first."""
        return self._read(source, limit=limit, newest_first=True)

    def _read(
        self, source: str, limit: int | None, newest_first: bool
    ) -> list[QualityPoint]:
        import json

        order = "DESC" if newest_first else "ASC"
        query = (
            "SELECT id, source, recorded_at, overall, row_count, column_count, dimensions "
            f"FROM quality_runs WHERE source = ? ORDER BY recorded_at {order}, id {order}"
        )
        parameters: tuple[Any, ...] = (str(source),)
        if limit is not None:
            query += " LIMIT ?"
            parameters += (int(limit),)
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [
            QualityPoint(
                id=int(row[0]),
                source=str(row[1]),
                recorded_at=str(row[2]),
                overall=float(row[3]),
                row_count=int(row[4]),
                column_count=int(row[5]),
                dimensions={str(k): float(v) for k, v in json.loads(row[6]).items()},
            )
            for row in rows
        ]

    def latest(self, source: str) -> QualityPoint | None:
        points = self.recent(source, limit=1)
        return points[0] if points else None

    def sources(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT source FROM quality_runs ORDER BY source"
            ).fetchall()
        return [str(row[0]) for row in rows]

    # ------------------------------------------------------------- baselines

    def set_baseline(self, source: str, run_id: int) -> None:
        """Pin one recorded run as the baseline for a source."""
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO baselines (source, run_id, set_at) VALUES (?, ?, ?) "
                "ON CONFLICT(source) DO UPDATE SET run_id = excluded.run_id, "
                "set_at = excluded.set_at",
                (str(source), int(run_id), datetime.now(timezone.utc).isoformat()),
            )

    def baseline(self, source: str) -> QualityPoint | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT run_id FROM baselines WHERE source = ?", (str(source),)
            ).fetchone()
            if row is None:
                return None
            found = connection.execute(
                "SELECT id, source, recorded_at, overall, row_count, column_count, dimensions "
                "FROM quality_runs WHERE id = ?",
                (int(row[0]),),
            ).fetchone()
        if found is None:
            return None
        import json

        return QualityPoint(
            id=int(found[0]),
            source=str(found[1]),
            recorded_at=str(found[2]),
            overall=float(found[3]),
            row_count=int(found[4]),
            column_count=int(found[5]),
            dimensions={str(k): float(v) for k, v in json.loads(found[6]).items()},
        )

    def clear(self, source: str | None = None) -> int:
        """Delete history. Returns the number of rows removed."""
        with self._connect() as connection:
            if source is None:
                removed = connection.execute("SELECT COUNT(*) FROM quality_runs").fetchone()[0]
                connection.execute("DELETE FROM quality_runs")
                connection.execute("DELETE FROM baselines")
            else:
                removed = connection.execute(
                    "SELECT COUNT(*) FROM quality_runs WHERE source = ?", (str(source),)
                ).fetchone()[0]
                connection.execute("DELETE FROM quality_runs WHERE source = ?", (str(source),))
                connection.execute("DELETE FROM baselines WHERE source = ?", (str(source),))
        return int(removed)


def trend_direction(points: list[QualityPoint]) -> str:
    """``improving``, ``declining`` or ``stable`` over the recorded runs.

    Compares the mean of the first half with the mean of the second, which
    ignores a single noisy run at either end in a way that first-vs-last does
    not.
    """
    if len(points) < 2:
        return "stable"
    half = len(points) // 2
    earlier = points[:half] or points[:1]
    later = points[-half:] or points[-1:]
    earlier_mean = sum(point.overall for point in earlier) / len(earlier)
    later_mean = sum(point.overall for point in later) / len(later)
    delta = later_mean - earlier_mean
    if delta > 0.5:
        return "improving"
    if delta < -0.5:
        return "declining"
    return "stable"


def render_trend_html(points: list[QualityPoint], source: str) -> str:
    """A compact trend table for the report."""
    if not points:
        return (
            f"<div class='trend'><p>No recorded runs for {source}.</p></div>"
        )
    direction = trend_direction(points)
    first, last = points[0].overall, points[-1].overall
    rows = "".join(
        f"<tr><td>{point.recorded_at[:19]}</td><td>{point.overall:.1f}</td>"
        f"<td>{point.row_count}</td></tr>"
        for point in points
    )
    return (
        "<div class='trend'>"
        f"<p><strong>{source}</strong>: {direction} "
        f"({first:.1f} \u2192 {last:.1f} over {len(points)} runs)</p>"
        "<table><thead><tr><th>Recorded</th><th>Score</th><th>Rows</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )
