"""Unit tests for the visual rule builder.

Covers the six behaviours the builder promises: every rule type produces the
right YAML, editing changes it, removing drops it, loading a library set appends
to it, invalid combinations are rejected before they reach the list, and the
generated YAML loads through the real rule schema.

The last group is the regression that matters most in practice: rules are built
against the columns in the buyer's *file* but run against the *mapped* frame, so
a rule whose field is never translated matches nothing and silently reports zero
failures. That failure mode looks exactly like "your data is fine", so it gets
its own tests.
"""

from __future__ import annotations

import re

import pandas as pd
import pytest

from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.rules import RuleConfigError, run_rules
from app_files.rules.builder import (
    COMMON_PATTERNS,
    CUSTOM_PATTERN,
    KIND_TO_ENGINE,
    DraftError,
    RuleDraft,
    RuleList,
    drafts_from_library,
    parse_rules_yaml,
    rules_to_yaml,
    unique_name,
)
from app_files.rules.execution import field_map, resolve_rules, run_with_rules
from app_files.utilities.rule_library import load_library

# --------------------------------------------------------------------- fixtures


@pytest.fixture
def columns() -> list[str]:
    return ["email", "phone", "status", "amount", "state"]


@pytest.fixture
def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "email": ["ann@x.com", "", "not-an-email", "dee@x.com"],
            "phone": ["+14155552671", "12345", "+14155552672", ""],
            "status": ["lead", "Customer", "partner", ""],
            "amount": [100.0, -30.0, 250.0, 0.0],
            "state": ["CA", "California", "NY", "TX"],
        }
    )


# --------------------------------------------------------------------- YAML shape


def test_every_rule_kind_maps_to_an_engine_type():
    assert set(KIND_TO_ENGINE.values()) <= {
        "required",
        "range",
        "length",
        "list_of_values",
        "regex",
    }


def test_required_rule_yaml(columns: list[str]):
    draft = RuleDraft(field="email", kind="required", severity="error")
    assert draft.to_dict() == {
        "name": "required_email",
        "field": "email",
        "type": "required",
        "severity": "error",
    }


def test_format_rule_resolves_a_named_pattern(columns: list[str]):
    draft = RuleDraft(field="email", kind="format", format_name="Email")
    payload = draft.to_dict()
    assert payload["type"] == "regex"
    assert payload["pattern"] == COMMON_PATTERNS["Email"]


def test_format_rule_uses_a_custom_pattern():
    draft = RuleDraft(
        field="sku", kind="format", format_name=CUSTOM_PATTERN, pattern=r"^[A-Z]{2}\d{4}$"
    )
    assert draft.to_dict()["pattern"] == r"^[A-Z]{2}\d{4}$"


def test_length_rule_yaml_exactly():
    draft = RuleDraft(field="state", kind="length", exactly=2)
    payload = draft.to_dict()
    assert payload["type"] == "length"
    assert payload["exactly"] == 2
    assert "min_length" not in payload and "max_length" not in payload


def test_length_rule_yaml_range_of_lengths():
    draft = RuleDraft(field="phone", kind="length", min_length=10, max_length=15)
    payload = draft.to_dict()
    assert payload["min_length"] == 10 and payload["max_length"] == 15
    assert "exactly" not in payload


def test_range_rule_yaml():
    draft = RuleDraft(field="amount", kind="range", min_value=0.0, max_value=500.0)
    payload = draft.to_dict()
    assert payload["type"] == "range"
    assert payload["min"] == 0.0 and payload["max"] == 500.0


def test_list_of_values_yaml_keeps_numbers_numeric():
    draft = RuleDraft(field="status", kind="list_of_values", values=["1", "2", "USA", "007"])
    assert draft.to_dict()["values"] == [1, 2, "USA", "007"]


def test_custom_name_and_message_are_carried_through():
    draft = RuleDraft(
        field="email", kind="required", name="email_must_exist", message="Email is missing"
    )
    payload = draft.to_dict()
    assert payload["name"] == "email_must_exist"
    assert payload["message"] == "Email is missing"


