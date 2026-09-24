"""Watch folders, incremental processing, and a job queue.

* **Watch folders** — a directory is scanned and every new or changed file
  becomes a work item. "New or changed" is decided against a record of what was
  seen last time (size and mtime), not against a timestamp the caller supplies,
  so a file that is edited in place is picked up again while an untouched one is
  not.

* **Incremental processing** — the state a previous run left behind, so the next
  run handles only what moved. This is what makes a nightly job over a growing
  folder cost time proportional to the new data rather than the whole history.

* **A job queue** — work in, work out, with a bounded number of jobs in flight.
  Queued, running, done and failed are tracked, and a capacity limit means the
  queue reports back-pressure instead of accepting unbounded work it cannot do.

All state lives under ``AUTOFLOW_HOME`` so nothing is written into the repo.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class QueueFullError(RuntimeError):
    """Raised when the queue is at its capacity and would have to drop work."""


def orchestrator_home() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base


# ------------------------------------------------------------- watch folders
@dataclass
class WatchedFile:
    path: str
    size: int
    modified: float
    fingerprint: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "size": self.size,
            "modified": self.modified,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WatchedFile":
        return cls(
            path=str(data["path"]),
            size=int(data.get("size", 0)),
            modified=float(data.get("modified", 0)),
            fingerprint=str(data.get("fingerprint", "")),
        )


def _fingerprint(path: Path) -> str:
    """Size and mtime as one string.

    Content hashing a multi-gigabyte file on every poll would defeat the point
    of watching; size plus mtime is what every file watcher uses, and it is
    wrong only when a file is edited to the same size within the same second.
    """
    stat = path.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def scan_watched_directory(
    directory: str | Path,
    *,
    patterns: tuple[str, ...] = ("*.csv", "*.xlsx", "*.xls", "*.json", "*.pdf"),
    known: dict[str, WatchedFile] | None = None,
) -> tuple[list[WatchedFile], list[WatchedFile], list[WatchedFile]]:
    """Scan a directory and split the files into new, changed, and gone.

    ``known`` is the previous scan's result, keyed by path. Returns
    ``(new, changed, removed)``.
    """
    base = Path(directory)
    if not base.is_dir():
        raise NotADirectoryError(f"Not a directory: {base}")

    previous = known or {}
    found: dict[str, WatchedFile] = {}
    for pattern in patterns:
        for candidate in sorted(base.glob(pattern)):
            if not candidate.is_file():
                continue
            found[str(candidate)] = WatchedFile(
                path=str(candidate),
                size=candidate.stat().st_size,
                modified=candidate.stat().st_mtime,
                fingerprint=_fingerprint(candidate),
            )

    new = [entry for key, entry in found.items() if key not in previous]
    changed = [
        entry
        for key, entry in found.items()
        if key in previous and previous[key].fingerprint != entry.fingerprint
    ]
    removed = [entry for key, entry in previous.items() if key not in found]
    return new, changed, removed


def watch_state_path(name: str = "watch") -> Path:
    return orchestrator_home() / "watch" / f"{name}.json"


def save_watch_state(entries: list[WatchedFile], name: str = "watch", path: str | Path | None = None) -> Path:
    target = Path(path) if path else watch_state_path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"scanned_at": datetime.now(timezone.utc).isoformat(), "files": [e.as_dict() for e in entries]}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return target


def load_watch_state(name: str = "watch", path: str | Path | None = None) -> dict[str, WatchedFile]:
    target = Path(path) if path else watch_state_path(name)
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {entry["path"]: WatchedFile.from_dict(entry) for entry in data.get("files", [])}


def poll_watch_folder(
    directory: str | Path, name: str = "watch", *, path: str | Path | None = None
) -> dict[str, Any]:
    """One poll: work out what changed, then remember the new state.

    Remembering on every poll — including when nothing changed — is deliberate:
    the state file is the only record of what has been seen, and a crash after
    the scan but before a run must not make the same file look new twice.
    """
    previous = load_watch_state(name, path=path)
    new, changed, removed = scan_watched_directory(directory, known=previous)
    state = {entry.path: entry for entry in (*new, *changed, *previous.values()) if entry.path not in {r.path for r in removed}}
    save_watch_state(list(state.values()), name=name, path=path)
    return {
        "new": [e.as_dict() for e in new],
        "changed": [e.as_dict() for e in changed],
        "removed": [e.as_dict() for e in removed],
        "pending": len(new) + len(changed),
    }


# ------------------------------------------------------- incremental processing
@dataclass
class IncrementalState:
    last_run: str = ""
    processed: list[str] = field(default_factory=list)
    last_watermark: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "last_run": self.last_run,
            "processed": list(self.processed),
            "last_watermark": self.last_watermark,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IncrementalState":
        return cls(
            last_run=str(data.get("last_run", "")),
            processed=list(data.get("processed", [])),
            last_watermark=str(data.get("last_watermark", "")),
        )


def incremental_state_path(job: str) -> Path:
    return orchestrator_home() / "incremental" / f"{job}.json"


def load_incremental_state(job: str, path: str | Path | None = None) -> IncrementalState:
    target = Path(path) if path else incremental_state_path(job)
    if not target.exists():
        return IncrementalState()
    try:
        return IncrementalState.from_dict(json.loads(target.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return IncrementalState()


def save_incremental_state(state: IncrementalState, job: str, path: str | Path | None = None) -> Path:
    target = Path(path) if path else incremental_state_path(job)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state.as_dict(), indent=2) + "\n", encoding="utf-8")
    return target


def incremental_work_list(
    candidates: list[str], state: IncrementalState, *, watermark: str = ""
) -> list[str]:
    """Which candidates still need processing.

    A candidate is skipped when it was processed in an earlier run *and* it is
    not newer than the watermark. Passing a watermark newer than a candidate's
    modified time is how "only rows added since yesterday" is expressed.
    """
    processed = set(state.processed)
    pending = []
    for candidate in candidates:
        if candidate not in processed:
            pending.append(candidate)
            continue
        if watermark and candidate > watermark:
            pending.append(candidate)
    return pending


def mark_processed(state: IncrementalState, items: list[str], *, watermark: str = "") -> IncrementalState:
    """Return the state to persist after handling ``items``.

    The processed list is deduplicated and sorted so the file is stable —
    a diff of two states shows what changed, not the order it happened in.
    """
    return IncrementalState(
        last_run=datetime.now(timezone.utc).isoformat(),
        processed=sorted(set(state.processed) | set(items)),
        last_watermark=watermark or state.last_watermark,
    )


# ------------------------------------------------------------------- job queue
@dataclass
class Job:
    id: str
    payload: dict[str, Any] = field(default_factory=dict)
    status: str = "queued"  # queued | running | done | failed
    attempts: int = 0
    result: Any = None
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "payload": dict(self.payload),
            "status": self.status,
            "attempts": self.attempts,
            "error": self.error,
        }


class JobQueue:
    """A bounded FIFO queue with a capacity limit.

    Capacity is checked at submit time and raises rather than quietly dropping
    work, so a producer that outruns the consumer finds out immediately.
    """

    def __init__(self, capacity: int = 100) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._jobs: dict[str, Job] = {}
        self._order: list[str] = []
        self._counter = 0

    @property
    def pending(self) -> int:
        return sum(1 for job in self._jobs.values() if job.status in {"queued", "running"})

    def submit(self, payload: dict[str, Any] | None = None, *, job_id: str = "") -> Job:
        if self.pending >= self.capacity:
            raise QueueFullError(
                f"Queue is full ({self.pending}/{self.capacity}). "
                "Wait for work to finish or raise the capacity."
            )
        self._counter += 1
        identifier = job_id or f"job-{self._counter}"
        if identifier in self._jobs:
            raise ValueError(f"Job id {identifier!r} already exists.")
        job = Job(id=identifier, payload=dict(payload or {}))
        self._jobs[identifier] = job
        self._order.append(identifier)
        return job

    def next_job(self) -> Job | None:
        for identifier in self._order:
            job = self._jobs[identifier]
            if job.status == "queued":
                job.status = "running"
                job.attempts += 1
                return job
        return None

    def complete(self, job_id: str, result: Any = None) -> Job:
        job = self._require(job_id)
        job.status = "done"
        job.result = result
        return job

    def fail(self, job_id: str, error: str) -> Job:
        job = self._require(job_id)
        job.status = "failed"
        job.error = error
        return job

    def retry(self, job_id: str) -> Job:
        job = self._require(job_id)
        if job.status != "failed":
            raise ValueError(f"Job {job_id!r} is {job.status}, not failed.")
        job.status = "queued"
        job.error = ""
        return job

    def drain(self, worker: Callable[[Job], Any], *, max_jobs: int = 0) -> dict[str, int]:
        """Process queued jobs with ``worker`` until empty (or ``max_jobs``).

        A worker that raises marks the job failed and the drain continues, so
        one bad job does not stop the batch.
        """
        handled = {"done": 0, "failed": 0}
        processed = 0
        while max_jobs == 0 or processed < max_jobs:
            job = self.next_job()
            if job is None:
                break
            processed += 1
            try:
                self.complete(job.id, worker(job))
                handled["done"] += 1
            except Exception as error:  # noqa: BLE001 - report, keep draining
                self.fail(job.id, f"{type(error).__name__}: {error}")
                handled["failed"] += 1
        return handled

    def counts(self) -> dict[str, int]:
        counts = {"queued": 0, "running": 0, "done": 0, "failed": 0}
        for job in self._jobs.values():
            counts[job.status] += 1
        return counts

    def _require(self, job_id: str) -> Job:
        if job_id not in self._jobs:
            raise KeyError(f"No job {job_id!r}.")
        return self._jobs[job_id]