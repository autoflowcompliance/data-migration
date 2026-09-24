"""One validator function per rule type.

Each function takes a value and a :class:`~app_files.rules.schema.Rule` and
returns ``True`` when the value satisfies the rule. Missing values are handled
by the engine (see ``engine.py``) rather than here, so ``required`` is the only
validator that has to reason about emptiness.

Range comparison is deliberately tolerant of accounting-formatted numbers:
``"$1,500.00"`` and ``"(250.00)"`` are parsed before comparison, so a range
rule works on bank/ledger data that has not been cleaned yet.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from typing import Any

from app_files.rules.schema import Rule


def _to_number(value: Any) -> float | None:
    """Parse a possibly-formatted numeric value, or None if it isn't one."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    upper = text.upper()
    if upper.endswith("DR"):
        negative = True
        text = text[:-2]
    elif upper.endswith("CR"):
        text = text[:-2]
    text = re.sub(r"[^0-9.\-]", "", text)
    if not text or text in {"-", ".", "-."}:
        return None
    try:
        number = float(Decimal(text))
    except (InvalidOperation, ValueError):
        return None
    return -abs(number) if negative else number


def check_required(value: Any, rule: Rule) -> bool:
    """Pass when the value is present and not blank."""
    if value is None:
        return False
    if isinstance(value, float) and value != value:  # NaN
        return False
    return str(value).strip() != ""


def check_range(value: Any, rule: Rule) -> bool:
    """Pass when the numeric value falls within [min, max] (inclusive)."""
    number = _to_number(value)
    if number is None:
        return False
    if rule.min is not None and number < rule.min:
        return False
    if rule.max is not None and number > rule.max:
        return False
    return True


def check_length(value: Any, rule: Rule) -> bool:
    """Pass when the string length matches exactly/min/max."""
    length = len(str(value).strip())
    if rule.exactly is not None:
        return length == rule.exactly
    if rule.min_length is not None and length < rule.min_length:
        return False
    if rule.max_length is not None and length > rule.max_length:
        return False
    return True


def check_list_of_values(value: Any, rule: Rule) -> bool:
    """Pass when the value is one of the allowed values."""
    text = str(value).strip()
    if rule.case_sensitive:
        return text in {str(v) for v in rule.values}
    folded = text.casefold()
    return folded in {str(v).strip().casefold() for v in rule.values}


def check_regex(value: Any, rule: Rule) -> bool:
    """Pass when the value matches the rule's regular expression."""
    try:
        return re.search(rule.pattern, str(value)) is not None
    except re.error as exc:
        raise ValueError(f"Rule {rule.name!r} has an invalid regex: {exc}") from exc


VALIDATORS = {
    "required": check_required,
    "range": check_range,
    "length": check_length,
    "list_of_values": check_list_of_values,
    "regex": check_regex,
}


def get_validator(rule_type: str):
    try:
        return VALIDATORS[rule_type]
    except KeyError:
        raise ValueError(
            f"No validator for rule type {rule_type!r}. Known: {', '.join(VALIDATORS)}"
        ) from None


_OPTIONS: dict[str, frozenset[str]] = {}


def registered_options() -> frozenset[str]:
    """Every extra YAML key any registered validator declared it understands."""
    merged: frozenset[str] = frozenset()
    for keys in _OPTIONS.values():
        merged |= keys
    return merged


def register_validator(
    rule_type: str,
    validator: Callable[[Any, Rule], bool],
    options: Iterable[str] | None = None,
    override: bool = False,
) -> Callable[[Any, Rule], bool]:
    """Add a rule type. The plugin system's registration point.

    ``options`` names the extra YAML keys this rule type carries. They land in
    :attr:`~app_files.rules.schema.Rule.options`, so a custom rule can be
    parameterised without a schema change. Declaring them also keeps the
    schema's unknown-key guard working: a key nobody declared is still a typo.
    """
    key = str(rule_type).strip()
    if not key:
        raise ValueError("A rule type needs a name")
    if not callable(validator):
        raise ValueError(
            f"Validator for {rule_type!r} must be callable, got {type(validator).__name__}"
        )
    if key in VALIDATORS and not override:
        raise ValueError(
            f"Rule type {rule_type!r} already exists. Pass override=True to replace it."
        )
    VALIDATORS[key] = validator
    _OPTIONS[key] = frozenset(str(name) for name in (options or ()))
    return validator


def registered_rule_types() -> list[str]:
    return sorted(VALIDATORS)