"""Module 10 — quality SLA and the action a regression should take.

Layer 5 answers "what is this run's quality" and "is it worse than the run we
accepted". Neither answer *does* anything, so a source that falls below an
agreed floor still reaches its destination and a regression is a line in a
report.

This package adds the two pieces the specification calls for and the frozen
layers could not express:

* an **SLA** — a per-dimension floor (``quality.sla.completeness: 0.98``) that a
  run is judged against, with a verdict naming every dimension that breached;
* a **regression action** — ``alert | block | quarantine``, so "this regressed"
  becomes a decision a run path can act on rather than a message.

Both read the existing ``Profile`` and ``BaselineComparison``. Neither writes
anything the pipeline sees, and neither changes a score. A run that declares no
``quality:`` block behaves exactly as before.

Dimensions are scored 0-100 by Layer 5 and floors are written 0-1 in config, so
the comparison normalises: a floor of ``0.98`` and one of ``98.0`` mean the same
thing, and both are accepted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app_files.core import ConfigError
from app_files.profiling.baseline import BaselineComparison
from app_files.profiling.dimensions import DIMENSIONS
from app_files.profiling.profiler import Profile

# A floor above 1.0 is read as a 0-100 percentage, matching Layer 5's scale.
_PERCENT_SCALE = 100.0


class Action(str, Enum):
    """What to do when a run regresses against its baseline.

    ``alert`` is the default because it is the only one that cannot lose data:
    the run completes and the operator is told. ``block`` stops the run before
    output is written; ``quarantine`` also stops it but marks the output as held
    for review rather than simply absent.
    """

    ALERT = "alert"
    BLOCK = "block"
    QUARANTINE = "quarantine"

    @classmethod
    def default(cls) -> "Action":
        return cls.ALERT

    @classmethod
    def parse(cls, value: Any) -> "Action":
        """Parse ``value``, failing closed on anything unrecognised."""
        if isinstance(value, Action):
            return value
        text = str(value).strip().lower()
        for action in cls:
            if action.value == text:
                return action
        known = ", ".join(action.value for action in cls)
        raise ConfigError(f"unknown regression action {value!r} (known: {known})")


@dataclass(frozen=True)
class SLABreach:
    """One dimension that fell below its floor."""

    dimension: str
    required: float
    actual: float

    @property
    def shortfall(self) -> float:
        """How far below the floor, in the same 0-1 units as ``required``."""
        return round(self.required - self.actual, 4)

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "required": self.required,
            "actual": round(self.actual, 4),
            "shortfall": self.shortfall,
        }


@dataclass
class SLAVerdict:
    """Whether a run met its SLA, and every dimension that did not."""

    passed: bool
    breaches: list[SLABreach] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "breaches": [breach.as_dict() for breach in self.breaches],
            "skipped": list(self.skipped),
        }

    def describe(self) -> str:
        """A console line a run can print."""
        if self.passed:
            return "Quality SLA met."
        parts = [
            f"{breach.dimension} {breach.actual:.1%} < {breach.required:.1%}"
            for breach in self.breaches
        ]
        return "Quality SLA breached: " + ", ".join(parts)


@dataclass
class QualitySLA:
    """Per-dimension floors, declared in config as fractions or percentages.

    An unset dimension (``None``) is not enforced. That is deliberately
    different from ``0.0``, which is a floor nothing can fail: the difference
    between "no floor agreed" and "any score is acceptable" matters when the
    SLA is being reviewed, so both are kept distinct.

    Floors are normalised to 0-1 on construction whichever way the object is
    built. ``from_block`` is the documented entry point, but building the
    dataclass directly is easy to do by accident, and a floor of ``98.0`` that
    stayed 98.0 would compare against a 0-100 score and never fire — a silent
    no-op in the one check meant to catch bad data.

    Two forms are accepted and the boundary is explicit, because ``1.5`` is
    genuinely ambiguous — 150% (a typo) or 1.5%? Guessing would be fail-open in
    the check whose whole job is to fail closed, so the ambiguous middle is
    refused rather than interpreted:

    * ``0.0``–``1.0`` is a fraction: ``0.98`` means 98%.
    * a whole number ``2``–``100`` is a percentage: ``98`` means 98%.
    * anything else is refused, with the message saying which form to write.
    """

    completeness: float | None = None
    uniqueness: float | None = None
    validity: float | None = None
    consistency: float | None = None
    timeliness: float | None = None

    def __post_init__(self) -> None:
        for name in DIMENSIONS:
            value = getattr(self, name)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ConfigError(f"quality.sla.{name} must be a number, got {value!r}")
            numeric = float(value)
            if numeric < 0:
                raise ConfigError(f"quality.sla.{name} must not be negative")
            if numeric <= 1.0:
                setattr(self, name, numeric)
                continue
            if numeric > _PERCENT_SCALE or numeric != int(numeric):
                raise ConfigError(
                    f"quality.sla.{name}={value} is ambiguous or out of range; "
                    "write a fraction between 0 and 1 (e.g. 0.98) or a whole "
                    "percentage (e.g. 98)"
                )
            setattr(self, name, numeric / _PERCENT_SCALE)

    @classmethod
    def from_block(cls, block: dict[str, Any] | None) -> "QualitySLA":
        """Build an SLA from a ``quality.sla`` mapping.

        Unknown dimension names are refused rather than ignored: a typo'd
        ``completness: 0.98`` that silently enforces nothing is the exact
        failure mode an SLA exists to prevent.
        """
        if not block:
            return cls()
        if not isinstance(block, dict):
            raise ConfigError(
                f"quality.sla must be a mapping, got {type(block).__name__}"
            )
        for name in block:
            if name not in DIMENSIONS:
                known = ", ".join(sorted(DIMENSIONS))
                raise ConfigError(
                    f"quality.sla: unknown dimension {name!r} (known: {known})"
                )
        # Normalisation, range checks and type checks all live in __post_init__,
        # so a direct construction and a parsed block cannot disagree.
        return cls(**block)

    def declared(self) -> dict[str, float]:
        """Only the floors that were actually set."""
        return {
            name: getattr(self, name)
            for name in DIMENSIONS
            if getattr(self, name) is not None
        }

    def as_dict(self) -> dict[str, Any]:
        return dict(self.declared())


def evaluate_sla(profile_result: Profile, sla: QualitySLA) -> SLAVerdict:
    """Judge ``profile_result`` against ``sla``.

    A dimension the frame had nothing to evaluate is *skipped*, not failed. A
    contact file with no date column cannot have a timeliness score, and
    failing it would punish the file for its shape rather than its quality —
    the same reasoning Layer 5 uses when it drops inapplicable dimensions from
    the overall average.
    """
    breaches: list[SLABreach] = []
    skipped: list[str] = []

    for dimension, floor in sla.declared().items():
        applicable = getattr(profile_result, "applicable", None)
        if applicable is not None and dimension not in applicable:
            skipped.append(dimension)
            continue
        if dimension not in profile_result.scores:
            skipped.append(dimension)
            continue
        actual = float(profile_result.scores[dimension]) / _PERCENT_SCALE
        if actual < floor:
            breaches.append(
                SLABreach(dimension=dimension, required=floor, actual=actual)
            )

    return SLAVerdict(passed=not breaches, breaches=breaches, skipped=skipped)


@dataclass
class RegressionDecision:
    """What a regression action decided for one run."""

    action: Action
    regressed: bool
    comparison: BaselineComparison | None = None

    @property
    def proceed(self) -> bool:
        """Whether the run may continue to write output."""
        if not self.regressed:
            return True
        return self.action is Action.ALERT

    @property
    def quarantine(self) -> bool:
        return self.regressed and self.action is Action.QUARANTINE

    def summary(self) -> str:
        if not self.regressed:
            return "No regression against baseline."
        dimensions = (
            ", ".join(self.comparison.regressed_dimensions)
            if self.comparison is not None
            else "unknown"
        )
        if self.action is Action.ALERT:
            return f"Regression in {dimensions}; alerted, run continues."
        if self.action is Action.QUARANTINE:
            return f"Regression in {dimensions}; output quarantined for review."
        return f"Regression in {dimensions}; run blocked before output."

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "regressed": self.regressed,
            "proceed": self.proceed,
            "quarantine": self.quarantine,
            "dimensions": list(self.comparison.regressed_dimensions)
            if self.comparison is not None
            else [],
        }


def regression_action(history: Any, action: Action | str = Action.ALERT) -> RegressionDecision:
    """Turn a run's quality history into a proceed/stop decision.

    ``history`` is the ``QualityHistory`` the existing ``record_quality``
    returns. A source with no baseline has no comparison, so it cannot regress
    and every action lets it through — a first run must not be blocked by a
    check that needs history to mean anything.
    """
    resolved = Action.parse(action)
    comparison = getattr(history, "comparison", None)
    regressed = comparison is not None and comparison.alerting
    return RegressionDecision(action=resolved, regressed=regressed, comparison=comparison)


__all__ = [
    "Action",
    "QualitySLA",
    "RegressionDecision",
    "SLABreach",
    "SLAVerdict",
    "evaluate_sla",
    "regression_action",
]
