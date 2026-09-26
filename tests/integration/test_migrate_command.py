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


# A config that declares the blocks the pipeline does not run on its own. The
# migrate command used to ignore every one of them, so a rehearsal reported no
# duplicates and a --commit wrote raw emails for a config that says mask them.
DECLARED = """
crm: Declared
version: "1.0"
fields:
  - name: email
    required: true
    aliases: ["Email Address"]
  - name: firstname
    aliases: ["First Name"]
  - name: lastname
    aliases: ["Last Name"]
  - name: phone
    aliases: ["Phone"]
rules:
  - name: email_shape
    field: email
    type: regex
    pattern: "^[^@\\\\s]+@[^@\\\\s]+\\\\.[^@\\\\s]+$"
    severity: warning
privacy:
  default_strategy: redact
  fields:
    - column: email
      strategy: hash
    - column: phone
      strategy: partial
dedupe:
  rules:
    - columns: [firstname, lastname]
      threshold: 0.85
      metric: jaro_winkler
"""

DECLARED_SOURCE = (
    "Email Address,First Name,Last Name,Phone\n"
    "john@acme.com,John,Smith,+14155550100\n"
    "jon@acme.com,Jon,Smith,+14155550101\n"
    "jane@acme.com,Jane,Doe,+14155550102\n"
)


class TestDeclaredBlocksBind:
    """A rehearsal must report, and a commit must apply, every declared block."""

    @pytest.fixture
    def declared_config(self, tmp_path):
        path = tmp_path / "declared.yaml"
        path.write_text(DECLARED, encoding="utf-8")
        return path

    @pytest.fixture
    def declared_source(self, tmp_path):
        path = tmp_path / "declared.csv"
        path.write_text(DECLARED_SOURCE, encoding="utf-8")
        return path

    def test_the_rehearsal_names_every_declared_block(
        self, home, declared_config, declared_source, tmp_path, capsys
    ):
        main([
            "migrate", "-i", str(declared_source), "-c", str(declared_config),
            "-o", str(tmp_path / "out"),
        ])
        out = capsys.readouterr().out
        assert "Config-declared steps" in out
        assert "rules:" in out
        assert "privacy:" in out
        assert "dedupe: 1 near-duplicate row(s) removed" in out

    def test_the_rehearsal_reports_the_pipeline_dedupe_as_zero(
        self, home, declared_config, declared_source, tmp_path
    ):
        # The pipeline's own dedupe count stays 0; the declared dedupe is what
        # removes the near-duplicate, and it is reported separately.
        from app_files.migration import dry_run

        report = dry_run(
            pd.read_csv(declared_source, dtype=str, keep_default_na=False),
            str(declared_config),
        )
        assert report.duplicates_removed == 0
        assert report.duplicates_merged == 1
        assert report.pii_masked > 0

    def test_a_rehearsal_writes_no_accepted_ruleset(
        self, home, declared_config, declared_source, tmp_path
    ):
        # Applying rules normally persists the accepted YAML under the state
        # home. A rehearsal that did that would not be a rehearsal.
        state = tmp_path / "state"
        main([
            "migrate", "-i", str(declared_source), "-c", str(declared_config),
            "-o", str(tmp_path / "out"),
        ])
        assert not (state / "rules").exists()

    def test_commit_masks_the_declared_pii(
        self, home, declared_config, declared_source, tmp_path
    ):
        out = tmp_path / "out"
        code = main([
            "migrate", "-i", str(declared_source), "-c", str(declared_config),
            "-o", str(out), "--commit",
        ])
        assert code == 0
        masked = pd.read_csv(out / "masked_data.csv", dtype=str, keep_default_na=False)
        # No raw address survives, and the phone keeps only its last four.
        assert not masked["email"].str.contains("@").any()
        assert masked["phone"].str.startswith("****").all()

    def test_commit_writes_the_declared_deliverables(
        self, home, declared_config, declared_source, tmp_path
    ):
        out = tmp_path / "out"
        main([
            "migrate", "-i", str(declared_source), "-c", str(declared_config),
            "-o", str(out), "--commit",
        ])
        assert (out / "masked_data.csv").is_file()
        assert (out / "deduped_data.csv").is_file()
        assert (out / "issues.csv").is_file()
        deduped = pd.read_csv(out / "deduped_data.csv", dtype=str, keep_default_na=False)
        assert len(deduped) == 2

    def test_commit_matches_the_flat_cli_clean_data(
        self, home, declared_config, declared_source, tmp_path
    ):
        # The committed clean frame is the pipeline's, not a masked one — the
        # same file the flat CLI writes. Masking is a separate deliverable.
        mig_out, cli_out = tmp_path / "mig", tmp_path / "cli"
        main([
            "migrate", "-i", str(declared_source), "-c", str(declared_config),
            "-o", str(mig_out), "--commit",
        ])
        main(["-i", str(declared_source), "-c", str(declared_config), "-o", str(cli_out)])
        assert (mig_out / "clean_data.csv").read_bytes() == (
            cli_out / "clean_data.csv"
        ).read_bytes()
