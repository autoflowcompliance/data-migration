"""Layer 7 — N-way reconciliation, configurable match logic, history."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.services.bank_reconciliation import (
    MatchComponent,
    MatchStrategy,
    MatchStrategyError,
    ReconciliationHistory,
    reconcile_multiway,
)
from app_files.services.bank_reconciliation.reconciler import reconcile_transactions

BANK = pd.DataFrame(
    {"date": ["2024-01-01", "2024-01-05", "2024-01-09"], "amount": [100.0, 50.0, 25.0]}
)
LEDGER = pd.DataFrame(
    {"date": ["2024-01-02", "2024-01-06", "2024-01-20"], "amount": [100.0, 50.0, 99.0]}
)
PROCESSOR = pd.DataFrame(
    {"date": ["2024-01-03", "2024-01-07"], "amount": [100.0, 50.0]}
)


@pytest.fixture
def strategy():
    return MatchStrategy.amount_and_date()


@pytest.fixture(autouse=True)
def _home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))


class TestMatchStrategy:
    def test_the_default_is_amount_and_date(self):
        assert [c.type for c in MatchStrategy.amount_and_date().components] == ["amount", "date"]

    def test_the_default_requires_both_components(self):
        assert MatchStrategy.amount_and_date().threshold == 2.0

    def test_a_strategy_round_trips_through_a_dict(self):
        strategy = MatchStrategy.from_dict(
            {"name": "ref", "components": [{"type": "reference", "column": "ref"}],
             "threshold": 1.0}
        )
        assert strategy.as_dict()["components"][0]["type"] == "reference"

    def test_an_unknown_component_type_is_rejected(self):
        with pytest.raises(MatchStrategyError, match="Unknown match component"):
            MatchComponent.from_dict({"type": "vibes", "column": "x"})

    def test_a_component_without_a_column_is_rejected(self):
        with pytest.raises(MatchStrategyError, match="needs a 'column'"):
            MatchComponent.from_dict({"type": "amount"})

    def test_a_non_positive_weight_is_rejected(self):
        with pytest.raises(MatchStrategyError, match="non-positive weight"):
            MatchComponent.from_dict({"type": "amount", "column": "amount", "weight": 0})

    def test_a_duplicated_column_is_rejected(self):
        with pytest.raises(MatchStrategyError, match="cannot use a column twice"):
            MatchStrategy.from_dict(
                {"components": [{"type": "amount", "column": "amount"},
                                {"type": "date", "column": "amount"}]}
            )

    def test_an_empty_component_list_is_rejected(self):
        with pytest.raises(MatchStrategyError, match="non-empty 'components'"):
            MatchStrategy.from_dict({"components": []})

    def test_a_threshold_above_the_total_weight_is_rejected(self):
        with pytest.raises(MatchStrategyError, match="at most the total"):
            MatchStrategy.from_dict(
                {"components": [{"type": "amount", "column": "amount"}], "threshold": 5.0}
            )

    def test_the_threshold_defaults_to_the_total_weight(self):
        strategy = MatchStrategy.from_dict(
            {"components": [{"type": "amount", "column": "amount", "weight": 3.0}]}
        )
        assert strategy.threshold == 3.0

    def test_matching_is_by_weighted_score(self):
        left = pd.Series({"amount": 100.0, "date": "2024-01-01"})
        right = pd.Series({"amount": 100.0, "date": "2024-01-01"})
        score, agreed = MatchStrategy.amount_and_date().score(left, right)
        assert score == 2.0
        assert set(agreed) == {"amount:amount", "date:date"}

    def test_a_date_outside_the_window_does_not_agree(self):
        left = pd.Series({"amount": 100.0, "date": "2024-01-01"})
        right = pd.Series({"amount": 100.0, "date": "2024-01-20"})
        score, agreed = MatchStrategy.amount_and_date().score(left, right)
        assert score == 1.0
        assert agreed == ["amount:amount"]


class TestNWayReconciliation:
    def test_three_sources_match_around_the_anchor(self, strategy):
        result = reconcile_multiway(
            {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR}, strategy
        )
        assert result.matched_groups == 2
        assert result.summary()["sources"] == ["bank", "ledger", "processor"]

    def test_a_group_names_one_row_per_source(self, strategy):
        result = reconcile_multiway(
            {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR}, strategy
        )
        assert set(result.groups[0].rows) == {"bank", "ledger", "processor"}

    def test_each_source_reports_its_own_unmatched_rows(self, strategy):
        result = reconcile_multiway(
            {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR}, strategy
        )
        counts = result.unmatched_counts()
        assert counts["bank"] == 1
        assert counts["ledger"] == 1
        assert counts["processor"] == 0

    def test_a_row_matching_some_sources_but_not_all_is_partial(self, strategy):
        bank = pd.DataFrame({"date": ["2024-01-01", "2024-01-05"], "amount": [100.0, 50.0]})
        ledger = pd.DataFrame({"date": ["2024-01-02", "2024-01-06"], "amount": [100.0, 50.0]})
        processor = pd.DataFrame({"date": ["2024-01-03"], "amount": [100.0]})
        result = reconcile_multiway(
            {"bank": bank, "ledger": ledger, "processor": processor}, strategy
        )
        assert result.matched_groups == 1
        assert len(result.partial) == 1
        assert result.partial[0]["missing_sources"] == ["processor"]

    def test_a_partial_row_stays_in_the_unmatched_frame(self, strategy):
        bank = pd.DataFrame({"date": ["2024-01-01", "2024-01-05"], "amount": [100.0, 50.0]})
        ledger = pd.DataFrame({"date": ["2024-01-02", "2024-01-06"], "amount": [100.0, 50.0]})
        processor = pd.DataFrame({"date": ["2024-01-03"], "amount": [100.0]})
        result = reconcile_multiway(
            {"bank": bank, "ledger": ledger, "processor": processor}, strategy
        )
        assert result.unmatched_counts()["bank"] == 1
        assert result.unmatched_counts()["ledger"] == 1

    def test_no_rows_cross_between_groups(self, strategy):
        result = reconcile_multiway(
            {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR}, strategy
        )
        for name in result.sources:
            used = [group.rows[name] for group in result.groups]
            assert len(used) == len(set(used))

    def test_a_clean_three_way_reconciles_completely(self, strategy):
        same = pd.DataFrame({"date": ["2024-01-01"], "amount": [100.0]})
        result = reconcile_multiway({"a": same, "b": same, "c": same}, strategy)
        assert result.matched_groups == 1
        assert all(count == 0 for count in result.unmatched_counts().values())

    def test_fewer_than_two_sources_is_an_error(self, strategy):
        with pytest.raises(ValueError, match="at least two sources"):
            reconcile_multiway({"only": BANK}, strategy)

    def test_the_strategy_name_is_recorded(self, strategy):
        result = reconcile_multiway({"a": BANK, "b": LEDGER}, strategy)
        assert result.summary()["strategy"] == "amount_and_date"

    def test_render_lists_unmatched_per_source(self, strategy):
        text = reconcile_multiway(
            {"bank": BANK, "ledger": LEDGER, "processor": PROCESSOR}, strategy
        ).render()
        assert "bank: 1" in text
        assert "ledger: 1" in text


class TestAgreementWithTheFrozenMatcher:
    """The two-source case must reproduce the existing engine, not approximate it."""

    def test_matched_counts_agree(self, strategy):
        frozen = reconcile_transactions(BANK, LEDGER, "date", "amount", "date", "amount", 2)
        mine = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        assert len(frozen["matches"]) == mine.matched_groups

    def test_bank_only_agrees(self, strategy):
        frozen = reconcile_transactions(BANK, LEDGER, "date", "amount", "date", "amount", 2)
        mine = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        assert len(frozen["bank_only"]) == mine.unmatched_counts()["bank"]

    def test_ledger_only_agrees(self, strategy):
        frozen = reconcile_transactions(BANK, LEDGER, "date", "amount", "date", "amount", 2)
        mine = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        assert len(frozen["ledger_only"]) == mine.unmatched_counts()["ledger"]

    def test_the_date_window_agrees(self):
        bank = pd.DataFrame({"date": ["2024-01-01"], "amount": [100.0]})
        ledger = pd.DataFrame({"date": ["2024-01-05"], "amount": [100.0]})
        frozen = reconcile_transactions(bank, ledger, "date", "amount", "date", "amount", 2)
        tight = reconcile_multiway(
            {"bank": bank, "ledger": ledger}, MatchStrategy.amount_and_date(date_window_days=2)
        )
        wide = reconcile_multiway(
            {"bank": bank, "ledger": ledger}, MatchStrategy.amount_and_date(date_window_days=4)
        )
        assert len(frozen["matches"]) == tight.matched_groups == 0
        assert wide.matched_groups == 1


class TestConfigurableMatchLogic:
    def test_a_reference_strategy_matches_on_reference(self):
        feed = pd.DataFrame({"ref": ["A1", "A2"], "amount": [100.0, 50.0]})
        ledger = pd.DataFrame({"ref": ["A1", "A2"], "amount": [999.0, 50.0]})
        strategy = MatchStrategy.from_dict(
            {"name": "reference", "components": [
                {"type": "reference", "column": "ref", "weight": 1.0},
                {"type": "amount", "column": "amount", "weight": 1.0},
            ], "threshold": 1.0}
        )
        assert reconcile_multiway({"feed": feed, "ledger": ledger}, strategy).matched_groups == 2

    def test_a_tighter_strategy_matches_fewer(self):
        feed = pd.DataFrame({"ref": ["A1", "A2"], "amount": [100.0, 50.0]})
        ledger = pd.DataFrame({"ref": ["A1", "A2"], "amount": [999.0, 50.0]})
        amount_only = MatchStrategy.from_dict(
            {"name": "amount_only", "components": [{"type": "amount", "column": "amount"}],
             "threshold": 1.0}
        )
        assert reconcile_multiway({"feed": feed, "ledger": ledger}, amount_only).matched_groups == 1

    def test_two_strategies_produce_different_match_sets_on_one_input(self):
        feed = pd.DataFrame({"ref": ["A1", "A2"], "amount": [100.0, 50.0]})
        ledger = pd.DataFrame({"ref": ["A1", "A2"], "amount": [999.0, 50.0]})
        loose = MatchStrategy.from_dict(
            {"name": "loose", "components": [
                {"type": "reference", "column": "ref"},
                {"type": "amount", "column": "amount"},
            ], "threshold": 1.0}
        )
        tight = MatchStrategy.from_dict(
            {"name": "tight", "components": [
                {"type": "reference", "column": "ref"},
                {"type": "amount", "column": "amount"},
            ], "threshold": 2.0}
        )
        loose_groups = reconcile_multiway({"feed": feed, "ledger": ledger}, loose).matched_groups
        tight_groups = reconcile_multiway({"feed": feed, "ledger": ledger}, tight).matched_groups
        assert loose_groups > tight_groups

    def test_weighted_amount_survives_a_different_reference(self):
        # A weight of 2 on the amount lets it match even when the reference differs.
        feed = pd.DataFrame({"ref": ["A1"], "amount": [100.0]})
        ledger = pd.DataFrame({"ref": ["B9"], "amount": [100.0]})
        strategy = MatchStrategy.from_dict(
            {"name": "amount_heavy", "components": [
                {"type": "amount", "column": "amount", "weight": 2.0},
                {"type": "reference", "column": "ref", "weight": 1.0},
            ], "threshold": 2.0}
        )
        assert reconcile_multiway({"feed": feed, "ledger": ledger}, strategy).matched_groups == 1

    def test_a_text_component_matches_case_insensitively(self):
        feed = pd.DataFrame({"vendor": ["Acme Ltd"]})
        ledger = pd.DataFrame({"vendor": ["ACME LTD"]})
        strategy = MatchStrategy.from_dict(
            {"name": "vendor", "components": [{"type": "text", "column": "vendor"}],
             "threshold": 1.0}
        )
        assert reconcile_multiway({"feed": feed, "ledger": ledger}, strategy).matched_groups == 1

    def test_a_blank_reference_does_not_match_another_blank(self):
        feed = pd.DataFrame({"ref": ["", "A1"]})
        ledger = pd.DataFrame({"ref": ["", "A1"]})
        strategy = MatchStrategy.from_dict(
            {"name": "ref", "components": [{"type": "reference", "column": "ref"}],
             "threshold": 1.0}
        )
        # Only A1 matches; the two blanks must not pair up.
        assert reconcile_multiway({"feed": feed, "ledger": ledger}, strategy).matched_groups == 1

    def test_a_currency_formatted_amount_is_understood(self):
        feed = pd.DataFrame({"amount": ["$1,200.50"]})
        ledger = pd.DataFrame({"amount": [1200.5]})
        strategy = MatchStrategy.from_dict(
            {"name": "amount", "components": [{"type": "amount", "column": "amount"}],
             "threshold": 1.0}
        )
        assert reconcile_multiway({"feed": feed, "ledger": ledger}, strategy).matched_groups == 1


class TestReconciliationHistory:
    def test_a_run_is_recorded(self, strategy):
        store = ReconciliationHistory()
        result = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        store.record("acme", result, run_at="2024-01-15T00:00:00+00:00")
        assert len(store.runs("acme")) == 1

    def test_history_is_empty_for_an_unknown_name(self):
        assert ReconciliationHistory().runs("nobody") == []

    def test_runs_survive_a_reopened_store(self, strategy):
        store = ReconciliationHistory()
        result = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        store.record("acme", result, run_at="2024-01-15T00:00:00+00:00")
        assert len(ReconciliationHistory(store.root).runs("acme")) == 1

    def test_months_are_compared(self, strategy):
        store = ReconciliationHistory()
        result = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        store.record("acme", result, run_at="2024-01-15T00:00:00+00:00")
        store.record("acme", result, run_at="2024-02-15T00:00:00+00:00")
        report = store.compare_months("acme")
        assert [month["month"] for month in report["months"]] == ["2024-01", "2024-02"]
        assert report["deltas"][0]["matched_delta"] == 0

    def test_a_decline_shows_as_a_negative_delta(self, strategy):
        store = ReconciliationHistory()
        good = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        degraded = reconcile_multiway(
            {"bank": pd.DataFrame({"date": ["2024-01-01"], "amount": [1.0]}),
             "ledger": LEDGER},
            strategy,
        )
        store.record("acme", good, run_at="2024-01-15T00:00:00+00:00")
        store.record("acme", degraded, run_at="2024-02-15T00:00:00+00:00")
        delta = store.compare_months("acme")["deltas"][0]
        assert delta["matched_delta"] == -2

    def test_render_trend_lists_each_month(self, strategy):
        store = ReconciliationHistory()
        result = reconcile_multiway({"bank": BANK, "ledger": LEDGER}, strategy)
        store.record("acme", result, run_at="2024-01-15T00:00:00+00:00")
        assert "2024-01" in store.render_trend("acme")
