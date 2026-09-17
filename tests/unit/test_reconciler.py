"""Unit tests for the bank reconciliation service.

Covers the messy-input handling in ``clean_currency_amount`` — the part that
decides whether a statement line is matchable at all — plus the matching rules
in ``reconcile_transactions``.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.services.bank_reconciliation.reconciler import (
    clean_currency_amount,
    reconcile_transactions,
    run_reconciliation,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1500.00", 1500.0),
        ("$1,234.56", 1234.56),
        ("  $1,234.56  ", 1234.56),
        ("(150.00)", -150.0),
        ("(1,200.50)", -1200.5),
        ("-180.00", -180.0),
        ("1200.00 CR", 1200.0),
        ("1200.00 DR", -1200.0),
        ("1,200.00 cr", 1200.0),
        ("0", 0.0),
        ("+250.00", 250.0),
    ],
)
def test_clean_currency_amount_parses_accounting_formats(raw: str, expected: float):
    assert clean_currency_amount(raw) == pytest.approx(expected)


@pytest.mark.parametrize("raw", ["", "   ", "N/A", "abc", None, "12.3.4"])
def test_clean_currency_amount_rejects_unparseable_values(raw):
    assert clean_currency_amount(raw) is None


def _frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    bank = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-03", "2024-01-06", "2024-01-20"]),
            "Amount": [1500.0, -250.0, 800.0],
            "Description": ["invoice", "card purchase", "mystery deposit"],
        }
    )
    ledger = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-03", "2024-01-07", "2024-01-28"]),
            "Amount": [1500.0, -250.0, -999.0],
            "Description": ["invoice", "card purchase", "uncleared cheque"],
        }
    )
    return bank, ledger


def test_matches_on_amount_and_date_inside_tolerance():
    bank, ledger = _frames()
    result = reconcile_transactions(
        bank, ledger, "Date", "Amount", "Date", "Amount", 2
    )
    # 1500 matches exactly; -250 matches with a one-day difference.
    assert len(result["matches"]) == 2
    assert {match["amount"] for match in result["matches"]} == {1500.0, -250.0}


def test_the_mismatched_rows_are_not_matched():
    bank, ledger = _frames()
    result = reconcile_transactions(
        bank, ledger, "Date", "Amount", "Date", "Amount", 2
    )
    matched = {match["amount"] for match in result["matches"]}
    assert 800.0 not in matched
    assert -999.0 not in matched
    assert len(result["bank_only"]) == 1
    assert len(result["ledger_only"]) == 1


def test_zero_tolerance_rejects_a_one_day_difference():
    bank, ledger = _frames()
    result = reconcile_transactions(
        bank, ledger, "Date", "Amount", "Date", "Amount", 0
    )
    assert {match["amount"] for match in result["matches"]} == {1500.0}


def test_each_transaction_matches_at_most_once():
    """Two identical ledger rows must not both claim the same bank row."""
    bank = pd.DataFrame(
        {"Date": pd.to_datetime(["2024-01-03"]), "Amount": [100.0], "Note": ["a"]}
    )
    ledger = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-03", "2024-01-03"]),
            "Amount": [100.0, 100.0],
            "Note": ["a", "b"],
        }
    )
    result = reconcile_transactions(bank, ledger, "Date", "Amount", "Date", "Amount", 0)
    assert len(result["matches"]) == 1
    assert len(result["ledger_only"]) == 1


def test_amounts_differing_by_a_cent_do_not_match():
    bank = pd.DataFrame({"Date": pd.to_datetime(["2024-01-03"]), "Amount": [100.0]})
    ledger = pd.DataFrame({"Date": pd.to_datetime(["2024-01-03"]), "Amount": [100.01]})
    result = reconcile_transactions(bank, ledger, "Date", "Amount", "Date", "Amount", 0)
    assert result["matches"] == []
    assert len(result["bank_only"]) == 1
    assert len(result["ledger_only"]) == 1


def test_unmatched_output_drops_the_internal_flag():
    bank, ledger = _frames()
    result = reconcile_transactions(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
    assert "_matched" not in result["bank_only"].columns
    assert "_matched" not in result["ledger_only"].columns


def test_original_frames_are_not_mutated():
    bank, ledger = _frames()
    bank_before = bank.copy()
    ledger_before = ledger.copy()
    reconcile_transactions(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
    pd.testing.assert_frame_equal(bank, bank_before)
    pd.testing.assert_frame_equal(ledger, ledger_before)


def test_summary_reports_duplicates_removed():
    data = b"Date,Amount\n2024-01-03,100\n2024-01-03,100\n2024-01-04,50\n"
    ledger = b"Date,Amount\n2024-01-03,100\n2024-01-04,50\n"
    result = run_reconciliation(data, ledger, "Date", "Amount", "Date", "Amount", 0)
    assert result["summary"]["bank_duplicates_removed"] == 1
    assert result["summary"]["bank_transactions"] == 2


def test_missing_column_raises_key_error_for_the_ui_to_explain(bank_csv, ledger_csv):
    with pytest.raises(KeyError):
        run_reconciliation(
            bank_csv.read_bytes(), ledger_csv.read_bytes(),
            "Date", "Nope", "Date", "Amount", 2,
        )


def test_unparseable_dates_become_unmatched_rather_than_crashing():
    bank = b"Date,Amount\nnot-a-date,100\n"
    ledger = b"Date,Amount\n2024-01-03,100\n"
    result = run_reconciliation(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
    # Nothing matched, and the row is reported instead of silently dropped.
    assert result["summary"]["matched"] == 0
    assert result["summary"]["missing_from_books"] == 1


def test_garbage_amount_is_flagged_not_matched():
    bank = b"Date,Amount\n2024-01-03,abc\n"
    ledger = b"Date,Amount\n2024-01-03,0\n"
    result = run_reconciliation(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
    assert result["summary"]["missing_from_books"] == 1


def test_empty_files_are_handled_without_error():
    header = b"Date,Amount\n"
    result = run_reconciliation(header, header, "Date", "Amount", "Date", "Amount", 2)
    assert result["summary"]["matched"] == 0
    assert result["summary"]["bank_transactions"] == 0