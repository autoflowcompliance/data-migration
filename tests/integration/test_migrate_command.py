"""Layer 18 was library-only: no run a buyer could invoke reached it.

These tests drive ``python -m app_files.cli migrate``, the command that exposes
the four migration-safety steps. The guarantee under test is that the default
is a rehearsal: the analysis, rollback copy and runbook are written, but no
migration output is, and a blocking issue exits non-zero.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from app_files.cli import main

CLEAN = "Email Address,First Name,Last Name\njohn@acme.com,John,Smith\njane@acme.com,Jane,Doe\n"
BLOCKING = "Email Address,Stray Column\njohn@acme.com,xyz\njane@acme.com,abc\n"


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.fixture
def clean_source(tmp_path):
    path = tmp_path / "contacts.csv"
    path.write_text(CLEAN, encoding="utf-8")
    return path


class TestRehearsal:
    def test_the_analysis_is_written(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        code = main(["migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out)])
        assert code == 0
        assert (out / "pre_migration.txt").is_file()
        assert (out / "pre_migration.json").is_file()
        data = json.loads((out / "pre_migration.json").read_text(encoding="utf-8"))
        assert data["rows"] == 2
        assert "quality" in data

    def test_the_rollback_copy_is_written(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        main(["migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out)])
        assert (out / "rollback" / "contacts.rollback.csv").is_file()
        assert (out / "rollback" / "contacts.rollback.nulls.json").is_file()

    def test_the_runbook_is_written_from_the_config(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        main(["migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out)])
        runbook = (out / "runbook.txt").read_text(encoding="utf-8")
        assert "1." in runbook
        assert "rollback copy" in runbook

    def test_a_schedule_is_named_in_the_runbook(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        main([
            "migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out),
            "--schedule", "0 2 * * *",
        ])
        assert "0 2 * * *" in (out / "runbook.txt").read_text(encoding="utf-8")

    def test_no_migration_output_is_written(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        main(["migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out)])
        assert not (out / "clean_data.csv").exists()

    def test_the_rehearsal_message_is_printed(self, home, clean_source, tmp_path, capsys):
        main(["migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(tmp_path / "out")])
        assert "Rehearsal complete, nothing was migrated" in capsys.readouterr().out


class TestCommit:
    def test_commit_writes_the_migration(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        code = main([
            "migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out), "--commit",
        ])
        assert code == 0
        assert (out / "clean_data.csv").is_file()
        clean = pd.read_csv(out / "clean_data.csv")
        assert len(clean) == 2

    def test_commit_still_writes_the_safety_artifacts(self, home, clean_source, tmp_path):
        out = tmp_path / "out"
        main([
            "migrate", "-i", str(clean_source), "-c", "hubspot", "-o", str(out), "--commit",
        ])
        assert (out / "rollback" / "contacts.rollback.csv").is_file()
        assert (out / "runbook.txt").is_file()


class TestBlockingIssue:
    @pytest.fixture
    def blocking_source(self, tmp_path):
        path = tmp_path / "contacts.csv"
        path.write_text(BLOCKING, encoding="utf-8")
        return path

    def test_a_blocking_issue_exits_non_zero(self, home, blocking_source, tmp_path, capsys):
        code = main(["migrate", "-i", str(blocking_source), "-c", "hubspot", "-o", str(tmp_path / "out")])
        assert code == 1
        assert "Blocking issues found" in capsys.readouterr().err

    def test_the_block_still_writes_the_analysis(self, home, blocking_source, tmp_path):
        out = tmp_path / "out"
        main(["migrate", "-i", str(blocking_source), "-c", "hubspot", "-o", str(out)])
        report = (out / "pre_migration.txt").read_text(encoding="utf-8")
        assert "Ready to migrate: no" in report

    def test_no_migration_output_on_a_block(self, home, blocking_source, tmp_path):
        out = tmp_path / "out"
        main(["migrate", "-i", str(blocking_source), "-c", "hubspot", "-o", str(out)])
        assert not (out / "clean_data.csv").exists()

    def test_commit_overrides_the_block(self, home, blocking_source, tmp_path):
        out = tmp_path / "out"
        code = main([
            "migrate", "-i", str(blocking_source), "-c", "hubspot", "-o", str(out), "--commit",
        ])
        assert code == 0
        assert (out / "clean_data.csv").is_file()


class TestRollbackRestores:
    def test_the_rollback_copy_restores_the_original(self, home, clean_source, tmp_path):
        from app_files.cli import _read_csv
        from app_files.migration import build_rollback, restore_rollback

        original = _read_csv(clean_source)
        rollback = build_rollback(original, tmp_path / "rb", source_name="contacts.csv")
        restored = restore_rollback(rollback)
        assert restored.shape == original.shape
        pd.testing.assert_frame_equal(
            original.fillna("__NA__"), restored.fillna("__NA__"), check_dtype=False
        )
