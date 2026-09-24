"""N-way reconciliation and reconciliation history."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.services.bank_reconciliation import (
    MultiReconciliationError,
    compare_reconciliations,
    read_history,
    reconcile_many,
    record_reconciliation,
)


def _statement(rows):
    return pd.DataFrame(rows, columns=["Date", "Amount"])


BANK = _statement(
    [
        ("2026-01-01", "100.00"),
        ("2026-01-02", "250.00"),
        ("2026-01-03", "75.50"),
        ("2026-01-04", "10.00"),
    ]
)
LEDGER = _statement(
    [
        ("2026-01-01", "100.00"),
        ("2026-01-02", "250.00"),
        ("2026-01-05", "75.50"),  # 2 days late but within tolerance
    ]
)
PROCESSOR = _statement(
    [
        ("2026-01-01", "100.00"),
        ("2026-01-02", "250.00"),
    ]
)


def test_three_way_reconciliation_classifies_by_membership():
    result = reconcile_many(
        {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR},
        date_col="Date",
        amount_col="Amount",
    )
    # 100.00 and 250.00 are in all three.
    assert result.summary()["matched_everywhere"] == 2
    # 75.50 is in bank and ledger but not the processor: partial, and named.
    partial = [p for p in result.partial if p["amount"] == 75.5]
    assert len(partial) == 1
    assert partial[0]["present_in"] == ["bank", "ledger"]
    assert partial[0]["missing_from"] == ["processor"]


def test_transactions_unique_to_one_source_are_listed_separately():
    result = reconcile_many(
        {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR},
        date_col="Date",
        amount_col="Amount",
    )
    amounts = [row["amount"] for row in result.unique_to["bank"]]
    assert 10.0 in amounts
    assert result.unique_to["processor"] == []


def test_two_sources_still_work():
    result = reconcile_many(
        {"bank": BANK, "ledger": LEDGER}, date_col="Date", amount_col="Amount"
    )
    assert result.summary()["sources"] == ["bank", "ledger"]
    # Every bank row finds a counterpart: 100, 250, and 75.50 within tolerance.
    assert result.summary()["matched_everywhere"] == 3
    assert result.summary()["unique"]["bank"] == 1  # 10.00 has no counterpart


def test_one_source_is_rejected():
    with pytest.raises(MultiReconciliationError, match="at least 2"):
        reconcile_many({"bank": BANK}, date_col="Date", amount_col="Amount")


def test_missing_column_is_rejected_with_the_source_named():
    processor = pd.DataFrame({"Amount": ["100.00"]})  # no Date column
    with pytest.raises(MultiReconciliationError, match="processor"):
        reconcile_many(
            {"bank": BANK, "processor": processor},
            date_col="Date",
            amount_col="Amount",
        )


def test_unparseable_rows_are_counted_not_dropped():
    messy = _statement(
        [("2026-01-01", "100.00"), ("not-a-date", "50.00"), ("2026-01-02", "oops")]
    )
    result = reconcile_many(
        {"bank": BANK, "messy": messy}, date_col="Date", amount_col="Amount"
    )
    assert result.summary()["unreadable"]["messy"] == 2


def test_tolerance_is_respected():
    strict = reconcile_many(
        {"bank": BANK, "ledger": LEDGER},
        date_col="Date",
        amount_col="Amount",
        date_tolerance_days=0,
    )
    # 75.50 is 2 days apart, so with no tolerance it is unique to each side.
    assert [row["amount"] for row in strict.unique_to["bank"]].count(75.5) == 1
    assert [row["amount"] for row in strict.unique_to["ledger"]].count(75.5) == 1

    loose = reconcile_many(
        {"bank": BANK, "ledger": LEDGER},
        date_col="Date",
        amount_col="Amount",
        date_tolerance_days=2,
    )
    # With the default tolerance it matches across both sources.
    assert any(entry["amount"] == 75.5 for entry in loose.matched_everywhere)


# ------------------------------------------------------------------- history
def test_history_records_each_run(tmp_path):
    path = tmp_path / "history.jsonl"
    record_reconciliation({"matched": 3, "missing_from_books": 1}, label="jan", path=path)
    record_reconciliation({"matched": 4, "missing_from_books": 0}, label="feb", path=path)
    entries = read_history(path)
    assert [e["label"] for e in entries] == ["jan", "feb"]
    assert entries[0]["summary"]["matched"] == 3


def test_comparing_runs_reports_direction():
    before = {"matched": 3, "missing_from_books": 2, "recorded_but_never_cleared": 1}
    after = {"matched": 5, "missing_from_books": 0, "recorded_but_never_cleared": 1}
    comparison = compare_reconciliations(before, after)
    assert comparison["direction"] == "improving"
    assert comparison["changes"]["matched"]["delta"] == 2
    assert comparison["changes"]["missing_from_books"]["delta"] == -2


def test_history_honours_autoflow_home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    record_reconciliation({"matched": 1})
    assert (tmp_path / "reconciliation_history" / "history.jsonl").exists()


def test_empty_history_is_an_empty_list(tmp_path):
    assert read_history(tmp_path / "nothing.jsonl") == []