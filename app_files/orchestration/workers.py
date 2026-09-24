"""Workers that drain the queue.

A worker claims one job, runs its handler under a resource budget, and records
the outcome. Running several workers is the same code with a shared queue: the
claim is atomic (see ``JobQueue.claim``), so three workers process three
distinct jobs and never the same one twice.

A handler registry maps ``kind`` to a callable ``(payload) -> dict``. That is
the seam that keeps this layer from knowing what a job does: the batch runner,
a pipeline call, a reconciliation, all register as a kind. The registry has the
same additive rule as the plugin system, so a worker deployment can add kinds
without editing this module.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app_files.orchestration.limits import LimitBreach, ResourceBudget, describe
from app_files.orchestration.queue import Job, JobQueue, JobState

Handler = Callable[[dict[str, Any]], dict[str, Any]]

HANDLERS: dict[str, Handler] = {}


def register_handler(kind: str, handler: Handler, override: bool = False) -> Handler:
    """Add a job kind. Refuses to shadow an existing kind unless overridden."""
    key = str(kind).strip()
    if not key:
        raise ValueError("A job kind needs a name")
    if not callable(handler):
        raise ValueError(f"Handler for {kind!r} must be callable, got {type(handler).__name__}")
    if key in HANDLERS and not override:
        raise ValueError(
            f"Job kind {kind!r} already exists. Pass override=True to replace it."
        )
    HANDLERS[key] = handler
    return handler


def get_handler(kind: str) -> Handler:
    try:
        return HANDLERS[kind]
    except KeyError:
        raise ValueError(
            f"No handler for job kind {kind!r}. Known: {', '.join(sorted(HANDLERS))}"
        ) from None


def registered_kinds() -> list[str]:
    return sorted(HANDLERS)


@dataclass
class WorkerReport:
    """What one worker did, for the caller's summary and for tests."""

    worker: str
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    requeued: int = 0
    total_seconds: float = 0.0
    jobs: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "worker": self.worker,
            "processed": self.processed,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
            "requeued": self.requeued,
            "total_seconds": round(self.total_seconds, 3),
            "jobs": list(self.jobs),
        }


@dataclass
class Worker:
    """Drains a queue until it is empty (or a budget of work is done)."""

    name: str
    queue: JobQueue
    max_jobs: int | None = None
    available_mb: float | None = None
    """When set, a job declaring more memory than this is failed before it runs."""
    sleep_seconds: float = 0.0
    """A pause between jobs, for a polling worker."""

    def _admit(self, job: Job) -> str | None:
        from app_files.orchestration.limits import affordable

        if not affordable(job.spec.limits, available_mb=self.available_mb):
            return (
                f"Job declares {job.spec.limits.max_memory_mb:.0f} MB but only "
                f"{self.available_mb:.0f} MB is available"
            )
        return None

    def run_once(self) -> Job | None:
        """Claim and run a single job. Returns the finished job, or None."""
        job = self.queue.claim(self.name)
        if job is None:
            return None
        self._execute(job)
        return self.queue.get(job.id)

    def run(self, max_jobs: int | None = None) -> WorkerReport:
        report = WorkerReport(worker=self.name)
        limit = max_jobs if max_jobs is not None else self.max_jobs
        started = time.monotonic()
        while limit is None or report.processed < limit:
            job = self.queue.claim(self.name)
            if job is None:
                break
            report.processed += 1
            report.jobs.append(job.id)
            outcome = self._execute(job)
            if outcome is JobState.SUCCEEDED:
                report.succeeded += 1
            elif outcome is JobState.QUEUED:
                report.requeued += 1
            else:
                report.failed += 1
            if self.sleep_seconds:
                time.sleep(self.sleep_seconds)
        report.total_seconds = time.monotonic() - started
        return report

    def _execute(self, job: Job) -> JobState:
        refusal = self._admit(job)
        if refusal:
            self.queue.fail(job.id, refusal)
            return JobState.FAILED

        budget = ResourceBudget(limits=job.spec.limits)
        try:
            handler = get_handler(job.spec.kind)
            result = handler(job.spec.payload) or {}
        except LimitBreach as exc:
            return self._on_failure(job, f"Resource limit exceeded: {exc}")
        except Exception as exc:  # noqa: BLE001 - any handler failure is a job failure
            return self._on_failure(job, f"{type(exc).__name__}: {exc}")

        usage = budget.usage()
        message = budget.breach()
        if message:
            return self._on_failure(job, f"Resource limit exceeded: {message}")
        result = dict(result)
        result.setdefault("usage", usage.as_dict())
        self.queue.succeed(job.id, result)
        _emit(job, JobState.SUCCEEDED)
        return JobState.SUCCEEDED

    def _on_failure(self, job: Job, error: str) -> JobState:
        if self.queue.retryable(job):
            self.queue.requeue(job.id)
            _emit(job, JobState.QUEUED)
            return JobState.QUEUED
        self.queue.fail(job.id, error)
        _emit(job, JobState.FAILED, error)
        return JobState.FAILED


@dataclass
class WorkerPool:
    """Several workers over one queue.

    Workers run in sequence by default, which is deterministic and enough to
    prove the claim is exclusive. A deployment runs each worker in its own
    process; ``run_workers(threads=True)`` does that in-process for a test or a
    single-host deployment.
    """

    queue: JobQueue
    count: int = 3
    available_mb: float | None = None

    def reports(self, max_jobs: int | None = None) -> list[WorkerReport]:
        reports = []
        for index in range(self.count):
            worker = Worker(
                name=f"{self.queue.path.name}-worker-{index}",
                queue=self.queue,
                available_mb=self.available_mb,
            )
            reports.append(worker.run(max_jobs=max_jobs))
        return reports

    def reports_concurrent(self, max_jobs: int | None = None) -> list[WorkerReport]:
        from concurrent.futures import ThreadPoolExecutor

        def run(index: int) -> WorkerReport:
            worker = Worker(
                name=f"{self.queue.path.name}-worker-{index}",
                queue=self.queue,
                available_mb=self.available_mb,
            )
            return worker.run(max_jobs=max_jobs)

        with ThreadPoolExecutor(max_workers=self.count) as pool:
            return list(pool.map(run, range(self.count)))


def run_workers(
    queue: JobQueue,
    count: int = 3,
    max_jobs: int | None = None,
    available_mb: float | None = None,
    threads: bool = False,
) -> list[WorkerReport]:
    pool = WorkerPool(queue=queue, count=count, available_mb=available_mb)
    if threads:
        return pool.reports_concurrent(max_jobs=max_jobs)
    return pool.reports(max_jobs=max_jobs)


def _emit(job: Job, state: JobState, error: str | None = None) -> None:
    try:
        from app_files.plugins.events import LifecycleEvent, emit

        event = {
            JobState.SUCCEEDED: LifecycleEvent.JOB_FINISHED,
            JobState.FAILED: LifecycleEvent.JOB_FINISHED,
            JobState.QUEUED: LifecycleEvent.JOB_SUBMITTED,
        }.get(state)
        if event is not None:
            emit(event, {"job": job.id, "kind": job.spec.kind, "state": state.value,
                         "error": error})
    except Exception:  # noqa: BLE001 - emitting is best-effort
        pass


__all__ = [
    "HANDLERS",
    "Handler",
    "Worker",
    "WorkerPool",
    "WorkerReport",
    "describe",
    "get_handler",
    "register_handler",
    "registered_kinds",
    "run_workers",
]
