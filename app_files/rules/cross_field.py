"""Cross-field rules: one rule, more than one column.

The frozen engine validates one field at a time (``range``, ``length``,
``regex`` and friends). Some of the rules a buyer actually wants span two:
``close_date`` must not precede ``open_date``; ``total`` must equal
``subtotal + tax``. Those cannot be expressed as a per-field rule without
lying about which field failed.

This module adds exactly that, as a sibling to the engine. It produces the
same ``Issue`` objects, so cross-field failures flow into the existing issues
CSV and QA report with no change to the reporter.

Operators are declared as YAML-safe strings, so a rule set can live in a
config alongside the single-field rules:

    cross_field:
      - name: close_after_open
        type: date_order
        fields: [open_date, close_date]
        severity: error
      - name: total_matches_parts
        type: sum_equals
        fields: [total, subtotal, tax]
        tolerance: 0.01
      - name: shipped_before_refund
        type: compare
        fields: [ship_date, refund_date]
        operator: "<="
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any

import pandas as pd

from app_files.transforms import is_missing

CROSS_FIELD_TYPES = ("compare", "sum_equals", "date_order")
COMPARISON_OPERATORS = ("<", "<=", "==", "!=", ">", ">=")


class CrossFieldRuleError(ValueError):
    """Raised when a cross-field rule is malformed."""


@dataclass
class CrossFieldRule:
    """A rule that reads two or more columns and reports one row-level failure."""

    name: str
    type: str
    fields: list[str]
    severity: str = "error"
    operator: str | None = None
    tolerance: float = 0.0
    message: str = ""
    date_format: str | None = None

    _KNOWN = frozenset(
        {
            "name", "type", "fields", "severity", "operator", "tolerance",
            "message", "date_format",
        }
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CrossFieldRule:
        if not isinstance(data, dict):
            raise CrossFieldRuleError(
                f"Each cross-field rule must be a mapping, got {type(data).__name__}"
            )
        unknown = set(data) - cls._KNOWN
        if unknown:
            raise CrossFieldRuleError(
                f"Cross-field rule has unknown keys: {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(cls._KNOWN))}"
            )
        name = str(data.get("name", "")).strip()
        if not name:
            raise CrossFieldRuleError("Cross-field rule needs a name")
        rule_type = str(data.get("type", "")).strip().lower()
        if rule_type not in CROSS_FIELD_TYPES:
            raise CrossFieldRuleError(
                f"Cross-field rule {name!r} has unknown type {rule_type!r}. "
                f"Allowed: {', '.join(CROSS_FIELD_TYPES)}"
            )
        raw_fields = data.get("fields")
        if not isinstance(raw_fields, (list, tuple)) or len(raw_fields) < 2:
            raise CrossFieldRuleError(
                f"Cross-field rule {name!r} needs a 'fields' list of at least two columns"
            )
        fields = [str(item).strip() for item in raw_fields]
        if len(set(fields)) != len(fields):
            # A repeated column makes a row lookup ambiguous, so the rule would
            # silently evaluate nothing rather than compare two values.
            raise CrossFieldRuleError(
                f"Cross-field rule {name!r} lists a column more than once: "
                f"{', '.join(fields)}"
            )
        if rule_type == "sum_equals" and len(fields) < 3:
            raise CrossFieldRuleError(
                f"Cross-field rule {name!r} of type sum_equals needs total plus at "
                "least two parts"
            )
        operator = data.get("operator")
        if rule_type == "compare":
            if operator is None:
                raise CrossFieldRuleError(
                    f"Cross-field rule {name!r} of type compare needs an 'operator'"
                )
            operator = str(operator).strip()
            if operator not in COMPARISON_OPERATORS:
                raise CrossFieldRuleError(
                    f"Cross-field rule {name!r} has unknown operator {operator!r}. "
                    f"Allowed: {', '.join(COMPARISON_OPERATORS)}"
                )
        severity = str(data.get("severity", "error")).strip().lower()
        if severity not in ("error", "warning", "info"):
            raise CrossFieldRuleError(
                f"Cross-field rule {name!r} has unknown severity {severity!r}"
            )
        return cls(
            name=name,
            type=rule_type,
            fields=fields,
            severity=severity,
            operator=operator,
            tolerance=float(data.get("tolerance", 0.0) or 0.0),
            message=str(data.get("message", "")),
            date_format=data.get("date_format"),
        )

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "fields": list(self.fields),
            "severity": self.severity,
        }
        if self.operator:
            payload["operator"] = self.operator
        if self.tolerance:
            payload["tolerance"] = self.tolerance
        if self.message:
            payload["message"] = self.message
        if self.date_format:
            payload["date_format"] = self.date_format
        return payload

    def describe(self) -> str:
        if self.type == "compare":
            return f"{self.fields[0]} {self.operator} {self.fields[1]}"
        if self.type == "sum_equals":
            total, *parts = self.fields
            return f"{total} equals the sum of {' + '.join(parts)}"
        return f"{self.fields[0]} on or before {self.fields[1]}"


@dataclass
class CrossFieldResult:
    """Outcome of running cross-field rules over a frame."""

    issues: list[Any] = dataclass_field(default_factory=list)
    rules_run: int = 0
    skipped_rules: list[str] = dataclass_field(default_factory=list)
    failures_by_rule: dict[str, int] = dataclass_field(default_factory=dict)

    @property
    def total_failures(self) -> int:
        return len(self.issues)

    def summary(self) -> dict[str, Any]:
        return {
            "rules_run": self.rules_run,
            "rule_failures": self.total_failures,
            "skipped_rules": list(self.skipped_rules),
            "failures_by_rule": dict(self.failures_by_rule),
        }


def _as_number(value: Any) -> float | None:
    if is_missing(value):
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("$", "").replace("£", "").replace("€", "")
    try:
        return float(text)
    except ValueError:
        return None


def _as_datetime(value: Any, date_format: str | None) -> pd.Timestamp | None:
    if is_missing(value):
        return None
    try:
        return pd.to_datetime(value, format=date_format, errors="coerce")
    except (ValueError, TypeError):
        return None


def _compare(left: float, right: float, operator: str) -> bool:
    if operator == "<":
        return left < right
    if operator == "<=":
        return left <= right
    if operator == "==":
        return left == right
    if operator == "!=":
        return left != right
    if operator == ">":
        return left > right
    return left >= right


def run_cross_field_rules(
    frame: pd.DataFrame, rules: Iterable[CrossFieldRule]
) -> CrossFieldResult:
    """Evaluate cross-field rules and return the row-level failures.

    A rule whose columns are missing from the frame is reported in
    ``skipped_rules`` rather than raising, so one rule set can be shared across
    configs whose mapped output differs. A row with a blank in any of the
    rule's columns is skipped: "empty" belongs to the completeness check.
    """
    from app_files.validators.quality_validator import Issue

    outcome = CrossFieldResult()
    for rule in rules:
        absent = [name for name in rule.fields if name not in frame.columns]
        if absent:
            outcome.skipped_rules.append(rule.name)
            continue
        outcome.rules_run += 1
        failures = 0
        for index, row in frame[rule.fields].iterrows():
            failed = _row_fails(rule, row)
            if failed is None:
                continue
            if failed:
                failures += 1
                outcome.issues.append(
                    Issue(
                        row=int(index),  # type: ignore[call-overload]  # index is a row label
                        field=rule.fields[0],
                        check=f"cross_field:{rule.name}",
                        severity=rule.severity,
                        message=rule.message
                        or f"{rule.describe()} was violated on this row",
                    )
                )
        if failures:
            outcome.failures_by_rule[rule.name] = failures
    return outcome


def _row_fails(rule: CrossFieldRule, row: pd.Series) -> bool | None:
    """True/False whether the row violates the rule; None when it cannot be judged."""
    if rule.type == "compare":
        left_num = _as_number(row[rule.fields[0]])
        right_num = _as_number(row[rule.fields[1]])
        if left_num is None or right_num is None:
            return None
        return not _compare(left_num, right_num, rule.operator or ">=")

    if rule.type == "sum_equals":
        total = _as_number(row[rule.fields[0]])
        parts = [_as_number(row[name]) for name in rule.fields[1:]]
        if total is None or any(part is None for part in parts):
            return None
        expected = sum(part for part in parts if part is not None)
        return abs(total - expected) > rule.tolerance

    left_date = _as_datetime(row[rule.fields[0]], rule.date_format)
    right_date = _as_datetime(row[rule.fields[1]], rule.date_format)
    if left_date is None or right_date is None or pd.isna(left_date) or pd.isna(right_date):
        return None
    return bool(left_date > right_date)


def apply_cross_field_rules(result: Any, rules: Iterable[CrossFieldRule]) -> CrossFieldResult:
    """Run cross-field rules against a pipeline result and merge the failures.

    Mirrors ``apply_rules``: failures land in the same issue list the core
    validator fills, so the QA report and quality score pick them up with no
    change to either.
    """
    outcome = run_cross_field_rules(result.clean_frame, rules)
    if outcome.issues:
        result.validation.issues.extend(outcome.issues)
    return outcome


def load_cross_field_rules(data: dict[str, Any]) -> list[CrossFieldRule]:
    """Read the ``cross_field:`` block from a config mapping."""
    if not isinstance(data, dict):
        raise CrossFieldRuleError("Config must be a mapping containing 'cross_field'")
    raw = data.get("cross_field", []) or []
    if not isinstance(raw, list):
        raise CrossFieldRuleError("'cross_field' must be a list of rules")
    return [CrossFieldRule.from_dict(item) for item in raw]


__all__ = [
    "COMPARISON_OPERATORS",
    "CROSS_FIELD_TYPES",
    "CrossFieldResult",
    "CrossFieldRule",
    "CrossFieldRuleError",
    "apply_cross_field_rules",
    "load_cross_field_rules",
    "run_cross_field_rules",
]
