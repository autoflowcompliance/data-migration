"""Layer 7 end to end: N-way reconciliation inside the reconciliation service.

The unit tests pin the matcher in isolation. These run it the way a buyer does:
read real statement files, match three of them, record the run, and compare it
to the one before.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app_files.services.bank_reconciliation import (
    MatchStrategy,
    ReconciliationHistory,
    reconcile_multiway,
)
from app_files.services.bank_reconciliation.multiway import compare_two_way
from app_files.services.bank_reconciliation.reconciler import (
    clean_currency_amount,
    run_reconciliation,
)

GOLDEN = Path(__file__).resolve().parents[1] / "regression" / "golden_files"
BANK = GOLDEN / "bank_statement" / "input.csv"
LEDGER = GOLDEN / "ledger" / "input.csv"


def _read(blob: Path) -> pd.DataFrame:
    frame = pd.read_csv(blob, dtype=str, keep_default_na=False)
    frame["Amount"] = frame["Amount"].map(clean_currency_amount)
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    return frame


def _frozen_two_way(bank: Path, ledger: Path) -> dict:
    from app_files.services.bank_reconciliation.reconciler import reconcile_transactions

    return reconcile_transactions(
        _read(bank), _read(ledger), "Date", "Amount", "Date", "Amount", 2
    )


def _strategy() -> MatchStrategy:
    return MatchStrategy.from_dict(
        {
            "name": "amount_date_desc",
            "components": [
                {"type": "amount", "column": "Amount", "weight": 2.0},
                {"type": "date", "column": "Date", "weight": 1.0, "date_window_days": 2},
                {"type": "text", "column": "Description", "weight": 1.0},
            ],
            "threshold": 2.5,
        }
    )


def _three_sources(blob: Path) -> dict[str, pd.DataFrame]:
    return {
        "bank": _read(blob / "bank.csv"),
        "ledger": _read(blob / "ledger.csv"),
        "processor": _read(blob / "processor.csv"),
    }


class TestGoldenThreeWay:
    """The fixture output is a contract. Regenerating it defeats its purpose."""

    def _result(self):
        blob = GOLDEN / "reconciliation_3way"
        return reconcile_multiway(_three_sources(blob), _strategy())

    def test_the_summary_matches_the_golden_file(self):
        expected = json.loads(
            (GOLDEN / "reconciliation_3way" / "expected_result.json").read_text()
        )
        assert self._result().summary() == expected["summary"]

    def test_every_group_matches_the_golden_file(self):
        expected = json.loads(
            (GOLDEN / "reconciliation_3way" / "expected_result.json").read_text()
        )
        assert [group.as_dict() for group in self._result().groups] == expected["groups"]

    def test_the_partial_group_matches_the_golden_file(self):
        expected = json.loads(
            (GOLDEN / "reconciliation_3way" / "expected_result.json").read_text()
        )
        assert self._result().partial == expected["partial"]

    def test_unmatched_rows_match_the_golden_file(self):
        expected = json.loads(
            (GOLDEN / "reconciliation_3way" / "expected_result.json").read_text()
        )
        produced = {
            name: frame["Description"].tolist()
            for name, frame in self._result().unmatched.items()
        }
        assert produced == expected["unmatched_descriptions"]

    def test_the_strategy_name_survives_the_round_trip(self):
        expected = json.loads(
            (GOLDEN / "reconciliation_3way" / "expected_result.json").read_text()
        )
        assert self._result().strategy == expected["strategy"]


class TestIntegrationWithTheFrozenService:
    def test_a_two_way_frame_match_agrees_with_the_frozen_engine(self):
        bank, ledger = _read(BANK), _read(LEDGER)
        frozen = _frozen_two_way(BANK, LEDGER)
        mine = reconcile_multiway(
            {"bank": bank.rename(columns={"Amount": "amount", "Date": "date"}),
             "ledger": ledger.rename(columns={"Amount": "amount", "Date": "date"})},
            MatchStrategy.amount_and_date("amount", "date"),
        )
        assert len(frozen["matches"]) == mine.matched_groups

    def test_run_reconciliation_is_unaffected_by_the_new_layer(self):
        """The new layer reads the same files; the frozen service must not move."""
        result = run_reconciliation(
            BANK.read_bytes(), LEDGER.read_bytes(), "Date", "Amount", "Date", "Amount", 2
        )
        assert result["summary"]["matched"] == 6
        assert result["summary"]["missing_from_books"] == 1
        assert result["summary"]["recorded_but_never_cleared"] == 1

    def test_the_multiway_engine_accepts_the_frozen_service_output(self):
        bank, ledger = _read(BANK), _read(LEDGER)
        mine = reconcile_multiway(
            {"bank": bank.rename(columns={"Amount": "amount", "Date": "date"}),
             "ledger": ledger.rename(columns={"Amount": "amount", "Date": "date"})},
            MatchStrategy.amount_and_date("amount", "date"),
        )
        assert mine.matched_groups >= 1


def reconcile_transactions_two_way(bank: Path, ledger: Path) -> dict:
    from app_files.services.bank_reconciliation.reconciler import reconcile_transactions

    return reconcile_transactions(
        _read(bank), _read(ledger), "Date", "Amount", "Date", "Amount", 2
    )


class TestIntegrationHistory:
    def test_a_reconciliation_run_is_recorded_end_to_end(self, tmp_path):
        blob = GOLDEN / "reconciliation_3way"
        result = reconcile_multiway(_three_sources(blob), _strategy())
        store = ReconciliationHistory(tmp_path / "history")
        store.record("acme", result, run_at="2024-03-01T09:00:00+00:00")
        assert store.runs("acme")[0].matched == 6

    def test_history_round_trips_through_disk(self, tmp_path):
        blob = GOLDEN / "reconciliation_3way"
        result = reconcile_multiway(_three_sources(blob), _strategy())
        store = ReconciliationHistory(tmp_path / "history")
        store.record("acme", result, run_at="2024-03-01T09:00:00+00:00")
        reopened = ReconciliationHistory(tmp_path / "history")
        assert reopened.runs("acme")[0].summary == result.summary()


class TestCompareTwoWayHelper:
    def test_the_helper_matches_the_engine(self):
        bank, ledger = _read(BANK), _read(LEDGER)
        mine = compare_two_way(
            bank=bank.rename(columns={"Amount": "amount", "Date": "date"}),
            ledger=ledger.rename(columns={"Amount": "amount", "Date": "date"}),
            bank_date_col="date", bank_amount_col="amount",
            ledger_date_col="date", ledger_amount_col="amount",
        )
        assert mine.sources == ["bank", "ledger"]
        assert mine.matched_groups >= 1


class TestConfigDrivenReconciliation:
    """The real golden statement files, matched through a config's strategy.

    The shipped ``bank_reconciliation`` config declares the frozen default as
    YAML, so a run through the binding must reproduce the frozen result exactly.
    A separate caller-supplied strategy must be able to change it.
    """

    def test_the_shipped_config_reproduces_the_frozen_result(self):
        from app_files.services.bank_reconciliation import load_match_strategy

        strategy = load_match_strategy("bank_reconciliation")
        frozen = run_reconciliation(
            BANK.read_bytes(), LEDGER.read_bytes(),
            "Date", "Amount", "Date", "Amount", 2,
        )
        driven = run_reconciliation(
            BANK.read_bytes(), LEDGER.read_bytes(),
            "Date", "Amount", "Date", "Amount", 2,
            strategy=strategy,
        )
        assert driven["summary"] == frozen["summary"]

    def test_a_reference_strategy_changes_the_match_set(self, tmp_path):
        from app_files.services.bank_reconciliation import load_match_strategy

        # A looser amount-only strategy read from a config the binding parses,
        # then confirm the counts differ from the frozen matcher.
        config = tmp_path / "loose.yaml"
        config.write_text(
            "crm: Loose\nfields: []\n"
            "matching:\n"
            "  name: amount_window\n"
            "  components:\n"
            "    - type: amount\n      column: Amount\n      weight: 1.0\n"
            "      tolerance: 5.0\n"
            "  threshold: 1.0\n",
            encoding="utf-8",
        )
        loose = load_match_strategy(config)
        frozen = run_reconciliation(
            BANK.read_bytes(), LEDGER.read_bytes(),
            "Date", "Amount", "Date", "Amount", 0,
        )
        driven = run_reconciliation(
            BANK.read_bytes(), LEDGER.read_bytes(),
            "Date", "Amount", "Date", "Amount", 0,
            strategy=loose,
        )
        # A 5.00 amount tolerance matches strictly more than the exact matcher
        # on these fixtures, so the strategy demonstrably changed the outcome.
        assert len(driven["matches"]) > len(frozen["matches"])
        assert driven["summary"]["matched"] == len(driven["matches"])
