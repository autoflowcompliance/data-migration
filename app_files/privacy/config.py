"""Configuration for the privacy layer: what to detect, and how to mask it.

Configuration driven, like the rest of the pipeline: no column names or
patterns are hardcoded. A config can be declared inline or loaded from YAML::

    privacy:
      default_strategy: redact
      detect:
        passport: false
      fields:
        - column: email
          kinds: [email]
          strategy: hash
        - column: notes
          kinds: [custom:employee_id]
          strategy: redact
      custom_patterns:
        employee_id:
          pattern: 'EMP-\\d{6}'
          label: Employee ID
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

STRATEGIES = ("redact", "hash", "tokenize", "partial")

#: Detectors that ship enabled. ``passport`` is off by default because the
#: generic pattern has no checksum and will match ordinary identifiers; switch
#: it on once the column or the pattern is known.
DEFAULT_DETECTORS: dict[str, bool] = {
    "email": True,
    "phone": True,
    "credit_card": True,
    "national_id": True,
    "iban": True,
    "passport": False,
}


class PrivacyConfigError(ValueError):
    """Raised when a privacy config is malformed."""


@dataclass
class CustomPattern:
    name: str
    pattern: str
    label: str = ""

    @property
    def kind(self) -> str:
        return f"custom:{self.name}"

    @classmethod
    def from_dict(cls, name: str, data: Any) -> CustomPattern:
        pattern: Any
        label: Any
        if isinstance(data, str):
            pattern, label = data, ""
        elif isinstance(data, dict):
            pattern = data.get("pattern")
            label = data.get("label", "")
        else:
            raise PrivacyConfigError(
                f"Custom pattern {name!r} must be a string or a mapping, got {type(data).__name__}"
            )
        if not pattern:
            raise PrivacyConfigError(f"Custom pattern {name!r} has no 'pattern'")
        try:
            re.compile(pattern)
        except re.error as exc:
            raise PrivacyConfigError(
                f"Custom pattern {name!r} is not a valid regex: {exc}"
            ) from None
        return cls(name=name, pattern=pattern, label=label or name)


@dataclass
class FieldRule:
    """How one column is masked. ``kinds`` empty means every detected kind."""

    column: str
    strategy: str | None = None
    kinds: list[str] = field(default_factory=list)
    salt: str | None = None

    _KNOWN = frozenset({"column", "strategy", "kinds", "salt"})

    @classmethod
    def from_dict(cls, data: Any) -> FieldRule:
        if not isinstance(data, dict):
            raise PrivacyConfigError(
                f"Each field rule must be a mapping, got {type(data).__name__}"
            )
        unknown = set(data) - cls._KNOWN
        if unknown:
            raise PrivacyConfigError(
                f"Field rule has unknown keys: {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(cls._KNOWN))}"
            )
        column = data.get("column")
        if not column:
            raise PrivacyConfigError("Each field rule needs a 'column'")
        strategy = data.get("strategy")
        if strategy is not None:
            _check_strategy(strategy)
        kinds = data.get("kinds", [])
        if isinstance(kinds, str):
            kinds = [kinds]
        if not all(isinstance(k, str) for k in kinds):
            raise PrivacyConfigError(f"Field rule for {column!r} has non-string 'kinds'")
        return cls(column=str(column), strategy=strategy, kinds=list(kinds), salt=data.get("salt"))


def _check_strategy(strategy: Any) -> str:
    normalised = str(strategy).strip().lower()
    if normalised not in STRATEGIES:
        raise PrivacyConfigError(
            f"Unknown masking strategy {strategy!r}. Available: {', '.join(STRATEGIES)}"
        )
    return normalised


@dataclass
class PrivacyConfig:
    enabled: bool = False
    default_strategy: str = "redact"
    detectors: dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_DETECTORS))
    fields: list[FieldRule] = field(default_factory=list)
    custom_patterns: list[CustomPattern] = field(default_factory=list)
    hash_salt: str | None = None
    token_key: str | None = None
    """Reversible-token key. Falls back to ``token_key_env`` then the
    ``DATAREADY_PII_KEY`` environment variable."""
    token_key_env: str = "DATAREADY_PII_KEY"
    region: str = "US"
    vault_path: str | None = None
    """Where tokenized originals are written, if anywhere. Never implied."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PrivacyConfig:
        if not isinstance(data, dict):
            raise PrivacyConfigError(f"Privacy config must be a mapping, got {type(data).__name__}")
        block = data.get("privacy", data)
        if not isinstance(block, dict):
            raise PrivacyConfigError(f"'privacy' must be a mapping, got {type(block).__name__}")

        known = {
            "enabled", "default_strategy", "detect", "fields", "custom_patterns",
            "hash_salt", "token_key", "token_key_env", "region", "vault_path",
        }
        unknown = set(block) - known
        if unknown:
            raise PrivacyConfigError(
                f"Privacy config has unknown keys: {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(known))}"
            )

        detectors = dict(DEFAULT_DETECTORS)
        raw_detect = block.get("detect", {})
        if raw_detect is not None:
            if not isinstance(raw_detect, dict):
                raise PrivacyConfigError("'detect' must be a mapping of detector name to bool")
            for name, value in raw_detect.items():
                detectors[str(name)] = bool(value)

        custom: list[CustomPattern] = []
        raw_custom = block.get("custom_patterns", {}) or {}
        if not isinstance(raw_custom, dict):
            raise PrivacyConfigError("'custom_patterns' must be a mapping of name to pattern")
        for name, spec in raw_custom.items():
            custom.append(CustomPattern.from_dict(str(name), spec))

        raw_fields = block.get("fields", []) or []
        if not isinstance(raw_fields, list):
            raise PrivacyConfigError("'fields' must be a list of field rules")
        fields = [FieldRule.from_dict(item) for item in raw_fields]

        strategy = block.get("default_strategy", "redact")
        return cls(
            enabled=bool(block.get("enabled", True)),
            default_strategy=_check_strategy(strategy),
            detectors=detectors,
            fields=fields,
            custom_patterns=custom,
            hash_salt=block.get("hash_salt"),
            token_key=block.get("token_key"),
            token_key_env=str(block.get("token_key_env", "DATAREADY_PII_KEY")),
            region=str(block.get("region", "US")),
            vault_path=block.get("vault_path"),
        )

    def resolve_token_key(self) -> str | None:
        if self.token_key:
            return self.token_key
        return os.environ.get(self.token_key_env) or None

    def rule_for(self, column: str) -> FieldRule | None:
        for rule in self.fields:
            if rule.column == column:
                return rule
        return None

    def strategy_for(self, column: str, kind: str) -> str:
        rule = self.rule_for(column)
        if rule is None:
            return self.default_strategy
        if rule.kinds and kind not in rule.kinds:
            return "none"
        return rule.strategy or self.default_strategy

    def salt_for(self, column: str) -> str | None:
        rule = self.rule_for(column)
        if rule is not None and rule.salt is not None:
            return rule.salt
        return self.hash_salt

    def enabled_kinds(self) -> list[str]:
        kinds = [name for name, on in self.detectors.items() if on]
        kinds.extend(pattern.kind for pattern in self.custom_patterns)
        return kinds


def load_privacy_config(path: str | Path | None) -> PrivacyConfig:
    if path is None:
        return PrivacyConfig()
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if "privacy" not in data:
        return PrivacyConfig()
    return PrivacyConfig.from_dict(data)
