"""The final sweep: one end-to-end run that touches every layer, plus the
failure paths a buyer tries before they buy.

Two things are pinned here.

*One config, everything on.* A single mapping config enables de-duplication,
normalisation, mapping and buyer-defined rules, and the run around it enables
profiling and lineage. From that one run every deliverable must appear on disk.
If a layer silently stops emitting an artefact, this fails rather than leaving a
gap the operator would only notice on a real job.

*Failure paths fail cleanly.* Malformed YAML, a field missing its required
``name``, an empty file, a missing file, an unknown config and unparseable dates
must each produce a clear message and a non-zero exit, never a traceback and
never a silent success.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from app_files.cli import main
from app_files.collaboration.comparison import build_comparison, render_comparison_html
from app_files.collaboration.shareable_report import build_from_result
from app_files.collaboration.workspaces import run_in_workspace
from app_files.ingestion import read_any
from app_files.intelligence import detect, suggest
from app_files.lineage import LineageTracker, render_lineage_html
from app_files.pipeline import run_pipeline, write_deliverables
from app_files.profiling import profile, render_qa_report_with_profile
from app_files.rules import run_rules_for
from app_files.services.bank_reconciliation.reconciler import run_reconciliation

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES = REPO_ROOT / "app_files" / "samples"


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Keep baselines, workspaces and audit trails out of the working tree."""
    home = tmp_path / "home"
    monkeypatch.setenv("AUTOFLOW_HOME", str(home))
    monkeypatch.setenv("DATAREADY_HOME", str(home))
    return home


EVERYTHING_ON = {
    "crm": "Sweep",
    "version": "1.0",
    "cleaning": {
        "remove_duplicates": True,
        "trim_whitespace": True,
        "collapse_internal_whitespace": True,
        "lowercase_emails": True,
        "standardize_dates": True,
        "standardize_phones": True,
        "fix_scientific_notation": True,
        "normalize_unicode": True,
    },
    "fields": [
        {
            "name": "firstname",
            "required": True,
            "transform": "split_full_name_first",
            "aliases": ["First Name", "Given Name", "Full Name"],
        },
        {
            "name": "lastname",
            "required": True,
            "transform": "split_full_name_last",
            "aliases": ["Last Name", "Surname", "Full Name"],
        },
        {
            "name": "email",
            "required": True,
            "unique": True,
            "transform": "email_lowercase",
            "aliases": ["Email Address", "E-mail"],
        },
        {
            "name": "phone",
            "transform": "phone_e164",
            "aliases": ["Phone 1", "Phone Number", "Mobile"],
        },
        {"name": "company", "aliases": ["Company Name", "Organisation", "Account Name"]},
        {"name": "createdate", "transform": "date_iso",
         "aliases": ["Created Date", "Date Created", "Hire Date", "Join Date"]},
    ],
    "rules": [
        {"name": "email_required", "field": "email", "type": "required", "severity": "error"},
        {
            "name": "phone_e164_format",
            "field": "phone",
            "type": "regex",
            "pattern": "^\\+[1-9]\\d{6,14}$",
            "severity": "warning",
            "message": "Phone is not in E.164 form (e.g. +15551234567)",
        },
        {
            "name": "firstname_length",
            "field": "firstname",
            "type": "length",
            "min_length": 2,
            "severity": "warning",
        },
    ],
}


@pytest.fixture
def everything_config(tmp_path) -> Path:
    path = tmp_path / "sweep_everything.yaml"
    path.write_text(yaml.safe_dump(EVERYTHING_ON, sort_keys=False), encoding="utf-8")
    return path


