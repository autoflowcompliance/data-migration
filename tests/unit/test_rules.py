"""Unit tests for the rule engine: one test per rule type."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.rules import (
    RULE_TYPES,
    Rule,
    RuleConfigError,
    load_rules,
    run_rules,
    run_rules_for,
)


def make_rule(**kwargs) -> Rule:
    """Build a rule through ``from_dict``, the same path config loading uses."""
    return Rule.from_dict(kwargs)


@pytest.fixture
def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "amount": [100, 250, -30, None],
            "phone": ["+14155552671", "12345", "+441632960961", ""],
            "status": ["lead", "Customer", "partner", ""],
            "state": ["CA", "California", "NY", "TX"],
        }
    )


def test_rule_types_cover_the_specified_checks():
    assert set(RULE_TYPES) == {"range", "length", "list_of_values", "regex", "required"}


def test_required_flags_empty_values(frame: pd.DataFrame):
    result = run_rules(frame, [make_rule(field="amount", type="required")])
    assert result.total_failures == 1
    assert result.issues[0].check == "rule:required_amount"
    assert result.issues[0].row == 3


def test_range_flags_out_of_bounds(frame: pd.DataFrame):
    result = run_rules(frame, [make_rule(field="amount", type="range", min=0)])
    assert result.total_failures == 1
    assert result.issues[0].row == 2


def test_range_with_min_and_max(frame: pd.DataFrame):
    result = run_rules(frame, [make_rule(field="amount", type="range", min=0, max=200)])
    flagged = {issue.row for issue in result.issues}
    assert flagged == {1, 2}


def test_length_exactly_flags_wrong_size(frame: pd.DataFrame):
    result = run_rules(frame, [make_rule(field="state", type="length", exactly=2)])
    assert result.total_failures == 1
    assert result.issues[0].row == 1


def test_length_min_length_skips_blanks(frame: pd.DataFrame):
    result = run_rules(frame, [make_rule(field="phone", type="length", min_length=10)])
    # Row 3 is blank; "empty" is the core validator's job, so length skips it.
    assert {issue.row for issue in result.issues} == {1}


def test_list_of_values_is_case_insensitive_by_default(frame: pd.DataFrame):
    rule = make_rule(field="status", type="list_of_values", values=["lead", "customer"])
    result = run_rules(frame, [rule])
    # "Customer" is accepted; "partner" fails; the blank is skipped.
    assert {issue.row for issue in result.issues} == {2}


def test_list_of_values_can_be_case_sensitive(frame: pd.DataFrame):
    rule = make_rule(
        field="status", type="list_of_values", values=["lead", "customer"],
        case_sensitive=True,
    )
    result = run_rules(frame, [rule])
    # Now "Customer" fails too.
    assert {issue.row for issue in result.issues} == {1, 2}


def test_regex_flags_non_matching(frame: pd.DataFrame):
    rule = make_rule(field="phone", type="regex", pattern=r"^\+[1-9]\d{6,14}$")
    result = run_rules(frame, [rule])
    assert {issue.row for issue in result.issues} == {1}


def test_schema_requires_type_specific_parameters():
    with pytest.raises(RuleConfigError):
        make_rule(field="amount", type="range")
    with pytest.raises(RuleConfigError):
        make_rule(field="phone", type="regex")
    with pytest.raises(RuleConfigError):
        make_rule(field="status", type="list_of_values", values=[])
    with pytest.raises(RuleConfigError):
        make_rule(field="state", type="length")


def test_unknown_type_is_rejected():
    with pytest.raises(RuleConfigError):
        make_rule(field="x", type="not_a_rule")


def test_unknown_field_key_is_rejected():
    with pytest.raises(RuleConfigError):
        make_rule(field="x", type="required", bogus=1)


def test_severity_is_validated():
    with pytest.raises(RuleConfigError):
        make_rule(field="x", type="required", severity="catastrophe")


def test_rule_without_field_is_rejected():
    with pytest.raises(RuleConfigError):
        make_rule(type="required")


def test_rule_on_absent_column_is_skipped(frame: pd.DataFrame):
    result = run_rules(frame, [make_rule(field="not_a_column", type="required")])
    assert result.rules_run == 0
    assert result.total_failures == 0


def test_custom_message_is_used(frame: pd.DataFrame):
    rule = make_rule(field="amount", type="required", message="Amount must be present")
    result = run_rules(frame, [rule])
    assert result.issues[0].message == "Amount must be present"


def test_default_name_is_type_and_field():
    assert make_rule(field="amount", type="required").name == "required_amount"


def test_explicit_name_is_kept():
    rule = make_rule(name="amount_present", field="amount", type="required")
    assert rule.name == "amount_present"


def test_failures_are_counted_per_rule(frame: pd.DataFrame):
    rules = [
        make_rule(name="amount_range", field="amount", type="range", min=0),
        make_rule(name="state_len", field="state", type="length", exactly=2),
    ]
    result = run_rules(frame, rules)
    assert result.rules_run == 2
    assert result.failures_by_rule == {"amount_range": 1, "state_len": 1}
    assert result.summary()["rule_failures"] == 2


def test_rule_failures_use_configured_severity(frame: pd.DataFrame):
    rule = make_rule(field="amount", type="required", severity="warning")
    result = run_rules(frame, [rule])
    assert result.issues[0].severity == "warning"


def test_load_rules_from_config_and_run(contacts_frame: pd.DataFrame):
    from app_files.mappers import load_mapping_config, map_data

    mapped = map_data(contacts_frame, load_mapping_config("hubspot")).frame
    result = run_rules_for(mapped, "hubspot")
    assert result.rules_run == 2
    # The sample's only rule violation is a non-E.164 phone ("555-000").
    assert result.failures_by_rule == {"phone_e164_format": 1}


def test_every_config_loads_and_runs_against_a_mapped_frame(contacts_frame: pd.DataFrame):
    from app_files.mappers import available_crms, load_mapping_config, map_data
    from app_files.rules import load_rules_for

    for crm in available_crms():
        mapped = map_data(contacts_frame, load_mapping_config(crm)).frame
        # Running must never raise, even when a config declares no rules.
        run_rules(mapped, load_rules_for(crm))


def test_malformed_rules_yaml_raises_config_error():
    with pytest.raises(RuleConfigError):
        load_rules({"rules": [{"field": "x"}]})
    with pytest.raises(RuleConfigError):
        load_rules({"rules": "not-a-list"})


def test_config_without_rules_yields_empty_list():
    assert load_rules({"fields": []}) == []
    assert load_rules(None) == []


def test_rules_load_from_real_yaml_files():
    from app_files.rules import load_rules_for

    assert {rule.name for rule in load_rules_for("hubspot")} == {
        "lastname_required", "phone_e164_format",
    }
    assert {rule.name for rule in load_rules_for("bank_reconciliation")} == {
        "amount_present", "amount_within_expected_range",
    }
    # A config with no rules block returns an empty list, not an error.
    assert load_rules_for("pipedrive") == []
    assert load_rules_for("no_such_config") == []