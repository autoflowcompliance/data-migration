"""The profiler registry: one registration point, the existing plugin one.

The specification is explicit that the extension point is
``app_files/plugins/registry.py`` and not a second registry. So this module
owns the storage and the accessor, and ``PluginRegistry.profiler`` is the
plugin-facing way in — the same pattern ``transform``, ``rule_type``,
``output_format`` and ``destination`` already follow.

Built-ins are registered at import so a caller gets statistics and patterns
without loading anything.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

PROFILER_KIND = "profiler"

# A profiler takes a frame and returns whatever it likes; the registry only
# enforces that it is callable, exactly as ``register_transform`` does.
Profiler = Callable[[pd.DataFrame], Any]

PROFILERS: dict[str, Profiler] = {}


def register_profiler(name: str, function: Profiler, override: bool = False) -> Profiler:
    """Add a profiler to the registry.

    A callable is required because a non-callable registration fails later,
    inside a run, with an error that names the value rather than the profiler
    that produced it — the same reasoning as ``register_transform``.
    """
    key = str(name).strip()
    if not key:
        raise ValueError("A profiler needs a name")
    if not callable(function):
        raise ValueError(
            f"Profiler {name!r} must be callable, got {type(function).__name__}"
        )
    if key in PROFILERS and not override:
        raise ValueError(
            f"Profiler {name!r} already exists. Pass override=True to replace it."
        )
    PROFILERS[key] = function
    return function


def get_profiler(name: str) -> Profiler:
    """The named profiler, or a ``KeyError`` naming it."""
    try:
        return PROFILERS[str(name)]
    except KeyError:
        known = ", ".join(profiler_names()) or "none"
        raise KeyError(f"No profiler {name!r}. Registered: {known}") from None


def profiler_names() -> list[str]:
    return sorted(PROFILERS)


def _statistics(frame: pd.DataFrame) -> list[Any]:
    from app_files.profiling.column_stats import column_statistics

    return column_statistics(frame)


def _patterns(frame: pd.DataFrame) -> list[Any]:
    from app_files.profiling.patterns import infer_column_pattern

    return infer_column_pattern(frame)


register_profiler("statistics", _statistics)
register_profiler("patterns", _patterns)

__all__ = [
    "PROFILER_KIND",
    "PROFILERS",
    "Profiler",
    "get_profiler",
    "profiler_names",
    "register_profiler",
]
