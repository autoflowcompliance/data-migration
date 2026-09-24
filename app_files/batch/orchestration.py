"""Scheduling, dependency chains, retries and incremental processing.

Four triggers and behaviours layered onto the existing batch engine. None of
them changes how a file is processed; they decide *when* a job runs and *what
happens* when it fails.

- **Schedule**: a cron expression and the next few fire times, so a caller can
  drive the existing batch runner on a timer. ``due()`` answers "should this job
  run now" without a long-running process.
- **Dependency chains**: a job waits on named predecessors. A failed upstream
  job halts everything downstream of it.
- **Retry**: exponential backoff with a cap, for a transient failure.
- **Incremental**: fingerprint each processed record so a repeat run over an
  unchanged file does no work.

There is no daemon here. The scheduler computes times; the caller decides when
to tick it, which keeps the behaviour testable without sleeping.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.transforms import is_missing

# ------------------------------------------------------------------ cron


@dataclass(frozen=True)
class CronSchedule:
    """A five-field cron expression: minute hour day month weekday."""

    expression: str

    def __post_init__(self) -> None:
        fields = self.expression.split()
        if len(fields) != 5:
            raise ValueError(
                f"Cron expression needs 5 fields, got {len(fields)}: {self.expression!r}"
            )
        object.__setattr__(self, "_fields", tuple(fields))

    @property
    def _parsed(self) -> tuple[str, str, str, str, str]:
        fields = getattr(self, "_fields", None)
        if fields is None:
            # ``__post_init__`` may be skipped when a frozen copy is rebuilt.
            fields = tuple(self.expression.split())
            object.__setattr__(self, "_fields", fields)
        return fields

    @staticmethod
    def _match(field: str, value: int, low: int, high: int) -> bool:
        if field == "*":
            return True
        for part in field.split(","):
            step = 1
            if "/" in part:
                part, _, step_text = part.partition("/")
                step = int(step_text)
            if part == "*":
                start, end = low, high
            elif "-" in part:
                start_text, _, end_text = part.partition("-")
                start, end = int(start_text), int(end_text)
            else:
                start = end = int(part)
            if start <= value <= end and (value - start) % step == 0:
                return True
        return False

    def matches(self, moment: datetime) -> bool:
        minute, hour, day, month, weekday = self._parsed
        # Cron weekday is 0=Sunday; Python's is 0=Monday.
        cron_weekday = (moment.weekday() + 1) % 7
        return (
            self._match(minute, moment.minute, 0, 59)
            and self._match(hour, moment.hour, 0, 23)
            and self._match(day, moment.day, 1, 31)
            and self._match(month, moment.month, 1, 12)
            and self._match(weekday, cron_weekday, 0, 6)
        )

    def next_after(self, moment: datetime, limit_days: int = 366) -> datetime | None:
        """The first matching minute strictly after ``moment``."""
        candidate = moment.replace(second=0, microsecond=0) + timedelta(minutes=1)
        deadline = candidate + timedelta(days=limit_days)
        while candidate < deadline:
            if self.matches(candidate):
                return candidate
            candidate += timedelta(minutes=1)
        return None

    def upcoming(self, count: int, start: datetime | None = None) -> list[datetime]:
        moment = start or datetime.now(timezone.utc)
        found: list[datetime] = []
        for _ in range(count):
            nxt = self.next_after(moment)
            if nxt is None:
                break
            found.append(nxt)
            moment = nxt
        return found


@dataclass
class ScheduledJob:
    """A cron expression bound to a named job."""

    name: str
    schedule: CronSchedule
    last_run: datetime | None = None

    def is_due(self, now: datetime) -> bool:
        if not self.schedule.matches(now):
            return False
        if self.last_run is None:
            return True
        return self.last_run.replace(second=0, microsecond=0) < now.replace(
            second=0, microsecond=0
        )

    def mark_run(self, when: datetime) -> None:
        self.last_run = when

    def next_run(self, now: datetime | None = None) -> datetime | None:
        return self.schedule.next_after(now or datetime.now(timezone.utc))


def parse_schedule(expression: str) -> CronSchedule:
    return CronSchedule(expression)


# ------------------------------------------------------------- dependency chains


@dataclass
class JobNode:
    name: str
    depends_on: list[str] = field(default_factory=list)


class DependencyCycleError(Exception):
    """Raised when job dependencies form a cycle."""


def resolve_order(nodes: Iterable[JobNode]) -> list[str]:
    """Topological order: every job appears after everything it depends on."""
    graph = {node.name: list(node.depends_on) for node in nodes}
    unknown = {dep for deps in graph.values() for dep in deps} - set(graph)
    if unknown:
        raise ValueError(f"Dependencies reference unknown jobs: {', '.join(sorted(unknown))}")
    ordered: list[str] = []
    placed: set[str] = set()
    while len(ordered) < len(graph):
        ready = sorted(
            name
            for name, deps in graph.items()
            if name not in placed and all(dep in placed for dep in deps)
        )
        if not ready:
            remaining = sorted(set(graph) - placed)
            raise DependencyCycleError(
                f"Dependency cycle among: {', '.join(remaining)}"
            )
        for name in ready:
            ordered.append(name)
            placed.add(name)
    return ordered


@dataclass
class ChainOutcome:
    """Which jobs ran and which were skipped because an upstream job failed."""

    order: list[str]
    ran: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    @property
    def halted(self) -> bool:
        return bool(self.skipped)

    def as_dict(self) -> dict[str, Any]:
        return {
            "order": self.order,
            "ran": self.ran,
            "skipped": self.skipped,
            "failed": self.failed,
        }


def run_chain(
    nodes: Iterable[JobNode],
    execute: Callable[[str], bool],
) -> ChainOutcome:
    """Run jobs in dependency order, halting downstream of a failure.

    ``execute(name)`` returns True on success. A job whose predecessor failed is
    skipped rather than run, so a broken upstream cannot produce half-updated
    downstream state.
    """
    nodes = list(nodes)
    graph = {node.name: list(node.depends_on) for node in nodes}
    order = resolve_order(nodes)
    outcome = ChainOutcome(order=order)
    state: dict[str, str] = {}
    for name in order:
        blocked = [dep for dep in graph[name] if state.get(dep) != "ok"]
        if blocked:
            outcome.skipped.append(name)
            state[name] = "skipped"
            continue
        try:
            succeeded = bool(execute(name))
        except Exception:  # noqa: BLE001 - a raising job is a failed job
            succeeded = False
        if succeeded:
            outcome.ran.append(name)
            state[name] = "ok"
        else:
            outcome.failed.append(name)
            state[name] = "failed"
    return outcome


# ------------------------------------------------------------------ retry


@dataclass
class RetryPolicy:
    attempts: int = 3
    base_delay: float = 1.0
    factor: float = 2.0
    max_delay: float = 60.0
    sleep: Callable[[float], None] = time.sleep

    def delay_for(self, attempt: int) -> float:
        """Backoff before ``attempt`` (1-based). Capped at ``max_delay``."""
        if attempt <= 1:
            return 0.0
        return min(self.base_delay * (self.factor ** (attempt - 2)), self.max_delay)


@dataclass
class RetryOutcome:
    succeeded: bool
    attempts: int
    result: Any = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "succeeded": self.succeeded,
            "attempts": self.attempts,
            "error": self.error,
        }


def run_with_retry(
    action: Callable[[], Any], policy: RetryPolicy | None = None
) -> RetryOutcome:
    """Run ``action``, retrying with backoff up to the policy's attempt limit."""
    policy = policy or RetryPolicy()
    last_error: str | None = None
    for attempt in range(1, max(policy.attempts, 1) + 1):
        try:
            return RetryOutcome(True, attempt, result=action())
        except Exception as exc:  # noqa: BLE001 - retried, then reported
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < policy.attempts:
                delay = policy.delay_for(attempt + 1)
                if delay:
                    policy.sleep(delay)
    return RetryOutcome(False, max(policy.attempts, 1), None, last_error)


