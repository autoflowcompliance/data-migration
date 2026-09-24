"""Distributed workers and resource limits.

The single-process queue is enough for one box; a fleet needs to agree on who
does what and on how much memory and time a job may take.

* **Worker pool** — a set of named workers that lease jobs from the queue by
  ``lease`` (a claim that expires), so a worker that dies mid-job does not hold
  the job forever. Leases are the mechanism that makes "distributed" honest
  rather than "a second process that also reads the same queue".

* **Resource limits** — per-job ceilings on rows and bytes, checked *before* the
  work starts. A job that would exceed its limit is refused with the numbers
  that refused it, rather than being allowed to exhaust the box.

Everything is deterministic and clock-injectable, so lease expiry is tested by
moving the clock rather than by sleeping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from app_files.orchestration.watcher import Job, JobQueue, QueueFullError


class LeaseError(RuntimeError):
    """Raised when a lease is invalid, held by someone else, or expired."""


class ResourceLimitExceeded(RuntimeError):
    """Raised when a job's declared size exceeds its limit."""

    def __init__(self, resource: str, requested: float, limit: float) -> None:
        self.resource = resource
        self.requested = requested
        self.limit = limit
        super().__init__(
            f"{resource} of {requested:g} exceeds the limit of {limit:g}."
        )


@dataclass
class ResourceLimits:
    max_rows: int = 1_000_000
    max_bytes: int = 512 * 1024 * 1024
    max_minutes: float = 30.0

    def check(self, *, rows: int = 0, bytes_: int = 0, minutes: float = 0.0) -> None:
        if self.max_rows and rows > self.max_rows:
            raise ResourceLimitExceeded("rows", rows, self.max_rows)
        if self.max_bytes and bytes_ > self.max_bytes:
            raise ResourceLimitExceeded("bytes", bytes_, self.max_bytes)
        if self.max_minutes and minutes > self.max_minutes:
            raise ResourceLimitExceeded("minutes", minutes, self.max_minutes)

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_rows": self.max_rows,
            "max_bytes": self.max_bytes,
            "max_minutes": self.max_minutes,
        }


@dataclass
class Lease:
    job_id: str
    worker: str
    expires_at: datetime

    def expired(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(timezone.utc)) >= self.expires_at

    def as_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "worker": self.worker,
            "expires_at": self.expires_at.isoformat(),
        }


@dataclass
class Worker:
    name: str
    capacity: int = 4
    active: list[str] = field(default_factory=list)
    completed: int = 0
    failed: int = 0

    def has_room(self) -> bool:
        return len(self.active) < self.capacity

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capacity": self.capacity,
            "active": list(self.active),
            "completed": self.completed,
            "failed": self.failed,
        }


class WorkerPool:
    """A fleet of workers leasing from one queue."""

    def __init__(
        self,
        queue: JobQueue,
        workers: list[Worker] | None = None,
        *,
        lease_seconds: int = 300,
        limits: ResourceLimits | None = None,
    ) -> None:
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be at least 1")
        self.queue = queue
        self.workers = {worker.name: worker for worker in (workers or [])}
        self.lease_seconds = lease_seconds
        self.limits = limits or ResourceLimits()
        self._leases: dict[str, Lease] = {}

    def add_worker(self, name: str, capacity: int = 4) -> Worker:
        worker = Worker(name=name, capacity=capacity)
        self.workers[name] = worker
        return worker

    def lease_next(self, worker_name: str, *, now: datetime | None = None) -> Lease | None:
        """Give ``worker_name`` its next job, or ``None`` if there is none.

        Reclaims expired leases first, so a dead worker's job returns to the
        queue instead of being lost.
        """
        if worker_name not in self.workers:
            raise LeaseError(f"Unknown worker {worker_name!r}.")
        worker = self.workers[worker_name]
        if not worker.has_room():
            return None

        self._reclaim_expired(now)

        job = self.queue.next_job()
        if job is None:
            return None

        moment = now or datetime.now(timezone.utc)
        lease = Lease(
            job_id=job.id,
            worker=worker_name,
            expires_at=moment + timedelta(seconds=self.lease_seconds),
        )
        self._leases[job.id] = lease
        worker.active.append(job.id)
        return lease

    def _reclaim_expired(self, now: datetime | None = None) -> list[str]:
        reclaimed = []
        for job_id, lease in list(self._leases.items()):
            if not lease.expired(now):
                continue
            del self._leases[job_id]
            worker = self.workers.get(lease.worker)
            if worker and job_id in worker.active:
                worker.active.remove(job_id)
            job = self.queue._jobs.get(job_id)
            if job and job.status == "running":
                job.status = "queued"  # back in the pool for someone else
            reclaimed.append(job_id)
        return reclaimed

    def renew(self, job_id: str, *, now: datetime | None = None) -> Lease:
        lease = self._require_lease(job_id)
        moment = now or datetime.now(timezone.utc)
        lease.expires_at = moment + timedelta(seconds=self.lease_seconds)
        return lease

    def release(self, job_id: str, *, succeeded: bool, error: str = "") -> Job:
        lease = self._require_lease(job_id)
        worker = self.workers.get(lease.worker)
        if worker and job_id in worker.active:
            worker.active.remove(job_id)
        del self._leases[job_id]
        if succeeded:
            if worker:
                worker.completed += 1
            return self.queue.complete(job_id)
        if worker:
            worker.failed += 1
        return self.queue.fail(job_id, error)

    def check_resources(self, *, rows: int = 0, bytes_: int = 0, minutes: float = 0.0) -> None:
        self.limits.check(rows=rows, bytes_=bytes_, minutes=minutes)

    def counts(self) -> dict[str, Any]:
        return {
            "workers": {name: w.as_dict() for name, w in self.workers.items()},
            "active_leases": len(self._leases),
            "queue": self.queue.counts(),
        }

    def _require_lease(self, job_id: str) -> Lease:
        if job_id not in self._leases:
            raise LeaseError(f"No active lease for {job_id!r}.")
        return self._leases[job_id]


def run_pool(
    pool: WorkerPool,
    worker_names: list[str],
    handler: Callable[[Job], Any],
    *,
    max_jobs: int = 0,
) -> dict[str, int]:
    """Drain a pool by round-robin over the named workers.

    A handler that raises releases the job as failed and the round-robin
    continues, so one poisoned payload does not stall the fleet.
    """
    handled = {"done": 0, "failed": 0}
    processed = 0
    while max_jobs == 0 or processed < max_jobs:
        progressed = False
        for name in worker_names:
            if max_jobs and processed >= max_jobs:
                break
            lease = pool.lease_next(name)
            if lease is None:
                continue
            progressed = True
            processed += 1
            try:
                handler(pool.queue._jobs[lease.job_id])
            except Exception as error:  # noqa: BLE001 - record and continue
                pool.release(lease.job_id, succeeded=False, error=f"{type(error).__name__}: {error}")
                handled["failed"] += 1
            else:
                pool.release(lease.job_id, succeeded=True)
                handled["done"] += 1
        if not progressed:
            break
    return handled