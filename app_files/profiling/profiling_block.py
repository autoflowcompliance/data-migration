"""Bind a config's ``profiling:`` block into a run.

The column statistics, pattern inference and outlier detection live in the
sibling modules of this package; nothing read them from a config. This is the
same additive binding as privacy, normalization, dedupe and quality: the block
is resolved through the one shared precedence chain
(``app_files/core/config.py``), and a config that declares no ``profiling:``
block produces no binding and changes nothing.

Named ``profiling_block`` rather than ``binding`` because
``profiling/binding.py`` already owns the quality-history store, and
overwriting it would be a change to an existing layer rather than an addition.

The block shape::

    profiling:
      statistics:
        enabled: true
        top_values: 5
      patterns:
        enabled: true
      outliers:
        enabled: true
        method: iqr          # iqr | zscore | isolation_forest
        k: 1.5

Unknown keys anywhere in the block are refused. A typo'd ``statistic:`` that
silently profiled nothing would be worse than no block at all, because the
operator would believe a report was being produced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.core import ConfigError, Layer
from app_files.core.config import resolve
from app_files.profiling.column_stats import ColumnStats, column_statistics
from app_files.profiling.outliers import (
    METHODS,
    OutlierResult,
    detect_outliers,
)
from app_files.profiling.patterns import InferredPattern, infer_column_pattern

MODULE = "profiling"
_KNOWN_TOP_LEVEL = {"statistics", "patterns", "outliers"}
_KNOWN_STATISTICS = {"enabled", "top_values"}
_KNOWN_PATTERNS = {"enabled"}
_KNOWN_OUTLIERS = {"enabled", "method", "k", "contamination", "seed", "columns"}

# The k a method uses when the block names a method but no k. Kept here rather
# than imported as a private name so the default is visible in one place.
_DEFAULT_K = {"iqr": 1.5, "zscore": 3.0}


class ProfilingBlockError(ConfigError):
    """Raised when a ``profiling:`` block cannot be resolved into safe settings."""


@dataclass
class ProfilingBinding:
    """A resolved ``profiling:`` policy, applied to one frame."""

    statistics_enabled: bool = False
    patterns_enabled: bool = False
    outliers_enabled: bool = False
    top_values: int = 5
    method: str = "iqr"
    k: float | None = None
    contamination: float | None = None
    seed: int = 0
    outlier_columns: list[str] | None = None
    statistics: list[ColumnStats] = field(default_factory=list)
    patterns: dict[str, InferredPattern] = field(default_factory=dict)
    outliers: dict[str, OutlierResult] = field(default_factory=dict)
    provenance: dict[str, Layer] = field(default_factory=dict)

    @staticmethod
    def defaults() -> dict[str, Any]:
        """The values a bare ``profiling:`` block resolves to.

        Every section defaults to off. Profiling costs time on a wide frame,
        so it is opt-in — a config that declares nothing pays nothing, which is
        the same rule the other block bindings follow.
        """
        return {
            "statistics": {"enabled": False, "top_values": 5},
            "patterns": {"enabled": False},
            "outliers": {"enabled": False, "method": "iqr", "seed": 0},
        }

    def source_of(self, dotted_key: str) -> Layer | None:
        return self.provenance.get(dotted_key)

    def summary(self) -> dict[str, Any]:
        return {
            "statistics": {stats.name: stats.as_dict() for stats in self.statistics},
            "patterns": {
                name: pattern.as_dict() for name, pattern in self.patterns.items()
            },
            "outliers": {
                name: result.as_dict() for name, result in self.outliers.items()
            },
        }


def _check_keys(block: dict[str, Any]) -> None:
    unknown = set(block) - _KNOWN_TOP_LEVEL
    if unknown:
        known = ", ".join(sorted(_KNOWN_TOP_LEVEL))
        raise ProfilingBlockError(
            f"profiling: unknown key(s) {', '.join(sorted(unknown))} (known: {known})"
        )
    for section, allowed in (
        ("statistics", _KNOWN_STATISTICS),
        ("patterns", _KNOWN_PATTERNS),
        ("outliers", _KNOWN_OUTLIERS),
    ):
        value = block.get(section)
        if isinstance(value, dict):
            bad = set(value) - allowed
            if bad:
                known = ", ".join(sorted(allowed))
                raise ProfilingBlockError(
                    f"profiling.{section}: unknown key(s) {', '.join(sorted(bad))} "
                    f"(known: {known})"
                )


def _as_bool(module: str, key: str, value: Any) -> bool:
    if isinstance(value, bool):
        return value
    raise ProfilingBlockError(f"{module}.{key} must be true or false, got {value!r}")


def profiling_from_config(
    config: dict[str, Any],
    *,
    with_provenance: bool = False,
    env: dict[str, str] | None = None,
    cli: dict[str, Any] | None = None,
) -> ProfilingBinding | None:
    """Resolve ``config``'s ``profiling:`` block, or ``None`` if it declares none.

    ``None`` is the signal to a caller to do no work and write no artifact.
    """
    block = config.get(MODULE)
    if block is None:
        return None
    if not isinstance(block, dict):
        raise ProfilingBlockError(
            f"profiling: must be a mapping, got {type(block).__name__}"
        )
    if not block:
        return None

    _check_keys(block)

    try:
        resolved = resolve(
            MODULE,
            ProfilingBinding.defaults(),
            yaml_values=block,
            env=env,
            cli=cli,
            with_provenance=with_provenance,
        )

        statistics = resolved.get("statistics") or {}
        patterns = resolved.get("patterns") or {}
        outliers = resolved.get("outliers") or {}
        for name, section in (
            ("statistics", statistics),
            ("patterns", patterns),
            ("outliers", outliers),
        ):
            if not isinstance(section, dict):
                raise ProfilingBlockError(
                    f"profiling.{name} must be a mapping, got {type(section).__name__}"
                )

        top_values = statistics.get("top_values", 5)
        if isinstance(top_values, bool) or not isinstance(top_values, int):
            raise ProfilingBlockError(
                "profiling.statistics.top_values must be a whole number, "
                f"got {top_values!r}"
            )
        if top_values < 0:
            raise ProfilingBlockError(
                "profiling.statistics.top_values must not be negative"
            )

        method = str(outliers.get("method", "iqr")).strip().lower()
        if method not in METHODS:
            raise ProfilingBlockError(
                "profiling.outliers.method must be one of "
                f"{', '.join(METHODS)}, got {method!r}"
            )

        raw_k = outliers.get("k")
        if raw_k is not None:
            if isinstance(raw_k, bool) or not isinstance(raw_k, (int, float)):
                raise ProfilingBlockError(
                    f"profiling.outliers.k must be a number, got {raw_k!r}"
                )
            if raw_k <= 0:
                raise ProfilingBlockError("profiling.outliers.k must be positive")
        else:
            raw_k = _DEFAULT_K.get(method)

        raw_contamination = outliers.get("contamination")
        if raw_contamination is not None:
            if isinstance(raw_contamination, bool) or not isinstance(
                raw_contamination, (int, float)
            ):
                raise ProfilingBlockError(
                    "profiling.outliers.contamination must be a number, "
                    f"got {raw_contamination!r}"
                )
            if not 0 < raw_contamination < 1:
                raise ProfilingBlockError(
                    "profiling.outliers.contamination must be between 0 and 1"
                )

        seed = outliers.get("seed", 0)
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ProfilingBlockError(
                f"profiling.outliers.seed must be a whole number, got {seed!r}"
            )

        columns = outliers.get("columns")
        if columns is not None and not isinstance(columns, list):
            raise ProfilingBlockError(
                "profiling.outliers.columns must be a list of column names, "
                f"got {type(columns).__name__}"
            )
    except ConfigError as exc:
        raise ProfilingBlockError(str(exc)) from exc

    return ProfilingBinding(
        statistics_enabled=_as_bool(
            MODULE, "statistics.enabled", statistics.get("enabled", False)
        ),
        patterns_enabled=_as_bool(
            MODULE, "patterns.enabled", patterns.get("enabled", False)
        ),
        outliers_enabled=_as_bool(
            MODULE, "outliers.enabled", outliers.get("enabled", False)
        ),
        top_values=int(top_values),
        method=method,
        k=None if raw_k is None else float(raw_k),
        contamination=None if raw_contamination is None else float(raw_contamination),
        seed=int(seed),
        outlier_columns=[str(name) for name in columns] if columns else None,
        provenance=getattr(resolved, "provenance", {}),
    )


def _numeric_columns(frame: pd.DataFrame, requested: list[str] | None) -> list[str]:
    """The columns to test for outliers: the requested ones, or the numeric ones.

    A text column has no outliers to find, and running a numeric method over
    one would either raise or report every value. Narrowing here keeps the
    report to columns where the answer means something.
    """
    from app_files.profiling.column_stats import summarize_column

    names = requested if requested is not None else list(frame.columns)
    numeric: list[str] = []
    for name in names:
        if name not in frame.columns:
            raise ProfilingBlockError(
                f"profiling.outliers.columns names {name!r}, which is not in the frame"
            )
        if summarize_column(frame, str(name)).kind == "numeric":
            numeric.append(str(name))
    return numeric


def bind_profiling(frame: pd.DataFrame, config: dict[str, Any]) -> ProfilingBinding | None:
    """Resolve the block and run its declared sections against ``frame``."""
    binding = profiling_from_config(config)
    if binding is None:
        return None

    if binding.statistics_enabled:
        binding.statistics = column_statistics(frame, top_values=binding.top_values)
    if binding.patterns_enabled:
        binding.patterns = {
            pattern.name: pattern for pattern in infer_column_pattern(frame)
        }
    if binding.outliers_enabled:
        # Each method takes its own parameters; passing the union would raise
        # on a keyword the method does not accept.
        kwargs: dict[str, Any] = {}
        if binding.method == "isolation_forest":
            kwargs["seed"] = binding.seed
            if binding.contamination is not None:
                kwargs["contamination"] = binding.contamination
        else:
            kwargs["k"] = binding.k
        for name in _numeric_columns(frame, binding.outlier_columns):
            binding.outliers[name] = detect_outliers(
                frame[name], method=binding.method, column=name, **kwargs
            )
    return binding


__all__ = [
    "ProfilingBinding",
    "ProfilingBlockError",
    "bind_profiling",
    "profiling_from_config",
]
