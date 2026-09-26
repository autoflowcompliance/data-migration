"""Module 10 from the CLI: judge a file against a ``quality:`` block.

The SLA and regression action are only useful if a run path reads them. These
tests drive the real ``python -m app_files.cli quality check`` against real
files and the real SQLite history, so the exit codes are the ones an operator's
cron job would actually see.

The load-bearing case is the last class: a config that declares no ``quality:``
block must behave exactly as before, because that is the additive guarantee.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.cli import main

GOOD = (
    "Email Address,First Name,Last Name,Company\n"
    "john@acme.com,John,Smith,Acme\n"
    "jane@acme.com,Jane,Doe,Globex\n"
    "sam@acme.com,Sam,Ray,Initech\n"
    "kim@acme.com,Kim,Hart,Umbrella\n"
)

# Two rows lost and one field blanked: completeness and uniqueness both fall,
# which is a real regression rather than the same score relabelled.
DEGRADED = (
    "Email Address,First Name,Last Name,Company\n"
    "john@acme.com,John,Smith,\n"
    "jane@acme.com,Jane,,\n"
)

# Meets a low SLA but is still well below the baseline, so it exercises the
# regression path rather than stopping at the SLA gate.
REGRESSED_BUT_WITHIN_SLA = (
    "Email Address,First Name,Last Name,Company\n"
    "john@acme.com,John,Smith,Acme\n"
    "jane@acme.com,Jane,Doe,Globex\n"
    "sam@acme.com,Sam,Ray,Initech\n"
    "kim@acme.com,Kim,Hart,\n"
)

CONFIG = """\
crm: Quality check
version: "1.0"
fields:
  - name: email
    source: Email Address
  - name: first_name
    source: First Name
  - name: last_name
    source: Last Name
  - name: company
    source: Company
quality:
  sla:
    completeness: 0.9
  regression:
    threshold: 5
    action: block
"""

# A low SLA floor so the regression action is what decides the exit code.
CONFIG_LOW_SLA = CONFIG.replace("completeness: 0.9", "completeness: 0.5")

CONFIG_NO_QUALITY = """\
crm: Quality check
version: "1.0"
fields:
  - name: email
    source: Email Address
  - name: first_name
    source: First Name
  - name: last_name
    source: Last Name
  - name: company
    source: Company
