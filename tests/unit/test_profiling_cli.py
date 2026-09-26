"""Interface tests for the profiling extension's CLI / API / SDK adapters.

Written before the implementation. Each adapter is a thin shim over
``bind_profiling`` — no second implementation of the statistics.
"""

from __future__ import annotations

import json

import pytest

from app_files.cli import main

CSV = b"amount,who\n1,a@x.com\n2,b@y.org\n3,c@z.net\n4,d@w.io\n5,e@v.co\n1000,f@u.me\n"

CONFIG = """
fields:
  - name: amount
    source: amount
profiling:
  statistics:
    enabled: true
  patterns:
    enabled: true
  outliers:
    enabled: true
    method: iqr
"""


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.fixture
def fixtures(home):
    config = home / "profiling.yaml"
    config.write_text(CONFIG, encoding="utf-8")
    data = home / "data.csv"
    data.write_bytes(CSV)
    return config, data


# ------------------------------------------------------------------- CLI
class TestCLI:
    def test_profile_columns_writes_a_report(self, fixtures, tmp_path):
        config, data = fixtures
        out = tmp_path / "out"
        code = main(["profile", "columns", str(data), "--config", str(config),
                     "-o", str(out)])
        assert code == 0
        report = out / "profiling_report.json"
        assert report.exists()
        payload = json.loads(report.read_text())
        assert payload["statistics"]["amount"]["kind"] == "numeric"
        assert payload["outliers"]["amount"]["count"] == 1

    def test_the_cli_prints_a_human_summary(self, fixtures, capsys):
        config, data = fixtures
        main(["profile", "columns", str(data), "--config", str(config)])
        out = capsys.readouterr().out
        assert "amount" in out
        assert "outlier" in out.lower()

    def test_a_config_without_the_block_exits_two(self, home, tmp_path, capsys):
        config = home / "bare.yaml"
        config.write_text("fields:\n  - name: amount\n    source: amount\n", encoding="utf-8")
        data = home / "data.csv"
        data.write_bytes(CSV)
        code = main(["profile", "columns", str(data), "--config", str(config)])
        assert code == 2
        assert "profiling" in capsys.readouterr().err.lower()

    def test_a_missing_config_exits_two(self, home, tmp_path):
        data = home / "data.csv"
        data.write_bytes(CSV)
        code = main(["profile", "columns", str(data), "--config", str(home / "nope.yaml")])
        assert code == 2

    def test_the_method_can_be_chosen_on_the_cli(self, fixtures, tmp_path):
        config, data = fixtures
        out = tmp_path / "out2"
        code = main(["profile", "columns", str(data), "--config", str(config),
                     "--outlier-method", "zscore", "-o", str(out)])
        assert code == 0
        payload = json.loads((out / "profiling_report.json").read_text())
        assert payload["outliers"]["amount"]["method"] == "zscore"

    def test_the_pre_existing_profile_report_flag_still_works(self, fixtures, tmp_path):
        # ``--profile-report`` on the main command is the pre-existing surface
        # and must be untouched by this extension.
        config, data = fixtures
        out = tmp_path / "legacy"
        code = main(["-i", str(data), "-c", str(config), "-o", str(out),
                     "--profile-report"])
        assert code == 0
        assert (out / "profile.json").exists()
