"""The binding that gives Layer 5's history a caller (see profiling/binding.py).

Exercised in isolation against a real SQLite store under a temporary
``AUTOFLOW_HOME``: the point of these tests is that the *store* is the real one,
so "recorded" means a row exists and reads back, not that a stub was called.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.profiling import TrendStore, profile
from app_files.profiling.binding import pin_baseline, record_quality, source_key

GOOD = pd.DataFrame(
    {
        "email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
        "name": ["Ann", "Ben", "Cal", "Dee"],
    }
)
DEGRADED = pd.DataFrame({"email": ["a@x.com", None], "name": [None, None]})


@pytest.fixture
def home(tmp_path, monkeypatch):
    state = tmp_path / "state"
    monkeypatch.setenv("AUTOFLOW_HOME", str(state))
    return state


class TestSourceKey:
    def test_a_bare_name_is_its_own_key(self):
        assert source_key("contacts.csv") == "contacts"

    def test_a_path_is_reduced_to_the_stem(self):
        assert source_key("/data/2024/contacts.csv") == "contacts"

    def test_a_path_object_works(self, tmp_path):
        assert source_key(tmp_path / "june.xlsx") == "june"

    def test_an_extensionless_name_is_kept(self):
        assert source_key("contacts") == "contacts"


class TestRecordQuality:
    def test_a_run_is_written_and_read_back(self, home):
        history = record_quality("contacts.csv", profile(GOOD))
        assert history.run_id > 0
        assert history.recorded.overall == pytest.approx(profile(GOOD).overall)
        assert len(TrendStore().trend("contacts")) == 1

    def test_the_recorded_point_is_part_of_the_history(self, home):
        history = record_quality("contacts.csv", profile(GOOD))
        assert history.history[-1].id == history.run_id

    def test_no_baseline_yet_means_no_comparison(self, home):
        history = record_quality("contacts.csv", profile(GOOD))
        assert history.comparison is None
        assert history.alerting is False

    def test_repeated_runs_accumulate(self, home):
        for _ in range(4):
            record_quality("contacts.csv", profile(GOOD))
        assert len(TrendStore().trend("contacts")) == 4

    def test_sources_do_not_share_history(self, home):
        record_quality("a.csv", profile(GOOD))
        record_quality("b.csv", profile(GOOD))
        store = TrendStore()
        assert len(store.trend("a")) == 1
        assert len(store.trend("b")) == 1

    def test_the_summary_reports_the_trend_and_score(self, home):
        record_quality("contacts.csv", profile(GOOD))
        summary = record_quality("contacts.csv", profile(GOOD)).summary()
        assert summary["source"] == "contacts"
        assert summary["runs_recorded"] == 2
        assert summary["baseline_set"] is False

    def test_a_drop_is_flagged_once_a_baseline_exists(self, home):
        record_quality("contacts.csv", profile(GOOD))
        pin_baseline("contacts.csv", profile(GOOD))
        history = record_quality("contacts.csv", profile(DEGRADED))
        assert history.comparison is not None
        assert history.alerting is True
        assert history.comparison.overall_delta < 0


class TestPinBaseline:
    def test_the_run_is_recorded_and_pinned(self, home):
        point = pin_baseline("contacts.csv", profile(GOOD))
        store = TrendStore()
        assert store.baseline("contacts") is not None
        assert store.baseline("contacts").id == point.id
        assert len(store.trend("contacts")) == 1

    def test_re_pinning_replaces_the_baseline(self, home):
        first = pin_baseline("contacts.csv", profile(GOOD))
        second = pin_baseline("contacts.csv", profile(DEGRADED))
        assert TrendStore().baseline("contacts").id == second.id
        assert second.id != first.id

    def test_pinning_twice_keeps_both_runs_in_the_history(self, home):
        pin_baseline("contacts.csv", profile(GOOD))
        pin_baseline("contacts.csv", profile(GOOD))
        assert len(TrendStore().trend("contacts")) == 2


class TestAnomalyDetection:
    def test_a_source_with_little_history_is_still_learning(self, home):
        history = record_quality("contacts.csv", profile(GOOD))
        assert history.anomaly is not None
        assert history.anomaly.learning is True
        assert history.anomalous is False

    def test_enough_history_learns_a_range(self, home):
        for _ in range(5):
            record_quality("contacts.csv", profile(GOOD))
        history = record_quality("contacts.csv", profile(GOOD))
        assert history.anomaly.learning is False
        assert history.anomalous is False

    def test_a_run_outside_the_learned_range_is_an_anomaly(self, home):
        for _ in range(5):
            record_quality("contacts.csv", profile(GOOD))
        history = record_quality("contacts.csv", profile(DEGRADED))
        assert history.anomalous is True
        assert "completeness" in [item.dimension for item in history.anomaly.anomalies]

    def test_the_anomaly_does_not_use_the_current_run_as_a_sample(self, home):
        """The range is learned before this run is recorded, so a single wild
        run cannot widen the range that would judge it."""
        for _ in range(5):
            record_quality("contacts.csv", profile(GOOD))
        history = record_quality("contacts.csv", profile(DEGRADED))
        assert history.anomaly.samples == 5
        assert history.anomalous is True

    def test_the_summary_lists_the_anomalous_dimensions(self, home):
        for _ in range(5):
            record_quality("contacts.csv", profile(GOOD))
        summary = record_quality("contacts.csv", profile(DEGRADED)).summary()
        assert "completeness" in summary["anomalies"]


class TestInjectedStore:
    def test_an_explicit_store_is_used(self, home, tmp_path):
        store = TrendStore(path=tmp_path / "elsewhere.db")
        record_quality("contacts.csv", profile(GOOD), store=store)
        assert store.path.is_file()
        assert len(store.trend("contacts")) == 1

    def test_the_default_store_honours_autoflow_home(self, home):
        record_quality("contacts.csv", profile(GOOD))
        assert (home / "trends" / "quality.db").is_file()