def test_severity_is_written_through():
    for severity in ("error", "warning", "info"):
        draft = RuleDraft(field="email", kind="required", severity=severity)
        assert draft.to_dict()["severity"] == severity


def test_common_patterns_are_valid_regexes():
    for name, pattern in COMMON_PATTERNS.items():
        if name == CUSTOM_PATTERN:
            assert pattern == ""
            continue
        re.compile(pattern)


def test_each_named_pattern_matches_what_it_claims():
    assert re.search(COMMON_PATTERNS["Email"], "ann@example.com")
    assert not re.search(COMMON_PATTERNS["Email"], "not-an-email")
    assert re.search(COMMON_PATTERNS["Phone (US)"], "+14155552671")
    assert re.search(COMMON_PATTERNS["Phone (international)"], "+441632960961")
    assert re.search(COMMON_PATTERNS["URL"], "https://example.com")
    assert re.search(COMMON_PATTERNS["Date (ISO)"], "2024-01-05")
    assert not re.search(COMMON_PATTERNS["Date (ISO)"], "05/01/2024")


# --------------------------------------------------------------------- list ops


def test_adding_rules_appends_to_the_yaml(columns: list[str]):
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required"))
    rules.add(RuleDraft(field="email", kind="format", format_name="Email"))
    parsed = parse_rules_yaml(rules.to_yaml())
    assert [rule.type for rule in parsed] == ["required", "regex"]


def test_duplicate_rule_names_are_disambiguated():
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required"))
    second = rules.add(RuleDraft(field="email", kind="required"))
    assert second.rule_name() == "required_email_2"
    assert rules.names() == ["required_email", "required_email_2"]


def test_editing_a_rule_updates_the_yaml():
    rules = RuleList()
    rules.add(RuleDraft(field="amount", kind="range", min_value=0.0))
    edited = RuleDraft(field="amount", kind="range", min_value=10.0, max_value=99.0)
    rules.replace(0, edited)
    payload = parse_rules_yaml(rules.to_yaml())[0]
    assert payload.min == 10.0 and payload.max == 99.0


def test_editing_does_not_leave_the_old_rule_behind():
    rules = RuleList()
    rules.add(RuleDraft(field="amount", kind="range", min_value=0.0))
    rules.replace(0, RuleDraft(field="amount", kind="required"))
    parsed = parse_rules_yaml(rules.to_yaml())
    assert len(parsed) == 1
    assert parsed[0].type == "required"


def test_editing_a_missing_rule_is_rejected():
    with pytest.raises(DraftError):
        RuleList().replace(3, RuleDraft(field="email", kind="required"))


def test_removing_a_rule_removes_it_from_the_yaml():
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required"))
    rules.add(RuleDraft(field="phone", kind="required"))
    rules.remove(0)
    parsed = parse_rules_yaml(rules.to_yaml())
    assert [rule.field for rule in parsed] == ["phone"]


def test_removing_a_missing_rule_is_rejected():
    with pytest.raises(DraftError):
        RuleList().remove(0)


def test_empty_list_serializes_to_an_empty_rules_list():
    assert parse_rules_yaml(RuleList().to_yaml()) == []


def test_unique_name_helper():
    assert unique_name("required_email", []) == "required_email"
    assert unique_name("required_email", ["required_email"]) == "required_email_2"
    assert (
        unique_name("required_email", ["required_email", "required_email_2"])
        == "required_email_3"
    )


# --------------------------------------------------------------------- invalid


def test_length_rule_with_no_length_is_rejected():
    with pytest.raises(DraftError, match="length"):
        RuleDraft(field="state", kind="length").validate()


def test_length_rule_with_min_above_max_is_rejected():
    with pytest.raises(DraftError, match="cannot be greater"):
        RuleDraft(field="state", kind="length", min_length=10, max_length=2).validate()


def test_range_rule_with_no_bounds_is_rejected():
    with pytest.raises(DraftError, match="range"):
        RuleDraft(field="amount", kind="range").validate()


