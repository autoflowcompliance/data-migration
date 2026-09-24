"""Layer 4 integration: cross-field failures must reach the real QA report.

These run the actual pipeline and then merge cross-field outcomes the way a
caller would. The point is the wiring: an issue raised by a cross-field rule
must land in the same ``validation.issues`` list the core validator fills, so
``issues_frame()`` and the rendered report pick it up with no change to either.

The fixture puts a small ZIP next to a large phone number, so
``phone < zip`` fails on every row and the merge is easy to count.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.pipeline import run_pipeline
from app_files.reporters.html_reporter import render_qa_report
from app_files.rules import (
    CrossFieldRule,
    CrossFieldRuleError,
    apply_cross_field_rules,
    run_cross_field_rules,
)

SOURCE = pd.DataFrame(
    {
        "Email Address": ["a@x.com", "b@x.com", "c@x.com"],
        "Phone": ["+14155552671", "+14155552672", "+14155552673"],
        "ZIP": ["94105", "10001", "20001"],
        "Full Name": ["Jane Doe", "John Smith", "Amy Lee"],
    }
)


@pytest.fixture
def result():
    return run_pipeline(SOURCE, crm="hubspot", run_structural_check=False)


def _always_fails(name: str) -> CrossFieldRule:
    # A huge phone number is never below a five-digit ZIP, so this fails on
    # every row and the merge count is unambiguous.
    return CrossFieldRule.from_dict(
        {"name": name, "type": "compare", "fields": ["phone", "zip"], "operator": "<"}
    )


class TestCrossFieldMergesIntoThePipeline:
    def test_failures_are_appended_to_the_validation_issues(self, result):
        before = len(result.validation.issues)
        outcome = apply_cross_field_rules(result, [_always_fails("phone_below_zip")])
        assert outcome.total_failures > 0
        assert len(result.validation.issues) == before + outcome.total_failures

    def test_the_failures_appear_in_the_issues_frame(self, result):
        apply_cross_field_rules(result, [_always_fails("phone_below_zip")])
        frame = result.validation.issues_frame()
        assert "cross_field:phone_below_zip" in set(frame["check"])

    def test_a_two_column_rule_resolves_against_the_mapped_frame(self, result):
        rule = CrossFieldRule.from_dict(
            {"name": "phone_vs_zip", "type": "compare",
             "fields": ["phone", "zip"], "operator": ">="}
        )
        outcome = apply_cross_field_rules(result, [rule])
        assert outcome.rules_run == 1
        assert outcome.total_failures == 0
        assert not outcome.skipped_rules

    def test_a_rule_on_an_absent_column_is_reported_not_raised(self, result):
        rule = CrossFieldRule.from_dict(
            {"name": "ghost", "type": "compare",
             "fields": ["not_a_column", "phone"], "operator": "<"}
        )
        outcome = apply_cross_field_rules(result, [rule])
        assert outcome.skipped_rules == ["ghost"]
        assert outcome.total_failures == 0

    def test_the_rendered_report_shows_the_cross_field_rule(self, result):
        apply_cross_field_rules(result, [_always_fails("phone_below_zip")])
        # The reporter is rendered from the current issues, so re-rendering
        # shows the merged failures without any change to the reporter itself.
        refreshed = render_qa_report(
            report=result.validation,
            mapping_log=result.mapping_log(),
            cleaning_log=result.cleaning_log(),
            mapped=result.clean_frame,
            crm=result.mapping_config.crm,
            project_name="Data migration",
            source_filename="upload.csv",
        )
        assert "phone_below_zip" in refreshed

    def test_the_quality_score_reflects_errors(self, result):
        before = result.validation.quality_score
        apply_cross_field_rules(result, [_always_fails("phone_below_zip")])
        assert result.validation.quality_score <= before

    def test_running_without_cross_field_rules_changes_nothing(self, result):
        before = list(result.validation.issues)
        apply_cross_field_rules(result, [])
        assert result.validation.issues == before

    def test_a_pure_run_reports_zero_cross_field_failures(self, result):
        from app_files.rules import load_cross_field_rules

        outcome = run_cross_field_rules(result.clean_frame, load_cross_field_rules({}))
        assert outcome.total_failures == 0

    def test_a_repeated_column_is_rejected_up_front(self):
        # Otherwise the lookup is ambiguous and the rule silently passes.
        with pytest.raises(CrossFieldRuleError, match="more than once"):
            CrossFieldRule.from_dict(
                {"name": "x", "type": "compare", "fields": ["phone", "phone"],
                 "operator": "!="}
            )
