"""Golden file for the quality-history binding (Layer 5 trend + baseline).

Known input, a pinned baseline, and the exact baseline comparison the degraded
run must produce. Before this binding, ``TrendStore`` and
``compare_to_stored_baseline`` had no caller in the application: a run scored a
source and forgot it, so a regression could not be detected on the run it
happened.

Do not regenerate ``expected_comparison.json`` to make this green. If a
dimension that fell stops being flagged, the binding has come undone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app_files.profiling import profile
from app_files.profiling.binding import pin_baseline, record_quality

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "quality_history"


@pytest.fixture
def comparison(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    import pandas as pd

    baseline = pd.read_csv(GOLDEN / "contacts.csv")
    degraded = pd.read_csv(GOLDEN / "contacts_degraded.csv")
    pin_baseline("contacts.csv", profile(baseline))
    history = record_quality("contacts.csv", profile(degraded))
    return baseline, degraded, history


def _observed(comparison) -> dict:
    baseline, degraded, history = comparison
    return {
        "alerting": history.alerting,
        "baseline": {
            "overall": round(history.comparison.overall_baseline, 1),
            "dimensions": {
                name: round(value, 1) for name, value in profile(baseline).scores.items()
            },
        },
        "current": {
            "overall": round(history.comparison.overall_current, 1),
            "dimensions": {
                name: round(value, 1) for name, value in profile(degraded).scores.items()
            },
        },
        "drifts": [drift.as_dict() for drift in history.comparison.drifts],
        "regressed": history.comparison.regressed_dimensions,
    }


def test_the_comparison_matches_the_golden_file(comparison):
    expected = json.loads((GOLDEN / "expected_comparison.json").read_text(encoding="utf-8"))
    assert _observed(comparison) == expected


def test_the_golden_run_alerts_on_the_real_drop(comparison):
    """The guard the fixture exists for: a 50-point completeness drop must alert."""
    _, _, history = comparison
    assert history.alerting is True
    assert "completeness" in history.comparison.regressed_dimensions
    assert history.comparison.overall_delta == pytest.approx(-16.7, abs=0.1)


def test_the_baseline_run_is_still_in_the_history(comparison):
    """The pinned run and the degraded run are both recorded, in order."""
    _, _, history = comparison
    assert len(history.history) == 2
    assert history.history[0].overall == pytest.approx(100.0)
    assert history.recorded.id == history.run_id
