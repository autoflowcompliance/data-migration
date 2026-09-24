"""Golden file for the dedupe binding (Layer 2 fuzzy dedupe).

Known input, known deduped output, and the exact merge log. Before this
binding, the config's ``dedupe:`` block was readable (``FuzzyRule.from_dict``)
but no run applied it, so every near-duplicate survived.

Do not regenerate the expected files to make this green. If the deduped CSV
loses a merge or a score, the binding has come undone.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.dedupe.binding import apply_configured_dedupe
from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "dedupe_wiring"
CONFIG = str(GOLDEN / "crm.yaml")


@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    frame = read_any(GOLDEN / "contacts.csv")
    result = run_pipeline(
        frame, crm=CONFIG, project_name="Golden", source_filename="contacts.csv"
    )
    outcome = apply_configured_dedupe(result.clean_frame, CONFIG)
    assert outcome is not None, "the golden config declares dedupe"
    return result, outcome


def test_the_undeduped_output_matches_the_golden_file(run):
    result, _ = run
    produced = result.clean_frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_clean.csv").read_text(encoding="utf-8")


def test_the_deduped_output_matches_the_golden_file(run):
    _, outcome = run
    produced = outcome.frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_deduped.csv").read_text(encoding="utf-8")


def test_the_merge_log_matches_the_golden_file(run):
    _, outcome = run
    produced = outcome.merges_frame().to_csv(index=False)
    assert produced == (GOLDEN / "expected_merges.csv").read_text(encoding="utf-8")


def test_the_golden_run_folds_the_near_duplicates(run):
    """The guard the fixture exists for: the spec's John/Jon pair merges at
    0.85, and the score that drove the merge is recorded."""
    _, outcome = run
    assert outcome.duplicates_removed == 2
    deduped = outcome.frame.to_csv(index=False)
    assert "John,Smith" in deduped
    assert "Jon,Smith" not in deduped
    assert "0.9333" in outcome.merges_frame().to_csv(index=False)