# ------------------------------------------------------- incremental processing


def state_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "incremental"


def record_fingerprint(record: Mapping[Any, Any], columns: list[str] | None = None) -> str:
    """A stable id for one record's values."""
    keys = columns if columns is not None else sorted(str(key) for key in record)
    parts = []
    for key in keys:
        value = record.get(key)
        parts.append("" if is_missing(value) else str(value))
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return digest[:32]


@dataclass
class IncrementalStore:
    """Remembers which records a source has already delivered."""

    source: str
    path: Path | None = None

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = state_dir() / f"{_slug(self.source)}.json"

    def _load(self) -> set[str]:
        if self.path is None or not self.path.exists():
            return set()
        try:
            return set(json.loads(self.path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            return set()

    def seen(self) -> set[str]:
        return self._load()

    def new_records(
        self, frame: pd.DataFrame, columns: list[str] | None = None
    ) -> pd.DataFrame:
        """The rows of ``frame`` whose fingerprint has not been seen before."""
        known = self._load()
        if not len(frame):
            return frame.copy()
        keep = [
            index
            for index, record in enumerate(frame.to_dict("records"))
            if record_fingerprint(record, columns) not in known
        ]
        return frame.iloc[keep].reset_index(drop=True)

    def commit(
        self, frame: pd.DataFrame, columns: list[str] | None = None
    ) -> int:
        """Mark every row of ``frame`` as seen. Returns the total now known."""
        known = self._load()
        for record in frame.to_dict("records"):
            known.add(record_fingerprint(record, columns))
        location = self.path
        assert location is not None
        location.parent.mkdir(parents=True, exist_ok=True)
        location.write_text(json.dumps(sorted(known)), encoding="utf-8")
        return len(known)

    def clear(self) -> int:
        count = len(self._load())
        if self.path is not None and self.path.exists():
            self.path.unlink()
        return count


def _slug(text: str) -> str:
    keep = [ch if ch.isalnum() or ch in "-_." else "_" for ch in str(text)]
    return "".join(keep) or "unnamed"
