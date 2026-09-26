"""Module 10 — Data Quality Scoring: SLA enforcement and regression action.

Most of Module 10 already existed: ``profiling/dimensions.py`` computes the five
dimensions, ``trends.py`` stores them, ``baseline.py`` compares a run to a
pinned baseline. What was missing is the part that makes a score *act*:

* an **SLA** — a floor per dimension that a run must meet, which the spec asks
  for as ``quality.sla.completeness: 0.98``;
* a **regression action** — the spec's ``alert | block | quarantine``, where
  today ``compare_to_baseline`` only knows how to say "this regressed".

Both are additive: they read the existing ``Profile`` and
``BaselineComparison`` and write nothing the pipeline sees. These tests are
written against the interface before the implementation, and every one of them
is a behaviour the old code could not express.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.profiling.profiler import profile
from app_files.quality import (
    Action,
    QualitySLA,
    SLAVerdict,
    evaluate_sla,
    regression_action,
)


@pytest.fixture
def healthy() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
            "phone": ["+14155552671", "+12025550143", "+13105550123", "+16175550199"],
            "name": ["A", "B", "C", "D"],
        }
    )


@pytest.fixture
def degraded() -> pd.DataFrame:
    """Same shape, but half the emails are blank and one is invalid."""
    return pd.DataFrame(
        {
            "email": ["a@x.com", "", "not-an-email", ""],
            "phone": ["+14155552671", "+12025550143", "+13105550123", "+16175550199"],
            "name": ["A", "B", "C", "D"],
        }
    )


class TestSLAThresholds:
    """The SLA is a per-dimension floor, scored 0-1 in config, 0-100 internally."""

    def test_a_run_meeting_every_floor_passes(self, healthy):
        sla = QualitySLA(completeness=0.9, validity=0.9)
        verdict = evaluate_sla(profile(healthy), sla)
        assert verdict.passed
        assert verdict.breaches == []

    def test_a_run_under_a_floor_fails_and_names_the_dimension(self, degraded):
        sla = QualitySLA(completeness=0.98)
        verdict = evaluate_sla(profile(degraded), sla)
        assert not verdict.passed
        assert [breach.dimension for breach in verdict.breaches] == ["completeness"]

    def test_the_breach_reports_required_actual_and_shortfall(self, degraded):
        sla = QualitySLA(completeness=0.98)
        breach = evaluate_sla(profile(degraded), sla).breaches[0]
        assert breach.required == 0.98
        assert breach.actual < 0.98
        assert breach.shortfall == pytest.approx(0.98 - breach.actual, abs=0.001)

    def test_config_percentages_and_fractions_agree(self, healthy):
        # 0.98 in config and 98.0 mean the same floor.
        assert evaluate_sla(profile(healthy), QualitySLA(completeness=0.98)).passed == (
            evaluate_sla(profile(healthy), QualitySLA(completeness=98.0)).passed
        )

    def test_an_unset_dimension_is_not_enforced(self, healthy):
        # Only completeness is set; validity is left alone even if it were 0.
        sla = QualitySLA(completeness=0.9)
        assert evaluate_sla(profile(healthy), sla).passed

    def test_a_dimension_the_frame_cannot_evaluate_is_skipped_not_failed(self):
        # A frame with no emails cannot have a validity score. Failing it would
        # punish a frame for not containing the column at all.
        frame = pd.DataFrame({"name": ["A", "B"]})
        sla = QualitySLA(validity=0.99)
        verdict = evaluate_sla(profile(frame), sla)
        assert verdict.passed
        assert verdict.skipped == ["validity"]

    def test_an_empty_sla_passes_everything(self, degraded):
        assert evaluate_sla(profile(degraded), QualitySLA()).passed

    def test_the_verdict_summarises_for_a_console_line(self, degraded):
        verdict = evaluate_sla(profile(degraded), QualitySLA(completeness=0.98))
        summary = verdict.summary()
        assert summary["passed"] is False
        assert summary["breaches"][0]["dimension"] == "completeness"


class TestSLAParsing:
    """The SLA is declared in YAML under ``quality.sla``."""

    def test_known_dimensions_parse_from_the_block(self):
        sla = QualitySLA.from_block(
            {"completeness": 0.98, "validity": 0.95, "uniqueness": 0.99}
        )
        assert sla.completeness == 0.98
        assert sla.validity == 0.95
        assert sla.uniqueness == 0.99

    def test_a_zero_is_respected_not_treated_as_unset(self):
        # 0.0 means "enforce nothing", which is different from "not declared".
        sla = QualitySLA.from_block({"completeness": 0.0})
        assert sla.completeness == 0.0

    def test_an_unknown_dimension_is_refused(self):
        from app_files.core import ConfigError

        with pytest.raises(ConfigError, match="completness"):
            QualitySLA.from_block({"completness": 0.9})

    def test_a_value_out_of_range_is_refused(self):
        from app_files.core import ConfigError

        with pytest.raises(ConfigError, match="completeness"):
            QualitySLA.from_block({"completeness": 1.5})

    def test_a_non_numeric_value_is_refused(self):
        from app_files.core import ConfigError

        with pytest.raises(ConfigError, match="completeness"):
            QualitySLA.from_block({"completeness": "high"})

    def test_a_whole_percentage_is_accepted(self):
        # 98 is a percentage; it must land as the same floor as 0.98.
        assert QualitySLA.from_block({"completeness": 98}).completeness == 0.98

    def test_a_fractional_value_above_one_is_refused_as_ambiguous(self):
        # 1.5 is 150% (a typo) or 1.5%? Refusing beats guessing in a check
        # whose job is to fail closed.
        from app_files.core import ConfigError

        with pytest.raises(ConfigError, match="ambiguous"):
            QualitySLA.from_block({"completeness": 1.5})

    def test_a_direct_construction_normalises_the_same_way(self):
        # The bug this guards: QualitySLA(completeness=98.0) built directly
        # used to keep 98.0 and compare it against a 0-100 score, so it never
        # fired — a silent no-op in the one check meant to catch bad data.
        assert QualitySLA(completeness=98.0).completeness == 0.98
        assert QualitySLA(completeness=0.98).completeness == 0.98

    def test_a_direct_construction_is_range_checked_too(self):
        from app_files.core import ConfigError

        with pytest.raises(ConfigError, match="completeness"):
            QualitySLA(completeness=250)


class TestRegressionAction:
    """The spec's ``regression.action``: what a detected regression should do."""

    def test_alert_is_the_safe_default(self):
        assert Action.default() is Action.ALERT

    def test_the_three_actions_parse(self):
        assert Action.parse("alert") is Action.ALERT
        assert Action.parse("block") is Action.BLOCK
        assert Action.parse("quarantine") is Action.QUARANTINE

    def test_an_unknown_action_is_refused(self):
        from app_files.core import ConfigError

        with pytest.raises(ConfigError, match="explode"):
            Action.parse("explode")

    def test_a_regressed_run_under_alert_proceeds(self, healthy, degraded, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        from app_files.profiling.binding import pin_baseline, record_quality

        pin_baseline("contacts.csv", profile(healthy))
        history = record_quality("contacts.csv", profile(degraded))
        decision = regression_action(history, Action.ALERT)
        assert decision.regressed
        assert decision.proceed is True

    def test_a_regressed_run_under_block_does_not_proceed(
        self, healthy, degraded, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        from app_files.profiling.binding import pin_baseline, record_quality

        pin_baseline("contacts.csv", profile(healthy))
        history = record_quality("contacts.csv", profile(degraded))
        decision = regression_action(history, Action.BLOCK)
        assert decision.regressed
        assert decision.proceed is False

    def test_a_regressed_run_under_quarantine_does_not_proceed(
        self, healthy, degraded, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        from app_files.profiling.binding import pin_baseline, record_quality

        pin_baseline("contacts.csv", profile(healthy))
        history = record_quality("contacts.csv", profile(degraded))
        decision = regression_action(history, Action.QUARANTINE)
        assert decision.regressed
        assert decision.proceed is False
        assert decision.quarantine is True

    def test_a_clean_run_proceeds_under_every_action(
        self, healthy, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        from app_files.profiling.binding import pin_baseline, record_quality

        pin_baseline("contacts.csv", profile(healthy))
        history = record_quality("contacts.csv", profile(healthy))
        for action in (Action.ALERT, Action.BLOCK, Action.QUARANTINE):
            decision = regression_action(history, action)
            assert not decision.regressed, action
            assert decision.proceed is True, action

    def test_a_source_with_no_baseline_cannot_regress(self, healthy):
        from app_files.profiling.binding import QualityHistory

        history = QualityHistory(
            source="fresh.csv", run_id=1, recorded=None, history=[], comparison=None
        )
        for action in (Action.ALERT, Action.BLOCK, Action.QUARANTINE):
            decision = regression_action(history, action)
            assert not decision.regressed
            assert decision.proceed is True

    def test_the_decision_explains_itself(self, healthy, degraded, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        from app_files.profiling.binding import pin_baseline, record_quality

        pin_baseline("contacts.csv", profile(healthy))
        history = record_quality("contacts.csv", profile(degraded))
        decision = regression_action(history, Action.BLOCK)
        assert "completeness" in decision.summary()
