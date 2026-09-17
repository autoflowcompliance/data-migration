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
import pytest

from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.services.bank_reconciliation.reconciler import run_reconciliation

GOLDEN = Path(__file__).resolve().parent / "golden_files"


def test_golden_files_are_present():
    """Guard against a checkout that silently lost the fixtures."""
    for name, files in {
        "contacts": {"input.csv", "expected_output.csv"},
        "bank_statement": {"input.csv", "expected_bank_only.csv"},
        "ledger": {"input.csv", "expected_ledger_only.csv"},
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