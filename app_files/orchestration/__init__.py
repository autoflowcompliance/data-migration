"""Layer 14 — a durable job queue, distributed workers, and resource limits.

The batch layer runs a folder. This layer runs a queue: jobs are submitted,
persisted, claimed by a worker, and completed, and none of those steps require
the submitter to stay alive.

The design constraints that shape everything here:

* A job must not be lost. The queue is a JSONL log on disk under
  ``AUTOFLOW_HOME``, append-only for submissions and rewritten atomically for a
  state change, so a crash leaves either the old state or the new state and
  never a torn one.
* One job must not starve the system. A worker honours a resource budget and
  refuses to start a job it cannot afford.
* Priority must mean something. Lanes are drained high-first, and within a lane
  the oldest submission wins, so a burst of low-priority work cannot leapfrog a
  high-priority job that has been waiting.

No existing layer changes. The queue calls the same ``run_batch`` / pipeline
entry points the CLI does; it is a trigger and a bookkeeper, not a second
pipeline.
"""

from __future__ import annotations

from app_files.orchestration.limits import (
    LimitBreach,
    ResourceBudget,
    ResourceLimits,
    ResourceUsage,
    check_budget,
    measure,
)
from app_files.orchestration.queue import (
    Job,
    JobQueue,
    JobSpec,
    JobState,
    Priority,
    queue_path,
)
from app_files.orchestration.workers import (
    HANDLERS,
    Worker,
    WorkerPool,
    WorkerReport,
    get_handler,
    register_handler,
    registered_kinds,
    run_workers,
)

__all__ = [
    "HANDLERS",
    "Job",
    "JobQueue",
    "JobSpec",
    "JobState",
    "LimitBreach",
    "Priority",
    "ResourceBudget",
    "ResourceLimits",
    "ResourceUsage",
    "Worker",
    "WorkerPool",
    "WorkerReport",
    "check_budget",
    "get_handler",
    "measure",
    "queue_path",
    "register_handler",
    "registered_kinds",
    "run_workers",
]
