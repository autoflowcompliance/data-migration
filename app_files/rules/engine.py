"""Run configured rules against a mapped DataFrame.

The engine appends failures to the same ``Issue`` list the built-in quality
validator uses, so custom rules flow straight into the existing issues CSV and
QA report without any change to the core validator.

Missing-value handling: a blank value fails only a ``required`` rule. Range,
length, list-of-values and regex rules skip blanks, because "empty" is already
reported by the core validator's completeness check — reporting it again here
would double-count the same problem.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.rules.schema import Rule, RuleConfigError, load_rules
from app_files.rules.validators import get_validator
from app_files.transforms import is_missing


@dataclass
class RuleResult:
    """Outcome of running a rule set over a frame."""

    issues: list[Any]
    """``Issue`` objects (same type the core validator produces)."""
    rules_run: int = 0
    failures_by_rule: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.failures_by_rule is None:
            self.failures_by_rule = {}

    @property
    def total_failures(self) -> int:
        return len(self.issues)

    def summary(self) -> dict[str, Any]:
        return {
            "rules_run": self.rules_run,
            "rule_failures": self.total_failures,
            "failures_by_rule": dict(self.failures_by_rule or {}),
        }


def run_rules(frame: pd.DataFrame, rules: list[Rule]) -> RuleResult:
    """Validate ``frame`` against ``rules`` and return the failures.

    Rules referencing a column that isn't in the frame are skipped rather than
    raising, so a rule set can be shared across configs whose mapped output
    differs slightly.
    """
    from app_files.validators.quality_validator import Issue

    issues: list[Any] = []
    failures: dict[str, int] = {}
    executed = 0

    for rule in rules:
        if rule.field not in frame.columns:
            continue
        executed += 1
        validator = get_validator(rule.type)
        failures[rule.name] = 0
        for index, value in frame[rule.field].items():
            missing = is_missing(value)
            if missing and rule.type != "required":
                continue
            if validator(value, rule):
                continue
            failures[rule.name] += 1
            if rule.message:
                message = rule.message
            elif rule.type == "required":
                message = f"Required field '{rule.field}' is empty"
            else:
                message = f"Value {str(value).strip()!r} is not {rule.describe()}"
            issues.append(
                Issue(
                    row=int(index),
                    field=rule.field,
                    check=f"rule:{rule.name}",
                    severity=rule.severity,
                    message=message,
                )
            )

    return RuleResult(
        issues=issues,
        rules_run=executed,
        failures_by_rule={name: count for name, count in failures.items() if count},
    )


def run_rules_from_config(frame: pd.DataFrame, config: Any) -> RuleResult:
    """Load rules from any config YAML mapping and run them.

    Accepts a mapping (an already-parsed YAML dict) or an object with a
    ``raw``/``data`` attribute holding one.
    """
    if config is None:
        return RuleResult(issues=[], rules_run=0)
    data: dict[str, Any]
    if isinstance(config, dict):
        data = config
    else:
        data = getattr(config, "raw", None) or getattr(config, "data", None) or {}
    if not isinstance(data, dict):
        raise RuleConfigError("Config must be a mapping containing a 'rules' list")
    return run_rules(frame, load_rules(data))


def load_rules_for(crm_or_path: str | Path) -> list[Rule]:
    """Load just the ``rules:`` block from a config, by CRM name or path.

    Resolves the config the same way ``load_mapping_config`` does, so a caller
    can pass ``"hubspot"`` and get that config's rules without needing the raw
    YAML itself. Returns an empty list when the config declares no rules.
    """
    import yaml

    from app_files.mappers.schema import CONFIG_DIR

    path = Path(crm_or_path)
    if not path.exists():
        path = CONFIG_DIR / f"{str(crm_or_path).strip().lower()}.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return load_rules(data)


def run_rules_for(frame: pd.DataFrame, crm_or_path: str | Path) -> RuleResult:
    """Convenience: load a CRM's rules and run them against a frame."""
    return run_rules(frame, load_rules_for(crm_or_path))