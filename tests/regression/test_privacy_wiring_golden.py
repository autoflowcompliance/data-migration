"""Golden file for the privacy binding (Layer 13's read of a config ``privacy:``).

Known input, known masked output, and the exact detections a run must report.
The point of the fixture is ``expected_masked.csv``: before this binding, the
config's ``privacy:`` block was readable but never applied in a run, so the
values in it reached the output intact.

Do not regenerate the expected files to make this green. If the masked CSV
loses the hash or keeps a raw email, the binding has come undone.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.privacy.binding import apply_configured_privacy

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "privacy_wiring"
CONFIG = str(GOLDEN / "crm.yaml")


@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    frame = read_any(GOLDEN / "contacts.csv")
    result = run_pipeline(
        frame, crm=CONFIG, project_name="Golden", source_filename="contacts.csv"
    )
    outcome = apply_configured_privacy(result.clean_frame, CONFIG)
    assert outcome is not None, "the golden config declares privacy"
    return result, outcome


def test_the_unmasked_output_matches_the_golden_file(run):
    """The pipeline's own file is the control: it must stay unmasked."""
    result, _ = run
    produced = result.clean_frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_clean.csv").read_text(encoding="utf-8")


def test_the_masked_output_matches_the_golden_file(run):
    _, outcome = run
    produced = outcome.masked_frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_masked.csv").read_text(encoding="utf-8")


def test_the_detections_match_the_golden_file(run):
    _, outcome = run
    produced = outcome.detections_frame().to_csv(index=False)
    assert produced == (GOLDEN / "expected_detections.csv").read_text(encoding="utf-8")


def test_the_golden_email_is_hashed_not_present(run):
    """The guard the fixture exists for: the raw address is gone, the hash
    is deterministic, and the phone keeps its last four."""
    _, outcome = run
    masked = outcome.masked_frame.to_csv(index=False)
    assert "ann.smith@example.com" not in masked
    assert "f37d883a83178ebc6bedcfb87dd7948377c202068641e2ceaebbfce8d4ffa51f" in masked
    assert "********3000" in masked
    assert "[REDACTED]" in masked
