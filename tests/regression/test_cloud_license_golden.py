"""Golden file for cloud licensing (Layer 11).

A known activation, two seats and two metered runs must produce a known
subscription state. Timestamps and seat ids vary per run, so the golden pins
the shape a bill is computed from: the account, plan, seat names and active
flags, and the run and row totals.

If this breaks, the change is guilty until proven innocent. Do not regenerate
the expected file to make the test green.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.licensing import sign
from app_files.licensing.cloud import CloudLicense, CloudLicenseStore

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "cloud_license"


def _subscription(tmp_path):
    licence = CloudLicense(CloudLicenseStore(tmp_path / "cloud"))
    issued = "2026-01-01T00:00:00"
    account = "acme@example.com"
    licence.activate(
        account, issued, sign(account, issued), seats=2, expires="2027-01-01T00:00:00"
    )
    licence.add_seat("alice")
    licence.add_seat("bob")
    licence.record_run(rows=1200)
    licence.record_run(rows=300)
    return licence


def test_cloud_subscription_state_golden(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    expected = json.loads((GOLDEN / "expected_state.json").read_text())
    licence = _subscription(tmp_path)

    raw = json.loads((tmp_path / "cloud" / "cloud_license.json").read_text())
    actual = {
        "account": raw["account"],
        "plan": raw["plan"],
        "seats": raw["seats"],
        "seat_names": [seat["name"] for seat in raw["seats_used"]],
        "seats_active": [seat["active"] for seat in raw["seats_used"]],
        "runs": raw["runs"],
        "rows": raw["rows"],
        "trial": raw["trial"],
    }
    assert actual == expected

    usage = licence.usage()
    assert usage["seats_used"] == expected["seats"]
    assert usage["seats_remaining"] == 0


def test_the_golden_subscription_verifies(tmp_path, monkeypatch):
    """A fixture nobody can verify is not a useful golden."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    _subscription(tmp_path)
    record = CloudLicenseStore(tmp_path / "cloud").load()
    assert record is not None
    assert record.verify_signature() is True
    assert record.is_expired() is False
