"""Unit tests for the licensing layer: signing, loading and demo limits."""

from __future__ import annotations

import json

import pytest

from app_files.licensing import (
    DEMO_LIMITS,

    LimitExceededError,
    apply_row_limit,
    check_file_size,
    config_home,
    current_mode,
    license_path,
    load_license,
    resolve_limits,
    sign,
    signature_matches,
    verify_license,
    write_license,
)


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Point the config directory at a temp folder for every test."""
    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


def _license(email="buyer@acme.com", issued="2025-01-01"):
    return {
        "email": email,
        "issued": issued,
        "version": "1.0",
        "signature": sign(email, issued),
    }


# ------------------------------------------------------------------- signing
def test_signature_is_deterministic_and_matches_itself():
    first = sign("buyer@acme.com", "2025-01-01")
    second = sign("buyer@acme.com", "2025-01-01")
    assert first == second
    assert signature_matches("buyer@acme.com", "2025-01-01", first)


def test_signature_changes_with_the_payload():
    assert sign("a@x.com", "2025-01-01") != sign("b@x.com", "2025-01-01")
    assert sign("a@x.com", "2025-01-01") != sign("a@x.com", "2025-01-02")


def test_signature_rejects_a_non_string():
    assert signature_matches("a@x.com", "2025-01-01", None) is False


# ------------------------------------------------------------------ verifying
def test_verify_accepts_a_correctly_signed_license():
    result = verify_license(_license())
    assert result.valid
    assert result.email == "buyer@acme.com"
    assert result.issued == "2025-01-01"


def test_verify_rejects_a_tampered_email():
    data = _license()
    data["email"] = "thief@example.com"
    result = verify_license(data)
    assert not result.valid
    assert "signature" in (result.reason or "").lower()


def test_verify_reports_missing_fields():
    result = verify_license({"email": "a@x.com"})
    assert not result.valid
    assert "issued" in (result.reason or "")


@pytest.mark.parametrize("bad", [None, [], "a string", 42])
def test_verify_rejects_non_objects(bad):
    assert not verify_license(bad).valid


# ------------------------------------------------------------------- loading
def test_load_license_returns_invalid_when_absent():
    result = load_license()
    assert not result.valid
    assert "demo mode" in (result.reason or "").lower()


def test_write_then_load_round_trips():
    path = write_license(_license())
    assert path == license_path()
    loaded = load_license()
    assert loaded.valid
    assert loaded.email == "buyer@acme.com"


def test_write_license_creates_the_config_directory():
    write_license(_license())
    assert config_home().is_dir()


def test_load_license_survives_a_corrupt_file():
    path = license_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    result = load_license()
    assert not result.valid
    assert "could not be read" in (result.reason or "").lower()


def test_license_file_is_written_as_readable_json():
    write_license(_license())
    data = json.loads(license_path().read_text(encoding="utf-8"))
    assert data["email"] == "buyer@acme.com"
    assert data["signature"] == sign("buyer@acme.com", "2025-01-01")


def test_current_mode_reflects_disk_state():
    licence, limits = current_mode()
    assert not licence.valid
    assert limits.demo

    write_license(_license())
    licence, limits = current_mode()
    assert licence.valid
    assert not limits.demo


# -------------------------------------------------------------------- limits
def test_demo_limits_match_the_documented_values():
    assert DEMO_LIMITS["max_rows"] == 500
    assert DEMO_LIMITS["max_file_size_mb"] == 5
    assert DEMO_LIMITS["output_formats"] == ["csv"]
    assert DEMO_LIMITS["watermark"] is True
    assert DEMO_LIMITS["lineage"] is False
    assert DEMO_LIMITS["batch"] is False
    assert DEMO_LIMITS["branding"] is False


def test_full_limits_impose_nothing():
    limits = resolve_limits(True)
    assert not limits.demo
    assert limits.max_rows is None
    assert limits.max_file_size_mb is None
    assert "excel" in limits.output_formats
    assert limits.lineage and limits.batch and limits.branding


def test_unlicensed_resolves_to_demo_limits():
    assert resolve_limits(False).demo
    assert resolve_limits(False).max_rows == 500


def test_check_file_size_allows_a_file_within_the_limit():
    check_file_size(1_000, resolve_limits(False))


def test_check_file_size_rejects_an_oversized_file():
    with pytest.raises(LimitExceededError) as excinfo:
        check_file_size(6 * 1024 * 1024, resolve_limits(False))
    assert "5 MB" in str(excinfo.value)


def test_check_file_size_is_a_no_op_when_licensed():
    check_file_size(500 * 1024 * 1024, resolve_limits(True))


def test_apply_row_limit_truncates_to_the_demo_maximum(contacts_frame):
    frame = contacts_frame
    result = apply_row_limit(frame, resolve_limits(False))
    assert len(result.frame) == min(len(frame), 500)
    assert result.truncated == (len(frame) > 500)


def test_apply_row_limit_keeps_everything_when_licensed():
    import pandas as pd

    frame = pd.DataFrame({"a": range(900)})
    result = apply_row_limit(frame, resolve_limits(True))
    assert len(result.frame) == 900
    assert not result.truncated