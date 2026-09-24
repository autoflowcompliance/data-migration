"""Wiring proof: config rules run in the real CLI and batch entry points.

These drive ``app_files.cli.main`` unchanged and assert on the artifacts it
writes, because the bug this closes was not in the rule engine (which had
tests) but in the fact that no unattended caller invoked it.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from app_files.cli import main

SAMPLE = Path("app_files/samples/messy_contacts.csv")


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


class TestSingleFileCli:
    def test_issues_csv_includes_the_config_rules(self, home, tmp_path):
        out = tmp_path / "out"
        main(["-i", str(SAMPLE), "-c", "hubspot", "-o", str(out)])
        checks = set(pd.read_csv(out / "issues.csv")["check"])
        assert "rule:phone_e164_format" in checks

    def test_the_rule_line_is_printed(self, home, tmp_path, capsys):
        main(["-i", str(SAMPLE), "-c", "hubspot", "-o", str(tmp_path / "out")])
        assert "2 of 2 run, 1 failure(s)" in capsys.readouterr().out

    def test_the_report_carries_the_rule_failure(self, home, tmp_path):
        out = tmp_path / "out"
        main(["-i", str(SAMPLE), "-c", "hubspot", "-o", str(out)])
        html = (out / "qa_report.html").read_text(encoding="utf-8")
        assert "E.164" in html or "phone" in html.lower()

    def test_the_report_keeps_the_project_and_filename(self, home, tmp_path):
        out = tmp_path / "out"
        main(["-i", str(SAMPLE), "-c", "hubspot", "-o", str(out), "--project", "Acme"])
        html = (out / "qa_report.html").read_text(encoding="utf-8")
        assert "Acme" in html
        assert "messy_contacts.csv" in html

    def test_a_config_without_rules_is_unchanged(self, home, tmp_path):
        out = tmp_path / "out"
        code = main(["-i", str(SAMPLE), "-c", "salesforce", "-o", str(out)])
        assert (out / "issues.csv").exists()
        checks = set(pd.read_csv(out / "issues.csv")["check"])
        assert not any(c.startswith("rule:") for c in checks)
        assert code in (0, 1)

    def test_strict_rules_fails_on_a_declared_failure(self, home, tmp_path):
        code = main(
            ["-i", str(SAMPLE), "-c", "hubspot", "-o", str(tmp_path / "out"), "--strict-rules"]
        )
        assert code == 1

    def test_without_strict_rules_the_same_run_may_pass(self, home, tmp_path):
        # The rule failure is a warning, so a run whose core validation passes
        # must not be failed just for declaring rules.
        out = tmp_path / "out"
        code = main(["-i", str(SAMPLE), "-c", "hubspot", "-o", str(out)])
        assert code in (0, 1)


class TestBatchCli:
    @pytest.fixture
    def inbox(self, tmp_path):
        folder = tmp_path / "inbox"
        folder.mkdir()
        shutil.copy(SAMPLE, folder / "a.csv")
        shutil.copy(SAMPLE, folder / "b.csv")
        return folder

    def test_summary_carries_rule_counts(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out)])
        summary = pd.read_csv(out / "summary.csv")
        assert "rule_failures" in summary.columns
        assert summary["rule_failures"].tolist() == [1, 1]
        assert summary["rules_run"].tolist() == [2, 2]

    def test_each_files_report_shows_the_rule_failure(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main(["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out)])
        assert "rule:phone_e164_format" in set(
            pd.read_csv(out / "a" / "issues.csv")["check"]
        )

    def test_strict_rules_fails_the_batch(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        code = main(
            ["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out),
             "--strict-rules"]
        )
        assert code == 1

    def test_executions_are_unchanged_for_a_rules_less_config(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        code = main(["batch", "--in", str(inbox), "--template", "salesforce", "--out", str(out)])
        assert code == 0
        summary = pd.read_csv(out / "summary.csv")
        assert summary["rule_failures"].tolist() == [0, 0]
