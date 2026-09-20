"""Deterministic rule builder: form input in, schema-valid YAML out.

A buyer who has never written YAML picks a column, picks one of the five rule
types the engine supports, fills in the parameters the form shows them, and
the tool writes the YAML. There is no model, no API key and no network call
here — the same form input always produces the same YAML.

Two vocabularies are kept deliberately separate:

* the **engine** speaks ``required | range | length | list_of_values | regex``
  (see :mod:`app_files.rules.schema`);
* the **buyer** sees "Valid format" for ``regex``, because a bookkeeper should
  not have to know what a regular expression is.

:data:`KIND_TO_ENGINE` maps one onto the other, and :data:`COMMON_PATTERNS`
lets "Email" be a dropdown choice rather than a regex someone has to type.

Everything in this module is pure: no Streamlit, no file writes, no I/O. That
is what makes the builder testable without a browser and what keeps the frozen
rule engine untouched.
"""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field as dataclass_field
from typing import Any, Iterable

import yaml

from app_files.rules.schema import RULE_TYPES, SEVERITIES, Rule, RuleConfigError

# --------------------------------------------------------------------- vocabulary

#: What the dropdown offers, mapped to the engine's rule type. Order is the
#: order the buyer sees, which is breadth-first: the two rules most people want
#: first, then the numeric/structural ones.
KIND_TO_ENGINE: dict[str, str] = {
    "required": "required",
    "format": "regex",
    "length": "length",
    "range": "range",
    "list_of_values": "list_of_values",
}

#: Buyer-facing label for each dropdown option.
KIND_LABELS: dict[str, str] = {
    "required": "Required",
    "format": "Valid format",
    "length": "Length",
    "range": "Range",
    "list_of_values": "List of values",
}

CUSTOM_PATTERN = "Custom pattern"

#: Named regexes so nobody has to type one. Values are the exact patterns
#: written to YAML; a test asserts each one compiles.
COMMON_PATTERNS: dict[str, str] = {
    "Email": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    "Phone (US)": r"^\+1\d{10}$",
    "Phone (international)": r"^\+[1-9]\d{6,14}$",
    "URL": r"^https?://",
    "Date (ISO)": r"^\d{4}-\d{2}-\d{2}$",
    CUSTOM_PATTERN: "",
}


class DraftError(ValueError):
    """Raised when a half-filled form cannot become a valid rule."""


# --------------------------------------------------------------------- the draft


