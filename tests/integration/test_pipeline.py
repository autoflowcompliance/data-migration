"""Integration tests: full pipeline runs on the sample files.

Two acceptance criteria from the brief:

* run ``messy_contacts.csv`` through the whole pipeline and assert the output shape
* run ``bank_statement.csv`` against ``ledger.csv`` and assert the reconciliation
  report shows the expected mismatches
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.ingestion import read_any
from app_files.lineage import LineageTracker
from app_files.mappers import load_mapping_config
from app_files.output import write_any
from app_files.pipeline import run_pipeline
from app_files.profiling import DIMENSION_NAMES, profile
from app_files.rules import run_rules_for
from app_files.services.bank_reconciliation.reconciler import run_reconciliation


# ------------------------------------------------------------------ contacts
def test_messy_contacts_pipeline_produces_expected_shape(contacts_csv: Path):
    source = read_any(contacts_csv)
    result = run_pipeline(source, crm="hubspot")

    assert len(source) == 7
    frame = result.clean_frame
    # One exact duplicate row is removed by the cleaner, and the mapping
    # produces the hubspot canonical columns.
    assert len(frame) == 6
    assert {field.name for field in load_mapping_config("hubspot").fields} <= set(frame.columns)
    assert frame["email"].str.lower().tolist() == frame["email"].tolist()


def test_messy_contacts_pipeline_summary_is_consistent(contacts_csv: Path):
    source = read_any(contacts_csv)
    result = run_pipeline(source, crm="hubspot")
    summary = result.summary()

    assert summary["rows_in"] == 7
    assert summary["rows_out"] == len(result.clean_frame)
    assert summary["duplicates_removed"] == 1
    assert 0 <= summary["quality_score"] <= 100


def test_messy_contacts_qa_report_is_rendered(contacts_csv: Path):
    result = run_pipeline(read_any(contacts_csv), crm="hubspot")
    assert result.qa_report_html
    assert "<html" in result.qa_report_html.lower()


def test_messy_contacts_issues_are_reported(contacts_csv: Path):
    result = run_pipeline(read_any(contacts_csv), crm="hubspot")
    issues = result.validation.issues_frame()
    assert list(issues.columns) == ["row", "field", "check", "severity", "message"]


def test_messy_contacts_profiles_across_five_dimensions(contacts_csv: Path):
    result = run_pipeline(read_any(contacts_csv), crm="hubspot")
    result_profile = profile(result.clean_frame)
    assert set(result_profile.scores) == set(DIMENSION_NAMES)


def test_messy_contacts_rules_flow_into_the_issues_list(contacts_csv: Path):
    from app_files.mappers import map_data

    mapped = map_data(read_any(contacts_csv), load_mapping_config("hubspot")).frame
    rule_result = run_rules_for(mapped, "hubspot")
    assert rule_result.rules_run == 2
    assert all(issue.check.startswith("rule:") for issue in rule_result.issues)


def test_lineage_tracing_does_not_alter_the_output(contacts_csv: Path):
    source = read_any(contacts_csv)
    plain = run_pipeline(source, crm="hubspot")
    tracked = run_pipeline(source, crm="hubspot", lineage_tracker=LineageTracker())

    # The trace id column is stripped before output, so data is identical.
    pd.testing.assert_frame_equal(plain.clean_frame, tracked.clean_frame)
    assert plain.summary() == tracked.summary()
    assert "_lineage_id" not in tracked.clean_frame.columns


def test_lineage_tracing_records_transformations(contacts_csv: Path):
    tracker = LineageTracker()
    result = run_pipeline(read_any(contacts_csv), crm="hubspot", lineage_tracker=tracker)
    log = result.lineage_log()
    assert len(log) > 0
    assert {"source_row", "output_row", "field", "before", "after", "action"} <= set(log.columns)
    # At least one cleaned value and one mapped value are recorded.
    actions = tracker.actions()
    assert "clean" in actions
    assert any(action.startswith("map:") for action in actions)
    assert "removed_duplicate" in actions


def test_pipeline_output_written_in_all_four_formats(tmp_path: Path, contacts_csv: Path):
    result = run_pipeline(read_any(contacts_csv), crm="hubspot")
    for fmt in ("csv", "excel", "json", "sql"):
        path = write_any(result.clean_frame, tmp_path / f"clean_{fmt}", fmt)
        assert path.exists() and path.stat().st_size > 0


# ---------------------------------------------------------------------- bank
@pytest.fixture
def reconciliation(bank_csv: Path, ledger_csv: Path) -> dict:
    return run_reconciliation(
        bank_csv.read_bytes(), ledger_csv.read_bytes(),
        "Date", "Amount", "Date", "Amount", 2,
    )


def test_reconciliation_counts(reconciliation: dict):
    summary = reconciliation["summary"]
    assert summary["bank_transactions"] == 7
    assert summary["ledger_transactions"] == 7
    # Six rows match on amount + date within tolerance.
    assert summary["matched"] == 6
    assert summary["missing_from_books"] == 1
    assert summary["recorded_but_never_cleared"] == 1


def test_reconciliation_flags_the_mystery_deposit(reconciliation: dict):
    bank_only = reconciliation["bank_only"]
    assert len(bank_only) == 1
    assert "MYSTERY DEPOSIT" in bank_only.iloc[0]["Description"]
    assert float(bank_only.iloc[0]["Amount"]) == 800.0


def test_reconciliation_flags_the_uncleared_cheque(reconciliation: dict):
    ledger_only = reconciliation["ledger_only"]
    assert len(ledger_only) == 1
    assert "NEVER CLEARED" in ledger_only.iloc[0]["Description"]
    assert float(ledger_only.iloc[0]["Amount"]) == -999.0


def test_reconciliation_does_not_silently_match_the_mismatch(reconciliation: dict):
    """The 800 deposit and the 999 cheque must appear in *no* matched pair."""
    matched_amounts = [match["amount"] for match in reconciliation["matches"]]
    assert 800.0 not in matched_amounts
    assert -999.0 not in matched_amounts


def test_reconciliation_tolerates_a_one_day_clearing_difference(reconciliation: dict):
    """The 3200 client payment clears the day after the ledger entry."""
    by_amount = {match["amount"]: match["date_diff_days"] for match in reconciliation["matches"]}
    assert by_amount[3200.0] == 1


def test_reconciliation_with_zero_tolerance_matches_fewer_rows(
    bank_csv: Path, ledger_csv: Path
):
    strict = run_reconciliation(
        bank_csv.read_bytes(), ledger_csv.read_bytes(),
        "Date", "Amount", "Date", "Amount", 0,
    )
    assert strict["summary"]["matched"] < 6


def test_reconciliation_of_a_file_against_itself_matches_everything(bank_csv: Path):
    data = bank_csv.read_bytes()
    result = run_reconciliation(data, data, "Date", "Amount", "Date", "Amount", 0)
    summary = result["summary"]
    assert summary["matched"] == 7
    assert summary["missing_from_books"] == 0
    assert summary["recorded_but_never_cleared"] == 0


def test_reconciliation_parses_accounting_amount_formats(bank_csv: Path, ledger_csv: Path):
    """'(250.00)' in the bank file matches '-250.00' in the ledger."""
    result = run_reconciliation(
        bank_csv.read_bytes(), ledger_csv.read_bytes(),
        "Date", "Amount", "Date", "Amount", 2,
    )
    matched_amounts = sorted(match["amount"] for match in result["matches"])
    assert -250.0 in matched_amounts


def test_reconciliation_reports_a_missing_column_clearly(bank_csv: Path, ledger_csv: Path):
    with pytest.raises(KeyError):
        run_reconciliation(
            bank_csv.read_bytes(), ledger_csv.read_bytes(),
            "Date", "NotAColumn", "Date", "Amount", 2,
        )


def _prepared(frame: pd.DataFrame, date_format: str | None = None) -> pd.DataFrame:
    """Parse the date/amount columns an adapter returns into matchable types."""
    out = frame.copy()
    out["Date"] = pd.to_datetime(out["Date"], format=date_format, errors="coerce")
    out["Amount"] = out["Amount"].astype(str).str.replace("(", "-", regex=False).str.replace(")", "", regex=False).astype(float)
    return out


def test_bank_statement_pdf_reconciles_like_the_csv(bank_csv: Path, bank_pdf: Path, ledger_csv: Path):
    """A PDF statement and the equivalent CSV produce the same discrepancies.

    ``run_reconciliation`` takes CSV bytes, so a PDF is ingested to a frame
    first and matched with ``reconcile_transactions``. The PDF prints dates
    US-style (01/03/2024) where the CSV is ISO.
    """
    from app_files.services.bank_reconciliation.reconciler import reconcile_transactions

    from_csv = run_reconciliation(
        bank_csv.read_bytes(), ledger_csv.read_bytes(),
        "Date", "Amount", "Date", "Amount", 2,
    )
    ledger = read_any(ledger_csv)
    ledger["Date"] = pd.to_datetime(ledger["Date"], errors="coerce")
    ledger["Amount"] = ledger["Amount"].astype(float)

    from_pdf = reconcile_transactions(
        _prepared(read_any(bank_pdf), date_format="%m/%d/%Y"),
        ledger, "Date", "Amount", "Date", "Amount", 2,
    )

    assert len(from_pdf["matches"]) == len(from_csv["matches"]) == 6
    assert len(from_pdf["bank_only"]) == len(from_csv["bank_only"]) == 1
    assert len(from_pdf["ledger_only"]) == len(from_csv["ledger_only"]) == 1
    # Both routes flag the same two discrepancies.
    assert "MYSTERY DEPOSIT" in from_pdf["bank_only"].iloc[0]["Description"]
    assert "NEVER CLEARED" in from_pdf["ledger_only"].iloc[0]["Description"]