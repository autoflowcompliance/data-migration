"""Watch a folder and process a file the moment it lands.

A trigger, not a new pipeline. When a supported file appears and stops
changing, this hands it to the same :func:`app_files.batch.runner.process_one`
the batch command uses, so the output is what a manual run would have produced.

Three details decide whether this is safe to point at a real inbox:

* **A file that is still being written must not be read.** An export lands in
  multiple writes; reading at the first write yields a truncated file that
  passes enough checks to produce a plausible, wrong output. A file is only
  ready once its size and mtime have held steady for ``settle_seconds``.
* **A file already processed must not be processed again.** Delivery folders
  are not emptied by the sender, so without a record every poll reprocesses the
  whole folder. The record is a fingerprint (size + mtime); a genuinely changed
  file is new again, an untouched one is not.
* **Temp names are not deliverables.** ``.part``, ``.tmp``, ``.crdownload`` and
  ``~$…`` are in-progress markers, not files to migrate.

The clock and the sleep are injectable so a test can advance time instead of
waiting for it.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app_files.batch.runner import BatchItem, process_one
from app_files.ingestion import available_extensions

#: Extensions that mean "still arriving". Checked before the supported list.
IN_PROGRESS_SUFFIXES = (".part", ".partial", ".tmp", ".crdownload", ".download", ".filepart")

#: Office and editors write a lock file beside the real one; skip the sibling.
IN_PROGRESS_PREFIXES = ("~$", ".~")


def is_deliverable(path: Path) -> bool:
    """Whether ``path`` looks like a finished source file rather than debris."""
    name = path.name
    if name.startswith(IN_PROGRESS_PREFIXES):
        return False
    if path.suffix.lower() in IN_PROGRESS_SUFFIXES:
        return False
    if not path.is_file():
        return False
    return path.suffix.lower() in set(available_extensions())


def watch_state_path() -> Path:
    """Where processed fingerprints live. Honours ``AUTOFLOW_HOME``.

    Runtime state, so it must not default into the source tree: an installed
    client has read-only program files, and a watcher that can only remember
    what it has seen by writing into its own package would reprocess an inbox
    forever.
    """
    override = os.getenv("AUTOFLOW_HOME")
    root = Path(override) if override else Path.home() / ".autoflow"
    return root / "watch_state.json"


@dataclass
class WatchRecord:
    """What a processed file looked like, so it is not processed twice."""

    size: int
    mtime: float

    def as_dict(self) -> dict[str, Any]:
        return {"size": self.size, "mtime": self.mtime}

    @classmethod
    def of(cls, path: Path) -> WatchRecord:
        stat = path.stat()
        return cls(size=stat.st_size, mtime=stat.st_mtime)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WatchRecord:
        return cls(size=int(data["size"]), mtime=float(data["mtime"]))


@dataclass
class WatchState:
    """The record of what has been handled and what is still arriving.

    Both halves are persisted, not held in memory, because the two ways this is
    run are a long-lived loop *and* a cron job that starts a fresh process every
    minute. An in-memory settle window would make the cron path never process
    anything: every run would see the file for the first time.
    """

    path: Path

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # An unreadable state file means "unknown", never "everything is
            # new": reprocessing an inbox on a corrupt byte would double-deliver.
            return {}
        return data if isinstance(data, dict) else {}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def load(self) -> dict[str, dict[str, dict[str, Any]]]:
        """The handled map, ``{watch_key: {path: {size, mtime}}}``."""
        handled = {
            key: section.get("handled", {}) if isinstance(section, dict) else {}
            for key, section in self._load().items()
        }
        return handled

    def handled(self, watch_key: str, path: Path) -> bool:
        record = self.load().get(watch_key, {}).get(str(path))
        if record is None:
            return False
        try:
            return WatchRecord.from_dict(record) == WatchRecord.of(path)
        except OSError:
            return False

    def mark(self, watch_key: str, path: Path) -> None:
        data = self._load()
        section = data.setdefault(watch_key, {})
        section.setdefault("handled", {})[str(path)] = WatchRecord.of(path).as_dict()
        section.get("seen", {}).pop(str(path), None)
        self._save(data)

    def first_seen(self, watch_key: str, path: Path) -> tuple[float, int, float] | None:
        """The earlier observation of this exact file, or ``None``."""
        section = self._load().get(watch_key) or {}
        record = (section.get("seen") or {}).get(str(path))
        if record is None:
            return None
        try:
            observed = WatchRecord.from_dict(record)
            if observed != WatchRecord.of(path):
                return None
            return float(record["first_seen"]), observed.size, observed.mtime
        except (KeyError, OSError, TypeError, ValueError):
            return None

    def mark_seen(self, watch_key: str, path: Path, now: float) -> None:
        data = self._load()
        section = data.setdefault(watch_key, {})
        seen = section.setdefault("seen", {})
        record = WatchRecord.of(path)
        seen[str(path)] = {
            "first_seen": now,
            "size": record.size,
            "mtime": record.mtime,
        }
        self._save(data)


@dataclass
class WatchOutcome:
    """One file's fate in a poll."""

    file: str
    status: str
    item: BatchItem | None = None
    reason: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "processed" and self.item is not None and self.item.ok

    def as_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "status": self.status,
            "reason": self.reason,
            "rows_out": self.item.rows_out if self.item else 0,
            "score": self.item.score if self.item else None,
        }


