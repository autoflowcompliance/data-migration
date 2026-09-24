"""Automation and orchestration: schedules, triggers, dependencies, retries.

Four pieces that turn a manual tool into a pipeline. Each is deterministic and
clock-injectable, so "run every night at 2am" and "retry with backoff" are
tested by moving the clock rather than by waiting.

* **Schedules** — a cron expression is parsed and the next fire time computed.
  This is the *decision*, not a running daemon: the platform (systemd, Render
  cron, a Kubernetes CronJob) owns the timer, and this tells it when to fire.

* **Event triggers** — a rule that decides whether an event starts a run. A file
  landing in S3, a webhook, or an upstream job finishing are all "an event", and
  the same matcher handles all three.

* **Dependency chains** — a job runs only when its dependencies have succeeded.
  A failed dependency blocks the dependent job, which is what stops a pipeline
  from quietly running on stale input.

* **Retry with exponential backoff** — a transient failure is retried with a
  growing delay, capped, and gives up after a limit. The retry is a pure
  function of the attempt number, so it is fully testable.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

# ------------------------------------------------------------------- schedules
class ScheduleError(RuntimeError):
    """Raised for an invalid cron expression."""


_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "weekday": (0, 6),
}


@dataclass(frozen=True)
class CronExpression:
    """A parsed five-field cron expression."""

    minute: frozenset[int]
    hour: frozenset[int]
    day: frozenset[int]
    month: frozenset[int]
    weekday: frozenset[int]
    source: str = ""

    @classmethod
    def parse(cls, expression: str) -> "CronExpression":
        fields = expression.split()
        if len(fields) != 5:
            raise ScheduleError(
                f"A cron expression needs exactly 5 fields "
                f"(minute hour day month weekday); got {len(fields)} in {expression!r}."
            )
        parsed = {
            name: cls._parse_field(value, name)
            for name, value in zip(_FIELD_RANGES, fields)
        }
        return cls(source=expression, **parsed)

    @classmethod
    def _parse_field(cls, value: str, name: str) -> frozenset[int]:
        low, high = _FIELD_RANGES[name]
        values: set[int] = set()
        for part in value.split(","):
            step = 1
            if "/" in part:
                part, _, step_text = part.partition("/")
                if not step_text.isdigit() or int(step_text) < 1:
                    raise ScheduleError(f"Invalid step in {name} field: {value!r}.")
                step = int(step_text)
            if part in {"*", ""}:
                start, end = low, high
            elif "-" in part:
                start_text, _, end_text = part.partition("-")
                start, end = cls._int(start_text, name), cls._int(end_text, name)
            else:
                start = end = cls._int(part, name)
            if start > end or not (low <= start <= high) or not (low <= end <= high):
                raise ScheduleError(f"{name} value {part!r} is outside {low}-{high}.")
            values.update(range(start, end + 1, step))
        if not values:
            raise ScheduleError(f"{name} field {value!r} matched no values.")
        return frozenset(values)

    @staticmethod
    def _int(text: str, name: str) -> int:
        try:
            return int(text)
        except ValueError as exc:
            raise ScheduleError(f"{name} field is not a number: {text!r}.") from exc

    def matches(self, moment: datetime) -> bool:
        weekday = (moment.weekday() + 1) % 7  # cron: 0 = Sunday
        return (
            moment.minute in self.minute
            and moment.hour in self.hour
            and moment.day in self.day
            and moment.month in self.month
            and weekday in self.weekday
        )

    def next_after(self, moment: datetime, limit_days: int = 366) -> datetime:
        """The first fire time strictly after ``moment``."""
        candidate = (moment + timedelta(minutes=1)).replace(second=0, microsecond=0)
        deadline = moment + timedelta(days=limit_days)
        while candidate <= deadline:
            if self.matches(candidate):
                return candidate
            candidate += timedelta(minutes=1)
        raise ScheduleError(
            f"No fire time for {self.source!r} within {limit_days} days; "
            f"the expression matches no real date."
        )


def next_run(expression: str, *, after: datetime | None = None) -> datetime:
    """When a schedule next fires. ``after`` defaults to now (UTC)."""
    cron = CronExpression.parse(expression)
    reference = after or datetime.now(timezone.utc)
    return cron.next_after(reference)


# -------------------------------------------------------------- event triggers
@dataclass
class EventTrigger:
    """Start a job when a matching event arrives.

    ``source`` is ``file``, ``webhook`` or ``job``; ``contains`` matches the
    event's detail. A file trigger watches for a suffix; a job trigger watches
    for upstream completion; a webhook trigger matches a field value.
    """

    job: str
    source: str = "file"
    contains: str = ""
    suffix: str = ""

    def matches(self, event: dict[str, Any]) -> bool:
        if event.get("source") != self.source:
            return False
        haystack = str(event.get("detail", ""))
        if self.contains and self.contains not in haystack:
            return False
        if self.suffix and not haystack.lower().endswith(self.suffix.lower()):
            return False
        return True


def events_that_fire(triggers: list[EventTrigger], event: dict[str, Any]) -> list[str]:
    """Every job an event should start, in declaration order."""
    return [trigger.job for trigger in triggers if trigger.matches(event)]


# ------------------------------------------------------------ dependency chains
class DependencyError(RuntimeError):
    """Raised for a circular or unsatisfiable dependency graph."""


@dataclass
class JobGraph:
    """Jobs and their dependencies. A job runs only when all deps succeeded."""

    jobs: dict[str, list[str]] = field(default_factory=dict)

    def add(self, job: str, depends_on: list[str] | None = None) -> "JobGraph":
        self.jobs[job] = list(depends_on or [])
        return self

    def detect_cycle(self) -> list[str] | None:
        """A cycle, as the list of jobs in it, or ``None`` if acyclic."""
        WHITE, GREY, BLACK = 0, 1, 2
        colour = {job: WHITE for job in self.jobs}
        stack: list[str] = []

        def visit(job: str) -> list[str] | None:
            colour[job] = GREY
            stack.append(job)
            for dep in self.jobs.get(job, []):
                if dep not in colour:
                    raise DependencyError(f"Job {job!r} depends on unknown job {dep!r}.")
                if colour[dep] == GREY:
                    return stack[stack.index(dep):] + [dep]
                if colour[dep] == WHITE:
                    found = visit(dep)
                    if found:
                        return found
            stack.pop()
            colour[job] = BLACK
            return None

        for job in self.jobs:
            if colour[job] == WHITE:
                found = visit(job)
                if found:
                    return found
        return None

    def ready(self, statuses: dict[str, str]) -> list[str]:
        """Jobs whose dependencies have all succeeded and which have not run.

        A job with a failed or unknown dependency is not ready — this is what
        stops a dependent job from running on stale or missing input.
        """
        if self.detect_cycle():
            raise DependencyError("Dependency graph contains a cycle.")
        ready = []
        for job, deps in self.jobs.items():
            if statuses.get(job) in {"running", "succeeded", "failed"}:
                continue
            if all(statuses.get(dep) == "succeeded" for dep in deps):
                ready.append(job)
        return ready

    def run_order(self) -> list[str]:
        """A topological order; raises on a cycle."""
        cycle = self.detect_cycle()
        if cycle:
            raise DependencyError(f"Dependency cycle: {' -> '.join(cycle)}")
        order: list[str] = []
        remaining = dict(self.jobs)
        while remaining:
            progressed = False
            for job, deps in list(remaining.items()):
                if all(dep in order for dep in deps):
                    order.append(job)
                    del remaining[job]
                    progressed = True
            if not progressed:
                raise DependencyError("Dependency graph cannot be resolved.")
        return order


# ---------------------------------------------------------------- retry policy
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = 1.0
    multiplier: float = 2.0
    max_delay: float = 60.0

    def delay_for(self, attempt: int) -> float:
        """Seconds to wait before attempt ``attempt`` (1-based)."""
        if attempt < 1:
            raise ValueError("attempt is 1-based")
        delay = self.base_delay * (self.multiplier ** (attempt - 1))
        return min(delay, self.max_delay)

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_attempts

    def run(
        self,
        operation: Callable[[], Any],
        *,
        sleep: Callable[[float], None] | None = None,
    ) -> tuple[Any, int, list[float]]:
        """Run ``operation``, retrying on exception.

        Returns ``(result, attempts_used, delays_waited)``. The final exception
        is re-raised if every attempt fails.
        """
        waiter = sleep or time.sleep
        delays: list[float] = []
        attempt = 1
        while True:
            try:
                return operation(), attempt, delays
            except Exception:
                if not self.should_retry(attempt):
                    raise
                delay = self.delay_for(attempt)
                delays.append(delay)
                waiter(delay)
                attempt += 1