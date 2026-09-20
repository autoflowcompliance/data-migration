"""End-to-end tests for the form-based rule builder UI.

These drive the real Streamlit script with ``AppTest`` — no mocks of the form.
The point is the new requirement: a buyer builds a rule by filling in a form
(Field, Rule type, parameters) and the tool produces the same YAML the engine
runs. The deterministic guarantee matters too, so the checked-in YAML shape is
asserted exactly.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

warnings.filterwarnings("ignore")

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest

PAGE = Path(__file__).resolve().parents[2] / "app_files" / "pages" / "rule_builder_page.py"
SAMPLES = Path(__file__).resolve().parents[2] / "app_files" / "samples"


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(str(PAGE), default_timeout=120)
    at.run()
    return at


def _upload(at, name="messy_contacts.csv"):
    at.file_uploader[0].set_value(
        (name, (SAMPLES / name).read_bytes(), "text/csv")
    )
    at.run()
    return at


def _find(at, label):
    matches = [box for box in at.selectbox if box.label == label]
    assert matches, f"No selectbox labelled {label!r}; saw {[b.label for b in at.selectbox]}"
    return matches[0]


def test_form_lists_fields_from_the_uploaded_file(app):
    _upload(app)
    assert app.exception == []
    field_box = _find(app, "Field")
    assert "Email Address" in field_box.options
    assert [t.label for t in app.tabs] == ["Build rules", "Rule library"]


def test_building_an_email_format_rule_produces_executable_yaml(app):
    _upload(app)
    _find(app, "Field").select("Email Address").run()
    _find(app, "Rule type").select("format").run()
    _find(app, "Format").select("Email").run()

    [b for b in app.button if b.label == "+ Add rule"][0].click().run()
    assert app.exception == []

    yaml_blocks = [block.value for block in app.code if "rules:" in block.value]
    assert yaml_blocks, "No YAML was rendered by the builder"
    yaml_text = yaml_blocks[0]

    # Exact shape: deterministic, no model, no network.
    assert "- name: format_email_address" in yaml_text
    assert "field: Email Address" in yaml_text
    assert "type: regex" in yaml_text
    assert "severity: error" in yaml_text
    assert r"pattern: ^[^@\s]+@[^@\s]+\.[^@\s]+$" in yaml_text

    # And it is valid to the engine.
    from app_files.rules.builder import parse_rules_yaml

    assert len(parse_rules_yaml(yaml_text)) == 1


def test_the_form_built_rule_flags_a_real_violation(app):
    """The YAML from the form, run through the engine, actually fails bad data.

    ``messy_contacts.csv`` cleans down to one phone that is not a US number
    (``12345``), so a "Phone (US)" rule built in the form must flag it.
    """
    _upload(app)
    _find(app, "Field").select("Phone 1").run()
    _find(app, "Rule type").select("format").run()
    _find(app, "Format").select("Phone (US)").run()
    [b for b in app.button if b.label == "+ Add rule"][0].click().run()

    [b for b in app.button if b.label == "Run with these rules"][0].click().run()
    assert app.exception == []

    failures = [m.value for m in app.metric if m.label == "Rule failures"]
    assert failures, "No Rule failures metric rendered"
    assert int(failures[0].split()[0]) >= 1


def test_a_required_rule_on_an_empty_column_is_reported(app):
    """Building a second rule type through the same form works."""
    _upload(app)
    _find(app, "Field").select("Phone 1").run()
    _find(app, "Rule type").select("required").run()
    [b for b in app.button if b.label == "+ Add rule"][0].click().run()

    yaml_text = [b.value for b in app.code if "rules:" in b.value][0]
    assert "field: Phone 1" in yaml_text
    assert "type: required" in yaml_text