@dataclass
class WatchFolder:
    """Poll a folder; process each finished file once."""

    input_dir: Path
    template: str
    output_dir: Path
    state_path: Path | None = None
    settle_seconds: float = 2.0
    output_format: str = "csv"
    project_name: str = "Watch run"
    _pending: dict[str, tuple[float, int, float]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self.input_dir = Path(self.input_dir)
        self.output_dir = Path(self.output_dir)
        self.state_path = Path(self.state_path) if self.state_path else watch_state_path()

    @property
    def watch_key(self) -> str:
        return str(self.input_dir.resolve())

    @property
    def state(self) -> WatchState:
        return WatchState(self.state_path)

    def candidates(self) -> list[Path]:
        """Deliverable files in the folder, in stable order."""
        if not self.input_dir.is_dir():
            return []
        return sorted(
            (path for path in self.input_dir.iterdir() if is_deliverable(path)),
            key=lambda path: path.name.lower(),
        )

    def ready(self, now: float | None = None) -> list[Path]:
        """Files that have stopped changing and have not been handled yet.

        The first sighting of a file is written to disk, so a cron invocation
        that exits immediately still counts as the first observation and the
        *next* invocation can complete the settle window. A file whose size or
        mtime has moved since the last observation restarts its window.
        """
        moment = time.time() if now is None else now
        found: list[Path] = []
        state = self.state
        for path in self.candidates():
            if state.handled(self.watch_key, path):
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            observation = self._pending.get(str(path))
            if observation is None:
                observation = state.first_seen(self.watch_key, path)
            if observation is None:
                self._pending[str(path)] = (moment, stat.st_size, stat.st_mtime)
                state.mark_seen(self.watch_key, path, moment)
                continue
            first_seen, size, mtime = observation
            if stat.st_size != size or stat.st_mtime != mtime:
                # Still being written: restart the window from this size.
                self._pending[str(path)] = (moment, stat.st_size, stat.st_mtime)
                state.mark_seen(self.watch_key, path, moment)
                continue
            if moment - first_seen >= self.settle_seconds:
                found.append(path)
        return found

    def process_ready(self, now: float | None = None) -> list[WatchOutcome]:
        """Run the pipeline over every ready file and record it as handled."""
        outcomes: list[WatchOutcome] = []
        for path in self.ready(now=now):
            item = process_one(
                path,
                template=self.template,
                out_dir=self.output_dir / path.stem,
                output_format=self.output_format,
                project_name=self.project_name,
            )
            # Marked even on failure: a file the pipeline rejects would
            # otherwise be retried forever, and the failure is already reported.
            self.state.mark(self.watch_key, path)
            self._pending.pop(str(path), None)
            outcomes.append(
                WatchOutcome(
                    file=path.name,
                    status="processed" if item.ok else "failed",
                    item=item,
                    reason="" if item.ok else item.error,
                )
            )
        return outcomes

    def run(
        self,
        iterations: int | None = None,
        poll_interval: float = 5.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
        on_progress: Callable[[WatchOutcome], None] | None = None,
    ) -> list[WatchOutcome]:
        """Poll forever, or ``iterations`` times when a bound is given."""
        collected: list[WatchOutcome] = []
        count = 0
        while iterations is None or count < iterations:
            count += 1
            for outcome in self.process_ready(now=clock()):
                collected.append(outcome)
                if on_progress is not None:
                    on_progress(outcome)
            if iterations is not None and count >= iterations:
                break
            sleep(poll_interval)
        return collected


def watch_once(
    input_dir: str | Path,
    template: str,
    output_dir: str | Path,
    **kwargs: Any,
) -> list[WatchOutcome]:
    """One settle-aware poll, for a cron or a test."""
    folder = WatchFolder(input_dir, template, output_dir, **kwargs)
    return folder.process_ready()


def watch(
    input_dir: str | Path,
    template: str,
    output_dir: str | Path,
    iterations: int | None = None,
    poll_interval: float = 5.0,
    on_progress: Callable[[WatchOutcome], None] | None = None,
    **kwargs: Any,
) -> list[WatchOutcome]:
    """Watch until interrupted (``iterations=None``) or for N polls."""
    folder = WatchFolder(input_dir, template, output_dir, **kwargs)
    return folder.run(
        iterations=iterations,
        poll_interval=poll_interval,
        on_progress=on_progress,
    )


__all__ = [
    "IN_PROGRESS_PREFIXES",
    "IN_PROGRESS_SUFFIXES",
    "WatchFolder",
    "WatchOutcome",
    "WatchRecord",
    "WatchState",
    "is_deliverable",
    "watch",
    "watch_once",
    "watch_state_path",
]
