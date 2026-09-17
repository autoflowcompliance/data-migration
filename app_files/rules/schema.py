"""Rule definition schema.

A rule is declared in any config YAML under a top-level ``rules:`` list::

    rules:
      - name: amount_positive
        field: amount
        type: range
        min: 0
        severity: error

Every rule carries a ``field``, a ``severity`` (error/warning/info) and
type-specific parameters. ``Rule.from_dict`` validates the type-specific
parameters up front so a malformed rule fails loudly at config load rather
than silently passing every row.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any

SEVERITIES = ("error", "warning", "info")
RULE_TYPES = ("required", "range", "length", "list_of_values", "regex")


class RuleConfigError(ValueError):
    """Raised when a rule is missing required parameters or is malformed."""


@dataclass
class Rule:
    """One validation rule.

    Only the parameters relevant to ``type`` are meaningful; the rest stay at
    their defaults. ``from_dict`` rejects unknown keys so typos are caught.
    """

    name: str
    field: str
    type: str
    severity: str = "error"
    # range
    min: float | None = None
    max: float | None = None
    # length
    exactly: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    # list_of_values
    values: list[Any] = dataclass_field(default_factory=list)
    case_sensitive: bool = False
    # regex
    pattern: str = ""
    message: str = ""
    """Optional human-readable override for the failure message."""

    _KNOWN = frozenset(
        {
            "name", "field", "type", "severity", "min", "max", "exactly",
            "min_length", "max_length", "values", "case_sensitive", "pattern",
            "message",
        }
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Rule:
        if not isinstance(data, dict):
            raise RuleConfigError(f"Each rule must be a mapping, got {type(data).__name__}")
        unknown = set(data) - cls._KNOWN
        if unknown:
            raise RuleConfigError(
                f"Rule has unknown keys: {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(cls._KNOWN))}"
            )
        if "type" not in data:
            raise RuleConfigError(f"Rule {data.get('name', data.get('field', '?'))!r} has no 'type'")
        rule_type = str(data["type"]).strip().lower()
        if rule_type not in RULE_TYPES:
            raise RuleConfigError(
                f"Unknown rule type {rule_type!r}. Known types: {', '.join(RULE_TYPES)}"
            )
        severity = str(data.get("severity", "error")).strip().lower()
        if severity not in SEVERITIES:
            raise RuleConfigError(
                f"Unknown severity {severity!r}. Known: {', '.join(SEVERITIES)}"
            )
        if "field" not in data:
            raise RuleConfigError("Every rule needs a 'field'")

        rule = cls(
            name=str(data.get("name") or f"{rule_type}_{data['field']}"),
            field=str(data["field"]),
            type=rule_type,
            severity=severity,
            min=_opt_float(data.get("min")),
            max=_opt_float(data.get("max")),
            exactly=_opt_int(data.get("exactly")),
            min_length=_opt_int(data.get("min_length")),
            max_length=_opt_int(data.get("max_length")),
            values=list(data.get("values") or []),
            case_sensitive=bool(data.get("case_sensitive", False)),
            pattern=str(data.get("pattern") or ""),
            message=str(data.get("message") or ""),
        )
        rule.validate_params()
        return rule

    def validate_params(self) -> None:
        """Verify the parameters required by this rule type are present."""
        if self.type == "range" and self.min is None and self.max is None:
            raise RuleConfigError(
                f"Rule {self.name!r} (range) needs at least one of 'min'/'max'"
            )
        if self.type == "length" and all(
            value is None for value in (self.exactly, self.min_length, self.max_length)
        ):
            raise RuleConfigError(
                f"Rule {self.name!r} (length) needs 'exactly', or 'min_length'/'max_length'"
            )
        if self.type == "list_of_values" and not self.values:
            raise RuleConfigError(
                f"Rule {self.name!r} (list_of_values) needs a non-empty 'values' list"
            )
        if self.type == "regex" and not self.pattern:
            raise RuleConfigError(f"Rule {self.name!r} (regex) needs a 'pattern'")

    def describe(self) -> str:
        """Human-readable summary used in failure messages."""
        if self.type == "range":
            parts = []
            if self.min is not None:
                parts.append(f"min {self.min}")
            if self.max is not None:
                parts.append(f"max {self.max}")
            return f"between {', '.join(parts)}"
        if self.type == "length":
            if self.exactly is not None:
                return f"exactly {self.exactly} characters"
            parts = []
            if self.min_length is not None:
                parts.append(f"at least {self.min_length}")
            if self.max_length is not None:
                parts.append(f"at most {self.max_length}")
            return f"{', '.join(parts)} characters"
        if self.type == "list_of_values":
            return f"one of {self.values}"
        if self.type == "regex":
            return f"matching /{self.pattern}/"
        if self.type == "required":
            return "present (not empty)"
        return self.type


def _opt_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise RuleConfigError(f"Expected a number, got {value!r}") from None


def _opt_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise RuleConfigError(f"Expected an integer, got {value!r}") from None


def load_rules(data: dict[str, Any] | None) -> list[Rule]:
    """Build rules from a config mapping, tolerating a missing/blank ``rules`` key.

    Configs that predate the rule engine simply have no ``rules`` key and get
    an empty list, so adding this layer cannot break an existing config.
    """
    if not data:
        return []
    raw = data.get("rules") or []
    if not isinstance(raw, list):
        raise RuleConfigError("'rules' must be a list of rule mappings")
    return [Rule.from_dict(item) for item in raw]