"""Batch layer: run a folder of files through the pipeline in one pass.

Sits beside the pipeline rather than inside it. ``run_batch`` is the entry
point; it never raises for a single bad file, and it always writes a combined
``summary.csv`` and ``dashboard.html`` so a batch of fifty files still produces
one thing a person can read.
"""

from app_files.batch.dashboard import render_dashboard, write_dashboard
from app_files.batch.orchestration import (
    ChainOutcome,
    CronSchedule,
    DependencyCycleError,
    IncrementalStore,
    JobNode,
    RetryOutcome,
    RetryPolicy,
    ScheduledJob,
    parse_schedule,
    record_fingerprint,
    resolve_order,
    run_chain,
    run_with_retry,
)
from app_files.batch.runner import (
    BatchItem,
    BatchResult,
    process_one,
    run_batch,
    supported_files,
)
from app_files.batch.summary import COLUMNS, summary_frame, write_summary

__all__ = [
    "COLUMNS",
    "BatchItem",
    "BatchResult",
    "ChainOutcome",
    "CronSchedule",
    "DependencyCycleError",
    "IncrementalStore",
    "JobNode",
    "RetryOutcome",
    "RetryPolicy",
    "ScheduledJob",
    "parse_schedule",
    "process_one",
    "record_fingerprint",
    "render_dashboard",
    "resolve_order",
    "run_batch",
    "run_chain",
    "run_with_retry",
    "summary_frame",
    "supported_files",
    "write_dashboard",
    "write_summary",
]