def test_range_rule_with_min_above_max_is_rejected():
    with pytest.raises(DraftError, match="cannot be greater"):
        RuleDraft(field="amount", kind="range", min_value=10.0, max_value=1.0).validate()


def test_list_of_values_rule_with_no_values_is_rejected():
    with pytest.raises(DraftError, match="allowed value"):
        RuleDraft(field="status", kind="list_of_values").validate()


def test_format_rule_with_no_pattern_is_rejected():
    with pytest.raises(DraftError, match="pattern"):
        RuleDraft(field="email", kind="format", format_name=CUSTOM_PATTERN, pattern="").validate()


def test_format_rule_with_a_broken_regex_is_rejected():
    with pytest.raises(DraftError, match="regular expression"):
        RuleDraft(
            field="email", kind="format", format_name=CUSTOM_PATTERN, pattern="[unclosed"
        ).validate()


def test_unknown_rule_kind_is_rejected():
    with pytest.raises(DraftError, match="kind"):
        RuleDraft(field="email", kind="teleport")


def test_unknown_severity_is_rejected():
    with pytest.raises(DraftError, match="severity"):
        RuleDraft(field="email", kind="required", severity="fatal").validate()


def test_missing_field_is_rejected():
    with pytest.raises(DraftError, match="field"):
        RuleDraft(field="  ", kind="required").validate()


def test_an_invalid_rule_never_reaches_the_list():
    rules = RuleList()
    with pytest.raises(DraftError):
        rules.add(RuleDraft(field="state", kind="length"))
    assert len(rules) == 0
    assert parse_rules_yaml(rules.to_yaml()) == []


# --------------------------------------------------------------------- schema


def test_generated_yaml_validates_against_the_rule_schema(columns: list[str]):
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required", severity="error"))
    rules.add(RuleDraft(field="email", kind="format", format_name="Email"))
    rules.add(RuleDraft(field="phone", kind="format", format_name="Phone (international)"))
    rules.add(RuleDraft(field="state", kind="length", exactly=2))
    rules.add(RuleDraft(field="amount", kind="range", min_value=0.0, max_value=500.0))
    rules.add(RuleDraft(field="status", kind="list_of_values", values=["lead", "Customer"]))
    parsed = parse_rules_yaml(rules.to_yaml())
    assert len(parsed) == 6
    assert {rule.type for rule in parsed} == {
        "required",
        "regex",
        "length",
        "range",
        "list_of_values",
    }


def test_parse_rejects_yaml_that_breaks_the_schema():
    with pytest.raises(RuleConfigError):
        parse_rules_yaml("rules:\n- field: email\n  type: length\n  severity: error\n")


def test_parse_rejects_a_non_mapping_document():
    with pytest.raises(RuleConfigError):
        parse_rules_yaml("- just\n- a\n- list\n")


def test_rules_to_yaml_handles_an_empty_list():
    assert rules_to_yaml([]) == "rules: []\n"


# --------------------------------------------------------------------- library


def test_library_rules_load_into_drafts(columns: list[str]):
    library = load_library()
    assert "email_validation" in library
    drafts = drafts_from_library(library["email_validation"].rules, columns)
    assert len(drafts) == len(library["email_validation"].rules)
    assert {draft.field for draft in drafts} == {"email"}


def test_loading_a_library_set_appends_to_the_current_list(columns: list[str]):
    rules = RuleList()
    rules.add(RuleDraft(field="status", kind="list_of_values", values=["lead"]))
    library = load_library()
    drafts = drafts_from_library(library["email_validation"].rules, columns)
    added = rules.extend(drafts)
    assert len(added) == len(drafts)
    assert len(rules) == 1 + len(drafts)
    parsed = parse_rules_yaml(rules.to_yaml())
    assert len(parsed) == len(rules)


def test_loading_a_library_set_twice_does_not_duplicate_names(columns: list[str]):
    rules = RuleList()
    library = load_library()
    drafts = drafts_from_library(library["email_validation"].rules, columns)
    rules.extend(drafts)
    rules.extend(drafts)
    assert len(set(rules.names())) == len(rules)


