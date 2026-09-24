"""Resource limits: a job gets a budget and is stopped when it exceeds it.

The measurement is deliberately dependency-free. ``resource.getrusage`` gives
peak resident memory on POSIX; where it is unavailable the usage is reported as
zero-by-default and only the wall-clock limit bites, which is the honest
degradation: better to enforce one limit everywhere than to pretend to enforce
three and silently skip them.

A limit is checked *before* a job starts, against the budget it declares, and
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


def cpu_seconds() -> float:
    if _resource is None:
        return 0.0
    usage = _resource.getrusage(_resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


@dataclass
class ResourceBudget:
    """Tracks one job's consumption against its limits."""

    limits: ResourceLimits = field(default_factory=ResourceLimits)
    started_at: float = field(default_factory=time.monotonic)
    _cpu_at_start: float = field(default_factory=cpu_seconds)
    _memory_at_start: float = field(default_factory=current_memory_mb)

    def usage(self) -> ResourceUsage:
        growth = max(0.0, current_memory_mb() - self._memory_at_start)
        return ResourceUsage(
            peak_memory_mb=growth,
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
    result = function(*args, **kwargs)
    usage = budget.usage()
    message = check_budget(budget.limits, usage)
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
]
