"""Bind a config's ``quality:`` block into a run.

The SLA and regression action live in ``app_files.quality``; nothing read them.
This is the same additive binding as privacy, normalization, dedupe and the
quality history: the block is resolved through the one shared precedence chain
(``app_files/core/config.py``), and a config that declares no ``quality:`` block
produces no binding and changes nothing.

The block shape::

    quality:
      sla:
        completeness: 0.98
        validity: 0.95
      regression:
        threshold: 2.0        # percentage points of drop before it counts
        action: alert         # alert | block | quarantine

Unknown keys anywhere in the block are refused. A typo'd ``slaa:`` that
silently enforced nothing would be worse than no block at all, because the
operator would believe a floor was in place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.core import ConfigError, Layer
from app_files.core.config import resolve
from app_files.profiling.baseline import DEFAULT_DROP_THRESHOLD
from app_files.profiling.profiler import Profile, profile
from app_files.quality import (
    Action,
    QualitySLA,
    RegressionDecision,
    SLAVerdict,
    evaluate_sla,
    regression_action,
)

MODULE = "quality"
_KNOWN_TOP_LEVEL = {"sla", "regression", "baseline"}
_KNOWN_REGRESSION = {"threshold", "action"}


class QualityBlockError(ConfigError):
    """Raised when a ``quality:`` block cannot be resolved into a safe policy."""


@dataclass
class QualityBinding:
    """A resolved ``quality:`` policy, applied to one frame.

    ``profile_result`` is the existing Layer 5 ``Profile``; this binding does
    not compute a second one.
    """

    sla: QualitySLA
    action: Action
    threshold: float
    profile_result: Profile | None = None
    verdict: SLAVerdict | None = None
    provenance: dict[str, Layer] = field(default_factory=dict)

    @staticmethod
    def defaults() -> dict[str, Any]:
        """The values a bare ``quality:`` block resolves to.

        No SLA is imposed by default: a floor nobody agreed to would fail runs
        for a policy that was never stated. The regression action defaults to
        ``alert``, which cannot lose data, and the threshold reuses Layer 5's
        existing constant so the two cannot drift.
        """
        return {
            "sla": {},
            "regression": {
                "action": Action.default().value,
                "threshold": DEFAULT_DROP_THRESHOLD,
            },
        }

    @property
    def breached(self) -> bool:
        return self.verdict is not None and not self.verdict.passed

    def decide(self, history: Any) -> RegressionDecision:
        """Apply the declared action to a run's quality history."""
        return regression_action(history, self.action)

    def summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "sla_declared": self.sla.declared(),
            "sla_breached": self.breached,
            "breaches": self.verdict.summary()["breaches"] if self.verdict else [],
            "skipped": list(self.verdict.skipped) if self.verdict else [],
            "action": self.action.value,
            "threshold": self.threshold,
        }
        if self.profile_result is not None:
            result["overall"] = round(float(self.profile_result.overall), 1)
        return result

    def describe(self) -> str:
        if self.verdict is None:
            return "Quality block declared; no SLA evaluated."
        return self.verdict.describe()


def _check_keys(block: dict[str, Any]) -> None:
    """Refuse an unknown key at any level of the block."""
    unknown = set(block) - _KNOWN_TOP_LEVEL
    if unknown:
        known = ", ".join(sorted(_KNOWN_TOP_LEVEL))
        raise QualityBlockError(
            f"quality: unknown key(s) {', '.join(sorted(unknown))} (known: {known})"
        )
    regression = block.get("regression")
    if isinstance(regression, dict):
        unknown = set(regression) - _KNOWN_REGRESSION
        if unknown:
            known = ", ".join(sorted(_KNOWN_REGRESSION))
            raise QualityBlockError(
                f"quality.regression: unknown key(s) {', '.join(sorted(unknown))} "
                f"(known: {known})"
            )


def quality_from_config(
    config: dict[str, Any],
    *,
    with_provenance: bool = False,
    env: dict[str, str] | None = None,
) -> QualityBinding | None:
    """Resolve ``config``'s ``quality:`` block, or ``None`` if it declares none.

    ``None`` is the signal to a caller to write no artifact and change no
    behaviour, exactly as the other block bindings do.
    """
    block = config.get(MODULE)
    if block is None:
        return None
    if not isinstance(block, dict):
        raise QualityBlockError(
            f"quality: must be a mapping, got {type(block).__name__}"
        )
    if not block:
        return None

    _check_keys(block)

    try:
        resolved = resolve(
            MODULE,
            QualityBinding.defaults(),
            yaml_values=block,
            env=env,
            with_provenance=with_provenance,
        )

        sla = QualitySLA.from_block(resolved.get("sla") or {})
        regression = resolved.get("regression") or {}
        if not isinstance(regression, dict):
            raise QualityBlockError(
                f"quality.regression must be a mapping, "
                f"got {type(regression).__name__}"
            )

        action = Action.parse(regression.get("action", Action.default().value))
        raw_threshold = regression.get("threshold", DEFAULT_DROP_THRESHOLD)
        if isinstance(raw_threshold, bool) or not isinstance(
            raw_threshold, (int, float)
        ):
            raise QualityBlockError(
                f"quality.regression.threshold must be a number, "
                f"got {raw_threshold!r}"
            )
        if raw_threshold < 0:
            raise QualityBlockError(
                "quality.regression.threshold must not be negative"
            )
    except ConfigError as exc:
        # One type for the caller to catch. The underlying errors from the
        # shared resolver and from QualitySLA already name the key; re-wrapping
        # keeps the message and adds nothing.
        raise QualityBlockError(str(exc)) from exc

    binding = QualityBinding(
        sla=sla,
        action=action,
        threshold=float(raw_threshold),
        provenance=getattr(resolved, "provenance", {}),
    )
    return binding


def bind_quality(
    frame: pd.DataFrame,
    config: dict[str, Any],
    *,
    env: dict[str, str] | None = None,
) -> QualityBinding | None:
    """Resolve the block and judge ``frame`` against it.

    Profiling is skipped entirely when no block is declared, so an unbound run
    does no extra work and cannot change its output.
    """
    binding = quality_from_config(config, env=env)
    if binding is None:
        return None
    binding.profile_result = profile(frame)
    binding.verdict = evaluate_sla(binding.profile_result, binding.sla)
    return binding


def check_regression(
    source: str,
    binding: QualityBinding,
    store: Any | None = None,
) -> RegressionDecision:
    """Judge a run against its source's *stored* baseline, reading nothing else.

    Deliberately read-only. ``record_quality`` writes a run into the history,
    which is right for a run that wants history and wrong for a check that is
    being asked a question — a gate that quietly appends to the thing it is
    measuring can move its own baseline. Recording is opt-in through
    ``--record``/``--baseline``; this only reads.

    A source with no pinned baseline cannot regress, so every action lets it
    through: a first check must not fail for want of history.
    """
    from app_files.profiling.baseline import compare_to_stored_baseline
    from app_files.profiling.binding import source_key
    from app_files.profiling.trends import TrendStore

    if binding.profile_result is None:
        return RegressionDecision(action=binding.action, regressed=False)

    store = store if store is not None else TrendStore()
    comparison = compare_to_stored_baseline(
        source_key(source), binding.profile_result, store, threshold=binding.threshold
    )
    decision = regression_action(
        _Comparison(comparison=comparison), binding.action
    )
    return decision


@dataclass
class _Comparison:
    """The minimum ``regression_action`` reads: an optional comparison."""

    comparison: Any | None


__all__ = [
    "QualityBinding",
    "QualityBlockError",
    "bind_quality",
    "check_regression",
    "quality_from_config",
]