def test_an_explicit_name_is_still_de_duplicated():
    """Two rules sharing a hand-typed name would merge their failure counts."""
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required", name="my_check"))
    rules.add(RuleDraft(field="phone", kind="required", name="my_check"))
    assert rules.names() == ["my_check", "my_check_2"]


def test_editing_a_rule_keeps_its_own_name():
    """Keeping the same name must not be mistaken for a collision."""
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required", name="my_check"))
    rules.replace(0, RuleDraft(field="email", kind="required", name="my_check"))
    assert rules.names() == ["my_check"]


def test_library_fields_are_repointed_at_real_columns():
    drafts = drafts_from_library(
        [{"name": "email_required", "field": "email", "type": "required", "severity": "error"}],
        ["Email Address", "Phone 1"],
    )
    assert drafts[0].field == "Email Address"


def test_library_matching_ignores_case_and_separators():
    """``EmailAddress`` in a file still satisfies a library rule for ``email``."""
    drafts = drafts_from_library(
        [{"name": "x", "field": "email", "type": "required", "severity": "error"}],
        ["EmailAddress"],
    )
    assert drafts[0].field == "EmailAddress"


def test_a_mapped_field_name_is_left_alone():
    """``createdate`` is a mapped target name, so it needs no repointing.

    The builder must not "correct" it to the source column ``Created Date``:
    the field map in the execution layer resolves it either way, and rewriting
    it would be a guess about which frame the buyer meant.
    """
    drafts = drafts_from_library(
        [{"name": "x", "field": "createdate", "type": "required", "severity": "error"}],
        ["Created Date"],
    )
    assert drafts[0].field == "createdate"


def test_library_matching_handles_underscored_names():
    drafts = drafts_from_library(
        [{"name": "x", "field": "phone", "type": "required", "severity": "error"}],
        ["Phone 1"],
    )
    assert drafts[0].field == "Phone 1"


def test_library_repoints_the_shipped_email_and_phone_sets():
    columns = ["First Name", "Email Address", "Phone 1", "Country"]
    for set_name, expected in (
        ("email_validation", "Email Address"),
        ("phone_validation", "Phone 1"),
        ("required_fields", None),
    ):
        drafts = drafts_from_library(load_library()[set_name].rules, columns)
        assert all(draft.field in columns for draft in drafts), set_name
        if expected is not None:
            assert {draft.field for draft in drafts} == {expected}, set_name


def test_every_shipped_library_set_runs_against_a_file_it_fits(contacts_csv, bank_csv, tmp_path):
    """Each library set must actually execute, not just load.

    A set only runs where its fields exist, so ``positive_amount`` is exercised
    against the bank config (the one that produces ``amount``) and the contact
    sets against the CRM config. Choosing the config per set is the point: an
    ``amount`` rule against a contacts file legitimately matches no column, and
    the builder must report that rather than pretend it ran.
    """
    matches = {
        "positive_amount": ("bank_reconciliation", bank_csv, "bank_statement.csv"),
    }
    default = ("hubspot", contacts_csv, "messy_contacts.csv")
    for name, rule_set in load_library().items():
        crm, path, filename = matches.get(name, default)
        source = read_any(path)
        drafts = drafts_from_library(rule_set.rules, [str(c) for c in source.columns])
        rules = RuleList()
        rules.extend(drafts)
        run = run_with_rules(
            source,
            rules.to_rules(),
            crm=crm,
            rules_path=tmp_path / f"{name}.yaml",
            source_filename=filename,
        )
        assert run.summary()["rules_run"] == len(drafts), name
        assert run.unmatched_rules == [], name


def test_an_amount_rule_against_contacts_is_reported_unmatched(contacts_csv, tmp_path):
    """The honest counterpart to the test above: no silent no-op."""
    source = read_any(contacts_csv)
    drafts = drafts_from_library(load_library()["positive_amount"].rules, ["email"])
    rules = RuleList()
    rules.extend(drafts)
    run = run_with_rules(
        source,
        rules.to_rules(),
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="messy_contacts.csv",
    )
    assert run.summary()["rules_run"] == 0
    assert run.unmatched_rules == ["amount_positive"]