@dataclass
class RuleDraft:
    """One rule as the form holds it, before it becomes YAML.

    This is a superset of :class:`~app_files.rules.schema.Rule` because the form
    needs to remember *which dropdown option* was chosen (``Email``) rather than
    only the pattern it resolved to, so that reopening a rule for editing
    re-selects the same option instead of dropping into "Custom pattern".
    """

    field: str
    kind: str
    severity: str = "error"
    name: str = ""
    message: str = ""

    # format
    format_name: str = "Email"
    pattern: str = ""

    # length
    exactly: int | None = None
    min_length: int | None = None
    max_length: int | None = None

    # range
    min_value: float | None = None
    max_value: float | None = None

    # list_of_values
    values: list[str] = dataclass_field(default_factory=list)

    def __post_init__(self) -> None:
        if self.kind not in KIND_TO_ENGINE:
            raise DraftError(
                f"Unknown rule kind {self.kind!r}. Known: {', '.join(KIND_TO_ENGINE)}"
            )

    # ---------------------------------------------------------------- resolution

    def resolved_pattern(self) -> str:
        """The regex this rule will actually run, honouring the dropdown choice."""
        if self.format_name == CUSTOM_PATTERN:
            return self.pattern
        return COMMON_PATTERNS.get(self.format_name, "")

    def engine_type(self) -> str:
        return KIND_TO_ENGINE[self.kind]

    def rule_name(self) -> str:
        """A stable, readable name, used in the YAML and the issues list."""
        if self.name:
            return self.name
        prefix = {
            "required": "required",
            "format": "format",
            "length": "length",
            "range": "range",
            "list_of_values": "allowed",
        }[self.kind]
        return f"{prefix}_{_slug(self.field)}"

    # ---------------------------------------------------------------- validation

    def validate(self) -> None:
        """Reject an incomplete rule *before* it reaches the rule list.

        The engine would reject these too, but only at load time — after the
        buyer has clicked Add and moved on. Failing here is what lets the form
        show "enter a minimum or a maximum" next to the input.
        """
        if not str(self.field).strip():
            raise DraftError("Choose a field first.")
        if self.severity not in SEVERITIES:
            raise DraftError(
                f"Unknown severity {self.severity!r}. Known: {', '.join(SEVERITIES)}"
            )
        if self.kind == "format":
            pattern = self.resolved_pattern()
            if not pattern.strip():
                raise DraftError("Enter a pattern, or pick one of the named formats.")
            if self.format_name == CUSTOM_PATTERN:
                _compile_pattern(pattern)
        if self.kind == "length":
            if all(v is None for v in (self.exactly, self.min_length, self.max_length)):
                raise DraftError(
                    "A length rule needs 'exactly', or a minimum and/or maximum."
                )
            if self.exactly is None and _both_set(self.min_length, self.max_length):
                if self.min_length > self.max_length:  # type: ignore[operator]
                    raise DraftError("Minimum length cannot be greater than maximum.")
        if self.kind == "range":
            if self.min_value is None and self.max_value is None:
                raise DraftError("A range rule needs a minimum and/or a maximum.")
            if _both_set(self.min_value, self.max_value):
                if self.min_value > self.max_value:  # type: ignore[operator]
                    raise DraftError("Minimum cannot be greater than maximum.")
        if self.kind == "list_of_values" and not self.values:
            raise DraftError("Enter at least one allowed value.")

    # ---------------------------------------------------------------- output

    def to_dict(self) -> dict[str, Any]:
        """The schema-shaped mapping, exactly as it will appear under ``rules:``."""
        self.validate()
        payload: dict[str, Any] = {
            "name": self.rule_name(),
            "field": self.field,
            "type": self.engine_type(),
            "severity": self.severity,
        }
        if self.kind == "format":
            payload["pattern"] = self.resolved_pattern()
        elif self.kind == "length":
            if self.exactly is not None:
                payload["exactly"] = self.exactly
            if self.min_length is not None:
                payload["min_length"] = self.min_length
            if self.max_length is not None:
                payload["max_length"] = self.max_length
        elif self.kind == "range":
            if self.min_value is not None:
                payload["min"] = self.min_value
            if self.max_value is not None:
                payload["max"] = self.max_value
        elif self.kind == "list_of_values":
            payload["values"] = coerce_values(self.values)
        if self.message:
            payload["message"] = self.message
        return payload

    def to_rule(self) -> Rule:
        """Build the engine's :class:`Rule` — the same validation path as YAML."""
        return Rule.from_dict(self.to_dict())

    def describe(self) -> str:
        """One line the buyer reads in the rule list."""
        if self.kind == "required":
            return f"{self.field} must not be empty"
        if self.kind == "format":
            label = self.format_name if self.format_name != CUSTOM_PATTERN else "pattern"
            return f"{self.field} must be a valid {label.lower()}"
        if self.kind == "length":
            if self.exactly is not None:
                return f"{self.field} must be exactly {self.exactly} characters"
            parts = []
            if self.min_length is not None:
                parts.append(f"at least {self.min_length}")
            if self.max_length is not None:
                parts.append(f"at most {self.max_length}")
            return f"{self.field} must be {', '.join(parts)} characters"
        if self.kind == "range":
            if self.min_value is not None and self.max_value is not None:
                return f"{self.field} must be between {self.min_value} and {self.max_value}"
            if self.min_value is not None:
                return f"{self.field} must be at least {self.min_value}"
            return f"{self.field} must be at most {self.max_value}"
        count = len(self.values)
        noun = "value" if count == 1 else "values"
        return f"{self.field} must be one of {count} {noun}"


