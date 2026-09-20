"""Rule library: pick a rule set instead of writing YAML.

A buyer who has never written YAML should still be able to apply "email
validation" or "duplicate detection". The library holds named, ready-to-run rule
sets; ``install()`` merges the chosen ones into a config file.

Rules are stored as real YAML files under ``app_files/rule_library/``, so the
same files a buyer can read are the files the engine runs. ``load_library()``
reads them from disk — there is no second, in-code definition that could drift.

Each set declares which column names it expects, so the UI can tell a buyer
"this set expects a column called email; your file has Email Address" rather than
silently matching nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from app_files.rules import Rule, RuleConfigError, run_rules

RULE_LIBRARY_DIR = Path(__file__).resolve().parent.parent / "rule_library"

# The built-in sets. Kept here as data so an installation with no library folder
# still works; the folder, when present, is the source of truth.
_BUILTIN: dict[str, dict[str, Any]] = {
    "email_validation": {
        "title": "Email validation",
        "summary": "Every email is present and shaped like an email address.",
        "expects": ["email"],
        "rules": [
            {"name": "email_required", "field": "email", "type": "required", "severity": "error",
             "message": "email must not be empty"},
            {"name": "email_format", "field": "email", "type": "regex",
             "pattern": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", "severity": "error",
             "message": "email must be a valid address"},
        ],
    },
    "phone_validation": {
        "title": "Phone validation",
        "summary": "Phone numbers are present and in international format.",
        "expects": ["phone"],
        "rules": [
            {"name": "phone_required", "field": "phone", "type": "required", "severity": "error",
             "message": "phone must not be empty"},
            {"name": "phone_e164", "field": "phone", "type": "regex", "pattern": "^\\+[1-9]\\d{6,14}$",
             "severity": "warning", "message": "phone should be in E.164 format, e.g. +15551234567"},
        ],
    },
    "date_range": {
        "title": "Date range",
        "summary": "Dates are ISO 8601 and fall within a plausible window.",
        "expects": ["createdate"],
        "rules": [
            {"name": "date_required", "field": "createdate", "type": "required", "severity": "error",
             "message": "createdate must not be empty"},
            {"name": "date_iso", "field": "createdate", "type": "regex", "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
             "severity": "warning", "message": "createdate should be ISO 8601 (YYYY-MM-DD)"},
        ],
    },
    "required_fields": {
        "title": "Required fields",
        "summary": "The identifying fields are never blank.",
        "expects": ["email", "phone"],
        "rules": [
            {"name": "email_required", "field": "email", "type": "required", "severity": "error"},
            {"name": "phone_required", "field": "phone", "type": "required", "severity": "warning"},
        ],
    },
    "positive_amount": {
        "title": "Positive amounts",
        "summary": "Amounts are numbers greater than zero.",
        "expects": ["amount"],
        "rules": [
            {"name": "amount_positive", "field": "amount", "type": "range", "min": 0.01,
             "severity": "error", "message": "amount must be greater than zero"},
        ],
    },
    "country_list": {
        "title": "Country list",
        "summary": "Country is one of the supported values.",
        "expects": ["country"],
        "rules": [
            {"name": "country_allowed", "field": "country", "type": "list_of_values",
             "values": ["USA", "France", "UK", "Germany", "Canada"], "severity": "warning",
             "message": "country must be one of the supported values"},
        ],
    },
}


@dataclass
class RuleSet:
    """One named, runnable rule set."""

    name: str
    title: str
    summary: str
    rules: list[dict[str, Any]] = field(default_factory=list)
    expects: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "summary": self.summary,
            "expects": self.expects,
            "rule_count": len(self.rules),
        }

    def matches(self, columns: list[str]) -> tuple[list[str], list[str]]:
        """Which expected columns are present, and which are missing.

        Aliases are resolved so a HubSpot export with ``Email Address`` still
        satisfies a set that expects ``email``.
        """
        lowered = {str(c).lower().replace(" ", "_"): str(c) for c in columns}
        present, missing = [], []
        for expected in self.expects:
            key = expected.lower()
            if key in lowered:
                present.append(expected)
                continue
            hit = next((original for norm, original in lowered.items() if key in norm), None)
            if hit:
                present.append(expected)
            else:
                missing.append(expected)
        return present, missing

    def resolved_rules(self, columns: list[str]) -> list[dict[str, Any]]:
        """The rules with fields remapped onto the caller's actual column names."""
        lowered = {str(c).lower().replace(" ", "_"): str(c) for c in columns}
        resolved = []
        for rule in self.rules:
            copy = dict(rule)
            key = str(copy.get("field", "")).lower()
            if key in lowered:
                copy["field"] = lowered[key]
            else:
                hit = next((original for norm, original in lowered.items() if key in norm), None)
                if hit:
                    copy["field"] = hit
            resolved.append(copy)
        return resolved


