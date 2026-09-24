"""Cloud deployment, backup, and disaster recovery."""

from __future__ import annotations

import json
import tarfile

import pytest

from app_files.platform.deployment import (
    BACKUP_FORMAT,
    DeploymentError,
    PROFILES,
    autoflow_home,
    create_backup,
    get_profile,
    read_backup_manifest,
    restore_backup,
    validate_deployment,
    verify_backup,
)


@pytest.fixture
def state_home(tmp_path):
    home = tmp_path / "state"
    home.mkdir()
    return home


# --------------------------------------------------------- deployment profiles
def test_profiles_are_named():
    assert {"local", "container", "cloud"} <= set(PROFILES)


def test_an_unknown_profile_is_a_clear_error():
    with pytest.raises(DeploymentError, match="Unknown deployment profile"):
        get_profile("mars")


def test_port_precedence_matches_the_server():
    report = validate_deployment("container", environ={"PORT": "10000", "DATAREADY_PORT": "8080"})
    port = next(c for c in report.checks if c.name == "port")
    assert "10000" in port.detail


def test_dataready_port_is_used_when_port_is_unset():
    report = validate_deployment("container", environ={"DATAREADY_PORT": "9000"})
    port = next(c for c in report.checks if c.name == "port")
    assert "9000" in port.detail


def test_a_writable_state_home_passes(tmp_path):
    report = validate_deployment("local", state_home=tmp_path / "home", environ={})
    home_check = next(c for c in report.checks if c.name == "state home")
    assert home_check.ok is True


def test_a_persistent_profile_without_a_state_env_warns(tmp_path):
    report = validate_deployment("cloud", state_home=tmp_path / "home", environ={})
    persistence = next(c for c in report.checks if c.name == "persistence")
    assert persistence.ok is False
    assert "lost on redeploy" in persistence.detail


def test_a_persistent_profile_with_a_state_env_passes(tmp_path):
    report = validate_deployment(
        "cloud", state_home=tmp_path / "home", environ={"AUTOFLOW_HOME": str(tmp_path)}
    )
    assert report.ok is True


def test_a_local_profile_needs_no_state_env(tmp_path):
    report = validate_deployment("local", state_home=tmp_path / "home", environ={})
    assert report.ok is True


def test_the_report_serialises(tmp_path):
    report = validate_deployment("local", state_home=tmp_path / "home", environ={})
    body = report.as_dict()
    assert body["ok"] is True
    assert {c["check"] for c in body["checks"]} == {"port", "state home"}


# ------------------------------------------------------------------- backup
def test_a_backup_contains_the_state_files(state_home):
    (state_home / "audit.jsonl").write_text('{"a":1}\n')
    (state_home / "profiles.json").write_text("{}")
    (state_home / "nested").mkdir()
    (state_home / "nested" / "baseline.json").write_text("{}")

    archive = create_backup(state_home.parent / "backup.tar.gz", home=state_home)
    assert archive.exists()

    manifest = read_backup_manifest(archive)
    assert manifest.format == BACKUP_FORMAT
    paths = {entry["path"] for entry in manifest.files}
    assert paths == {"audit.jsonl", "profiles.json", "nested/baseline.json"}


def test_the_manifest_records_a_digest_per_file(state_home):
    (state_home / "a.json").write_text('{"a":1}')
    archive = create_backup(state_home.parent / "b.tar.gz", home=state_home)
    entry = read_backup_manifest(archive).files[0]
    assert len(entry["sha256"]) == 64
    assert entry["size"] == len('{"a":1}')


def test_backup_ignores_files_that_do_not_match(state_home):
    (state_home / "a.json").write_text("{}")
    (state_home / "notes.txt").write_text("ignore me")
    archive = create_backup(state_home.parent / "b.tar.gz", home=state_home)
    paths = {entry["path"] for entry in read_backup_manifest(archive).files}
    assert paths == {"a.json"}


def test_a_missing_backup_is_a_clear_error(tmp_path):
    with pytest.raises(Exception, match="No backup"):
        read_backup_manifest(tmp_path / "nope.tar.gz")


def test_a_non_archive_is_a_clear_error(tmp_path):
    bad = tmp_path / "bad.tar.gz"
    bad.write_text("not a tar")
    with pytest.raises(Exception, match="not a readable archive"):
        read_backup_manifest(bad)


# ------------------------------------------------------------------ restore
def test_a_restore_returns_every_file(state_home, tmp_path):
    (state_home / "audit.jsonl").write_text('{"a":1}\n')
    archive = create_backup(tmp_path / "b.tar.gz", home=state_home)

    fresh = tmp_path / "fresh"
    result = restore_backup(archive, home=fresh)
    assert result.ok is True
    assert result.restored == ["audit.jsonl"]
    assert (fresh / "audit.jsonl").read_text() == '{"a":1}\n'


def test_a_corrupt_file_is_skipped_and_reported(state_home, tmp_path):
    (state_home / "audit.jsonl").write_text('{"a":1}\n')
    archive = create_backup(tmp_path / "b.tar.gz", home=state_home)

    # Rewrite the archive's payload so the digest no longer matches.
    import io

    with tarfile.open(archive, "r:gz") as source:
        members = {m.name: source.extractfile(m).read() for m in source.getmembers()}
    members["files/audit.jsonl"] = b'{"tampered":1}\n'
    with tarfile.open(archive, "w:gz") as dest:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            dest.addfile(info, io.BytesIO(data))

    fresh = tmp_path / "fresh"
    result = restore_backup(archive, home=fresh)
    assert result.ok is False
    assert result.failed[0]["path"] == "audit.jsonl"
    assert result.failed[0]["error"] == "digest mismatch"
    assert not (fresh / "audit.jsonl").exists()


def test_verify_reports_a_good_archive(state_home, tmp_path):
    (state_home / "a.json").write_text("{}")
    archive = create_backup(tmp_path / "b.tar.gz", home=state_home)
    assert verify_backup(archive) == {
        "format": BACKUP_FORMAT,
        "ok": True,
        "checked": 1,
        "good": ["a.json"],
        "bad": [],
    }


def test_verify_detects_a_tampered_archive(state_home, tmp_path):
    (state_home / "a.json").write_text("{}")
    archive = create_backup(tmp_path / "b.tar.gz", home=state_home)

    import io

    with tarfile.open(archive, "r:gz") as source:
        members = {m.name: source.extractfile(m).read() for m in source.getmembers()}
    members["files/a.json"] = b'{"x":1}'
    with tarfile.open(archive, "w:gz") as dest:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            dest.addfile(info, io.BytesIO(data))

    result = verify_backup(archive)
    assert result["ok"] is False
    assert result["bad"] == ["a.json"]


def test_home_defaults_follow_autoflow_home(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "custom"))
    assert autoflow_home() == tmp_path / "custom"