# --------------------------------------------------------------------- helpers


def _both_set(left: Any, right: Any) -> bool:
    return left is not None and right is not None


def _slug(text: str) -> str:
    """A field name as a YAML-friendly identifier: ``Email Address`` -> ``email_address``."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", str(text)).strip("_").lower()
    return cleaned or "field"


def _compile_pattern(pattern: str) -> None:
    try:
        re.compile(pattern)
    except re.error as exc:
        raise DraftError(f"That pattern is not a valid regular expression: {exc}") from None


def coerce_values(raw: Iterable[str]) -> list[Any]:
    """Turn textarea lines into ints/floats where that is unambiguous.

    Keeps ``1, 2, 3`` as numbers so a numeric column compares numerically, but
    leaves ``USA`` and ``007`` alone — a leading zero means a code, not a number.
    """
    values: list[Any] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item).strip()
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        if re.fullmatch(r"-?\d+", text) and not (text.startswith("0") and len(text) > 1):
            values.append(int(text))
        elif re.fullmatch(r"-?\d*\.\d+", text):
            values.append(float(text))
        else:
            values.append(text)
    return values


def unique_name(base: str, taken: Iterable[str]) -> str:
    """``format_email``, then ``format_email_2``, then ``format_email_3``."""
    existing = set(taken)
    if base not in existing:
        return base
    suffix = 2
    while f"{base}_{suffix}" in existing:
        suffix += 1
    return f"{base}_{suffix}"


# --------------------------------------------------------------------- the list


@dataclass
class RuleList:
    """The ordered set of rules the buyer has built in this session."""

    drafts: list[RuleDraft] = dataclass_field(default_factory=list)

    def __len__(self) -> int:
        return len(self.drafts)

    def __iter__(self):
        return iter(self.drafts)

    def names(self) -> list[str]:
        return [draft.rule_name() for draft in self.drafts]

    def add(self, draft: RuleDraft) -> RuleDraft:
        """Validate, de-duplicate the name, and store a copy.

        The copy matters: loading a library set twice passes the same draft
        objects in twice, and storing them by reference would put one object in
        two slots — editing either would silently change both. Returns the stored
        copy, which is what the UI reports back to the buyer.
        """
        draft.validate()
        stored = dataclasses.replace(draft, name=unique_name(draft.rule_name(), self.names()))
        self.drafts.append(stored)
        return stored

    def replace(self, index: int, draft: RuleDraft) -> RuleDraft:
        """Swap the rule at ``index`` for an edited copy of it.

        The rule being edited is excluded from the name check, so keeping its own
        name is not treated as a collision.
        """
        if not 0 <= index < len(self.drafts):
            raise DraftError(f"No rule at position {index}.")
        draft.validate()
        others = [d.name for i, d in enumerate(self.drafts) if i != index]
        stored = dataclasses.replace(draft, name=unique_name(draft.rule_name(), others))
        self.drafts[index] = stored
        return stored

    def remove(self, index: int) -> RuleDraft:
        if not 0 <= index < len(self.drafts):
            raise DraftError(f"No rule at position {index}.")
        return self.drafts.pop(index)

    def clear(self) -> None:
        self.drafts.clear()

    def extend(self, drafts: Iterable[RuleDraft]) -> list[RuleDraft]:
        return [self.add(draft) for draft in drafts]

    def rows(self) -> list[dict[str, Any]]:
        """What the rule list table renders, one row per rule."""
        return [
            {
                "index": index,
                "severity": draft.severity,
                "summary": draft.describe(),
                "name": draft.rule_name(),
                "field": draft.field,
            }
            for index, draft in enumerate(self.drafts)
        ]

    def to_dicts(self) -> list[dict[str, Any]]:
        return [draft.to_dict() for draft in self.drafts]

    def to_rules(self) -> list[Rule]:
        """The engine objects, validated through the same path as YAML."""
        return [draft.to_rule() for draft in self.drafts]

    def to_yaml(self) -> str:
        """Serialize to the schema's expected shape, ready to write to disk."""
        return rules_to_yaml(self.to_dicts())


