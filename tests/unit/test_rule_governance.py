"""Cross-field rules, rule versioning, and baseline comparison."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.rules import (
    CrossFieldError,
    CrossFieldRule,
    RuleConfigError,
    compare_to_baseline,
    diff_rule_versions,
    failures_from_results,
    read_rule_versions,
    record_rule_version,
    run_cross_field_rules,
    version_rules,
)

TRANSACTIONS = pd.DataFrame(
    {
        "country": ["US", "US", "CA", "US"],
        "state": ["NY", "New York", "ON", "CA"],
        "subtotal": [100, 50, 20, 10],
        "tax": [10, 5, 2, 1],
        "total": [110, 55, 22, 11],
    }
)


def test_cross_field_rule_against_a_literal():
    rule = CrossFieldRule(
        name="us_only",
        left="country",
        operator_name="equals",
        right="US",
        message="This dataset must be US-only.",
    )
    result = rule.evaluate(TRANSACTIONS)
    assert result.failed == 1  # the CA row
    assert result.passed == 3
    assert result.failures[0]["country"] == "CA"


def test_numeric_comparison_of_two_columns():
    # total must equal subtotal + tax; encode it as "total >= subtotal"
    rule = CrossFieldRule(
        name="total_covers_subtotal",
        left="total",
        operator_name="greater_or_equal",
        right="subtotal",
    )
    result = rule.evaluate(TRANSACTIONS)
    assert result.failed == 0
    assert result.passed == 4


def test_a_failing_column_rule_reports_the_offending_rows():
    frame = TRANSACTIONS.assign(total=[110, 55, 10, 11])  # row 2 is short
    rule = CrossFieldRule(
        name="total_at_least_expected",
        left="total",
        operator_name="greater_or_equal",
        right="subtotal",
    )
    result = rule.evaluate(frame)
    assert result.failed == 1
    assert result.failures[0]["row"] == 2


def test_blank_values_are_skipped_by_default():
    frame = pd.DataFrame({"a": ["1", "", "3"], "b": ["1", "2", ""]})
    rule = CrossFieldRule(name="eq", left="a", operator_name="equals", right="b")
    result = rule.evaluate(frame)
    assert result.passed == 1
    assert result.failed == 0


def test_missing_column_is_a_clear_error():
    rule = CrossFieldRule(name="bad", left="nope", operator_name="equals", right="US")
    with pytest.raises(CrossFieldError, match="nope"):
        rule.evaluate(TRANSACTIONS)


def test_unknown_operator_is_rejected_at_construction():
    with pytest.raises(CrossFieldError, match="operator"):
        CrossFieldRule(name="bad", left="a", operator_name="is_odd", right="b")


def test_numeric_strings_compare_numerically():
    frame = pd.DataFrame({"a": ["9", "10"], "b": ["10", "9"]})
    rule = CrossFieldRule(name="gt", left="a", operator_name="greater_than", right="b")
    result = rule.evaluate(frame)
    # Numerically: 10 > 9 passes, 9 > 10 fails. Lexically both would pass.
    assert result.passed == 1
    assert result.failed == 1
    assert result.failures[0]["row"] == 0


def test_run_cross_field_rules_runs_them_all():
    rules = [
        CrossFieldRule(name="r1", left="country", operator_name="equals", right="US"),
        CrossFieldRule(name="r2", left="total", operator_name="greater_or_equal", right="subtotal"),
    ]
    results = run_cross_field_rules(TRANSACTIONS, rules)
    assert [r.rule for r in results] == ["r1", "r2"]


# ---------------------------------------------------------------- versioning
def _rule_dicts():
    return [
        {"name": "email_required", "type": "required", "field": "email"},
        {"name": "phone_length", "type": "length", "field": "phone", "min": 10},
    ]


def test_version_is_content_based_and_stable():
    first = version_rules(_rule_dicts())
    second = version_rules(_rule_dicts())
    assert first.version == second.version
    assert first.rule_count == 2


def test_changing_a_rule_changes_the_version():
    before = version_rules(_rule_dicts())
    modified = _rule_dicts()
    modified[1]["min"] = 11
    after = version_rules(modified)
    assert before.version != after.version


def test_diff_reports_added_removed_and_changed():
    before = _rule_dicts()
    after = [
        {"name": "email_required", "type": "required", "field": "email"},
        {"name": "new_rule", "type": "required", "field": "company"},
    ]
    diff = diff_rule_versions(before, after)
    assert [r["name"] for r in diff.added] == ["new_rule"]
    assert [r["name"] for r in diff.removed] == ["phone_length"]
    assert diff.changed == []
    assert diff.empty is False


def test_identical_sets_diff_empty():
    assert diff_rule_versions(_rule_dicts(), _rule_dicts()).empty is True


def test_version_history_round_trips(tmp_path):
    path = tmp_path / "versions.jsonl"
    record_rule_version(version_rules(_rule_dicts()), path=path)
    record_rule_version(version_rules(_rule_dicts()), path=path)
    entries = read_rule_versions(path)
    assert len(entries) == 2
    assert entries[0]["version"] == entries[1]["version"]
    assert entries[0]["created_at"]


# --------------------------------------------------------------- baseline
def test_baseline_comparison_reports_direction():
    comparisons = compare_to_baseline(
        {"email_required": 12, "phone_length": 4},
        {"email_required": 3, "phone_length": 6},
    )
    by_rule = {c.rule: c for c in comparisons}
    assert by_rule["email_required"].direction == "improving"
    assert by_rule["email_required"].delta == -9
    assert by_rule["phone_length"].direction == "worsening"


def test_removed_rule_shows_as_an_improvement():
    comparisons = compare_to_baseline({"old_rule": 5}, {})
    assert comparisons[0].delta == -5
    assert comparisons[0].direction == "improving"


def test_new_rule_shows_as_a_new_failure_source():
    comparisons = compare_to_baseline({}, {"new_rule": 2})
    assert comparisons[0].baseline_failed == 0
    assert comparisons[0].direction == "worsening"


def test_failures_from_results_reads_rule_results():
    class FakeResult:
        def __init__(self, rule, failed):
            self.rule = rule
            self.failed = failed

    counts = failures_from_results(
        [FakeResult("a", 1), FakeResult("b", 0), FakeResult("a", 2)]
    )
    assert counts == {"a": 2, "b": 0}


def test_rule_config_error_is_still_the_schema_type():
    # Governance must not shadow the engine's own error type.
    assert issubclass(RuleConfigError, ValueError)