def test_library_keeps_a_rule_whose_column_is_absent():
    drafts = drafts_from_library(
        [{"name": "x", "field": "nonexistent", "type": "required", "severity": "error"}],
        ["email"],
    )
    assert drafts[0].field == "nonexistent"


def test_library_round_trips_a_named_pattern_back_to_the_dropdown():
    drafts = drafts_from_library(
        [
            {
                "name": "email_format",
                "field": "email",
                "type": "regex",
                "pattern": COMMON_PATTERNS["Email"],
                "severity": "error",
            }
        ],
        ["email"],
    )
    assert drafts[0].format_name == "Email"


def test_every_library_set_loads_into_the_builder(columns: list[str]):
    for name, rule_set in load_library().items():
        drafts = drafts_from_library(rule_set.rules, columns)
        assert len(drafts) == len(rule_set.rules), name
        # and each one survives the schema
        holder = RuleList()
        holder.extend(drafts)
        parsed = parse_rules_yaml(holder.to_yaml())
        assert len(parsed) == len(drafts), name


# --------------------------------------------------------------------- running


def test_built_rules_flag_a_real_violation(frame: pd.DataFrame):
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required"))
    outcome = run_rules(frame, rules.to_rules())
    assert outcome.rules_run == 1
    assert outcome.total_failures == 1


def test_built_format_rule_catches_a_bad_address(frame: pd.DataFrame):
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="format", format_name="Email"))
    outcome = run_rules(frame, rules.to_rules())
    assert outcome.failures_by_rule == {"format_email": 1}


def test_a_rule_on_a_missing_column_runs_nothing(frame: pd.DataFrame):
    """The engine's documented behaviour: unknown columns are skipped."""
    rules = RuleList()
    rules.add(RuleDraft(field="nowhere", kind="required"))
    assert run_rules(frame, rules.to_rules()).rules_run == 0


# --------------------------------------------------------------------- mapping
# Rules are built from the columns in the uploaded file, but the engine runs on
# the mapped frame. These tests pin the translation, because losing it makes a
# failing rule look like a pass.


def test_field_map_translates_source_columns_to_mapped_names(contacts_frame):
    result = run_pipeline(contacts_frame, crm="hubspot", source_filename="messy_contacts.csv")
    mapping = field_map(result)
    assert mapping["Email Address"] == "email"
    assert mapping["Country"] == "country"


def test_field_map_keeps_mapped_names_working(contacts_frame):
    result = run_pipeline(contacts_frame, crm="hubspot", source_filename="messy_contacts.csv")
    mapping = field_map(result)
    assert mapping["email"] == "email"


def test_resolve_rules_repoints_a_source_column(contacts_frame):
    result = run_pipeline(contacts_frame, crm="hubspot", source_filename="messy_contacts.csv")
    resolved, unmatched = resolve_rules(result, [RuleDraft(field="Email Address", kind="required").to_rule()])
    assert unmatched == []
    assert resolved[0].field == "email"


def test_resolve_rules_reports_an_unmatchable_field(contacts_frame):
    result = run_pipeline(contacts_frame, crm="hubspot", source_filename="messy_contacts.csv")
    resolved, unmatched = resolve_rules(result, [RuleDraft(field="nowhere", kind="required").to_rule()])
    assert resolved == []
    assert unmatched == ["required_nowhere"]


def test_run_with_rules_runs_a_source_named_rule(contacts_frame, tmp_path):
    """The end-to-end regression: a rule built from the file's column must run."""
    rules = RuleList()
    rules.add(RuleDraft(field="Email Address", kind="required"))
    run = run_with_rules(
        contacts_frame,
        rules.to_rules(),
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="messy_contacts.csv",
    )
    assert run.summary()["rules_run"] == 1
    assert run.unmatched_rules == []
    assert run.rule_result.total_failures >= 1


