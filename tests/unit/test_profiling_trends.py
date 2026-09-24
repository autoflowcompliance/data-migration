"""Quality trend tracking and baseline comparison."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.profiling import (
    TrendStore,
    compare_to_baseline,
    compare_to_stored_baseline,
    profile,
    trend_direction,
)


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return TrendStore(path=tmp_path / "trends" / "quality.db")


def clean_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
            "name": ["A", "B", "C", "D"],
            "amount": [1.0, 2.0, 3.0, 4.0],
        }
    )


def degraded_frame() -> pd.DataFrame:
    frame = clean_frame()
    frame.loc[0:2, "amount"] = None
    return frame


class TestTrendStore:
    def test_record_returns_an_id(self, store):
        first = store.record("src", profile(clean_frame()))
        second = store.record("src", profile(clean_frame()))
        assert second > first

    def test_trend_is_oldest_first(self, store):
        store.record("src", profile(degraded_frame()))
        store.record("src", profile(clean_frame()))
        points = store.trend("src")
        assert [round(p.overall, 1) for p in points] == [91.7, 100.0]

    def test_recent_is_newest_first(self, store):
        store.record("src", profile(degraded_frame()))
        store.record("src", profile(clean_frame()))
        assert round(store.recent("src", limit=1)[0].overall, 1) == 100.0

    def test_sources_are_separated(self, store):
        store.record("a", profile(clean_frame()))
        store.record("b", profile(clean_frame()))
        assert store.sources() == ["a", "b"]
        assert len(store.trend("a")) == 1

    def test_dimensions_are_stored(self, store):
        store.record("src", profile(clean_frame()))
        point = store.latest("src")
        assert point is not None
        assert set(point.dimensions) == {
            "completeness", "validity", "uniqueness", "consistency", "timeliness",
        }

    def test_latest_is_none_for_unknown_source(self, store):
        assert store.latest("never-seen") is None

    def test_clear_one_source(self, store):
        store.record("a", profile(clean_frame()))
        store.record("b", profile(clean_frame()))
        assert store.clear("a") == 1
        assert store.sources() == ["b"]

    def test_clear_all(self, store):
        store.record("a", profile(clean_frame()))
        store.record("b", profile(clean_frame()))
        assert store.clear() == 2
        assert store.sources() == []

    def test_history_survives_a_new_store_instance(self, store, tmp_path):
        store.record("src", profile(clean_frame()))
        reopened = TrendStore(path=tmp_path / "trends" / "quality.db")
        assert len(reopened.trend("src")) == 1

    def test_records_under_autoflow_home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        from app_files.profiling.trends import trend_db_path

        assert str(tmp_path) in str(trend_db_path())


class TestTrendDirection:
    def test_declining(self, store):
        scores = [profile(clean_frame()), profile(clean_frame()),
                  profile(degraded_frame()), profile(degraded_frame())]
        for score in scores:
            store.record("src", score)
        assert trend_direction(store.trend("src")) == "declining"

    def test_improving(self, store):
        scores = [profile(degraded_frame()), profile(degraded_frame()),
                  profile(clean_frame()), profile(clean_frame())]
        for score in scores:
            store.record("src", score)
        assert trend_direction(store.trend("src")) == "improving"

    def test_stable_with_one_run(self, store):
        store.record("src", profile(clean_frame()))
        assert trend_direction(store.trend("src")) == "stable"

    def test_stable_when_flat(self, store):
        for _ in range(4):
            store.record("src", profile(clean_frame()))
        assert trend_direction(store.trend("src")) == "stable"


class TestBaseline:
    def test_comparison_flags_the_regression(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        comparison = compare_to_stored_baseline("src", profile(degraded_frame()), store)
        assert comparison is not None
        assert comparison.alerting
        assert "completeness" in comparison.regressed_dimensions

    def test_no_alert_within_threshold(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        comparison = compare_to_stored_baseline("src", profile(clean_frame()), store)
        assert comparison is not None
        assert not comparison.alerting

    def test_overall_delta_is_reported(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        comparison = compare_to_baseline(
            profile(degraded_frame()), store.baseline("src"), source="src"
        )
        assert comparison.overall_delta < 0

    def test_comparison_is_none_without_a_baseline(self, store):
        assert compare_to_stored_baseline("src", profile(clean_frame()), store) is None

    def test_threshold_is_respected(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        comparison = compare_to_baseline(
            profile(degraded_frame()), store.baseline("src"), source="src", threshold=100.0
        )
        # A 100-point threshold cannot be breached by any drop below it.
        assert not comparison.alerting

    def test_baseline_can_be_re_pinned(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        store.set_baseline("src", store.record("src", profile(degraded_frame())))
        baseline = store.baseline("src")
        assert baseline is not None
        assert round(baseline.overall, 1) == 91.7

    def test_render_html_warns_on_regression(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        html = compare_to_stored_baseline(
            "src", profile(degraded_frame()), store
        ).render_html()
        assert "Regression" in html

    def test_render_html_is_quiet_when_within_baseline(self, store):
        store.set_baseline("src", store.record("src", profile(clean_frame())))
        html = compare_to_stored_baseline(
            "src", profile(clean_frame()), store
        ).render_html()
        assert "Within baseline" in html


class TestDimensionAnomalies:
    def _many_rows(self, blanks: int = 0) -> pd.DataFrame:
        size = 40
        frame = pd.DataFrame(
            {
                "email": [f"u{i}@x.com" for i in range(size)],
                "name": [f"N{i}" for i in range(size)],
                "amount": [float(i) for i in range(size)],
            }
        )
        if blanks:
            frame.loc[0 : blanks - 1, "amount"] = None
        return frame

    def _seed_history(self, store, blank_counts):
        for blanks in blank_counts:
            store.record("crm", profile(self._many_rows(blanks)))

    def test_learning_until_enough_runs(self, store):
        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0])
        report = detect_dimension_anomalies("crm", profile(self._many_rows()), store)
        assert report.learning
        assert report.clean
        assert "LEARNING" in report.status

    def test_flags_a_crash_in_completeness(self, store):
        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0, 1, 0, 1, 1])
        report = detect_dimension_anomalies("crm", profile(self._many_rows(30)), store)
        assert not report.learning
        assert [anomaly.dimension for anomaly in report.anomalies] == ["completeness"]
        assert report.anomalies[0].direction == "below"

    def test_no_anomaly_for_a_normal_run(self, store):
        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0, 1, 0, 1, 1])
        report = detect_dimension_anomalies("crm", profile(self._many_rows(1)), store)
        assert report.clean
        assert "OK" in report.status

    def test_ranges_are_bounded_to_zero_and_hundred(self, store):
        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0, 1, 0, 1, 1])
        report = detect_dimension_anomalies("crm", profile(self._many_rows()), store)
        for rng in report.ranges.values():
            assert 0.0 <= rng.low <= rng.high <= 100.0

    def test_stable_source_does_not_flag_a_one_point_wobble(self, store):
        """The MIN_STDDEV floor stops a flat source flagging trivial drift."""
        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0, 0, 0, 0, 0])
        report = detect_dimension_anomalies("crm", profile(self._many_rows(1)), store)
        assert report.clean

    def test_summary_is_json_safe(self, store):
        import json

        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0, 1, 0, 1, 1])
        report = detect_dimension_anomalies("crm", profile(self._many_rows(30)), store)
        json.dumps(report.summary())

    def test_render_html_alerts(self, store):
        from app_files.profiling import detect_dimension_anomalies

        self._seed_history(store, [0, 0, 1, 0, 1, 1])
        html = detect_dimension_anomalies(
            "crm", profile(self._many_rows(30)), store
        ).render_html()
        assert "alert" in html
        assert "completeness" in html

    def test_learn_ranges_computes_mean_and_bounds(self, store):
        from app_files.profiling import learn_ranges

        self._seed_history(store, [0, 0, 0, 0, 0])
        ranges = learn_ranges(store.recent("crm"))
        assert "completeness" in ranges
        assert ranges["completeness"].mean == pytest.approx(100.0)
        assert ranges["completeness"].samples == 5