def _run_everything(config_path: Path, source: Path, out: Path):
    """One run with every layer switched on, returning the artefacts written."""
    frame = read_any(source, filename=source.name)
    tracker = LineageTracker()
    result = run_pipeline(
        frame,
        crm=str(config_path),
        lineage_tracker=tracker,
        source_filename=source.name,
        project_name="Final sweep",
    )
    prof = profile(result.clean_frame)

    written = write_deliverables(result, out, include_lineage=True)

    # The scorecard is injected into the rendered report, not baked into the
    # core reporter, so the base report must stay unpolluted.
    report_html = render_qa_report_with_profile(
        result.qa_report_html, result.clean_frame, prof
    )
    (out / "qa_report.html").write_text(report_html, encoding="utf-8")

    comparison = build_comparison(frame, tracker, result.clean_frame)
    (out / "diff_report.html").write_text(
        render_comparison_html(comparison), encoding="utf-8"
    )
    (out / "lineage_view.html").write_text(
        render_lineage_html(tracker), encoding="utf-8"
    )
    (out / "shareable_report.html").write_text(
        build_from_result(
            result,
            comparison_html=render_comparison_html(comparison),
            source_filename=source.name,
            project_name="Final sweep",
        ),
        encoding="utf-8",
    )
    return result, tracker, prof, written, report_html


class TestOneConfigEverythingOn:
    """Every layer on, one real file, and every artefact accounted for."""

    def test_every_deliverable_appears(self, everything_config, tmp_path):
        out = tmp_path / "out"
        result, tracker, prof, written, report_html = _run_everything(
            everything_config, SAMPLES / "messy_contacts.csv", out
        )

        # The mapping config drives dedupe + normalisation + mapping + rules.
        assert result.summary()["duplicates_removed"] >= 1
        assert result.clean_frame["email"].is_unique
        assert result.clean_frame["phone"].fillna("").str.startswith("+").any()

        expected = {
            "clean_data.csv",
            "qa_report.html",
            "mapping_log.csv",
            "cleaning_log.csv",
            "issues.csv",
            "lineage_report.csv",
            "diff_report.html",
            "lineage_view.html",
            "shareable_report.html",
        }
        on_disk = {path.name for path in out.iterdir()}
        assert expected <= on_disk, sorted(expected - on_disk)
        assert all(value.is_file() and value.stat().st_size > 0
                   for value in written.values())

        # Profiling: five dimensions plus an overall.
        assert set(prof.scores) == {
            "completeness", "uniqueness", "validity", "consistency", "timeliness",
        }
        assert 0.0 <= prof.overall <= 100.0
        assert "Quality scorecard" in report_html
        assert "Quality scorecard" not in result.qa_report_html

        # Lineage was recorded, not merely enabled.
        assert not tracker.to_frame().empty

    def test_rules_run_against_the_mapped_frame(self, everything_config, tmp_path):
        result, *_ = _run_everything(
            everything_config, SAMPLES / "messy_contacts.csv", tmp_path / "out"
        )
        rules = run_rules_for(result.clean_frame, str(everything_config))
        assert rules.rules_run == 3
        assert rules.total_failures >= 1
        # Rules are written against source names and resolved to mapped ones.
        assert not getattr(rules, "unmatched_rules", [])

    def test_reconciliation_produces_a_report(self, everything_config, tmp_path):
        from app_files.utilities.reconciliation_dashboard import (
            build_dashboard,
            render_dashboard_html,
        )

        bank = (SAMPLES / "bank_statement.csv").read_bytes()
        ledger = (SAMPLES / "ledger.csv").read_bytes()
        rec = run_reconciliation(bank, ledger, "Date", "Amount", "Date", "Amount")
        assert rec["summary"]["matched"] >= 1
        assert rec["summary"]["missing_from_books"] >= 1

        out = tmp_path / "out"
        out.mkdir()
        dashboard = build_dashboard(rec, amount_column="Amount")
        (out / "reconciliation_report.html").write_text(
            render_dashboard_html(dashboard), encoding="utf-8"
        )
        assert (out / "reconciliation_report.html").stat().st_size > 0

    def test_quality_recording_and_notifications(self, everything_config, tmp_path):
        """The quality baseline and the suggestion list are both produced."""
        result, _, prof, *_ = _run_everything(
            everything_config, SAMPLES / "messy_contacts.csv", tmp_path / "out"
        )
        # Quality recording: the first run establishes a baseline, the second
        # compares against it — which is the only way a trend can exist.
        first = detect(result.clean_frame, name="sweep", quality_score=prof.overall)
        second = detect(result.clean_frame, name="sweep", quality_score=prof.overall)
        assert first.is_baseline_run is True
        assert second.is_baseline_run is False
        assert suggest(result.clean_frame).suggestions

    def test_workspace_run_writes_client_artefacts(self, everything_config, tmp_path):
        run = run_in_workspace(
            "Sweep_Client", SAMPLES / "messy_contacts.csv",
            config=str(everything_config), lineage=True,
        )
        names = {path.name for path in run.output_paths}
        assert any(name.endswith("_qa_report.html") for name in names)
        assert any(name.endswith("_lineage.csv") for name in names)
        assert run.audit_entry, "the run must land in the client audit trail"


