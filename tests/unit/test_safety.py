"""Pre-migration analysis, dry run, rollback files and the cutover runbook.

The dry-run test is the important one: it asserts the pipeline runs and reports
a plan while the output directory stays empty. Nobody should be able to claim
"dry run" and find they wrote files.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from app_files.safety import (
    analyse_before_migration,
    build_cutover_runbook,
    build_rollback_file,
    dry_run,
    write_cutover_runbook,
    write_pre_migration_report,
)

MESSY = pd.DataFrame(
    {
        "First Name": ["Ann", "Bob", "Ann", "Cara"],
        "Last Name": ["Lee", "Ray", "Lee", "Kim"],
        "Email Address": ["ANN@X.com", "bob@x.com", "ANN@X.com", ""],
        "Phone": ["(555) 123-4567", "555.987.6543", "(555) 123-4567", "5551112222"],
    }
)


# ------------------------------------------------------------- pre-migration
def test_analysis_reports_quality_issues_and_confidence():
    report = analyse_before_migration(MESSY, "hubspot")
    assert report.rows == 4
    assert report.columns == 4
    assert report.quality["overall"] > 0
    assert set(report.quality["scores"]) == {
        "completeness", "uniqueness", "validity", "consistency", "timeliness"
    }
    assert report.mapping_confidence["mapped_fields"] > 0


def test_analysis_flags_risks_without_writing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    report = analyse_before_migration(MESSY, "hubspot")
    # A duplicate row and a blank email are both risks worth naming.
    assert any("duplicate" in note.lower() for note in report.risk_notes)
    # Nothing was written: the directory is still empty.
    assert list(tmp_path.iterdir()) == []


def test_analysis_markdown_is_a_standalone_deliverable(tmp_path):
    report = analyse_before_migration(MESSY, "hubspot")
    path = write_pre_migration_report(report, tmp_path / "pre_migration.md")
    text = path.read_text()
    assert "# Pre-migration analysis" in text
    assert "Quality by dimension" in text
    assert "Overall quality" in text


def test_unmapped_columns_are_listed():
    frame = MESSY.assign(Internal_Ref=["a", "b", "c", "d"])
    report = analyse_before_migration(frame, "hubspot")
    assert "Internal_Ref" in report.unmapped_columns


# ------------------------------------------------------------------ dry run
def test_dry_run_reports_a_plan_and_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plan = dry_run(MESSY, "hubspot")
    assert plan.rows_in == 4
    assert plan.duplicates_removed == 1
    assert plan.rows_out == 3
    assert plan.row_drop == 1
    names = {o["name"] for o in plan.outputs}
    assert {"clean_data", "qa_report", "mapping_log", "issues", "lineage_report"} <= names
    # The critical guarantee: not one file was written.
    assert list(tmp_path.iterdir()) == []


def test_dry_run_output_names_match_the_real_run(tmp_path):
    from app_files.pipeline import run_pipeline, write_deliverables

    plan = dry_run(MESSY, "hubspot", output_format="csv")
    result = run_pipeline(MESSY, "hubspot", run_structural_check=False)
    written = write_deliverables(result, tmp_path / "out", output_format="csv")

    planned = {o["name"] for o in plan.outputs}
    assert planned <= set(written)
    for entry in plan.outputs:
        if "rows" in entry:
            assert written[entry["name"]].exists()
    # The clean file's planned row count equals the real one.
    clean_rows = len(pd.read_csv(written["clean_data"]))
    assert clean_rows == plan.rows_out


def test_dry_run_honours_output_format():
    plan = dry_run(MESSY, "hubspot", output_format="json")
    clean = next(o for o in plan.outputs if o["name"] == "clean_data")
    assert clean["filename"] == "clean_data.json"


# ------------------------------------------------------------- rollback file
def test_rollback_records_changes_and_removals(tmp_path):
    rollback = build_rollback_file(MESSY, "hubspot", source_filename="messy.csv")
    kinds = {entry.kind for entry in rollback.entries}
    assert "changed" in kinds  # "ANN@X.com" -> "ann@x.com"
    assert "removed" in kinds  # the duplicate row
    assert rollback.rows_in == 4
    assert rollback.rows_out == 3


def test_rollback_file_is_json_round_trippable(tmp_path):
    rollback = build_rollback_file(MESSY, "hubspot")
    path = rollback.write(tmp_path / "rollback.json")
    payload = json.loads(path.read_text())
    assert payload["rows_in"] == 4
    assert payload["changed"] >= 1
    assert isinstance(payload["entries"], list)


def test_rollback_entry_carries_before_and_after(tmp_path):
    rollback = build_rollback_file(MESSY, "hubspot")
    changed = [e for e in rollback.entries if e.kind == "changed"]
    email_change = next(e for e in changed if e.column == "Email Address")
    assert email_change.before == "ANN@X.com"
    assert email_change.after == "ann@x.com"


# ---------------------------------------------------------- cutover runbook
def test_runbook_is_a_checklist_with_real_numbers(tmp_path):
    rollback = build_rollback_file(MESSY, "hubspot", source_filename="messy.csv")
    plan = dry_run(MESSY, "hubspot")
    runbook = build_cutover_runbook(rollback, dry_run_plan=plan, output_dir="out", owner="Ann")

    assert "# Cutover runbook" in runbook
    assert "**4** → rows out: **3**" in runbook
    assert "Owner: Ann" in runbook
    assert "1. [ ]" in runbook  # it is a checklist
    assert "Rollback" in runbook
    assert "clean_data.csv" in runbook


def test_runbook_can_be_written_to_disk(tmp_path):
    rollback = build_rollback_file(MESSY, "hubspot")
    content = build_cutover_runbook(rollback)
    path = write_cutover_runbook(content, tmp_path / "RUNBOOK.md")
    assert path.read_text().startswith("# Cutover runbook")