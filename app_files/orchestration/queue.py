"""A durable, priority-aware job queue.

State lives in a JSONL log under ``AUTOFLOW_HOME``. Submission appends a line;
a state change appends a new line for the same job id; the current state of a
job is its latest line. That is what makes a crash survivable: an append is
atomic enough that a partial write is one unreadable last line, which the
loader skips, and no earlier state is disturbed.

An in-place rewrite would be simpler and is what this deliberately does not do:
a rewrite interrupted halfway loses the whole queue, which is exactly the
failure a durable queue exists to prevent.

Priority lanes are drained high-first. Within a lane the oldest submission
wins, so a burst of low-priority work cannot leapfrog a high-priority job that
has been waiting longer.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from app_files.orchestration.limits import ResourceLimits


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def terminal(self) -> bool:
        return self in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}


class Priority(int, Enum):
    HIGH = 0
    NORMAL = 1
    LOW = 2


def queue_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    root = Path(override) if override else Path(__file__).resolve().parent.parent.parent
    return root / "queue"


def queue_path(name: str = "jobs.jsonl") -> Path:
    return queue_dir() / name


@dataclass
class JobSpec:
    """What to run. ``kind`` selects the runner; ``payload`` carries arguments."""

    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    max_attempts: int = 1
    depends_on: list[str] = field(default_factory=list)
    """Job ids that must succeed before this one is eligible."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "payload": self.payload,
            "priority": int(self.priority),
            "limits": self.limits.as_dict(),
            "max_attempts": self.max_attempts,
            "depends_on": list(self.depends_on),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobSpec:
        from app_files.orchestration.limits import read_limits

        return cls(
            kind=str(data["kind"]),
            payload=dict(data.get("payload") or {}),
            priority=Priority(int(data.get("priority", Priority.NORMAL))),
            limits=read_limits(dict(data.get("limits") or {})),
            max_attempts=int(data.get("max_attempts", 1)),
            depends_on=list(data.get("depends_on") or []),
        )


@dataclass
class Job:
    """One job's current state."""

    id: str
    spec: JobSpec
    state: JobState = JobState.QUEUED
    submitted_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    attempts: int = 0
    worker: str = ""
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "spec": self.spec.as_dict(),
            "state": self.state.value,
            "submitted_at": self.submitted_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "attempts": self.attempts,
            "worker": self.worker,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        return cls(
            id=str(data["id"]),
            spec=JobSpec.from_dict(data["spec"]),
            state=JobState(str(data["state"])),
            submitted_at=float(data.get("submitted_at", 0.0)),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            attempts=int(data.get("attempts", 0)),
            worker=str(data.get("worker", "")),
            result=dict(data.get("result") or {}),
            error=data.get("error"),
        )

    @property
    def duration(self) -> float | None:
        if self.started_at is None or self.finished_at is None:
            return None
        return self.finished_at - self.started_at

    def eligible(self, states: dict[str, JobState]) -> bool:
        """A job runs when every job it depends on has succeeded."""
        return all(states.get(parent) is JobState.SUCCEEDED for parent in self.spec.depends_on)


