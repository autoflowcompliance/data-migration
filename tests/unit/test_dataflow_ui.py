"""DataFlow is the shipped UI, so its wiring is worth pinning down.

These tests exercise the real backend — the actual pipeline, profiler and
reconciler — over the bundled samples. Nothing here is mocked: the point is to
catch the failure this UI is most exposed to, which is calling a backend
function under the wrong name or with the wrong shape and having the page
render something plausible but wrong.

Streamlit itself is not exercised here; :mod:`app_files.dataflow.state` holds
the logic precisely so it can be tested without a browser.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.dataflow import state
from app_files.licensing import LimitExceededError, current_mode
from app_files.licensing.limits import Limits, resolve_limits

SAMPLES = Path(__file__).resolve().parents[2] / "app_files" / "samples"
CONTACTS_SAMPLE = SAMPLES / "messy_contacts.csv"
BANK_SAMPLE = SAMPLES / "bank_statement.csv"
LEDGER_SAMPLE = SAMPLES / "ledger.csv"


@pytest.fixture(scope="module")
def limits() -> Limits:
    _, resolved = current_mode()
    return resolved


# --------------------------------------------------------------------------
# Backend wiring
# --------------------------------------------------------------------------
def test_target_configs_come_from_the_mapper():
    configs = state.crm_choices()
    assert configs, "the config directory should yield target systems"
    assert "hubspot" in configs


def test_supported_types_come_from_the_ingestion_registry():
    types = state.supported_types()
    assert "csv" in types
    assert all(not kind.startswith(".") for kind in types)


def test_job_types_and_steps_are_stable():
    assert state.STEPS == ("Upload", "Configure", "Process", "Review")
    assert state.JOB_CRM in state.JOB_TYPES
    assert state.JOB_BANK in state.JOB_TYPES


def test_cleaning_config_is_built_from_the_form_values():
    config = state.build_cleaning_config(
        remove_duplicates=False, date_first=True, default_region="gb"
    )
    assert config.remove_duplicates is False
    assert config.date_first is True
    assert config.default_region == "GB"


def test_cleaning_config_region_falls_back_when_blank():
    assert state.build_cleaning_config(default_region="").default_region == "US"


# --------------------------------------------------------------------------
# The migration run, end to end
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def run(limits: Limits):
    data = CONTACTS_SAMPLE.read_bytes()
    return state.run_crm_migration(data, "messy_contacts.csv", "hubspot", limits)


def test_a_real_export_migrates(run):
    assert run.rows_out > 0
    assert 0.0 <= run.quality_score <= 100.0
    assert run.source_name == "messy_contacts.csv"


def test_the_summary_carries_the_numbers_the_page_shows(run):
    for key in ("rows_out", "quality_score", "duplicates_removed", "errors"):
        assert key in run.summary


def test_dimension_scores_are_real_profiler_output(run):
    scores = run.dimension_scores()
    assert scores, "the profiler should return a score per dimension"
    assert set(scores) <= set(state.DIMENSIONS)
    assert all(0.0 <= value <= 100.0 for value in scores.values())


def test_every_download_the_page_offers_is_renderable(run):
    artefacts = run.downloads()
    labels = [label for label, *_ in artefacts]
    assert "Clean CSV" in labels
    assert "QA Report" in labels
    assert "Mapping Log" in labels
    for label, _icon, payload, file_name, mime in artefacts:
        assert payload, f"{label} produced an empty payload"
        assert file_name and mime


def test_the_demo_row_cap_is_actually_applied():
    """The page must not bypass the licence when it runs the pipeline."""
    demo = resolve_limits(license_valid=False)
    assert demo.demo
    data = CONTACTS_SAMPLE.read_bytes()
    result = state.run_crm_migration(data, "messy_contacts.csv", "hubspot", demo)
    assert result.rows_out <= demo.max_rows


def test_an_oversize_upload_is_refused_before_it_runs():
    demo = resolve_limits(license_valid=False)
    assert demo.max_file_size_mb == 5
    huge = b"col\n" + b"x\n" * (7 * 1024 * 1024)
    with pytest.raises(LimitExceededError) as caught:
        state.run_crm_migration(huge, "huge.csv", "hubspot", demo)
    assert "MB" in str(caught.value)


def test_an_upload_under_the_cap_is_accepted():
    """Guards the test above: a small file must not be swept up by the check."""
    demo = resolve_limits(license_valid=False)
    data = CONTACTS_SAMPLE.read_bytes()
    assert len(data) < demo.max_file_size_mb * 1024 * 1024
    assert state.run_crm_migration(data, "messy_contacts.csv", "hubspot", demo).rows_out > 0


def test_an_unknown_extension_is_refused_with_advice():
    with pytest.raises(ValueError) as caught:
        state.run_crm_migration(b"x", "notes.rtf", "hubspot", resolve_limits(False))
    message = str(caught.value)
    assert "not a supported file type" in message
    assert "csv" in message


def test_migration_error_message_keeps_actionable_text():
    exc = ValueError("'.rtf' is not a supported file type. Supported: .csv")
    assert state.migration_error_message(exc) == str(exc)


def test_migration_error_message_wraps_the_unexpected():
    message = state.migration_error_message(KeyError("Email Address"))
    assert message.startswith("Something went wrong")
    assert "Email Address" in message


# --------------------------------------------------------------------------
# Bank reconciliation, end to end
# --------------------------------------------------------------------------
@pytest.mark.skipif(not BANK_SAMPLE.is_file(), reason="bank sample not bundled")
def test_reconciliation_runs_over_the_samples(limits: Limits):
    result = state.run_bank_reconciliation(
        BANK_SAMPLE.read_bytes(), LEDGER_SAMPLE.read_bytes(), limits
    )
    counts = state.reconciliation_counts(result)
    assert set(counts) == {"matched", "missing_from_books", "never_cleared"}
    assert counts["matched"] > 0


@pytest.mark.skipif(not BANK_SAMPLE.is_file(), reason="bank sample not bundled")
def test_reconciliation_downloads_name_their_own_frames(limits: Limits):
    result = state.run_bank_reconciliation(
        BANK_SAMPLE.read_bytes(), LEDGER_SAMPLE.read_bytes(), limits
    )
    artefacts = state.reconciliation_downloads(result)
    assert [label for label, *_ in artefacts] == ["Missing from books", "Never cleared"]
    for _label, _icon, payload, file_name, _mime in artefacts:
        assert file_name.endswith(".csv")
        assert isinstance(payload, str)


def test_reconciliation_checks_the_upload_size_before_reading_it():
    demo = resolve_limits(license_valid=False)
    huge = b"Date,Amount\n" + b"2024-01-01,1.00\n" * (400 * 1024)
    with pytest.raises(LimitExceededError):
        state.run_bank_reconciliation(huge, huge, demo)


# --------------------------------------------------------------------------
# The bits that are easy to get subtly wrong
# --------------------------------------------------------------------------
def test_file_size_label_is_human_readable():
    assert state.file_size("a.csv", b"x" * 10)[1] == "a.csv · 10 B"
    assert "KB" in state.file_size("a.csv", b"x" * 2048)[1]
    assert "MB" in state.file_size("a.csv", b"x" * (2 * 1024 * 1024))[1]


def test_empty_frame_guard_rejects_empty_frames():
    import pandas as pd

    assert state.empty_frame_guard(pd.DataFrame()) is None
    frame = pd.DataFrame({"a": [1]})
    assert state.empty_frame_guard(frame) is frame
    assert state.empty_frame_guard("not a frame") is None
