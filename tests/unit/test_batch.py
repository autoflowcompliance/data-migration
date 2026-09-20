"""Unit tests for the batch layer: folder iteration, summaries and dashboards."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.batch import (
    COLUMNS,
    process_one,
    run_batch,
    supported_files,
    summary_frame,
)
from app_files.batch.dashboard import render_dashboard


@pytest.fixture
def inbox(tmp_path, contacts_csv, bank_csv, ledger_csv) -> Path:
    """A folder holding a few real samples, as a client's inbox would."""
    folder = tmp_path / "inbox"
    folder.mkdir()
    for source in (contacts_csv, bank_csv, ledger_csv):
        (folder / source.name).write_bytes(source.read_bytes())
    return folder


# ------------------------------------------------------------------- scanning
def test_supported_files_finds_known_extensions(inbox):
    names = {path.name for path in supported_files(inbox)}
    assert names == {"messy_contacts.csv", "bank_statement.csv", "ledger.csv"}


def test_supported_files_ignores_other_extensions(inbox):
    # ``.txt`` is itself a supported tabular format, so pick something the
    # ingestion layer genuinely cannot read.
    (inbox / "diagram.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    assert "diagram.png" not in {path.name for path in supported_files(inbox)}


def test_supported_files_ignores_subdirectories(inbox):
    (inbox / "nested").mkdir()
    assert all(path.is_file() for path in supported_files(inbox))


def test_supported_files_returns_empty_for_a_missing_folder(tmp_path):
    assert supported_files(tmp_path / "nope") == []


def test_supported_files_is_sorted_case_insensitively(inbox):
    names = [path.name for path in supported_files(inbox)]
    assert names == sorted(names, key=str.lower)


# ------------------------------------------------------------------ one file
def test_process_one_writes_a_per_file_folder(inbox, tmp_path):
    out = tmp_path / "out"
    item = process_one(inbox / "messy_contacts.csv", "hubspot", out / "messy_contacts")
    assert item.ok
    assert item.rows_in > 0
    assert (out / "messy_contacts" / "clean_data.csv").is_file()


def test_process_one_reports_a_failure_without_raising(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_bytes(b"\x00\x01\x02 not a csv at all")
    item = process_one(bad, "hubspot", tmp_path / "out")
    assert item.status == "failed"
    assert item.error


def test_process_one_treats_an_empty_file_as_a_failure(tmp_path):
    """An empty read is not a success: a green tick beside it would mislead."""
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    item = process_one(empty, "hubspot", tmp_path / "out")
    assert item.status == "failed"
    assert "no rows" in item.error.lower()


def test_process_one_treats_a_headerless_file_as_a_failure(tmp_path):
    headerless = tmp_path / "headerless.csv"
    headerless.write_text("\n\n\n", encoding="utf-8")
    item = process_one(headerless, "hubspot", tmp_path / "out")
    assert item.status == "failed"


def test_process_one_excludes_failed_files_from_rows_out(tmp_path, contacts_csv):
    bad = tmp_path / "bad.csv"
    bad.write_text("", encoding="utf-8")
    item = process_one(bad, "hubspot", tmp_path / "out")
    assert item.rows_out == 0


# ------------------------------------------------------------------ the batch
def test_run_batch_processes_every_file(inbox, tmp_path):
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    assert result.processed == 3
    assert result.succeeded == 3
    assert result.failed == 0


def test_run_batch_writes_the_combined_summary_and_dashboard(inbox, tmp_path):
    out = tmp_path / "out"
    run_batch(inbox, template="hubspot", output_dir=out)
    assert (out / "summary.csv").is_file()
    assert (out / "dashboard.html").is_file()


def test_run_batch_writes_one_folder_per_file(inbox, tmp_path):
    out = tmp_path / "out"
    run_batch(inbox, template="hubspot", output_dir=out)
    for stem in ("messy_contacts", "bank_statement", "ledger"):
        assert (out / stem / "clean_data.csv").is_file()


def test_a_bad_file_does_not_sink_the_batch(inbox, tmp_path):
    """The whole point of the layer: forty good files survive one bad scan."""
    (inbox / "broken.csv").write_text("", encoding="utf-8")
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    assert result.processed == 4
    assert result.succeeded == 3
    assert result.failed == 1
    assert any(item.error for item in result.items if not item.ok)


def test_run_batch_reports_progress_before_each_file(inbox, tmp_path):
    seen: list[tuple[int, int, str]] = []
    run_batch(
        inbox,
        template="hubspot",
        output_dir=tmp_path / "out",
        on_progress=lambda i, total, name: seen.append((i, total, name)),
    )
    assert [index for index, _, _ in seen] == [1, 2, 3]
    assert all(total == 3 for _, total, _ in seen)


def test_run_batch_can_skip_writing_summary_files(inbox, tmp_path):
    out = tmp_path / "out"
    result = run_batch(
        inbox, template="hubspot", output_dir=out, write_summary_files=False
    )
    assert result.processed == 3
    assert not (out / "summary.csv").exists()


def test_run_batch_accepts_an_explicit_file_list(inbox, tmp_path):
    chosen = [inbox / "messy_contacts.csv"]
    result = run_batch(
        inbox, template="hubspot", output_dir=tmp_path / "out", files=chosen
    )
    assert result.processed == 1
    assert result.items[0].file == "messy_contacts.csv"


def test_run_batch_on_an_empty_folder_is_not_an_error(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = run_batch(empty, template="hubspot", output_dir=tmp_path / "out")
    assert result.processed == 0
    assert result.average_score == 0.0


def test_average_score_only_counts_successful_files(inbox, tmp_path):
    (inbox / "broken.csv").write_text("", encoding="utf-8")
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    ok_scores = [item.score for item in result.items if item.ok]
    assert result.average_score == pytest.approx(sum(ok_scores) / len(ok_scores), abs=0.1)


def test_total_rows_out_excludes_failures(inbox, tmp_path):
    (inbox / "broken.csv").write_text("", encoding="utf-8")
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    assert result.total_rows_out == sum(item.rows_out for item in result.items if item.ok)


def test_batch_result_serialises(inbox, tmp_path):
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    data = result.as_dict()
    assert data["processed"] == 3
    assert len(data["results"]) == 3
    assert set(data["results"][0]) >= {"file", "status", "rows_in", "rows_out", "score"}


# ------------------------------------------------------------------- summary
def test_summary_frame_has_the_documented_columns(inbox, tmp_path):
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    frame = summary_frame(result)
    assert list(frame.columns) == list(COLUMNS)


def test_summary_csv_matches_the_frame(inbox, tmp_path):
    out = tmp_path / "out"
    result = run_batch(inbox, template="hubspot", output_dir=out)
    written = pd.read_csv(out / "summary.csv", dtype=str, keep_default_na=False)
    assert len(written) == result.processed
    assert list(written.columns) == list(COLUMNS)


# ----------------------------------------------------------------- dashboard
def test_dashboard_lists_every_file(inbox, tmp_path):
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    html = render_dashboard(result)
    for name in ("messy_contacts.csv", "bank_statement.csv", "ledger.csv"):
        assert name in html


def test_dashboard_surfaces_a_failure(inbox, tmp_path):
    (inbox / "broken.csv").write_text("", encoding="utf-8")
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    html = render_dashboard(result)
    assert "broken.csv" in html
    assert "failed" in html.lower()


def test_dashboard_is_valid_standalone_html(inbox, tmp_path):
    result = run_batch(inbox, template="hubspot", output_dir=tmp_path / "out")
    html = render_dashboard(result)
    assert html.lstrip().lower().startswith("<!doctype html>")
    assert "</html>" in html