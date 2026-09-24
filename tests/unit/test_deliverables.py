"""Signed deliverables and push to a destination."""

from __future__ import annotations

import json

import pytest

from app_files.distribution.deliverables import (
    DeliveryError,
    file_digest,
    plan_push,
    push_deliverables,
    sign_deliverables,
    sign_file,
    verify_bundle,
    verify_file,
)


@pytest.fixture
def bundle_dir(tmp_path):
    (tmp_path / "clean_data.csv").write_text("email\nann@x.com\n")
    (tmp_path / "qa_report.html").write_text("<html>ok</html>")
    (tmp_path / "issues.csv").write_text("row,message\n")
    return tmp_path


def test_sign_file_returns_a_detached_record(bundle_dir):
    record = sign_file(bundle_dir / "clean_data.csv")
    assert record["file"] == "clean_data.csv"
    assert record["algorithm"] == "HMAC-SHA256"
    assert record["signature"]
    assert record["digest"] == file_digest(bundle_dir / "clean_data.csv")


def test_signature_verifies_against_the_original(bundle_dir):
    target = bundle_dir / "clean_data.csv"
    record = sign_file(target)
    assert verify_file(target, record) is True


def test_tampering_breaks_the_signature(bundle_dir):
    target = bundle_dir / "clean_data.csv"
    record = sign_file(target)
    target.write_text("email\nattacker@evil.com\n")
    assert verify_file(target, record) is False


def test_signing_a_missing_file_is_a_clear_error(bundle_dir):
    with pytest.raises(DeliveryError, match="missing file"):
        sign_file(bundle_dir / "nope.csv")


def test_sign_deliverables_writes_sidecars_and_a_manifest(bundle_dir):
    bundle = sign_deliverables(bundle_dir)
    assert (bundle_dir / "manifest.json").exists()
    assert (bundle_dir / "clean_data.csv.sig").exists()
    names = {record["file"] for record in bundle.records}
    assert names == {"clean_data.csv", "qa_report.html", "issues.csv"}
    # Signatures are not themselves signed.
    assert not any(name.endswith(".sig") for name in names)


def test_a_whole_bundle_verifies(bundle_dir):
    sign_deliverables(bundle_dir)
    result = verify_bundle(bundle_dir)
    assert result["ok"] is True
    assert result["checked"] == 3
    assert result["failures"] == []


def test_bundle_verification_names_the_bad_file(bundle_dir):
    sign_deliverables(bundle_dir)
    (bundle_dir / "issues.csv").write_text("tampered\n")
    result = verify_bundle(bundle_dir)
    assert result["ok"] is False
    assert result["failures"] == ["issues.csv"]


def test_missing_manifest_is_reported_not_raised(tmp_path):
    result = verify_bundle(tmp_path)
    assert result["ok"] is False
    assert "manifest" in result["reason"]


def test_resigning_a_signed_directory_does_not_sign_the_signatures(bundle_dir):
    sign_deliverables(bundle_dir)
    bundle = sign_deliverables(bundle_dir)
    assert all(not record["file"].endswith(".sig") for record in bundle.records)
    assert verify_bundle(bundle_dir)["ok"] is True


# -------------------------------------------------------------------- push
def test_push_plan_lists_every_file(bundle_dir):
    plan = plan_push(bundle_dir)
    assert set(plan.files) == {"clean_data.csv", "qa_report.html", "issues.csv"}


def test_push_plan_can_exclude_signatures(bundle_dir):
    sign_deliverables(bundle_dir)
    plan = plan_push(bundle_dir, include_signatures=False)
    assert not any(name.endswith(".sig") for name in plan.files)


def test_push_copies_to_a_local_destination(bundle_dir, tmp_path):
    destination = tmp_path / "delivered"
    result = push_deliverables(bundle_dir, destination=str(destination))
    assert result["ok"] is True
    assert set(result["sent"]) == {"clean_data.csv", "qa_report.html", "issues.csv"}
    assert (destination / "clean_data.csv").read_text() == (bundle_dir / "clean_data.csv").read_text()


def test_a_failing_transport_is_recorded_not_fatal(bundle_dir, tmp_path):
    def flaky(source, destination, relative):
        if relative == "issues.csv":
            raise RuntimeError("network dropped")
        return True

    result = push_deliverables(bundle_dir, destination="s3://bucket/prefix", transport=flaky)
    assert result["ok"] is False
    assert "issues.csv" not in result["sent"]
    assert result["failed"][0]["file"] == "issues.csv"
    assert "network dropped" in result["failed"][0]["error"]


def test_transport_returning_false_counts_as_a_failure(bundle_dir):
    result = push_deliverables(
        bundle_dir, destination="http://example", transport=lambda *a: False
    )
    assert result["ok"] is False
    assert len(result["failed"]) == 3


def test_push_to_a_missing_directory_errors(tmp_path):
    with pytest.raises(DeliveryError, match="Not a directory"):
        plan_push(tmp_path / "nope")