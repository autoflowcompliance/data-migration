"""Layer 19 — Schema drift gate: stop a changed source before it runs.

Layer 3's ``SchemaRegistry`` can *report* drift. Nothing acted on it, so a new,
removed or retyped column still reached the pipeline silently — the spec's
"no schema change reaches the pipeline silently" was unmet.

This layer decides, from the drift and how the mapping would land, whether a
run should proceed, proceed with warnings, or stop for a human. It is a policy
layer: it reads the frozen mapper's own suggestion machinery and writes nothing
the pipeline sees. Wiring it in is explicit and opt-in (``gate.check(...)``);
a run that never calls it behaves exactly as before.

Three verdicts:

``ok``       nothing changed, or there is no prior schema to compare against
``warn``     drift the mapping absorbs: an added column that maps to nothing,
             or a removed/retyped column no required target needed
``block``    drift that would leave a required target field unmapped — the run
             must not start unattended

An unknown source has no remembered schema and is never blocked: there is
nothing to have drifted from, so the gate cannot be the reason a first run
fails.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.mappers import load_mapping_config
from app_files.mappers.learning import (
    SchemaDrift,
    SchemaRegistry,
    normalise_column,
    schema_of,
)
from app_files.mappers.schema import MappingConfig
from app_files.mappers.yaml_mapper import _best_source
from app_files.pipeline import run_pipeline

OK = "ok"
WARN = "warn"
BLOCK = "block"


def _column_is_wanted(config: MappingConfig, column: str) -> bool:
    """Whether any target field would resolve to ``column`` by name or alias.

    This is the question that decides if a removed or retyped column matters:
    a column no target ever asked for can vanish harmlessly, and one a required
    target depended on cannot.
    """
    key = normalise_column(column)
    for target in config.fields:
        names = [target.name, *target.aliases]
        if any(normalise_column(name) == key for name in names):
            return True
    return False


def _matched_required(config: MappingConfig, columns: list[str]) -> set[str]:
    """Names of required target fields these columns can satisfy."""
    matched: set[str] = set()
    for target in config.fields:
        if not target.required:
            continue
        source, _score = _best_source(target, columns)
        if source is not None:
            matched.add(target.name)
    return matched


@dataclass
class DriftDecision:
    """What the gate decided, and why — both meant to be shown to a person."""

    source: str
    verdict: str
    reasons: list[str] = field(default_factory=list)
    blocked_columns: list[str] = field(default_factory=list)
    drift: SchemaDrift = field(default_factory=SchemaDrift)

    @property
    def proceed(self) -> bool:
        return self.verdict != BLOCK

    @property
    def has_drift(self) -> bool:
        return self.drift.has_drift

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "verdict": self.verdict,
            "proceed": self.proceed,
            "reasons": list(self.reasons),
            "blocked_columns": list(self.blocked_columns),
            "drift": self.drift.summary(),
        }

    def summary(self) -> str:
        if self.verdict == OK and not self.has_drift:
            base = f"No schema change for {self.source!r}."
            return base + (" " + " ".join(self.reasons) if self.reasons else "")
        headline = {
            OK: f"Schema change for {self.source!r} is benign.",
            WARN: f"Schema change for {self.source!r} may need attention.",
            BLOCK: f"Schema change for {self.source!r} must be reviewed before this run.",
        }[self.verdict]
        return headline + " " + " ".join(self.reasons)


class DriftBlocked(RuntimeError):
    """Raised when a run is stopped because the source schema changed."""

    def __init__(self, decision: DriftDecision):
        super().__init__(decision.summary())
        self.decision = decision


class DriftGate:
    """Decides whether a changed source may run, against the last schema seen.

    ``remember`` records the schema for a source. ``check`` compares a frame to
    the remembered schema and returns a :class:`DriftDecision`. Call ``remember``
    *after* a run has been accepted, so the next run is judged against what was
    actually migrated rather than against a schema that was never used.
    """

    def __init__(self, registry: SchemaRegistry | None = None):
        self.registry = registry or SchemaRegistry()

    def remember(self, source: str, frame: pd.DataFrame) -> None:
        self.registry.remember(source, frame)

    def last_schema(self, source: str) -> dict[str, str] | None:
        return self.registry.known(source)

    def guarded_run(
        self, source: str, frame: pd.DataFrame, crm: str, **pipeline_kwargs: Any
    ) -> tuple[Any, DriftDecision]:
        """Check drift, then run the real pipeline, then remember the schema.

        On a blocked verdict nothing runs: :class:`DriftBlocked` is raised with
        the decision attached. A ``warn`` verdict runs and is returned alongside
        the decision so the caller can surface it. This is the function that
        makes the gate binding rather than advisory — no schema change reaches
        the pipeline silently when a caller goes through it.
        """
        decision = self.check(source, frame, crm)
        if not decision.proceed:
            raise DriftBlocked(decision)
        result = run_pipeline(frame, crm, **pipeline_kwargs)
        self.remember(source, frame)
        return result, decision

    def check(self, source: str, frame: pd.DataFrame, crm: str) -> DriftDecision:
        """Judge ``frame`` for ``source`` against the target ``crm``.

        A source never seen before is ``ok``: there is no prior schema to drift
        from, and a first run must not be blocked by a gate meant to catch
        changes.
        """
        if self.registry.known(source) is None:
            return DriftDecision(
                source=source,
                verdict=OK,
                reasons=["first run for this source; nothing to compare against"],
            )

        drift = self.registry.check(source, frame)
        if not drift.has_drift:
            return DriftDecision(source=source, verdict=OK, drift=drift)

        config = load_mapping_config(crm)
        columns = [str(column) for column in frame.columns]
        known_columns = list(self.registry.known(source) or {})
        reasons: list[str] = []
        blocked: list[str] = []

        for name in drift.removed:
            if _column_is_wanted(config, name):
                blocked.append(name)
                reasons.append(
                    f"removed column {name!r} is required by the mapping"
                )
            else:
                reasons.append(f"removed column {name!r} was not mapped; ignored")

        for name in drift.retyped:
            # A retype only blocks when the column it describes is gone from
            # the frame, which the registry reports separately as removal. Here
            # the column is present, so the mapping still resolves it.
            reasons.append(f"retyped column {name!r}; the mapping still resolves it")

        for name in drift.added:
            reasons.append(f"added column {name!r} is unmapped; it will be ignored")

        # The decisive check is drift-relative: a required target that mapped
        # from the old schema but no longer maps is broken by the change. One
        # that was already unmapped before did not work before either, so the
        # gate must not pretend the drift caused it.
        lost = _matched_required(config, known_columns) - _matched_required(config, columns)
        for target_name in sorted(lost):
            reasons.append(
                f"required target {target_name!r} lost its source column in the change"
            )

        verdict = BLOCK if blocked or lost else WARN
        return DriftDecision(
            source=source,
            verdict=verdict,
            reasons=reasons,
            blocked_columns=blocked,
            drift=drift,
        )


__all__ = [
    "BLOCK",
    "OK",
    "WARN",
    "DriftBlocked",
    "DriftDecision",
    "DriftGate",
    "SchemaDrift",
    "schema_of",
]
