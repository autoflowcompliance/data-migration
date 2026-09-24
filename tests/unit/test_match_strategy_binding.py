"""A config's ``matching:`` block drives a reconciliation.

``MatchStrategy`` was complete and had no caller outside the tests, so tuning
match logic meant editing Python. These tests hold the YAML path to the same
behaviour as the frozen matcher and prove a strategy actually changes a result.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.cli import main
from app_files.services.bank_reconciliation import (
    MatchStrategy,
    reconcile_multiway,
    reconcile_transactions,
)
from app_files.services.bank_reconciliation.binding import (
    MatchStrategyConfigError,
    describe_match_strategy,
    load_match_strategy,
)
from app_files.services.bank_reconciliation.reconciler import (
    reconcile_transactions_with_strategy,
)

FROZEN = Path(__file__).resolve().parent.parent / "regression" / "golden_files" / "reconciliation"


def _frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    bank = pd.DataFrame(
        {
            "Date": ["2026-01-01", "2026-01-05"],
            "Amount": ["100.00", "50.00"],
        }
    )
    ledger = pd.DataFrame(
        {
            "Date": ["2026-01-02", "2026-01-05", "2026-01-09"],
            "Amount": ["100.00", "50.00", "9.99"],
        }
    )
    return bank, ledger


class TestYamlStrategy:
    def test_a_config_with_no_block_gets_none(self, tmp_path):
        config = tmp_path / "plain.yaml"
        config.write_text("crm: Plain\nfields: []\n", encoding="utf-8")
        assert load_match_strategy(config) is None

    def test_the_shipped_config_declares_the_frozen_default(self):
        strategy = load_match_strategy("bank_reconciliation")
        assert strategy is not None
        assert strategy.name == "amount_and_date"
        assert strategy.threshold == 2.0

    def test_a_malformed_block_is_rejected_loudly(self, tmp_path):
        config = tmp_path / "bad.yaml"
        config.write_text(
            "crm: Bad\nfields: []\nmatching:\n  components:\n    - type: wizard\n      column: X\n",
            encoding="utf-8",
        )
        with pytest.raises(MatchStrategyConfigError):
            load_match_strategy(config)

    def test_a_non_mapping_block_is_rejected(self, tmp_path):
        config = tmp_path / "bad.yaml"
        config.write_text("crm: Bad\nfields: []\nmatching: [one, two]\n", encoding="utf-8")
        with pytest.raises(MatchStrategyConfigError):
            load_match_strategy(config)

    def test_an_unknown_config_names_the_known_ones(self):
        with pytest.raises(FileNotFoundError):
            load_match_strategy("no_such_config_anywhere")

    def test_describe_covers_both_cases(self):
        assert describe_match_strategy(None) == "amount_and_date (frozen default)"
        strategy = MatchStrategy.amount_and_date("Amount", "Date", 2)
        described = describe_match_strategy(strategy)
        assert "amount:Amount" in described and "date:Date" in described

    def test_the_yaml_strategy_matches_the_frozen_matcher(self):
        """The shipped block must not change any existing reconciliation."""
        strategy = load_match_strategy("bank_reconciliation")
        bank, ledger = _frames()
        frozen = reconcile_transactions(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
        driven = reconcile_transactions_with_strategy(
            bank, ledger, strategy=strategy
        )
        assert len(driven["matches"]) == len(frozen["matches"])
        assert len(driven["bank_only"]) == len(frozen["bank_only"])
        assert len(driven["ledger_only"]) == len(frozen["ledger_only"])


class TestStrategyChangesTheResult:
    def test_a_reference_strategy_matches_what_amount_date_rejects(self, tmp_path):
        config = tmp_path / "ref.yaml"
        config.write_text(
            "crm: Ref\nfields: []\n"
            "matching:\n"
            "  name: reference_only\n"
            "  components:\n"
            "    - type: reference\n      column: Reference\n      weight: 1.0\n"
            "  threshold: 1.0\n",
            encoding="utf-8",
        )
        strategy = load_match_strategy(config)
        assert strategy is not None

        bank = pd.DataFrame({"Reference": ["R1"], "Amount": ["100"], "Date": ["2026-01-01"]})
        ledger = pd.DataFrame(
            {"Reference": ["R1"], "Amount": ["999"], "Date": ["2026-12-01"]}
        )
        # Frozen default: different amount and date, so no match.
        frozen = reconcile_transactions(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
        assert frozen["matches"] == []
        # Reference strategy: the reference alone carries the match.
        driven = reconcile_transactions_with_strategy(bank, ledger, strategy=strategy)
        assert len(driven["matches"]) == 1

    def test_a_weighted_threshold_is_honoured(self):
        rows = pd.DataFrame(
            {
                "amount": ["100.00"],
                "date": ["2026-01-01"],
                "reference": ["R1"],
            }
        )
        other = pd.DataFrame(
            {
                "amount": ["100.00"],
                "date": ["2026-09-01"],
                "reference": ["R9"],
            }
        )
        # Amount alone is weight 2; threshold 2 matches on the amount despite
        # the date and reference both differing.
        amount_only = MatchStrategy.from_dict(
            {
                "name": "amount_only",
                "components": [{"type": "amount", "column": "amount", "weight": 2.0}],
                "threshold": 2.0,
            }
        )
        result = reconcile_multiway({"a": rows, "b": other}, amount_only)
        assert result.matched_groups == 1


class TestReconcileCli:
    def test_the_cli_runs_and_writes_outputs(self, tmp_path, capsys):
        statement = tmp_path / "statement.csv"
        statement.write_text(
            "Date,Description,Amount\n2026-01-01,ACME,100.00\n", encoding="utf-8"
        )
        ledger = tmp_path / "ledger.csv"
        ledger.write_text(
            "Date,Description,Amount\n2026-01-02,ACME,100.00\n2026-01-09,GHOST,9.99\n",
            encoding="utf-8",
        )
        outdir = tmp_path / "out"
        code = main(
            [
                "reconcile",
                "--statement", str(statement),
                "--ledger", str(ledger),
                "-o", str(outdir),
            ]
        )
        assert code == 0
        assert (outdir / "matched.csv").exists()
        assert (outdir / "recorded_but_never_cleared.csv").exists()
        captured = capsys.readouterr().out
        assert "1 matched" in captured

    def test_a_bad_matching_block_exits_non_zero(self, tmp_path, capsys):
        statement = tmp_path / "s.csv"
        statement.write_text("Date,Amount\n2026-01-01,1.00\n", encoding="utf-8")
        ledger = tmp_path / "l.csv"
        ledger.write_text("Date,Amount\n2026-01-01,1.00\n", encoding="utf-8")
        config = tmp_path / "bad.yaml"
        config.write_text(
            "crm: Bad\nfields: []\nmatching: not-a-mapping\n", encoding="utf-8"
        )
        code = main(
            [
                "reconcile",
                "--statement", str(statement),
                "--ledger", str(ledger),
                "-c", str(config),
                "-o", str(tmp_path / "out"),
            ]
        )
        assert code == 2
        assert "Invalid matching configuration" in capsys.readouterr().err
