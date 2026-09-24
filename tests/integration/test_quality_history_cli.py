"""Layer 5's trend store and baseline comparison had no caller outside the
profiling package: a run scored a source and immediately forgot it, so "is this
source improving or rotting" and "is this run worse than the one we accepted"
could not be answered by running the tool.

These tests drive the real CLI with ``--record-quality``/``--baseline`` against
the real SQLite history under ``AUTOFLOW_HOME``. ``--fail-on-regression`` is
checked against a deliberately degraded file, so the regression is a real
completeness drop rather than a mocked comparison.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.cli import main
from app_files.profiling import TrendStore, profile


@pytest.fixture
def home(tmp_path, monkeypatch):
    state = tmp_path / "state"
    monkeypatch.setenv("AUTOFLOW_HOME", str(state))
    return state


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


GOOD = (
    "Email Address,First Name,Last Name,Company\n"
    "john@acme.com,John,Smith,Acme\n"
    "jane@acme.com,Jane,Doe,Globex\n"
    "sam@acme.com,Sam,Ray,Initech\n"
    "kim@acme.com,Kim,Hart,Umbrella\n"
)

# Two rows lost and one field blanked on every row: completeness and uniqueness
# both fall, which is a real regression, not a re-labelling of the same score.
DEGRADED = (
    "Email Address,First Name,Last Name,Company\n"
    "john@acme.com,,Smith,\n"
    "jane@acme.com,,Doe,\n"
)


class TestRecording:
    def test_a_run_records_its_score(self, home, tmp_path, capsys):
        source = _write(tmp_path / "contacts.csv", GOOD)
        code = main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
                     "--record-quality"])
        assert code == 0
        assert "Quality history: 1 run(s)" in capsys.readouterr().out
        assert (home / "trends" / "quality.db").is_file()

    def test_without_the_flag_nothing_is_recorded(self, home, tmp_path):
        source = _write(tmp_path / "contacts.csv", GOOD)
        main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out")])
        assert not (home / "trends").exists()

    def test_a_second_run_adds_to_the_history(self, home, tmp_path, capsys):
        source = _write(tmp_path / "contacts.csv", GOOD)
        for _ in range(3):
            main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
                  "--record-quality"])
            capsys.readouterr()
        points = TrendStore().trend("contacts")
        assert len(points) == 3

    def test_the_source_is_remembered_by_filename_not_full_path(self, home, tmp_path):
        source = _write(tmp_path / "contacts.csv", GOOD)
        main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
              "--record-quality"])
        # A copy elsewhere is the same source, so its history continues.
        other = _write(tmp_path / "nested" / "contacts.csv", GOOD)
        main(["-i", str(other), "-c", "hubspot", "-o", str(tmp_path / "out2"),
              "--record-quality"])
        assert len(TrendStore().trend("contacts")) == 2

    def test_the_reported_trend_reflects_a_decline(self, home, tmp_path, capsys):
        good = _write(tmp_path / "contacts.csv", GOOD)
        main(["-i", str(good), "-c", "hubspot", "-o", str(tmp_path / "a"),
              "--record-quality"])
        bad = _write(tmp_path / "nested" / "contacts.csv", DEGRADED)
        for out in ("b", "c"):
            main(["-i", str(bad), "-c", "hubspot", "-o", str(tmp_path / out),
                  "--record-quality"])
        capsys.readouterr()
        main(["-i", str(bad), "-c", "hubspot", "-o", str(tmp_path / "d"),
              "--record-quality"])
        assert "trend declining" in capsys.readouterr().out


class TestBaseline:
    def test_pinning_records_and_pins(self, home, tmp_path, capsys):
        source = _write(tmp_path / "contacts.csv", GOOD)
        code = main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
                     "--baseline"])
        assert code == 0
        assert "Baseline pinned for contacts" in capsys.readouterr().out
        store = TrendStore()
        assert store.baseline("contacts") is not None
        assert len(store.trend("contacts")) == 1

    def test_a_regression_is_reported_against_the_baseline(self, home, tmp_path, capsys):
        good = _write(tmp_path / "contacts.csv", GOOD)
        main(["-i", str(good), "-c", "hubspot", "-o", str(tmp_path / "a"), "--baseline"])
        bad = _write(tmp_path / "nested" / "contacts.csv", DEGRADED)
        capsys.readouterr()
        main(["-i", str(bad), "-c", "hubspot", "-o", str(tmp_path / "b"),
              "--record-quality"])
        out = capsys.readouterr().out
        assert "regression:" in out

    def test_fail_on_regression_exits_non_zero(self, home, tmp_path):
        good = _write(tmp_path / "contacts.csv", GOOD)
        main(["-i", str(good), "-c", "hubspot", "-o", str(tmp_path / "a"), "--baseline"])
        bad = _write(tmp_path / "nested" / "contacts.csv", DEGRADED)
        code = main(["-i", str(bad), "-c", "hubspot", "-o", str(tmp_path / "b"),
                     "--record-quality", "--fail-on-regression"])
        assert code == 1

    def test_an_unchanged_file_does_not_alert(self, home, tmp_path, capsys):
        source = _write(tmp_path / "contacts.csv", GOOD)
        main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "a"), "--baseline"])
        capsys.readouterr()
        code = main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "b"),
                     "--record-quality", "--fail-on-regression"])
        assert code == 0
        assert "regression:" not in capsys.readouterr().out

    def test_a_run_before_any_baseline_cannot_alert(self, home, tmp_path, capsys):
        source = _write(tmp_path / "contacts.csv", GOOD)
        code = main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
                     "--record-quality", "--fail-on-regression"])
        assert code == 0
        assert "regression:" not in capsys.readouterr().out


class TestBindingUnit:
    def test_record_quality_reports_the_history_it_wrote(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        import pandas as pd

        from app_files.profiling import record_quality

        frame = pd.read_csv(_write(tmp_path / "c.csv", GOOD))
        history = record_quality(tmp_path / "c.csv", profile(frame))
        assert history.source == "c"
        assert history.run_id > 0
        assert history.trend == "stable"
        assert history.comparison is None

    def test_pin_baseline_returns_the_pinned_point(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
        import pandas as pd

        from app_files.profiling import pin_baseline

        frame = pd.read_csv(_write(tmp_path / "c.csv", GOOD))
        point = pin_baseline("c", profile(frame))
        assert point.overall == pytest.approx(profile(frame).overall)
        assert TrendStore().baseline("c").id == point.id
