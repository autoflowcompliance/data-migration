"""Module 10's binding: a ``quality:`` block reaches CLI, API and a run.

The SLA and the regression action are useless if nothing reads them. This is
the same additive binding as privacy, normalization, dedupe and the quality
history before it: the module declares a config block, and the CLI, the API and
a run path all resolve it through the one shared helper in
``app_files/config_bindings.py``.

The load-bearing assertion here is the *unbound* case. A config with no
``quality:`` block must produce no SLA, no action and no extra output — a run
that worked before this module produces byte-identical output after it.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.quality import Action
from app_files.quality.binding import (
    QualityBinding,
    QualityBlockError,
    bind_quality,
    quality_from_config,
)


@pytest.fixture
def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "email": ["a@x.com", "b@x.com", "", "not-an-email"],
            "phone": ["+14155552671", "+12025550143", "+13105550123", "+16175550199"],
            "name": ["A", "B", "C", "D"],
        }
    )


class TestUnbound:
    """No block declared means nothing happens. This is the additive guarantee."""

    def test_an_absent_block_yields_no_binding(self, frame):
        assert bind_quality(frame, {}) is None

    def test_a_none_block_yields_no_binding(self, frame):
        assert bind_quality(frame, {"quality": None}) is None

    def test_an_empty_block_yields_no_binding(self, frame):
        # `quality:` with nothing under it declares nothing to enforce.
        assert bind_quality(frame, {"quality": {}}) is None

    def test_an_unrelated_block_is_ignored(self, frame):
        assert bind_quality(frame, {"privacy": {"email": "redact"}}) is None

    def test_an_unbound_config_is_not_an_error(self):
        assert quality_from_config({}) is None

    def test_an_unbound_config_profiles_nothing(self, frame):
        # Profiling is skipped entirely when no block is declared, so an
        # unbound run does no extra work.
        assert bind_quality(frame, {"privacy": {"email": "redact"}}) is None


class TestSLABinding:
    """A declared SLA is enforced against the frame."""

    def test_a_declared_sla_is_parsed(self):
        binding = quality_from_config({"quality": {"sla": {"completeness": 0.98}}})
        assert binding.sla.completeness == 0.98

    def test_the_run_is_judged_against_the_sla(self, frame):
        binding = bind_quality(frame, {"quality": {"sla": {"completeness": 0.98}}})
        assert binding.verdict.passed is False
        assert binding.verdict.breaches[0].dimension == "completeness"

    def test_a_frame_that_meets_its_sla_passes(self):
        clean = pd.DataFrame({"name": ["A", "B"], "email": ["a@x.com", "b@x.com"]})
        binding = bind_quality(clean, {"quality": {"sla": {"completeness": 0.9}}})
        assert binding.verdict.passed is True

    def test_the_binding_summarises_for_a_console_line(self, frame):
        binding = bind_quality(frame, {"quality": {"sla": {"completeness": 0.98}}})
        summary = binding.summary()
        assert summary["sla_breached"] is True
        assert summary["breaches"][0]["dimension"] == "completeness"


class TestRegressionBinding:
    """A declared action governs what a regression does."""

    def test_the_action_defaults_to_alert_when_unspecified(self):
        binding = quality_from_config({"quality": {"sla": {"completeness": 0.5}}})
        assert binding.action is Action.ALERT

    def test_the_declared_action_is_read(self):
        binding = quality_from_config(
            {"quality": {"regression": {"action": "block"}}}
        )
        assert binding.action is Action.BLOCK

    def test_an_unknown_action_is_refused_at_config_time(self):
        with pytest.raises(QualityBlockError, match="explode"):
            quality_from_config({"quality": {"regression": {"action": "explode"}}})

    def test_a_regression_threshold_is_read(self):
        binding = quality_from_config(
            {"quality": {"regression": {"threshold": 2.0}}}
        )
        assert binding.threshold == 2.0

    def test_an_unknown_top_level_key_is_refused(self):
        # Fail closed: a typo'd key must not silently enforce nothing.
        with pytest.raises(QualityBlockError, match="slaa"):
            quality_from_config({"quality": {"slaa": {"completeness": 0.9}}})


class TestFailClosed:
    """A malformed block is an error, not a silent no-op."""

    def test_a_non_mapping_block_is_refused(self, frame):
        with pytest.raises(QualityBlockError, match="quality"):
            bind_quality(frame, {"quality": "on"})

    def test_an_unknown_dimension_is_refused(self, frame):
        with pytest.raises(QualityBlockError, match="completness"):
            bind_quality(frame, {"quality": {"sla": {"completness": 0.9}}})

    def test_the_error_is_a_config_error(self):
        from app_files.core import ConfigError

        assert issubclass(QualityBlockError, ConfigError)


class TestPrecedence:
    """The block resolves through the one shared chain."""

    def test_env_overrides_the_yaml_sla(self, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_QUALITY_SLA_COMPLETENESS", "0.5")
        binding = quality_from_config({"quality": {"sla": {"completeness": 0.98}}})
        assert binding.sla.completeness == 0.5

    def test_env_overrides_the_yaml_action(self, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_QUALITY_REGRESSION_ACTION", "block")
        binding = quality_from_config({"quality": {"regression": {"action": "alert"}}})
        assert binding.action is Action.BLOCK

    def test_the_binding_reports_where_each_setting_came_from(self, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_QUALITY_SLA_COMPLETENESS", "0.5")
        binding = quality_from_config(
            {"quality": {"sla": {"completeness": 0.98}}}, with_provenance=True
        )
        assert binding.provenance["sla.completeness"].value == "env"


class TestDefaults:
    """The documented defaults, so a bare block is still usable."""

    def test_the_default_action_is_alert(self):
        assert QualityBinding.defaults()["regression"]["action"] == "alert"

    def test_the_default_threshold_is_the_existing_constant(self):
        from app_files.profiling.baseline import DEFAULT_DROP_THRESHOLD

        assert QualityBinding.defaults()["regression"]["threshold"] == (
            DEFAULT_DROP_THRESHOLD
        )

    def test_no_default_sla_is_imposed(self):
        # An unset floor must stay unset; defaulting it to something would
        # enforce a policy nobody agreed to.
        assert QualityBinding.defaults()["sla"] == {}