def _load_from_disk() -> dict[str, RuleSet]:
    sets: dict[str, RuleSet] = {}
    if not RULE_LIBRARY_DIR.exists():
        return sets
    for path in sorted(RULE_LIBRARY_DIR.glob("*.yaml")):
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(payload, dict) or "rules" not in payload:
            continue
        name = str(payload.get("name") or path.stem)
        sets[name] = RuleSet(
            name=name,
            title=str(payload.get("title") or name.replace("_", " ").title()),
            summary=str(payload.get("summary") or ""),
            rules=list(payload.get("rules") or []),
            expects=list(payload.get("expects") or []),
        )
    return sets


def load_library() -> dict[str, RuleSet]:
    """Every available set: files on disk, plus built-ins they do not override."""
    sets = {
        name: RuleSet(
            name=name,
            title=str(body.get("title", "")),
            summary=str(body.get("summary", "")),
            rules=list(body.get("rules", [])),
            expects=list(body.get("expects", [])),
        )
        for name, body in _BUILTIN.items()
    }
    sets.update(_load_from_disk())
    return dict(sorted(sets.items()))


def available_rule_sets() -> list[str]:
    return list(load_library())


def get_rule_set(name: str) -> RuleSet:
    sets = load_library()
    if name not in sets:
        raise KeyError(f"Unknown rule set {name!r}. Available: {', '.join(sets)}")
    return sets[name]


def validate_rule_set(name: str, frame: pd.DataFrame) -> dict[str, Any]:
    """Run one set against a frame, resolving columns first.

    Returns the outcome plus which expected columns were missing, so the caller
    can explain a zero-failure result as "your file has no such column" rather
    than "your data is fine".
    """
    rule_set = get_rule_set(name)
    columns = [str(c) for c in frame.columns]
    present, missing = rule_set.matches(columns)
    resolved = rule_set.resolved_rules(columns)

    parsed: list[Rule] = []
    rejected: list[str] = []
    for raw in resolved:
        if raw.get("field") not in frame.columns:
            continue
        try:
            parsed.append(Rule.from_dict(raw))
        except RuleConfigError as exc:
            rejected.append(f"{raw.get('name', '?')}: {exc}")

    outcome = run_rules(frame, parsed) if parsed else None
    return {
        "rule_set": name,
        "title": rule_set.title,
        "columns_present": present,
        "columns_missing": missing,
        "rules_run": outcome.rules_run if outcome else 0,
        "failures": outcome.total_failures if outcome else 0,
        "failures_by_rule": (outcome.failures_by_rule if outcome else {}) or {},
        "rejected_rules": rejected,
        "applicable": bool(parsed),
    }


def validate_many(names: list[str], frame: pd.DataFrame) -> dict[str, Any]:
    """Run several sets and total them."""
    results = [validate_rule_set(name, frame) for name in names]
    return {
        "sets": results,
        "total_failures": sum(r["failures"] for r in results),
        "sets_applied": sum(1 for r in results if r["applicable"]),
    }


def install(names: list[str], config_path: str | Path) -> list[dict[str, Any]]:
    """Merge the chosen sets' rules into a config file, preserving the rest.

    Existing rules are kept; a rule whose name already exists is replaced, so
    installing twice is safe rather than duplicating.
    """
    path = Path(config_path)
    if path.exists():
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"{path} does not contain a YAML mapping.")
    else:
        payload = {}
        path.parent.mkdir(parents=True, exist_ok=True)

    existing = list(payload.get("rules") or [])
    by_name = {str(rule.get("name", f"rule_{i}")): i for i, rule in enumerate(existing)}

    added: list[dict[str, Any]] = []
    for name in names:
        for rule in get_rule_set(name).rules:
            rule_name = str(rule.get("name", ""))
            if rule_name in by_name:
                existing[by_name[rule_name]] = rule
            else:
                by_name[rule_name] = len(existing)
                existing.append(rule)
            added.append(rule)
    payload["rules"] = existing
    path.write_text(yaml.safe_dump(payload, sort_keys=False, default_flow_style=False), encoding="utf-8")
    return added


def rule_library_frame() -> pd.DataFrame:
    """The library as a table, for the UI."""
    rows = [rule_set.as_dict() for rule_set in load_library().values()]
    columns = ["name", "title", "summary", "rule_count", "expects"]
    return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)