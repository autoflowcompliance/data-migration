"""Golden file for the normalization binding (Layer 2 address/currency).

Known input, known normalised output, and the exact conversion audit trail.
The point of the fixture is ``expected_normalized.csv``: before this binding,
the config's ``normalization:`` block was readable but no run applied it, so
addresses stayed in their raw formats and currencies stayed mixed.

Do not regenerate the expected files to make this green. If the normalised CSV
loses the canonical street form or a conversion, the binding has come undone.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.ingestion import read_any
from app_files.normalization.binding import apply_configured_normalization
from app_files.pipeline import run_pipeline

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "normalization_wiring"
CONFIG = str(GOLDEN / "crm.yaml")


@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    frame = read_any(GOLDEN / "orders.csv")
    result = run_pipeline(
        frame, crm=CONFIG, project_name="Golden", source_filename="orders.csv"
    )
    outcome = apply_configured_normalization(result.clean_frame, CONFIG)
    assert outcome is not None, "the golden config declares normalization"
    return result, outcome


def test_the_unnormalised_output_matches_the_golden_file(run):
    """The pipeline's own file is the control: it must stay un-normalised."""
    result, _ = run
    produced = result.clean_frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_clean.csv").read_text(encoding="utf-8")


def test_the_normalized_output_matches_the_golden_file(run):
    _, outcome = run
    produced = outcome.frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_normalized.csv").read_text(encoding="utf-8")


def test_the_conversion_audit_matches_the_golden_file(run):
    _, outcome = run
    produced = outcome.conversions_frame().to_csv(index=False)
    assert produced == (GOLDEN / "expected_conversions.csv").read_text(encoding="utf-8")


def test_the_golden_addresses_are_canonical(run):
    """The guard the fixture exists for: five-ish formats collapse to one
    canonical street form and every amount carries its rate and date."""
    _, outcome = run
    normalized = outcome.frame.to_csv(index=False)
    assert "123 N Maple Avenue, Springfield, IL 62704" in normalized
    assert "456 S Oak Street, Springfield, IL 62704" in normalized
    assert "1080.0" in normalized
    assert "635.0" in normalized
