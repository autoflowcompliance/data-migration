"""Validate every shipped config's rules against rules_schema.json.

The JSON schema is what editors use for autocomplete; the loader enforces the
same constraints at runtime. Keeping both in agreement is what stops a config
that an editor accepts from failing at runtime, or vice versa.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

CONFIG_DIR = Path(__file__).resolve().parents[2] / "app_files" / "configs"
SCHEMA_PATH = CONFIG_DIR / "schema" / "rules_schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture(scope="module")
def config_paths() -> list[Path]:
    return sorted(path for path in CONFIG_DIR.glob("*.yaml"))


def test_schema_file_is_valid_json_schema(schema: dict):
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft7Validator.check_schema(schema)


def test_every_config_rule_validates_against_the_schema(config_paths: list[Path], schema: dict):
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft7Validator(schema)

    checked = 0
    for path in config_paths:
        data = yaml.safe_load(path.read_text()) or {}
        rules = data.get("rules") or []
        if not rules:
            continue
        # The schema describes the whole `rules:` list, so validate it as one
        # document rather than rule by rule.
        errors = sorted(validator.iter_errors(rules), key=lambda e: list(e.path))
        assert not errors, (
            f"{path.name}: invalid rules block: "
            + "; ".join(error.message for error in errors)
        )
        checked += len(rules)
    assert checked > 0, "no rules were checked"


def test_the_schema_rejects_a_rule_missing_its_type_parameter(schema: dict):
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft7Validator(schema)
    # A range rule with neither min nor max is not valid.
    assert list(validator.iter_errors([{"field": "amount", "type": "range"}]))
    # A regex rule with no pattern is not valid.
    assert list(validator.iter_errors([{"field": "x", "type": "regex"}]))
    # An unknown key is not valid.
    assert list(validator.iter_errors([{"field": "x", "type": "required", "bogus": 1}]))


def test_the_schema_accepts_the_documented_examples(schema: dict):
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft7Validator(schema)
    examples = [
        {"name": "amount_positive", "field": "amount", "type": "range", "min": 0, "severity": "error"},
        {"name": "phone_length", "field": "phone", "type": "length", "exactly": 10, "severity": "warning"},
        {"name": "status_valid", "field": "status", "type": "list_of_values",
         "values": ["lead", "customer", "other"], "severity": "error"},
        {"name": "phone_re", "field": "phone", "type": "regex", "pattern": r"^\+[1-9]\d{6,14}$"},
        {"name": "req", "field": "email", "type": "required"},
    ]
    for example in examples:
        errors = list(validator.iter_errors([example]))
        assert not errors, f"{example['name']}: {[e.message for e in errors]}"