"""Rule versioning and sandbox promotion.

A rule set changes; when it does, someone should be able to answer "what
changed, who changed it, and would it have failed the files we already ran?".
This module stores every version of a rule set under ``AUTOFLOW_HOME`` and
makes the sandbox step part of the only path to production.

- ``save_version`` records a rule set (single-field or cross-field) as a new
  immutable version.
- ``sandbox_run`` evaluates a candidate version against recent frames without
  promoting it.
- ``promote`` moves a sandboxed version to production, refusing if it was
  never sandboxed, and records the decision.
- ``rollback_to`` restores an earlier version, appending a new version rather
  than deleting history.
- ``SandboxStore.history`` lists the versions for a rule set.

Versions are append-only. Rolling back does not erase the version that was
rolled back from, so the audit trail survives the reversal.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_files.rules.cross_field import (
    CrossFieldResult,
    CrossFieldRule,
    run_cross_field_rules,
)


class RuleVersionError(RuntimeError):
    """Raised when a version operation is invalid (e.g. promoting a stranger)."""


def rules_home() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "rules"


def _slug(text: str) -> str:
    keep = [ch if ch.isalnum() or ch in "-_." else "_" for ch in str(text)]
    return "".join(keep) or "ruleset"


@dataclass
class RuleVersion:
    """One immutable version of a rule set."""

    rule_set: str
    version: int
    status: str
    created_at: str
    single_field: list[dict[str, Any]] = field(default_factory=list)
    cross_field: list[dict[str, Any]] = field(default_factory=list)
    sandbox_runs: list[dict[str, Any]] = field(default_factory=list)
    note: str = ""

    @property
    def rule_count(self) -> int:
        return len(self.single_field) + len(self.cross_field)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_set": self.rule_set,
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at,
            "single_field": list(self.single_field),
            "cross_field": list(self.cross_field),
            "sandbox_runs": list(self.sandbox_runs),
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RuleVersion:
        return cls(
            rule_set=str(data["rule_set"]),
            version=int(data["version"]),
            status=str(data.get("status", "draft")),
            created_at=str(data.get("created_at", "")),
            single_field=list(data.get("single_field", [])),
            cross_field=list(data.get("cross_field", [])),
            sandbox_runs=list(data.get("sandbox_runs", [])),
            note=str(data.get("note", "")),
        )


@dataclass
class SandboxOutcome:
    """What a candidate version did to the sample frames, before promotion."""

    rule_set: str
    version: int
    frames_tested: int = 0
    failures: int = 0
    failures_by_rule: dict[str, int] = field(default_factory=dict)
    skipped_rules: list[str] = field(default_factory=list)
    per_frame: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_set": self.rule_set,
            "version": self.version,
            "frames_tested": self.frames_tested,
            "failures": self.failures,
            "failures_by_rule": dict(self.failures_by_rule),
            "skipped_rules": list(self.skipped_rules),
            "per_frame": list(self.per_frame),
        }

    def render(self) -> str:
        lines = [
            f"Sandbox: {self.rule_set} v{self.version}",
            "=" * 60,
            f"Frames tested: {self.frames_tested}",
            f"Failures: {self.failures}",
        ]
        for name, count in sorted(self.failures_by_rule.items()):
            lines.append(f"  {name}: {count}")
        if self.skipped_rules:
            lines.append("Skipped (column absent): " + ", ".join(self.skipped_rules))
        return "\n".join(lines)


class SandboxStore:
    """Version history and sandbox state for rule sets, under ``AUTOFLOW_HOME``."""

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else rules_home()

    def _path(self, rule_set: str) -> Path:
        return self.root / f"{_slug(rule_set)}.json"

    def history(self, rule_set: str) -> list[RuleVersion]:
        path = self._path(rule_set)
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [RuleVersion.from_dict(item) for item in payload.get("versions", [])]

    def _write(self, rule_set: str, versions: list[RuleVersion]) -> None:
        self._path(rule_set).parent.mkdir(parents=True, exist_ok=True)
        self._path(rule_set).write_text(
            json.dumps({"versions": [v.as_dict() for v in versions]}, indent=2),
            encoding="utf-8",
        )

    def latest(self, rule_set: str) -> RuleVersion | None:
        versions = self.history(rule_set)
        return versions[-1] if versions else None

    def production(self, rule_set: str) -> RuleVersion | None:
        for version in reversed(self.history(rule_set)):
            if version.status == "production":
                return version
        return None

    def save_version(
        self,
        rule_set: str,
        single_field: Iterable[Any] = (),
        cross_field: Iterable[Any] = (),
        note: str = "",
    ) -> RuleVersion:
        """Record a new immutable version. Starts in ``draft``."""
        versions = self.history(rule_set)
        version = RuleVersion(
            rule_set=rule_set,
            version=(versions[-1].version + 1) if versions else 1,
            status="draft",
            created_at=datetime.now(timezone.utc).isoformat(),
            single_field=[_rule_dict(rule) for rule in single_field],
            cross_field=[_rule_dict(rule) for rule in cross_field],
            note=note,
        )
        versions.append(version)
        self._write(rule_set, versions)
        return version

    def sandbox_run(
        self,
        rule_set: str,
        version: int,
        frames: Iterable[Any],
    ) -> SandboxOutcome:
        """Run a candidate against sample frames. Never promotes."""
        record = self._find(rule_set, version)
        outcome = SandboxOutcome(rule_set=rule_set, version=version)
        cross_rules = [CrossFieldRule.from_dict(item) for item in record.cross_field]
        for index, frame in enumerate(frames):
            outcome.frames_tested += 1
            result: CrossFieldResult = run_cross_field_rules(frame, cross_rules)
            outcome.failures += result.total_failures
            for name, count in result.failures_by_rule.items():
                outcome.failures_by_rule[name] = outcome.failures_by_rule.get(name, 0) + count
            for name in result.skipped_rules:
                if name not in outcome.skipped_rules:
                    outcome.skipped_rules.append(name)
            outcome.per_frame.append(
                {"frame": index, "rows": int(len(frame)), "failures": result.total_failures}
            )
        self._mutate(rule_set, version, lambda entry: entry.sandbox_runs.append(outcome.as_dict()))
        return outcome

    def promote(self, rule_set: str, version: int, note: str = "") -> RuleVersion:
        """Move a version to production. Requires a sandbox run first."""
        target = self._find(rule_set, version)
        if not target.sandbox_runs:
            raise RuleVersionError(
                f"Version {version} of {rule_set!r} has no sandbox run; "
                "no rule set reaches production without one"
            )
        if target.status == "production":
            return target
        versions = self.history(rule_set)
        for entry in versions:
            if entry.status == "production":
                entry.status = "superseded"
            elif entry.version == version:
                entry.status = "production"
                if note:
                    entry.note = note
        self._write(rule_set, versions)
        return self._find(rule_set, version)

    def rollback_to(self, rule_set: str, version: int, note: str = "") -> RuleVersion:
        """Restore an earlier version as a *new* version, preserving history."""
        target = self._find(rule_set, version)
        restored = self.save_version(
            rule_set,
            single_field=target.single_field,
            cross_field=target.cross_field,
            note=note or f"Rollback to version {version}",
        )
        # A rollback is a promotion decision too, so it carries an explicit
        # (empty) sandbox record rather than bypassing the promotion guard.
        self._mutate(
            rule_set,
            restored.version,
            lambda entry: entry.sandbox_runs.append(
                {"rollback_of": version, "frames_tested": 0, "failures": 0}
            ),
        )
        return self.promote(rule_set, restored.version, note=note or restored.note)

    def _mutate(
        self, rule_set: str, version: int, change: Any
    ) -> RuleVersion:
        """Apply ``change`` to one version and persist the whole list once.

        ``history`` returns fresh objects, so a mutation applied to one of them
        is lost unless the same list is written back.
        """
        versions = self.history(rule_set)
        target = next(
            (entry for entry in versions if entry.version == version), None
        )
        if target is None:
            raise RuleVersionError(f"No version {version} for {rule_set!r}")
        change(target)
        self._write(rule_set, versions)
        return target

    def _find(self, rule_set: str, version: int) -> RuleVersion:
        for record in self.history(rule_set):
            if record.version == version:
                return record
        raise RuleVersionError(f"No version {version} for {rule_set!r}")


def _rule_dict(rule: Any) -> dict[str, Any]:
    if hasattr(rule, "as_dict"):
        return dict(rule.as_dict())
    if isinstance(rule, dict):
        return dict(rule)
    return dataclass_dict(rule)


def dataclass_dict(rule: Any) -> dict[str, Any]:
    """Fallback for the rules layer's single-field ``Rule`` dataclass."""
    from dataclasses import asdict, is_dataclass

    if is_dataclass(rule) and not isinstance(rule, type):
        payload = asdict(rule)  # type: ignore[arg-type]
        return {key: value for key, value in payload.items() if not key.startswith("_")}
    raise RuleVersionError(f"Cannot serialise rule of type {type(rule).__name__}")


__all__ = [
    "RuleVersion",
    "RuleVersionError",
    "SandboxOutcome",
    "SandboxStore",
    "rules_home",
]
