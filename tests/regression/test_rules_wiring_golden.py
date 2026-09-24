"""Golden file for the rule binding (Layer 4).

Known input, known clean output, and the exact issues and per-rule table a
run must produce once the config's rules are applied. The point of the fixture
is the ``rule:phone_e164_format`` row: before this layer, a config's rules ran
in the UI only and that row never reached ``issues.csv``.

Do not regenerate the expected files to make this green. If the issues CSV
loses the rule row, the binding has come undone.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.ingestion import read_any
from app_files.rules.binding import run_configured

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "rules_wiring"

RUN_KWARGS = {"project_name": "Golden", "source_filename": "contacts.csv"}


@pytest.fixture
def built(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return run_configured(read_any(GOLDEN / "contacts.csv"), "hubspot", **RUN_KWARGS)


def test_the_clean_output_matches_the_golden_file(built):
    produced = built.result.clean_frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_clean.csv").read_text(encoding="utf-8")


def test_the_issues_match_the_golden_file(built):
    produced = built.result.validation.issues_frame().to_csv(index=False)
    assert produced == (GOLDEN / "expected_issues.csv").read_text(encoding="utf-8")


def test_the_rule_table_matches_the_golden_file(built):
    produced = built.rules_frame().to_csv(index=False)
    assert produced == (GOLDEN / "expected_rules.csv").read_text(encoding="utf-8")


def test_the_golden_rule_failure_is_present(built):
    """The guard the fixture exists for: the rule row is in the issues."""
    checks = set(built.result.validation.issues_frame()["check"])
    assert "rule:phone_e164_format" in checks


def test_the_rule_less_run_stays_byte_identical(tmp_path, monkeypatch):
    """A config without rules must produce exactly what the pipeline produced."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    from app_files.pipeline import run_pipeline

    frame = read_any(GOLDEN / "contacts.csv")
    plain = run_pipeline(frame, crm="salesforce", project_name="Golden",
                         source_filename="contacts.csv")
    built = run_configured(frame, "salesforce", **RUN_KWARGS)
    assert built.result.clean_frame.to_csv(index=False) == plain.clean_frame.to_csv(index=False)
    assert built.qa_report_html == plain.qa_report_html
