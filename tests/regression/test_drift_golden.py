"""Golden file for the schema drift gate (Layer 19).

A known baseline schema, a known drifted file, and the exact decision and clean
output the gate and pipeline must produce. Regenerating the expected files to
make this green would delete the only record of what "benign drift" means, so
don't: if the decision changes, decide whether the change is a bug first.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.drift import WARN, DriftGate, SchemaRegistry
from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "drift"


def _gate(tmp_path: Path) -> DriftGate:
    return DriftGate(SchemaRegistry(path=tmp_path / "schemas.json"))


def test_an_added_column_is_benign_drift(tmp_path):
    gate = _gate(tmp_path)
    gate.remember("contacts", read_any(GOLDEN / "baseline.csv"))
    decision = gate.check("contacts", read_any(GOLDEN / "drifted.csv"), "hubspot")
    expected = json.loads((GOLDEN / "expected_decision.json").read_text(encoding="utf-8"))
    assert decision.as_dict() == expected


def test_the_benign_decision_is_a_warning_that_proceeds(tmp_path):
    gate = _gate(tmp_path)
    gate.remember("contacts", read_any(GOLDEN / "baseline.csv"))
    decision = gate.check("contacts", read_any(GOLDEN / "drifted.csv"), "hubspot")
    assert decision.verdict == WARN
    assert decision.proceed is True


def test_the_guarded_run_output_matches_the_golden_clean_file(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    gate = _gate(tmp_path)
    gate.remember("contacts", read_any(GOLDEN / "baseline.csv"))
    result, decision = gate.guarded_run(
        "contacts", read_any(GOLDEN / "drifted.csv"), "hubspot", source_filename="drifted.csv"
    )
    # Compare the exact bytes the writer produces, not a re-read: reading the
    # golden back turns an empty cell into NaN while the pipeline holds None,
    # and that distinction is not what this fixture is protecting.
    produced = result.clean_frame.to_csv(index=False)
    assert produced == (GOLDEN / "expected_clean.csv").read_text(encoding="utf-8")
    assert decision.verdict == WARN


def test_the_pipeline_output_is_unchanged_by_the_gate(tmp_path, monkeypatch):
    """The gate is a policy layer: it does not alter what the pipeline produces."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    frame = read_any(GOLDEN / "drifted.csv")
    plain = run_pipeline(frame, crm="hubspot", source_filename="drifted.csv")
    gate = _gate(tmp_path)
    guarded, _decision = gate.guarded_run(
        "fresh-source", frame, "hubspot", source_filename="drifted.csv"
    )
    assert guarded.clean_frame.to_csv(index=False) == plain.clean_frame.to_csv(index=False)
