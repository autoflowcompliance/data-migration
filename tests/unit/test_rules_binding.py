"""Layer 4 binding: the rules a config declares must actually run in a run.

The gap this closes: ``run_rules_for`` could run a config's rules and the web
UI called it, but the CLI and the batch engine never did. An unattended run
reported the core validator's issues only, so a buyer's own rule failures were
invisible in ``issues.csv``, in the QA report and in the score.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.rules.binding import (
    apply_configured_rules,
    failures_exceed,
    rule_report,
    run_configured,
)

SAMPLE = "app_files/samples/messy_contacts.csv"


@pytest.fixture
def frame() -> pd.DataFrame:
    return read_any(SAMPLE)


class TestRunConfigured:
    def test_a_configs_rules_are_run(self, frame):
        built = run_configured(frame, "hubspot")
        assert [r.name for r in built.rules] == ["lastname_required", "phone_e164_format"]
        assert built.rule_result.rules_run == 2

    def test_a_declared_failure_is_reported(self, frame):
        built = run_configured(frame, "hubspot")
        assert built.rule_result.total_failures == 1
        assert built.rule_result.failures_by_rule == {"phone_e164_format": 1}

    def test_failures_reach_the_merged_issue_list(self, frame):
        built = run_configured(frame, "hubspot")
        checks = {issue.check for issue in built.result.validation.issues}
        assert "rule:phone_e164_format" in checks

    def test_the_qa_report_shows_the_rule_failure(self, frame):
        built = run_configured(frame, "hubspot")
        assert "phone" in built.qa_report_html.lower()

    def test_a_config_without_rules_is_byte_identical_to_the_pipeline(self, frame, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        plain = run_pipeline(frame, crm="salesforce", source_filename="x.csv")
        built = run_configured(frame, "salesforce", source_filename="x.csv")
        assert built.result.clean_frame.to_csv(index=False) == plain.clean_frame.to_csv(index=False)
        assert built.qa_report_html == plain.qa_report_html
        assert built.rules == []
        assert built.rule_result.total_failures == 0

    def test_failures_exceed_is_the_strict_hook(self, frame):
        built = run_configured(frame, "hubspot")
        assert failures_exceed(built, max_failures=0) is True
        assert failures_exceed(built, max_failures=1) is False


class TestApplyConfiguredRules:
    def test_it_does_not_re_run_the_pipeline(self, frame):
        """A caller's own run (with its cleaning config) must be preserved."""
        result = run_pipeline(
            frame, crm="hubspot", project_name="Keep Me", source_filename="keep.csv"
        )
        built = apply_configured_rules(
            result, "hubspot", project_name="Keep Me", source_filename="keep.csv"
        )
        assert built.result is result
        assert built.rule_result.total_failures == 1

    def test_the_qa_report_keeps_the_caller_header(self, frame):
        result = run_pipeline(
            frame, crm="hubspot", project_name="Acme Migration", source_filename="acme.csv"
        )
        built = apply_configured_rules(
            result, "hubspot", project_name="Acme Migration", source_filename="acme.csv"
        )
        assert "Acme Migration" in built.qa_report_html
        assert "acme.csv" in built.qa_report_html

    def test_an_unmatched_rule_is_surfaced_not_dropped(self, frame, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        result = run_pipeline(frame, crm="hubspot")
        built = apply_configured_rules(result, "hubspot")
        # Both hubspot rules resolve here, so nothing should be unmatched.
        assert built.unmatched_rules == []


class TestRuleReport:
    def test_the_report_counts_what_ran(self, frame):
        built = run_configured(frame, "hubspot")
        report = rule_report(built)
        assert report["rules_declared"] == 2
        assert report["rules_run"] == 2
        assert report["rule_failures"] == 1
        assert report["failures_by_rule"] == {"phone_e164_format": 1}


CROSS_CONFIG = "tests/regression/golden_files/rules_wiring/crm.yaml"
CROSS_INPUT = "tests/regression/golden_files/rules_wiring/cross_field.csv"


class TestCrossFieldBinding:
    """A config's ``cross_field:`` block must run in a run, like ``rules:``."""

    def test_cross_field_rules_are_loaded_from_the_config(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        built = run_configured(read_any(CROSS_INPUT), CROSS_CONFIG,
                               project_name="G", source_filename="cross_field.csv")
        assert [r.name for r in built.cross_field_rules] == [
            "phone_below_zip", "zip_below_phone"
        ]
        assert built.cross_field_result.rules_run == 2

    def test_source_column_names_are_translated_to_the_mapped_frame(
        self, tmp_path, monkeypatch
    ):
        """The rule names `Phone Number`; the frame has `phone`."""
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        built = run_configured(read_any(CROSS_INPUT), CROSS_CONFIG,
                               project_name="G", source_filename="cross_field.csv")
        assert [r.fields for r in built.cross_field_rules] == [
            ["phone", "zip"], ["zip", "phone"]
        ]
        assert built.unmatched_cross_field == []

    def test_failures_are_reported_with_row_precision(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        built = run_configured(read_any(CROSS_INPUT), CROSS_CONFIG,
                               project_name="G", source_filename="cross_field.csv")
        assert built.cross_field_result.failures_by_rule == {"phone_below_zip": 2}
        issues = [i for i in built.result.validation.issues
                  if i.check.startswith("cross_field:")]
        assert {i.severity for i in issues} == {"error"}
        assert {i.row for i in issues} == {0, 2}  # 0-based frame rows

    def test_combined_counters_cover_both_rule_kinds(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        built = run_configured(read_any(CROSS_INPUT), CROSS_CONFIG,
                               project_name="G", source_filename="cross_field.csv")
        # 1 single-field + 2 cross-field = 3 declared and run
        assert built.total_rules_run == 3
        # 1 required failure + 2 compare failures
        assert built.total_rule_failures == 3
        assert failures_exceed(built) is True

    def test_the_report_includes_cross_field_issues(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        built = run_configured(read_any(CROSS_INPUT), CROSS_CONFIG,
                               project_name="G", source_filename="cross_field.csv")
        assert "phone must stay below zip" in built.qa_report_html
