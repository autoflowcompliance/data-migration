"""Golden file for Module 10: a known file, a known SLA, a known verdict.

The SLA is a gate, so the thing worth pinning is that it fires on the run it
should and stays quiet on the run it should not. ``contacts.csv`` is complete
and passes; ``contacts_degraded.csv`` loses four of eight cells and must breach
completeness at 50% against a 98% floor.

Do not regenerate ``expected_sla.json`` to make this green. If the degraded run
stops breaching, the gate has come undone and that is the whole point of the
module.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from app_files.quality.binding import bind_quality

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "quality_sla"


@pytest.fixture
def bound():
    config = yaml.safe_load((GOLDEN / "quality.yaml").read_text(encoding="utf-8"))
    good = pd.read_csv(GOLDEN / "contacts.csv")
    degraded = pd.read_csv(GOLDEN / "contacts_degraded.csv")
    return bind_quality(good, config), bind_quality(degraded, config)


def _observed(bound) -> dict:
    good, degraded = bound
    return {
        "good": {
            "overall": round(float(good.profile_result.overall), 1),
            "scores": {
                name: round(float(value), 1)
                for name, value in good.profile_result.scores.items()
            },
            "sla_passed": good.verdict.passed,
            "breaches": good.verdict.summary()["breaches"],
            "skipped": good.verdict.skipped,
        },
        "degraded": {
            "overall": round(float(degraded.profile_result.overall), 1),
            "scores": {
                name: round(float(value), 1)
                for name, value in degraded.profile_result.scores.items()
            },
            "sla_passed": degraded.verdict.passed,
            "breaches": degraded.verdict.summary()["breaches"],
            "skipped": degraded.verdict.skipped,
        },
    }


def test_the_verdict_matches_the_golden_file(bound):
    expected = json.loads((GOLDEN / "expected_sla.json").read_text(encoding="utf-8"))
    assert _observed(bound) == expected


def test_the_clean_run_meets_the_sla(bound):
    good, _ = bound
    assert good.verdict.passed is True
    assert good.verdict.breaches == []


def test_the_degraded_run_breaches_on_the_real_drop(bound):
    """The guard the fixture exists for: a 50-point completeness drop must fire."""
    _, degraded = bound
    assert degraded.verdict.passed is False
    assert [breach.dimension for breach in degraded.verdict.breaches] == ["completeness"]
    assert degraded.verdict.breaches[0].actual == pytest.approx(0.5)
    assert degraded.verdict.breaches[0].required == pytest.approx(0.98)


def test_the_declared_action_is_carried_through(bound):
    from app_files.quality import Action

    good, _ = bound
    assert good.action is Action.BLOCK
    assert good.threshold == pytest.approx(5.0)


def test_the_uniqueness_floor_does_not_fire_on_a_unique_file(bound):
    """A declared floor that the data meets must stay silent.

    Both files have unique emails, so the 0.99 uniqueness floor must not
    appear in either verdict — a gate that fires on everything is not a gate.
    """
    good, degraded = bound
    assert "uniqueness" not in [b.dimension for b in good.verdict.breaches]
    assert "uniqueness" not in [b.dimension for b in degraded.verdict.breaches]
