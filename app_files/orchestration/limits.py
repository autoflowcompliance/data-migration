"""Resource limits: a job gets a budget and is stopped when it exceeds it.

Memory is measured two ways and the larger is enforced: resident-set growth
(``/proc/self/statm``) and traced Python allocation growth (``tracemalloc``,
started only when a memory limit is declared). Neither alone is enough. RSS
growth misses an allocation served from a recycled allocator arena -- the pages
are already resident, so nothing changes -- and traced allocation misses native
buffers. The warm-arena miss is not theoretical: 40 MB allocations slipped past
a 1 MB RSS-based limit 60 times out of 60.

On platforms where neither can be read the usage is zero and only the
wall-clock limit bites, which is the honest degradation: better to enforce one
limit everywhere than to pretend to enforce three and silently skip them.

A limit is checked before a job starts, against the budget it declares, and
again as it runs. The pre-check is what stops a job that claims to need more
memory than the machine has from starting and taking the machine down with it.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

try:  # POSIX only; absent on Windows
    import resource as _resource
except ImportError:  # pragma: no cover - Windows
    _resource = None  # type: ignore[assignment]


class LimitBreach(RuntimeError):
    """Raised when a job exceeds a declared resource limit."""


@dataclass(frozen=True)
class ResourceLimits:
    """The budget a job declares, and the ceiling the system enforces."""

    max_memory_mb: float | None = None
    max_cpu_seconds: float | None = None
    max_runtime_seconds: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_seconds": self.max_cpu_seconds,
            "max_runtime_seconds": self.max_runtime_seconds,
        }

    @property
    def unbounded(self) -> bool:
        return all(
            value is None
            for value in (self.max_memory_mb, self.max_cpu_seconds, self.max_runtime_seconds)
        )


@dataclass
class ResourceUsage:
    """What a job actually consumed."""

    peak_memory_mb: float = 0.0
    cpu_seconds: float = 0.0
    wall_seconds: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "peak_memory_mb": round(self.peak_memory_mb, 3),
            "cpu_seconds": round(self.cpu_seconds, 3),
            "wall_seconds": round(self.wall_seconds, 3),
        }


def current_memory_mb() -> float:
    """Resident set size in MB, or 0 where the platform cannot report it.

    Read from ``/proc/self/statm`` rather than ``getrusage``: ``ru_maxrss`` is a
    high-water mark that only ever rises, so it cannot answer "how much has this
    job added". For an in-process worker the interpreter's own footprint would
    otherwise count against every job and a small limit would fail everything.

    RSS is one of two measurements, not the only one. See
    :func:`traced_memory_mb` for why: once the C allocator has reused a freed
    arena, a fresh allocation of that size does not raise RSS at all, so a
    limit read from RSS alone silently misses it.
    """
    try:
        with open("/proc/self/statm", encoding="ascii") as handle:
            resident_pages = int(handle.read().split()[1])
    except (OSError, IndexError, ValueError):
        return 0.0
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (ValueError, OSError, AttributeError):
        return 0.0
    return resident_pages * page_size / (1024 * 1024)


def traced_memory_mb() -> tuple[float, float]:
    """``(current, peak)`` traced Python allocation in MB, or ``(0, 0)``.

    ``tracemalloc`` counts allocations the interpreter makes regardless of
    whether the OS had to fault new pages in, so an allocation served from a
    recycled arena still shows up. That is the case RSS growth cannot see, and
    it is not hypothetical: with a warm arena, 40 MB allocations slipped past a
    1 MB RSS-based limit 60 times out of 60.

    Tracing is only started by :class:`ResourceBudget` when a memory limit is
    actually declared, because it has a real cost and a job with no memory
    limit should not pay it.
    """
    try:
        import tracemalloc
    except ImportError:  # pragma: no cover - tracemalloc is stdlib
        return 0.0, 0.0
    if not tracemalloc.is_tracing():
        return 0.0, 0.0
    current, peak = tracemalloc.get_traced_memory()
    return current / (1024 * 1024), peak / (1024 * 1024)


def cpu_seconds() -> float:
    if _resource is None:
        return 0.0
    usage = _resource.getrusage(_resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


@dataclass
class ResourceBudget:
    """Tracks one job's consumption against its limits.

    Memory is the larger of two independent measurements: RSS growth (what the
    process actually holds) and traced Python allocation growth (what the
    interpreter handed out, even from recycled memory the OS never re-faulted).
    Taking the maximum is what closes the warm-arena hole -- RSS alone
    under-reports a reused arena to zero, and traced allocation alone misses
    native allocations, so neither is sufficient on its own.
    """

    limits: ResourceLimits = field(default_factory=ResourceLimits)
    started_at: float = field(default_factory=time.monotonic)
    _cpu_at_start: float = field(default_factory=cpu_seconds)
    _memory_at_start: float = field(default_factory=current_memory_mb)
    _traced_at_start: float = field(default=0.0)
    _owner_of_tracing: bool = field(default=False)
    _peak_traced_mb: float = field(default=0.0)

    def __post_init__(self) -> None:
        # Tracing is started only when a memory limit is declared: it has a real
        # cost, and a job with no memory limit must not pay for it. If tracing
        # is already running (a caller or an outer budget started it), the peak
        # is the process-wide one and is not attributable to this job, so the
        # RSS view carries that case.
        if self.limits.max_memory_mb is None:
            return
        import tracemalloc

        self._owner_of_tracing = not tracemalloc.is_tracing()
        if self._owner_of_tracing:
            tracemalloc.start()
        current, peak = traced_memory_mb()
        self._traced_at_start = current
        self._peak_traced_mb = peak

    def stop(self) -> None:
        """Release tracing if this budget started it. Safe to call repeatedly."""
        if not self._owner_of_tracing:
            return
        import tracemalloc

        self._owner_of_tracing = False
        if tracemalloc.is_tracing():
            tracemalloc.stop()

    def __enter__(self) -> ResourceBudget:
        return self

    def __exit__(self, *exc_info: Any) -> bool:
        self.stop()
        return False

    def usage(self) -> ResourceUsage:
        rss_growth = max(0.0, current_memory_mb() - self._memory_at_start)
        traced_growth = 0.0
        if self.limits.max_memory_mb is not None:
            # Tracing was (re)started at this budget's creation when it owns the
            # tracer, so the peak is already measured from the job's start.
            _current, peak = traced_memory_mb()
            traced_growth = max(0.0, peak - self._peak_traced_mb)
        return ResourceUsage(
            peak_memory_mb=max(rss_growth, traced_growth),
            cpu_seconds=max(0.0, cpu_seconds() - self._cpu_at_start),
            wall_seconds=max(0.0, time.monotonic() - self.started_at),
        )

    def breach(self) -> str | None:
        """The first limit exceeded, as a message, or None when within budget."""
        return check_budget(self.limits, self.usage())

    def require_within(self) -> ResourceUsage:
        """Raise :class:`LimitBreach` if a limit is exceeded; else return usage."""
        message = self.breach()
        if message:
            raise LimitBreach(message)
        return self.usage()


def check_budget(limits: ResourceLimits, usage: ResourceUsage) -> str | None:
    """Return the first exceeded limit as a message, or None."""
    if limits.max_memory_mb is not None and usage.peak_memory_mb > limits.max_memory_mb:
        return (
            f"Peak memory {usage.peak_memory_mb:.1f} MB exceeds the "
            f"{limits.max_memory_mb:.1f} MB limit"
        )
    if limits.max_cpu_seconds is not None and usage.cpu_seconds > limits.max_cpu_seconds:
        return (
            f"CPU time {usage.cpu_seconds:.1f}s exceeds the "
            f"{limits.max_cpu_seconds:.1f}s limit"
        )
    if limits.max_runtime_seconds is not None and usage.wall_seconds > limits.max_runtime_seconds:
        return (
            f"Runtime {usage.wall_seconds:.1f}s exceeds the "
            f"{limits.max_runtime_seconds:.1f}s limit"
        )
    return None


def affordable(limits: ResourceLimits, *, available_mb: float | None = None) -> bool:
    """Whether a job declaring these limits can be admitted right now.

    A declared memory limit larger than what is available is refused before the
    job starts: starting it would exhaust the machine rather than the job.
    """
    if limits.max_memory_mb is None or available_mb is None:
        return True
    return limits.max_memory_mb <= available_mb


def available_memory_mb() -> float | None:
    """Best-effort free memory, or None when it cannot be read without a helper."""
    try:
        pages = os.sysconf("SC_AVPHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return pages * page_size / (1024 * 1024)
    except (ValueError, OSError, AttributeError):
        return None


def measure(function, *args: Any, limits: ResourceLimits | None = None, **kwargs: Any):
    """Run ``function`` under a budget. Returns ``(result, usage)``.

    The limits are enforced after the call as well as, where the caller checks
    periodically, during it. A breach still returns the usage alongside the
    exception so a caller can record what happened.
    """
    budget = ResourceBudget(limits=limits or ResourceLimits())
    try:
        result = function(*args, **kwargs)
        usage = budget.usage()
        message = check_budget(budget.limits, usage)
    finally:
        budget.stop()
    if message:
        raise LimitBreach(message)
    return result, usage


def describe(limits: ResourceLimits) -> str:
    if limits.unbounded:
        return "no resource limits"
    parts = []
    if limits.max_memory_mb is not None:
        parts.append(f"memory <= {limits.max_memory_mb:.0f} MB")
    if limits.max_cpu_seconds is not None:
        parts.append(f"cpu <= {limits.max_cpu_seconds:.0f}s")
    if limits.max_runtime_seconds is not None:
        parts.append(f"runtime <= {limits.max_runtime_seconds:.0f}s")
    return "; ".join(parts)


def read_limits(config: dict[str, Any]) -> ResourceLimits:
    """Build limits from a config mapping, ignoring unknown keys."""
    known = {"max_memory_mb", "max_cpu_seconds", "max_runtime_seconds"}
    values = {key: config[key] for key in known if key in config and config[key] is not None}
    return ResourceLimits(**values)


__all__ = [
    "LimitBreach",
    "ResourceBudget",
    "ResourceLimits",
    "ResourceUsage",
    "affordable",
    "available_memory_mb",
    "check_budget",
    "cpu_seconds",
    "current_memory_mb",
    "describe",
    "measure",
    "read_limits",
    "traced_memory_mb",
]