def rules_to_yaml(dicts: list[dict[str, Any]]) -> str:
    """Render ``rules:`` in the same style the configs and library use."""
    if not dicts:
        return "rules: []\n"
    return yaml.safe_dump(
        {"rules": dicts},
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def parse_rules_yaml(text: str) -> list[Rule]:
    """Read a builder-written YAML document back through the schema.

    Raises :class:`~app_files.rules.schema.RuleConfigError` when the document
    does not satisfy the engine, which is how the UI tells the buyer that
    hand-edited YAML is wrong before a run rather than mid-run.
    """
    try:
        payload = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise RuleConfigError(f"That is not valid YAML: {exc}") from None
    if not isinstance(payload, dict):
        raise RuleConfigError("Expected a YAML mapping with a 'rules' list.")
    raw = payload.get("rules") or []
    if not isinstance(raw, list):
        raise RuleConfigError("'rules' must be a list.")
    return [Rule.from_dict(item) for item in raw]


# --------------------------------------------------------------------- library glue


def _normalise(text: str) -> str:
    """Compare column names the way a person would: ignore case, spaces, underscores.

    Makes a library rule's ``createdate`` find a file's ``Created Date``, and
    ``email`` find ``Email Address``.
    """
    return re.sub(r"[\s_]+", "", str(text)).lower()


def drafts_from_library(raw_rules: list[dict[str, Any]], columns: Iterable[str]) -> list[RuleDraft]:
    """Turn a rule library set's rules into editable drafts.

    Library rules name fields in their own vocabulary (``email``) while the
    buyer's file may call that column ``Email Address``, so each field is
    re-pointed at a real column when an obvious match exists. A rule whose field
    is nowhere in the file is still returned — the engine skips unknown columns,
    and the form shows the buyer what it will do rather than silently dropping it.
    """
    columns = [str(c) for c in columns]
    exact = {_normalise(c): c for c in columns}
    drafts: list[RuleDraft] = []
    for raw in raw_rules:
        if not isinstance(raw, dict):
            continue
        engine_type = str(raw.get("type", "")).strip().lower()
        if engine_type not in RULE_TYPES:
            continue
        field_name = str(raw.get("field", ""))
        key = _normalise(field_name)
        resolved_field = exact.get(key) or next(
            (original for norm, original in exact.items() if key and (key in norm or norm in key)),
            field_name,
        )
        draft = _draft_from_engine(raw, resolved_field)
        if draft is not None:
            drafts.append(draft)
    return drafts


def _draft_from_engine(raw: dict[str, Any], field_name: str) -> RuleDraft | None:
    """Map one engine rule back onto the form, re-selecting the right dropdowns."""
    engine_type = str(raw.get("type", "")).strip().lower()
    common = {
        "field": field_name,
        "severity": str(raw.get("severity", "error")).strip().lower(),
        "name": str(raw.get("name", "")),
        "message": str(raw.get("message", "")),
    }
    if engine_type == "required":
        return RuleDraft(kind="required", **common)
    if engine_type == "regex":
        pattern = str(raw.get("pattern", ""))
        match = next((n for n, p in COMMON_PATTERNS.items() if p and p == pattern), None)
        return RuleDraft(
            kind="format",
            format_name=match or CUSTOM_PATTERN,
            pattern=pattern,
            **common,
        )
    if engine_type == "length":
        return RuleDraft(
            kind="length",
            exactly=_as_int(raw.get("exactly")),
            min_length=_as_int(raw.get("min_length")),
            max_length=_as_int(raw.get("max_length")),
            **common,
        )
    if engine_type == "range":
        return RuleDraft(
            kind="range",
            min_value=_as_float(raw.get("min")),
            max_value=_as_float(raw.get("max")),
            **common,
        )
    if engine_type == "list_of_values":
        return RuleDraft(
            kind="list_of_values",
            values=[str(v) for v in (raw.get("values") or [])],
            **common,
        )
    return None


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
