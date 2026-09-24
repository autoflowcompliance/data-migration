"""Rule governance: cross-field rules, rule versioning, baseline comparison.

Three capabilities that turn a pile of per-column checks into a governed rule set:

* **Cross-field rules** — a condition that spans two or more columns, which a
  per-field rule cannot express. "If ``country`` is US, ``state`` must be a
  two-letter code"; "``end_date`` must not precede ``start_date``";
  "``total`` equals ``subtotal`` plus ``tax``". Each is evaluated row by row and
  reports the offending rows, the same way a single-field rule does.

* **Rule versioning** — every rule set gets a version. Two versions can be
  diffed, and each run records which version it used, so a change in results can
  be attributed to a rule change rather than to the data. The version hash is
  content-based, so the same rules always produce the same version.

* **Baseline comparison** — the pass/fail counts of a previous run, compared to
  the current one. "We had 12 failures, now we have 3" is the sentence that
  tells an operator the cleaning is working.

Pure logic, no network, deterministic.
"""

from __future__ import annotations

import hashlib
import json
import operator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

# ------------------------------------------------------------ cross-field rules
_OPERATORS = {
    "equals": operator.eq,
    "not_equals": operator.ne,
    "greater_than": operator.gt,
    "greater_or_equal": operator.ge,
    "less_than": operator.lt,
    "less_or_equal": operator.le,
    "contains": lambda a, b: b in str(a),
}


class CrossFieldError(ValueError):
    """Raised for a cross-field rule that cannot be compiled."""


@dataclass
class CrossFieldRule:
    """A condition spanning ``left`` and ``right`` columns.

    ``right`` is either a column name or a literal (a number, or a string when
    it is not the name of a column). ``left`` and ``right`` are coerced to
    numbers when both look numeric, so ``total`` vs ``subtotal + tax`` compares
    numerically rather than lexically.
    """

    name: str
    left: str
    operator_name: str
    right: str | float | int
    message: str = ""
    severity: str = "error"
    allow_blank: bool = True

    def __post_init__(self) -> None:
        if self.operator_name not in _OPERATORS:
            raise CrossFieldError(
                f"Unknown operator {self.operator_name!r}. "
                f"Available: {', '.join(sorted(_OPERATORS))}."
            )

    def evaluate(self, frame: pd.DataFrame) -> "CrossFieldResult":
        if self.left not in frame.columns:
            raise CrossFieldError(
                f"Rule {self.name!r} needs column {self.left!r}, "
                f"which is not in the frame."
            )
        right_is_column = isinstance(self.right, str) and self.right in frame.columns

        failures: list[dict[str, Any]] = []
        compared = 0
        for index, row in frame.iterrows():
            left_value = row[self.left]
            right_value = row[self.right] if right_is_column else self.right

            if self.allow_blank and (_is_blank(left_value) or _is_blank(right_value)):
                continue
            compared += 1

            left_number = _number(left_value)
            right_number = _number(right_value)
            if left_number is not None and right_number is not None:
                left_value, right_value = left_number, right_number

            try:
                ok = bool(_OPERATORS[self.operator_name](left_value, right_value))
            except TypeError:
                # Incomparable types are a failure, reported rather than raised:
                # a row of odd data must not stop the rule set.
                ok = False
            if not ok:
                failures.append(
                    {
                        "rule": self.name,
                        "row": int(index),
                        self.left: left_value,
                        str(self.right): right_value,
                        "message": self.message
                        or f"{self.left} {self.operator_name} {self.right} failed",
                    }
                )
        return CrossFieldResult(
            rule=self.name,
            severity=self.severity,
            passed=compared - len(failures),
            failed=len(failures),
            failures=failures,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "left": self.left,
            "operator": self.operator_name,
            "right": self.right,
            "message": self.message,
            "severity": self.severity,
        }


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return isinstance(value, str) and value.strip() == ""


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


@dataclass
class CrossFieldResult:
    rule: str
    severity: str
    passed: int
    failed: int
    failures: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "passed": self.passed,
            "failed": self.failed,
            "failures": self.failures,
        }


def run_cross_field_rules(
    frame: pd.DataFrame, rules: list[CrossFieldRule]
) -> list[CrossFieldResult]:
    return [rule.evaluate(frame) for rule in rules]


