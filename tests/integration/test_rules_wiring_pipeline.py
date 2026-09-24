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

# A core-valid file whose config rule then fails: the advisory case. The core
# validator raises no error, so only a declared rule can fail this run — which
# is what makes it a clean test of "advisory unless --strict-rules".
CLEAN_CONTACTS = (
    "First Name,Last Name,Email Address,Phone 1,Company,Title,Created Date,City,Country\n"
    "Ann,Smith,ann@example.com,not-a-phone,Acme Inc,CEO,2024-01-05,Boston,USA\n"
    "Bob,Jones,bob@example.com,512.876.5432,Globex,CTO,2024-02-10,Austin,USA\n"
)


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
        source = tmp_path / "clean.csv"
        source.write_text(CLEAN_CONTACTS, encoding="utf-8")
        code = main(["-i", str(source), "-c", "salesforce", "-o", str(out)])
        assert (out / "issues.csv").exists()
        checks = set(pd.read_csv(out / "issues.csv")["check"])
        assert not any(c.startswith("rule:") for c in checks)
        assert code == 0

    def test_strict_rules_fails_on_a_declared_failure(self, home, tmp_path):
        code = main(
            ["-i", str(SAMPLE), "-c", "hubspot", "-o", str(tmp_path / "out"), "--strict-rules"]
        )
        assert code == 1

    def test_without_strict_rules_a_declared_failure_still_exits_zero(self, home, tmp_path):
        # A declared rule failure is advisory: a run whose *core* validation
        # passes must not be failed just for declaring rules. Merging the rule
        # issue must not flip the exit code, or --strict-rules would be moot.
        out = tmp_path / "out"
        source = tmp_path / "clean.csv"
        source.write_text(CLEAN_CONTACTS, encoding="utf-8")
        code = main(["-i", str(source), "-c", "hubspot", "-o", str(out)])
        assert code == 0
        assert "rule:phone_e164_format" in set(
            pd.read_csv(out / "issues.csv")["check"]
        )

    def test_strict_rules_fails_the_same_core_clean_run(self, home, tmp_path):
        source = tmp_path / "clean.csv"
        source.write_text(CLEAN_CONTACTS, encoding="utf-8")
        code = main(
            ["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
             "--strict-rules"]
        )
        assert code == 1

    def test_a_core_validation_error_still_exits_one(self, home, tmp_path):
        """Advisory rules must not swallow a real core failure."""

        messy = tmp_path / "messy.csv"
        messy.write_text(
            "Email Address,First Name,Last Name,Phone 1,City,Country\n"
            ",Ann,Smith,(617) 498-3000,Boston,USA\n"
            "bob@example.com,Bob,Jones,512.876.5432,Austin,USA\n",
            encoding="utf-8",
        )
        out = tmp_path / "out"
        code = main(["-i", str(messy), "-c", "salesforce", "-o", str(out)])
        assert code == 1


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


CROSS_DIR = Path("tests/regression/golden_files/rules_wiring")


class TestCrossFieldConfigThroughTheCli:
    """A config path with a ``cross_field:`` block, driven through the CLI."""

    @pytest.fixture
    def cross_input(self, tmp_path):
        folder = tmp_path / "inbox"
        folder.mkdir()
        shutil.copy(CROSS_DIR / "cross_field.csv", folder / "cross.csv")
        return folder

    def test_issues_csv_has_cross_field_rows(self, home, cross_input, tmp_path):
        out = tmp_path / "out"
        main(["-i", str(cross_input / "cross.csv"),
              "-c", str(CROSS_DIR / "crm.yaml"), "-o", str(out)])
        checks = set(pd.read_csv(out / "issues.csv")["check"])
        assert "cross_field:phone_below_zip" in checks
        assert "rule:phone_required" in checks

    def test_the_rule_line_counts_both_kinds(self, home, cross_input, tmp_path, capsys):
        main(["-i", str(cross_input / "cross.csv"),
              "-c", str(CROSS_DIR / "crm.yaml"), "-o", str(tmp_path / "out")])
        assert "3 of 3 run, 3 failure(s)" in capsys.readouterr().out

    def test_strict_rules_fails_on_a_cross_field_failure(self, home, cross_input, tmp_path):
        code = main(["-i", str(cross_input / "cross.csv"),
                     "-c", str(CROSS_DIR / "crm.yaml"), "-o", str(tmp_path / "out"),
                     "--strict-rules"])
        assert code == 1
