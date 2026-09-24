"""Layer 18 — pre-migration analysis, rollback, dry run, runbook."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from app_files.migration import (
    PreMigrationReport,
    analyze_source,
    build_rollback,
    dry_run,
    generate_runbook,
    restore_rollback,
    write_pre_migration_report,
)

GOOD = pd.DataFrame(
    {
        "Email Address": ["a@x.com", "b@x.com", "c@x.com"],
        "Phone": ["+14155552671", "+14155552672", "+14155552673"],
        "Full Name": ["Jane Doe", "John Smith", "Amy Lee"],
    }
)


@pytest.fixture(autouse=True)
def _home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))


class TestPreMigrationAnalysis:
    def test_a_clean_source_is_ready(self):
        report = analyze_source(GOOD, "hubspot", "contacts.csv")
        assert report.ready
        assert report.rows == 3
        assert report.columns == 3

    def test_an_unmapped_column_blocks_the_migration(self):
        frame = GOOD.assign(Mystery=["1", "2", "3"])
        report = analyze_source(frame, "hubspot", "messy.csv")
        assert not report.ready
        assert "Mystery" in report.unmapped_columns
        assert any(issue.kind == "unmapped" for issue in report.blocking)

    def test_a_sparse_column_is_flagged(self):
        frame = pd.DataFrame({"Email Address": ["a@x.com", "", "", ""]})
        report = analyze_source(frame, "hubspot")
        assert any(issue.kind == "sparse_column" for issue in report.issues)

    def test_low_quality_is_blocking(self):
        frame = pd.DataFrame(
            {
                "Email Address": ["not-an-email"] * 10,
                "Phone": ["nope"] * 10,
                "Full Name": [""] * 10,
            }
        )
        report = analyze_source(frame, "hubspot")
        kinds = {issue.kind for issue in report.issues}
        assert "low_quality" in kinds

    def test_the_report_carries_the_field_map(self):
        report = analyze_source(GOOD, "hubspot")
        assert report.field_map["Email Address"] == "email"

    def test_render_names_the_source_and_the_verdict(self):
        text = analyze_source(GOOD, "hubspot", "contacts.csv").render()
        assert "contacts.csv" in text
        assert "Ready to migrate: yes" in text

    def test_write_produces_text_and_json(self, tmp_path):
        report = analyze_source(GOOD, "hubspot")
        path = write_pre_migration_report(report, tmp_path / "analysis.txt")
        assert path.exists()
        payload = json.loads(path.with_suffix(".json").read_text())
        assert payload["rows"] == 3
        assert "issues" in payload

    def test_analysis_writes_nothing_on_its_own(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        analyze_source(GOOD, "hubspot")
        assert list(tmp_path.iterdir()) == []

    def test_empty_report_dict_shape(self):
        report = PreMigrationReport("x", 0, 0, {}, 0.0)
        assert report.as_dict()["ready"] is True


class TestRollback:
    def test_a_rollback_restores_the_frame_exactly(self, tmp_path):
        rollback = build_rollback(GOOD, tmp_path, "contacts.csv")
        assert restore_rollback(rollback).equals(GOOD)

    @pytest.mark.parametrize(
        "frame",
        [
            pd.DataFrame({"n": [1, 2, 3], "amount": [1.5, 2.5, 3.5], "flag": [True, False, True]}),
            pd.DataFrame({"mixed": ["01", None, "abc"], "blank": ["", "x", None]}),
            pd.DataFrame({"i": [1, None, 3]}),
        ],
    )
    def test_restore_is_lossless_for_each_dtype(self, tmp_path, frame):
        rollback = build_rollback(frame, tmp_path, "c.csv")
        restored = restore_rollback(rollback)
        assert restored.equals(frame)
        assert (restored.dtypes.astype(str) == frame.dtypes.astype(str)).all()

    def test_a_leading_plus_phone_survives_the_round_trip(self, tmp_path):
        rollback = build_rollback(GOOD, tmp_path, "c.csv")
        assert restore_rollback(rollback)["Phone"][0] == "+14155552671"

    def test_a_tampered_rollback_is_refused(self, tmp_path):
        rollback = build_rollback(GOOD, tmp_path, "c.csv")
        rollback.path.write_text("tampered,data\n1,2\n")
        with pytest.raises(ValueError, match="changed since it was written"):
            restore_rollback(rollback)

    def test_a_missing_rollback_is_reported(self, tmp_path):
        rollback = build_rollback(GOOD, tmp_path, "c.csv")
        rollback.path.unlink()
        with pytest.raises(FileNotFoundError, match="missing"):
            restore_rollback(rollback)

    def test_the_checksum_is_recorded(self, tmp_path):
        rollback = build_rollback(GOOD, tmp_path, "c.csv")
        assert len(rollback.checksum) == 64
        assert rollback.as_dict()["rows"] == 3


class TestDryRun:
    def test_lists_the_columns_that_would_be_renamed(self):
        report = dry_run(GOOD, "hubspot")
        assert report.would_rename["Email Address"] == "email"
        assert report.would_rename["Phone"] == "phone"

    def test_reports_row_counts(self):
        report = dry_run(GOOD, "hubspot")
        assert report.rows_in == 3
        assert report.rows_out == 3

    def test_reports_duplicates_removed(self):
        frame = pd.concat([GOOD, GOOD], ignore_index=True)
        report = dry_run(frame, "hubspot")
        assert report.duplicates_removed == 3

    def test_marks_itself_as_not_written(self):
        assert dry_run(GOOD, "hubspot").written is False

    def test_writes_nothing_to_disk(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        dry_run(GOOD, "hubspot")
        assert list(tmp_path.iterdir()) == []

    def test_render_says_no_files_were_written(self):
        text = dry_run(GOOD, "hubspot").render()
        assert "No files were written." in text
        assert "Email Address -> email" in text


class TestRunbook:
    def test_steps_come_from_the_real_config(self):
        runbook = generate_runbook("hubspot", "Contoso")
        assert runbook.crm == "HubSpot"
        text = runbook.render()
        # Every target field in the config appears as a step.
        from app_files.mappers import load_mapping_config

        for target in load_mapping_config("hubspot").fields:
            assert target.name in text

    def test_includes_a_rollback_step(self):
        assert "rollback" in generate_runbook("hubspot").render().lower()

    def test_schedule_appears_only_when_given(self):
        assert "0 2 * * *" not in generate_runbook("hubspot").render()
        assert "0 2 * * *" in generate_runbook("hubspot", schedule="0 2 * * *").render()

    def test_the_runbook_is_writable(self, tmp_path):
        path = generate_runbook("hubspot").write(tmp_path / "runbook.txt")
        assert path.exists()
        assert "Cutover runbook" in path.read_text()

    def test_as_dict_round_trips(self):
        runbook = generate_runbook("hubspot", "Contoso")
        payload = runbook.as_dict()
        assert payload["project_name"] == "Contoso"
        assert payload["steps"] == runbook.steps