# ---------------------------------------------------------------- versioning
@dataclass
class RuleVersion:
    version: str
    rule_count: int
    created_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"version": self.version, "rule_count": self.rule_count, "created_at": self.created_at}


def version_rules(rules: list[Any], *, created_at: str = "") -> RuleVersion:
    """A content hash of the rule set.

    Two runs that used the same rules share a version; any change to any rule
    changes it. That is what lets a shift in results be attributed to a rule
    change rather than guessed at.
    """
    payload = json.dumps([_rule_dict(r) for r in rules], sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return RuleVersion(version=digest, rule_count=len(rules), created_at=created_at)


def _rule_dict(rule: Any) -> dict[str, Any]:
    if hasattr(rule, "as_dict"):
        return rule.as_dict()
    if isinstance(rule, dict):
        return rule
    return {k: v for k, v in vars(rule).items() if not k.startswith("_")}


@dataclass
class RuleDiff:
    added: list[dict[str, Any]]
    removed: list[dict[str, Any]]
    changed: list[dict[str, Any]]

    @property
    def empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def as_dict(self) -> dict[str, Any]:
        return {"added": self.added, "removed": self.removed, "changed": self.changed}


def diff_rule_versions(before: list[Any], after: list[Any]) -> RuleDiff:
    """What changed between two rule sets, by rule name."""
    before_by_name = {_rule_dict(r).get("name", ""): _rule_dict(r) for r in before}
    after_by_name = {_rule_dict(r).get("name", ""): _rule_dict(r) for r in after}

    added = [after_by_name[n] for n in after_by_name.keys() - before_by_name.keys()]
    removed = [before_by_name[n] for n in before_by_name.keys() - after_by_name.keys()]
    changed = [
        {"name": n, "before": before_by_name[n], "after": after_by_name[n]}
        for n in before_by_name.keys() & after_by_name.keys()
        if before_by_name[n] != after_by_name[n]
    ]
    return RuleDiff(added=added, removed=removed, changed=changed)


def version_history_path() -> Path:
    import os

    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path(__file__).resolve().parents[2]
    return base / "rule_versions.jsonl"


def record_rule_version(version: RuleVersion, *, path: str | Path | None = None) -> Path:
    """Append a version to the history log, so a run can be traced to its rules."""
    from datetime import datetime, timezone

    destination = Path(path) if path else version_history_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    entry = version.as_dict()
    entry["created_at"] = entry["created_at"] or datetime.now(timezone.utc).isoformat()
    with open(destination, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
    return destination


def read_rule_versions(path: str | Path | None = None) -> list[dict[str, Any]]:
    destination = Path(path) if path else version_history_path()
    if not destination.exists():
        return []
    entries = []
    with open(destination, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                entries.append(json.loads(line))
    return entries


# --------------------------------------------------------- baseline comparison
@dataclass
class BaselineComparison:
    rule: str
    baseline_failed: int
    current_failed: int

    @property
    def delta(self) -> int:
        return self.current_failed - self.baseline_failed

    @property
    def direction(self) -> str:
        if self.delta < 0:
            return "improving"
        if self.delta > 0:
            return "worsening"
        return "unchanged"

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "baseline_failed": self.baseline_failed,
            "current_failed": self.current_failed,
            "delta": self.delta,
            "direction": self.direction,
        }


def compare_to_baseline(
    baseline: dict[str, int], current: dict[str, int]
) -> list[BaselineComparison]:
    """Per-rule failure counts, before against now.

    A rule present in the baseline but not now is treated as 0 failures rather
    than dropped, so removing a rule shows up as an improvement instead of
    disappearing.
    """
    names = sorted(set(baseline) | set(current))
    return [
        BaselineComparison(
            rule=name,
            baseline_failed=int(baseline.get(name, 0)),
            current_failed=int(current.get(name, 0)),
        )
        for name in names
    ]


def failures_from_results(results: list[Any]) -> dict[str, int]:
    """Fold rule results into ``{rule_name: failed_count}``, for the baseline."""
    counts: dict[str, int] = {}
    for result in results:
        name = getattr(result, "rule", None) or getattr(result, "name", "")
        failed = getattr(result, "failed", None)
        if failed is None and isinstance(result, dict):
            name = result.get("rule", name)
            failed = result.get("failed", 0)
        counts[str(name)] = int(failed or 0)
    return counts