"""Golden-file regression tests.

Each folder under ``golden_files/`` holds a known input and the output that
input is expected to produce. If a future change alters the clean output of a
sample, these tests fail immediately.

If a golden file breaks, the change is guilty until proven innocent. Revert the
change or fix the bug — do not regenerate the expected output to make the test
green.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.privacy import PrivacyConfig, detect_frame, mask_frame
from app_files.services.bank_reconciliation.reconciler import run_reconciliation

GOLDEN = Path(__file__).resolve().parent / "golden_files"


def test_golden_files_are_present():
    """Guard against a checkout that silently lost the fixtures."""
    for name, files in {
        "contacts": {"input.csv", "expected_output.csv"},
        "bank_statement": {"input.csv", "expected_bank_only.csv"},
        "ledger": {"input.csv", "expected_ledger_only.csv"},
        "pii": {"input.csv", "expected_masked.csv"},
        "cross_field": {"input.csv", "rules.yaml", "expected_failures.json"},
        "reconciliation_3way": {
            "bank.csv", "ledger.csv", "processor.csv", "expected_result.json",
        },
        "orchestration": {"jobs.json", "expected_transcript.json"},
        "compliance": {"controls.json"},
        "cloud_license": {"expected_state.json"},
        "tenancy": {
            "expected_manifest.json", "render.yaml", "docker-compose.yml", "k8s.yaml",
        },
    }.items():
        folder = GOLDEN / name
        assert folder.is_dir(), f"missing golden folder: {name}"
        for filename in files:
            assert (folder / filename).exists(), f"missing {name}/{filename}"


def test_contacts_golden_output_is_unchanged():
    folder = GOLDEN / "contacts"
    source = read_any(folder / "input.csv")
    produced = run_pipeline(source, crm="hubspot").clean_frame
    expected = pd.read_csv(folder / "expected_output.csv", dtype=str, keep_default_na=False)

    # Compare as strings: the golden file has been through CSV round-tripping,
    # and dtype differences are not what this test is protecting.
    produced = produced.fillna("").astype(str).reset_index(drop=True)
    expected = expected.fillna("").astype(str).reset_index(drop=True)

    assert list(produced.columns) == list(expected.columns)
    assert produced.to_dict("records") == expected.to_dict("records")


def test_state_does_not_capture_the_country_column():
    """`state` must not be filled from a `Country` column.

    HubSpot's `state` field aliases `County`, which fuzzy-matches `Country` at
    0.923 — above the 0.82 threshold — so the state slot used to swallow the
    country values (the golden file previously recorded `state=USA`, `zip=`,
    `country=USA`). Mapping now claims columns in descending confidence order,
    so `country` takes `Country` at 1.0 and `state` is left empty.
    """
    source = read_any(GOLDEN / "contacts" / "input.csv")
    frame = run_pipeline(source, crm="hubspot").clean_frame
    assert all(value is None or value == "" for value in frame["state"])
    assert frame.iloc[0]["country"] == "USA"


def test_bank_statement_golden_bank_only_is_unchanged():
    bank = GOLDEN / "bank_statement" / "input.csv"
    ledger = GOLDEN / "ledger" / "input.csv"
    result = run_reconciliation(
        bank.read_bytes(), ledger.read_bytes(), "Date", "Amount", "Date", "Amount", 2
    )
    expected = pd.read_csv(
        GOLDEN / "bank_statement" / "expected_bank_only.csv",
        dtype=str, keep_default_na=False,
    )
    produced = result["bank_only"].fillna("").astype(str).reset_index(drop=True)
    assert len(produced) == len(expected)
    assert produced["Description"].tolist() == expected["Description"].tolist()


def test_ledger_golden_never_cleared_is_unchanged():
    bank = GOLDEN / "bank_statement" / "input.csv"
    ledger = GOLDEN / "ledger" / "input.csv"
    result = run_reconciliation(
        bank.read_bytes(), ledger.read_bytes(), "Date", "Amount", "Date", "Amount", 2
    )
    expected = pd.read_csv(
        GOLDEN / "ledger" / "expected_ledger_only.csv",
        dtype=str, keep_default_na=False,
    )
    produced = result["ledger_only"].fillna("").astype(str).reset_index(drop=True)
    assert len(produced) == len(expected)
    assert produced["Description"].tolist() == expected["Description"].tolist()


def test_reconciliation_totals_are_stable():
    bank = GOLDEN / "bank_statement" / "input.csv"
    ledger = GOLDEN / "ledger" / "input.csv"
    result = run_reconciliation(
        bank.read_bytes(), ledger.read_bytes(), "Date", "Amount", "Date", "Amount", 2
    )
    assert result["summary"] == {
        "bank_transactions": 7,
        "ledger_transactions": 7,
        "bank_duplicates_removed": 0,
        "ledger_duplicates_removed": 0,
        "matched": 6,
        "missing_from_books": 1,
        "recorded_but_never_cleared": 1,
    }


def test_pii_masking_golden_output_is_unchanged():
    """Known PII in, known redaction out. If this breaks, the change is guilty
    until proven innocent — do not regenerate the expected file."""
    folder = GOLDEN / "pii"
    source = pd.read_csv(folder / "input.csv", dtype=str, keep_default_na=False)
    produced = mask_frame(source, PrivacyConfig(enabled=True)).frame
    expected = pd.read_csv(folder / "expected_masked.csv", dtype=str, keep_default_na=False)

    assert list(produced.columns) == list(expected.columns)
    assert produced.fillna("").astype(str).to_dict("records") == expected.fillna("").astype(str).to_dict("records")


def test_pii_golden_input_is_fully_masked():
    """The point of the fixture: no sensitive value survives the pass."""
    folder = GOLDEN / "pii"
    source = pd.read_csv(folder / "input.csv", dtype=str, keep_default_na=False)
    config = PrivacyConfig(enabled=True)
    found = detect_frame(source, config)
    assert found.total == 9, "fixture should carry 9 planted PII values"

    rescan = detect_frame(mask_frame(source, config).frame, config)
    assert rescan.total == 0, "masked golden output must scan clean"


def test_cross_field_golden_failures_are_unchanged():
    """Known rows in, known cross-field failures out.

    The fixture pins two things at once: a rule with a custom message, and a
    severity that is not the default. Adding cross-field rules to the codebase
    must not quietly change which rows fail.
    """
    import json

    import yaml

    from app_files.rules import load_cross_field_rules, run_cross_field_rules

    folder = GOLDEN / "cross_field"
    source = read_any(folder / "input.csv")
    result = run_pipeline(source, crm="hubspot", run_structural_check=False)
    rules = load_cross_field_rules(yaml.safe_load((folder / "rules.yaml").read_text()))
    outcome = run_cross_field_rules(result.clean_frame, rules)

    produced = {
        "rules_run": outcome.rules_run,
        "total_failures": outcome.total_failures,
        "failures_by_rule": outcome.failures_by_rule,
        "skipped_rules": outcome.skipped_rules,
        "issues": [
            {
                "row": issue.row,
                "field": issue.field,
                "check": issue.check,
                "severity": issue.severity,
                "message": issue.message,
            }
            for issue in outcome.issues
        ],
    }
    expected = json.loads((folder / "expected_failures.json").read_text())
    assert produced == expected


def test_cross_field_golden_fixture_scans_for_skipped_rules():
    """A golden run that silently skipped a rule would make the fixture a lie."""
    import yaml

    from app_files.rules import load_cross_field_rules

    folder = GOLDEN / "cross_field"
    rules = load_cross_field_rules(yaml.safe_load((folder / "rules.yaml").read_text()))
    assert rules, "the cross-field fixture must carry rules"
    assert all(rule.fields for rule in rules)