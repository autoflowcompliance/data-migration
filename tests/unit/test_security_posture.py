"""Encryption at rest and the compliance posture report."""

from __future__ import annotations

import os
import stat

import pytest

from app_files.platform import (
    ENV_KEY,
    EncryptionError,
    KeyMissing,
    assess_compliance,
    decrypt_bytes,
    decrypt_file,
    encrypt_bytes,
    encrypt_file,
    generate_key,
    load_key,
)
from app_files.platform.security import platform_home, write_posture_report


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    monkeypatch.delenv(ENV_KEY, raising=False)
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "home"))
    return tmp_path


# ------------------------------------------------------------------- keys
def test_generating_a_key_writes_an_owner_only_file(tmp_path):
    path = tmp_path / "key"
    generate_key(path)
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode == stat.S_IRUSR | stat.S_IWUSR
    assert path.read_bytes()


def test_generating_a_key_refuses_to_overwrite(tmp_path):
    path = tmp_path / "key"
    generate_key(path)
    with pytest.raises(EncryptionError, match="already exists"):
        generate_key(path)


def test_loading_a_missing_key_is_a_clear_error(tmp_path):
    with pytest.raises(KeyMissing, match="No encryption key"):
        load_key(tmp_path / "nope")


def test_load_key_can_create_on_demand(tmp_path):
    key = load_key(tmp_path / "key", create=True)
    assert key
    assert (tmp_path / "key").exists()


def test_an_environment_key_is_used_when_present(monkeypatch):
    from cryptography.fernet import Fernet

    generated = Fernet.generate_key().decode()
    monkeypatch.setenv(ENV_KEY, generated)
    assert load_key() == generated.encode()


def test_a_malformed_environment_key_is_rejected(monkeypatch):
    monkeypatch.setenv(ENV_KEY, "not-a-key")
    with pytest.raises(EncryptionError, match="not a valid Fernet key"):
        load_key()


# --------------------------------------------------------------- round trip
def test_bytes_round_trip():
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    token = encrypt_bytes(b"hello world", key=key)
    assert token != b"hello world"
    assert decrypt_bytes(token, key=key) == b"hello world"


def test_decrypting_with_the_wrong_key_fails_cleanly():
    from cryptography.fernet import Fernet

    token = encrypt_bytes(b"secret", key=Fernet.generate_key())
    with pytest.raises(EncryptionError, match="Could not decrypt"):
        decrypt_bytes(token, key=Fernet.generate_key())


def test_file_round_trip(tmp_path):
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    source = tmp_path / "clean_data.csv"
    source.write_text("email\nann@x.com\n")

    encrypted = encrypt_file(source, key=key)
    assert encrypted.name == "clean_data.csv.enc"
    assert encrypted.read_bytes() != source.read_bytes()

    restored = decrypt_file(encrypted, key=key)
    assert restored.read_text() == "email\nann@x.com\n"


def test_encrypting_can_remove_the_plaintext(tmp_path):
    from cryptography.fernet import Fernet

    source = tmp_path / "secret.csv"
    source.write_text("x")
    encrypt_file(source, remove_plaintext=True, key=Fernet.generate_key())
    assert not source.exists()


def test_decrypting_rejects_a_file_without_the_suffix(tmp_path):
    from cryptography.fernet import Fernet

    source = tmp_path / "plain.csv"
    source.write_text("x")
    with pytest.raises(EncryptionError, match="does not look encrypted"):
        decrypt_file(source, key=Fernet.generate_key())


def test_encrypting_a_missing_file_is_a_clear_error(tmp_path):
    with pytest.raises(EncryptionError, match="missing file"):
        encrypt_file(tmp_path / "nope.csv")


# ------------------------------------------------------------ compliance
def test_posture_reports_unconfigured_encryption_when_no_key(tmp_path):
    report = assess_compliance()
    controls = {c.name: c for c in report.controls}
    assert controls["Encryption key configured"].status == "not_configured"


def test_posture_reports_configured_encryption_once_a_key_exists():
    generate_key()
    report = assess_compliance()
    controls = {c.name: c for c in report.controls}
    assert controls["Encryption key configured"].status == "configured"


def test_posture_marks_host_level_controls_as_manual():
    report = assess_compliance()
    controls = {c.name: c for c in report.controls}
    assert controls["Host disk encryption"].status == "manual"
    assert controls["Data retention"].status == "manual"


def test_posture_checks_the_audit_chain_when_given(tmp_path):
    from app_files.platform import AuditRecord

    audit = tmp_path / "audit.jsonl"
    record = AuditRecord.build(
        tenant="acme", action="run", actor="ann", target="file", ip="127.0.0.1",
        detail={}, previous_hash="0" * 64,
    )
    audit.write_text(__import__("json").dumps(record.as_dict()) + "\n")

    report = assess_compliance(audit_path=audit, tenants_root=tmp_path)
    controls = {c.name: c for c in report.controls}
    assert controls["Tamper-evident audit log"].status == "configured"
    assert controls["Tenant isolation"].status == "configured"


def test_posture_detects_a_broken_audit_chain(tmp_path):
    from app_files.platform import AuditRecord

    audit = tmp_path / "audit.jsonl"
    record = AuditRecord.build(
        tenant="acme", action="run", actor="ann", target="file", ip="127.0.0.1",
        detail={}, previous_hash="0" * 64,
    )
    tampered = record.as_dict()
    tampered["actor"] = "attacker"
    audit.write_text(__import__("json").dumps(tampered) + "\n")

    report = assess_compliance(audit_path=audit)
    controls = {c.name: c for c in report.controls}
    assert controls["Tamper-evident audit log"].status == "not_configured"


def test_posture_counts_configured_controls():
    generate_key()
    report = assess_compliance()
    assert report.configured >= 2  # encryption key + RBAC


def test_posture_renders_as_text():
    generate_key()
    text = assess_compliance().render_text()
    assert "Compliance posture" in text
    assert "[x]" in text
    assert "controls configured." in text


def test_posture_writes_a_json_report(tmp_path):
    report = assess_compliance()
    path = write_posture_report(report, tmp_path / "posture.json")
    assert path.exists()
    assert __import__("json").loads(path.read_text())["total"] == len(report.controls)