class JobQueue:
    """A persistent queue. Safe to open from more than one process on one host.

    The lock is an ``O_EXCL`` lock file, which is the portable-enough primitive:
    it is atomic on every filesystem this tool targets, and it fails loudly
    rather than silently interleaving two writers.
    """

    def __init__(self, path: str | Path | None = None, lock_timeout: float = 5.0):
        self.path = Path(path) if path else queue_path()
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.lock_timeout = lock_timeout

    # ------------------------------------------------------------- reading
    def _lines(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # A torn final line from a crash mid-append. Skipping it loses
                # at most the very last state change, never the queue.
                continue
        return records

    def jobs(self) -> dict[str, Job]:
        """The latest record per job id."""
        latest: dict[str, Job] = {}
        for record in self._lines():
            try:
                job = Job.from_dict(record)
            except (KeyError, ValueError):
                continue
            latest[job.id] = job
        return latest

    def get(self, job_id: str) -> Job | None:
        return self.jobs().get(job_id)

    def by_state(self, state: JobState) -> list[Job]:
        return [job for job in self.jobs().values() if job.state is state]

    def counts(self) -> dict[str, int]:
        counts = {state.value: 0 for state in JobState}
        for job in self.jobs().values():
            counts[job.state.value] += 1
        return counts

    # ------------------------------------------------------------- writing
    def _append(self, job: Job) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(job.as_dict(), sort_keys=True) + "\n")

    def submit(self, spec: JobSpec, job_id: str | None = None) -> Job:
        job = Job(id=job_id or uuid.uuid4().hex, spec=spec)
        with self._lock():
            unknown = [parent for parent in spec.depends_on if parent not in self.jobs()]
            if unknown:
                raise ValueError(
                    f"Job depends on unknown job(s): {', '.join(sorted(unknown))}"
                )
            self._append(job)
        return job

    def claim(self, worker: str = "") -> Job | None:
        """Take the next eligible job and mark it running, atomically.

        The whole select-and-mark runs under the lock, so two workers cannot
        claim the same job. Without that, two workers run the same job and the
        output is written twice.
        """
        with self._lock():
            jobs = self.jobs()
            states = {job_id: job.state for job_id, job in jobs.items()}
            eligible = [
                job
                for job in jobs.values()
                if job.state is JobState.QUEUED and job.eligible(states)
            ]
            if not eligible:
                return None
            eligible.sort(key=lambda job: (int(job.spec.priority), job.submitted_at, job.id))
            chosen = eligible[0]
            chosen.state = JobState.RUNNING
            chosen.started_at = time.time()
            chosen.attempts += 1
            chosen.worker = worker
            self._append(chosen)
            return chosen

    def _finish(
        self,
        job_id: str,
        state: JobState,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Job:
        with self._lock():
            job = self.jobs().get(job_id)
            if job is None:
                raise KeyError(f"No job {job_id!r}")
            job.state = state
            job.finished_at = time.time()
            if result is not None:
                job.result = result
            job.error = error
            self._append(job)
        return job

    def succeed(self, job_id: str, result: dict[str, Any] | None = None) -> Job:
        return self._finish(job_id, JobState.SUCCEEDED, result=result)

    def fail(self, job_id: str, error: str) -> Job:
        return self._finish(job_id, JobState.FAILED, error=error)

    def cancel(self, job_id: str) -> Job:
        """Cancel a job that has not started. A running job is left alone."""
        with self._lock():
            job = self.jobs().get(job_id)
            if job is None:
                raise KeyError(f"No job {job_id!r}")
            if job.state is not JobState.QUEUED:
                raise ValueError(
                    f"Job {job_id!r} is {job.state.value}; only queued jobs can be cancelled"
                )
            job.state = JobState.CANCELLED
            job.finished_at = time.time()
            self._append(job)
        return job

    def retryable(self, job: Job) -> bool:
        return job.attempts < job.spec.max_attempts

    def requeue(self, job_id: str) -> Job:
        """Put a failed job back in the queue for another attempt."""
        with self._lock():
            job = self.jobs().get(job_id)
            if job is None:
                raise KeyError(f"No job {job_id!r}")
            job.state = JobState.QUEUED
            job.started_at = None
            job.finished_at = None
            job.error = None
            self._append(job)
        return job

    def requeue_stale(self, older_than_seconds: float = 3600.0) -> list[str]:
        """Return jobs stuck running past a deadline to the queue.

        A worker that dies mid-job leaves a RUNNING record with no process
        behind it. Without this, that job is lost forever, which is the exact
        failure a durable queue is supposed to prevent.
        """
        cutoff = time.time() - older_than_seconds
        recovered = []
        for job in self.by_state(JobState.RUNNING):
            if job.started_at is not None and job.started_at < cutoff:
                self.requeue(job.id)
                recovered.append(job.id)
        return recovered

    def render(self, limit: int = 20) -> str:
        jobs = sorted(self.jobs().values(), key=lambda j: j.submitted_at, reverse=True)
        lines = [f"{'id':10} {'state':10} {'prio':5} {'kind':16} age"]
        for job in jobs[:limit]:
            age = f"{time.time() - job.submitted_at:.0f}s"
            lines.append(
                f"{job.id[:10]:10} {job.state.value:10} "
                f"{job.spec.priority.name.lower():5} {job.spec.kind:16} {age}"
            )
        if not jobs:
            lines.append("(queue empty)")
        return "\n".join(lines)

    # -------------------------------------------------------------- locking
    class _Lock:
        def __init__(self, path: Path, timeout: float):
            self.path = path
            self.timeout = timeout

        def __enter__(self):
            self.path.parent.mkdir(parents=True, exist_ok=True)
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    os.write(descriptor, str(os.getpid()).encode())
                    os.close(descriptor)
                    return self
                except FileExistsError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(
                            f"Could not lock {self.path} within {self.timeout}s. "
                            "Remove it if no other process is running."
                        ) from None
                    time.sleep(0.01)

        def __exit__(self, *exc):
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            return False

    def _lock(self) -> JobQueue._Lock:
        return JobQueue._Lock(self.lock_path, self.lock_timeout)


__all__ = [
    "Job",
    "JobQueue",
    "JobSpec",
    "JobState",
    "Priority",
    "queue_dir",
    "queue_path",
]
