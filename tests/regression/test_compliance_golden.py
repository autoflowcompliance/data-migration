"""Golden file for the compliance packet (Layer 13).

A known deployment configuration must produce a known control assessment.
Only the control *statuses* are pinned, not the evidence prose, because the
evidence quotes real paths and a golden that breaks when a checkout moves is a
golden nobody trusts. The statuses are the thing legal reads.

If this breaks, the change is guilty until proven innocent. Do not regenerate
the expected file to make the test green — a control that silently flipped from
``met`` to ``gap`` is exactly what this fixture exists to catch.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.governance import build_packet

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "compliance"


def test_compliance_controls_golden(tmp_path, monkeypatch):
    # Pinned to an empty home so the secret store is known to be absent and the
    # C.3 status is reproducible rather than dependent on the developer's disk.
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    expected = json.loads((GOLDEN / "controls.json").read_text())

    packet = build_packet(retention_days=365)
    actual = {
        "ready": packet.ready,
        "counts": packet.counts,
        "retention": packet.retention.as_dict(),
        "controls": [
            {
                "framework": control.framework,
                "control_id": control.control_id,
                "title": control.title,
                "status": control.status,
            }
            for control in packet.controls
        ],
    }
    assert actual == expected


def test_no_control_is_met_without_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    for control in build_packet().controls:
        assert control.evidence.strip(), f"{control.control_id} claims a status with no evidence"