class TestFailurePaths:
    """Each must fail cleanly: a message, a non-zero exit, no traceback."""

    def _run(self, capsys, *argv) -> tuple[int, str, str]:
        code = main(list(argv))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    def test_malformed_yaml(self, tmp_path, capsys):
        config = tmp_path / "bad.yaml"
        config.write_text("crm: X\nfields: [ this is : not valid yaml\n", encoding="utf-8")
        code, _, err = self._run(
            capsys, "-i", str(SAMPLES / "messy_contacts.csv"),
            "-c", str(config), "-o", str(tmp_path / "out"),
        )
        assert code == 2
        assert "Traceback" not in err
        assert "could not load the mapping config" in err

    def test_missing_required_field_name(self, tmp_path, capsys):
        config = tmp_path / "nofield.yaml"
        config.write_text(
            "crm: X\nfields:\n  - transform: email_lowercase\n", encoding="utf-8"
        )
        code, _, err = self._run(
            capsys, "-i", str(SAMPLES / "messy_contacts.csv"),
            "-c", str(config), "-o", str(tmp_path / "out"),
        )
        assert code == 2
        assert "Traceback" not in err
        assert "could not load the mapping config" in err

    def test_empty_file(self, tmp_path, capsys):
        empty = tmp_path / "empty.csv"
        empty.write_text("", encoding="utf-8")
        code, _, err = self._run(
            capsys, "-i", str(empty), "-c", "hubspot", "-o", str(tmp_path / "out")
        )
        assert code == 2
        assert "Traceback" not in err
        assert "empty" in err.lower()

    def test_missing_input_file(self, tmp_path, capsys):
        code, _, err = self._run(
            capsys, "-i", str(tmp_path / "nope.csv"),
            "-c", "hubspot", "-o", str(tmp_path / "out"),
        )
        assert code == 2
        assert "Traceback" not in err
        assert "Could not read" in err

    def test_unknown_config_names_the_known_set(self, tmp_path, capsys):
        code, _, err = self._run(
            capsys, "-i", str(SAMPLES / "messy_contacts.csv"),
            "-c", "nosuchcrm", "-o", str(tmp_path / "out"),
        )
        assert code == 2
        assert "Traceback" not in err
        assert "Known CRMs" in err

    def test_unparseable_dates_are_reported_not_dropped(self, tmp_path, capsys):
        """A bad date is a data problem, not a crash and not a silent success."""
        source = tmp_path / "baddates.csv"
        source.write_text(
            "First Name,Last Name,Email Address,Created Date\n"
            "John,Smith,john@x.com,not-a-date\n",
            encoding="utf-8",
        )
        code, out, err = self._run(
            capsys, "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out")
        )
        assert "Traceback" not in err
        assert "Wrote deliverables" in out
        issues = (tmp_path / "out" / "issues.csv").read_text(encoding="utf-8")
        assert "not-a-date" in issues
        # A warning only, so the run is not a hard failure.
        assert code == 0