def test_run_with_rules_flags_a_bad_country(tmp_path):
    source = read_any(
        b"First Name,Last Name,Email Address,Country\n"
        b"Ann,Smith,ann@example.com,France\n"
        b"Bob,Jones,bob@example.com,Atlantis\n",
        filename="contacts.csv",
    )
    rules = RuleList()
    rules.add(RuleDraft(field="Country", kind="list_of_values", values=["USA", "France"]))
    run = run_with_rules(
        source,
        rules.to_rules(),
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="contacts.csv",
    )
    assert run.rule_result.failures_by_rule == {"allowed_country": 1}
    assert "Atlantis" in run.issues_frame().to_string()


def test_run_with_rules_merges_into_the_qa_report(contacts_frame, tmp_path):
    rules = RuleList()
    rules.add(RuleDraft(field="Email Address", kind="required"))
    run = run_with_rules(
        contacts_frame,
        rules.to_rules(),
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="messy_contacts.csv",
    )
    assert "required_email_address" in run.qa_report_html
    assert run.rule_result.total_failures >= 1


def test_run_with_rules_writes_the_yaml_it_used(contacts_frame, tmp_path):
    target = tmp_path / "nested" / "rules.yaml"
    rules = RuleList()
    rules.add(RuleDraft(field="email", kind="required"))
    run = run_with_rules(
        contacts_frame,
        rules.to_rules(),
        crm="hubspot",
        rules_path=target,
        source_filename="messy_contacts.csv",
    )
    assert run.rules_path == target
    written = parse_rules_yaml(target.read_text(encoding="utf-8"))
    assert [rule.field for rule in written] == ["email"]


def test_rules_frame_reports_which_rules_ran(contacts_frame, tmp_path):
    rules = RuleList()
    rules.add(RuleDraft(field="Email Address", kind="required"))
    rules.add(RuleDraft(field="nowhere", kind="required"))
    run = run_with_rules(
        contacts_frame,
        rules.to_rules(),
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="messy_contacts.csv",
    )
    ran = dict(zip(run.rules_frame()["rule"], run.rules_frame()["ran"]))
    assert ran["required_email_address"] == "yes"
    assert ran["required_nowhere"] == "no"


def test_a_passing_rule_set_reports_no_failures(tmp_path):
    source = read_any(
        b"First Name,Last Name,Email Address,Country\n"
        b"Ann,Smith,ann@example.com,France\n",
        filename="contacts.csv",
    )
    rules = RuleList()
    rules.add(RuleDraft(field="Email Address", kind="format", format_name="Email"))
    run = run_with_rules(
        source,
        rules.to_rules(),
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="contacts.csv",
    )
    assert run.summary()["rules_run"] == 1
    assert run.summary()["rule_failures"] == 0


def test_no_rules_is_a_valid_run(contacts_frame, tmp_path):
    run = run_with_rules(
        contacts_frame,
        [],
        crm="hubspot",
        rules_path=tmp_path / "rules.yaml",
        source_filename="messy_contacts.csv",
    )
    assert run.summary()["rules_run"] == 0
    assert run.summary()["rule_failures"] == 0


# --------------------------------------------------------------------- deterministic
# The builder must not call a model, a network, or an API key. These tests pin
# the determinism that the no-AI requirement depends on.


def test_the_same_form_input_always_produces_the_same_yaml():
    def build() -> str:
        rules = RuleList()
        rules.add(RuleDraft(field="email", kind="format", format_name="Email"))
        rules.add(RuleDraft(field="status", kind="list_of_values", values=["a", "b"]))
        return rules.to_yaml()

    assert build() == build()


def test_the_builder_imports_no_network_or_model_libraries():
    """No requests, openai, httpx or urllib anywhere in the builder stack."""
    import inspect

    from app_files.rules import builder, execution

    forbidden = ("import requests", "import openai", "import httpx", "import urllib")
    for module in (builder, execution):
        source = inspect.getsource(module)
        for needle in forbidden:
            assert needle not in source, f"{module.__name__} uses {needle}"


def test_the_ai_rule_assistant_is_gone():
    """The natural-language assistant was removed in favour of this builder."""
    import importlib

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("app_files.intelligence.rule_assistant")