"""


@pytest.fixture
def home(tmp_path, monkeypatch):
    state = tmp_path / "state"
    monkeypatch.setenv("AUTOFLOW_HOME", str(state))
    return state


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _fixtures(tmp_path: Path, config_body: str = CONFIG):
    config = _write(tmp_path / "quality.yaml", config_body)
    good = _write(tmp_path / "good.csv", GOOD)
    degraded = _write(tmp_path / "degraded.csv", DEGRADED)
    return config, good, degraded


class TestSLACheck:
    """A declared SLA gates the exit code."""

    def test_a_file_meeting_its_sla_exits_zero(self, tmp_path, home, capsys):
        config, good, _ = _fixtures(tmp_path)
        code = main(["quality", "check", str(good), "--config", str(config)])
        assert code == 0
        assert "SLA met" in capsys.readouterr().out

    def test_a_file_under_its_sla_exits_non_zero(self, tmp_path, home, capsys):
        config, _, degraded = _fixtures(tmp_path)
        code = main(["quality", "check", str(degraded), "--config", str(config)])
        assert code != 0
        out = capsys.readouterr().out
        assert "completeness" in out

    def test_the_breach_line_names_the_shortfall(self, tmp_path, home, capsys):
        config, _, degraded = _fixtures(tmp_path)
        main(["quality", "check", str(degraded), "--config", str(config)])
        out = capsys.readouterr().out
        assert "%" in out and "90" in out.replace("0.9", "90")

    def test_a_config_with_no_sla_does_not_gate(self, tmp_path, home):
        config, _, degraded = _fixtures(
            tmp_path, CONFIG_NO_QUALITY + "quality:\n  regression:\n    action: block\n"
        )
        # No floors declared, so there is nothing to breach.
        code = main(["quality", "check", str(degraded), "--config", str(config)])
        assert code == 0


class TestRegressionCheck:
    """The declared action governs a regression against the pinned baseline.

    The baseline is keyed by source, so a regression is the *same* source
    arriving worse. These tests overwrite the file rather than checking a
    differently-named one, which is what a repeat run of a source looks like.
    """

    def test_the_first_run_pins_a_baseline_when_asked(self, tmp_path, home):
        config, good, _ = _fixtures(tmp_path)
        code = main(
            ["quality", "check", str(good), "--config", str(config), "--baseline"]
        )
        assert code == 0

    def test_a_clean_repeat_run_exits_zero(self, tmp_path, home):
        config, good, _ = _fixtures(tmp_path)
        main(["quality", "check", str(good), "--config", str(config), "--baseline"])
        code = main(["quality", "check", str(good), "--config", str(config)])
        assert code == 0

    def _pin_then_degrade(self, tmp_path, config_body):
        config, good, _ = _fixtures(tmp_path, config_body)
        main(["quality", "check", str(good), "--config", str(config), "--baseline"])
        # Same source, worse content: the regression a repeat run detects.
        good.write_text(REGRESSED_BUT_WITHIN_SLA, encoding="utf-8")
        return config, good

    def test_a_regressed_run_under_block_exits_non_zero(self, tmp_path, home, capsys):
        config, good = self._pin_then_degrade(tmp_path, CONFIG_LOW_SLA)
        code = main(["quality", "check", str(good), "--config", str(config)])
        assert code != 0
        assert "regression" in capsys.readouterr().out.lower()

    def test_a_regressed_run_under_alert_exits_zero(self, tmp_path, home, capsys):
        config, good = self._pin_then_degrade(
            tmp_path, CONFIG_LOW_SLA.replace("action: block", "action: alert")
        )
        code = main(["quality", "check", str(good), "--config", str(config)])
        # alert must not stop a run; it reports and lets it through.
        assert code == 0
        assert "alert" in capsys.readouterr().out.lower()

    def test_quarantine_reports_the_hold(self, tmp_path, home, capsys):
        config, good = self._pin_then_degrade(
            tmp_path, CONFIG_LOW_SLA.replace("action: block", "action: quarantine")
        )
        code = main(["quality", "check", str(good), "--config", str(config)])
        assert code != 0
        assert "quarantine" in capsys.readouterr().out.lower()

    def test_a_check_does_not_move_the_baseline_it_measures(self, tmp_path, home):
        # The regression check is read-only: a gate that appends to the history
        # it reads would let a bad run become its own baseline.
        config, good = self._pin_then_degrade(tmp_path, CONFIG_LOW_SLA)
        first = main(["quality", "check", str(good), "--config", str(config)])
        second = main(["quality", "check", str(good), "--config", str(config)])
        assert first == second != 0

    def test_a_different_source_is_not_judged_against_this_baseline(
        self, tmp_path, home
    ):
        # The baseline belongs to a source. Another file with no baseline of its
        # own cannot regress against one, however similar it looks.
        config, good, _ = _fixtures(tmp_path, CONFIG_LOW_SLA)
        other = _write(tmp_path / "other.csv", REGRESSED_BUT_WITHIN_SLA)
        main(["quality", "check", str(good), "--config", str(config), "--baseline"])
        code = main(["quality", "check", str(other), "--config", str(config)])
        assert code == 0


class TestUnbound:
    """No quality block means the command is a no-op that cannot fail a run."""

    def test_a_config_without_the_block_exits_zero(self, tmp_path, home, capsys):
        config, _, degraded = _fixtures(tmp_path, CONFIG_NO_QUALITY)
        code = main(["quality", "check", str(degraded), "--config", str(config)])
        assert code == 0
        assert "no quality" in capsys.readouterr().out.lower()

    def test_an_unbound_run_records_no_history(self, tmp_path, home):
        from app_files.profiling import TrendStore

        config, _, degraded = _fixtures(tmp_path, CONFIG_NO_QUALITY)
        main(["quality", "check", str(degraded), "--config", str(config)])
        assert TrendStore().sources() == []


class TestFailClosed:
    """A malformed block is a config error, not a silent pass."""

    def test_an_unknown_sla_dimension_is_refused(self, tmp_path, home, capsys):
        body = CONFIG.replace("completeness: 0.9", "completness: 0.9")
        config, _, degraded = _fixtures(tmp_path, body)
        code = main(["quality", "check", str(degraded), "--config", str(config)])
        assert code != 0
        assert "completness" in capsys.readouterr().err

    def test_a_missing_config_is_reported(self, tmp_path, home, capsys):
        _, _, degraded = _fixtures(tmp_path)
        code = main(
            ["quality", "check", str(degraded), "--config", str(tmp_path / "nope.yaml")]
        )
        assert code != 0
        assert "nope.yaml" in capsys.readouterr().err

    def test_a_missing_input_file_is_reported(self, tmp_path, home, capsys):
        config, _, _ = _fixtures(tmp_path)
        code = main(
            ["quality", "check", str(tmp_path / "missing.csv"), "--config", str(config)]
        )
        assert code != 0
        assert "missing.csv" in capsys.readouterr().err
