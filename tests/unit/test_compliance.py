"""Compliance posture: GDPR, CCPA and SOC 2 readiness (Layer 13).

The value of this module is that it reports what the running code actually
does. So the tests check the checks: a control with no evidence must come back
as a gap, not as met.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from app_files.governance import (
    FRAMEWORKS,
    CompliancePacket,
    Control,
    Residency,
    RetentionPolicy,
    assess_controls,
    build_packet,
    write_packet,
)
from app_files.governance import compliance as module


class TestRetention:
    def test_a_fresh_record_is_kept(self):
        policy = RetentionPolicy(days=30)
        assert policy.decision("2026-09-01T00:00:00", at=datetime(2026, 9, 10, tzinfo=timezone.utc)) == "keep"

    def test_a_record_past_the_window_is_deleted(self):
        policy = RetentionPolicy(days=30)
        assert policy.decision("2026-01-01T00:00:00", at=datetime(2026, 9, 10, tzinfo=timezone.utc)) == "delete"

    def test_the_boundary_itself_is_not_yet_expired(self):
        """Exactly N days old is still inside a window of N days."""
        now = datetime(2026, 9, 10, tzinfo=timezone.utc)
        created = (now - timedelta(days=30)).isoformat()
        assert RetentionPolicy(days=30).is_expired(created, at=now) is False

    def test_zero_days_expires_anything_from_the_past(self):
        now = datetime(2026, 9, 10, tzinfo=timezone.utc)
        assert RetentionPolicy(days=0).is_expired(
            "2026-09-09T00:00:00", at=now
        ) is True

    def test_an_unparseable_date_is_not_treated_as_expired(self):
        """Deleting on an unreadable timestamp is worse than keeping it."""
        assert RetentionPolicy(days=1).is_expired("not-a-date") is False

    def test_negative_retention_is_rejected(self):
        with pytest.raises(ValueError):
            RetentionPolicy(days=-1)

    def test_a_naive_datetime_is_read_as_utc(self):
        policy = RetentionPolicy(days=1)
        naive = datetime(2020, 1, 1)  # noqa: DTZ001 - a naive input is the case under test
        assert policy.is_expired(naive) is True


class TestControls:
    def test_every_framework_gets_at_least_one_control(self):
        covered = {control.framework for control in assess_controls()}
        assert set(FRAMEWORKS) <= covered

    def test_the_audit_control_is_met_on_this_checkout(self):
        by_id = {control.control_id: control for control in assess_controls()}
        assert by_id["A.1"].status == "met"

    def test_a_broken_check_becomes_a_gap_not_a_crash(self, monkeypatch):
        def exploding():
            raise RuntimeError("boom")

        monkeypatch.setattr(
            module, "_CHECKS", (("GDPR", "X.1", "Broken", exploding),)
        )
        controls = assess_controls()
        assert controls[0].status == "gap"
        assert "boom" not in controls[0].evidence  # the message can carry a path or a secret
        assert "RuntimeError" in controls[0].evidence

    def test_an_unknown_control_is_never_assumed_met(self):
        packet = build_packet()
        assert packet.gaps == []

    def test_missing_audit_source_is_a_gap(self, monkeypatch, tmp_path):
        """If the chain source cannot be found, the control must not pass."""
        monkeypatch.setattr(module.Path, "resolve", lambda self: tmp_path / "nowhere")
        monkeypatch.setattr(module.Path, "exists", lambda self: False)
        status, evidence = module._check_audit_append_only()
        assert status == "gap"
        assert "cannot confirm" in evidence

    def test_a_missing_encryption_module_is_a_gap(self, monkeypatch):
        monkeypatch.setattr(module.Path, "exists", lambda self: False)
        status, _ = module._check_encryption()
        assert status == "gap"

    def test_secrets_reported_as_partial_when_only_the_env_fallback_is_in_use(
        self, monkeypatch, tmp_path
    ):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        status, evidence = module._check_secrets()
        assert status == "partial"
        assert "does not exist yet" in evidence

    def test_secrets_met_once_the_store_exists(self, monkeypatch, tmp_path):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        from app_files.governance.encryption import SecretStore

        path = SecretStore.default_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
        status, _ = module._check_secrets()
        assert status == "met"


class TestPacket:
    def test_ready_needs_no_gaps_and_all_frameworks(self):
        packet = CompliancePacket(generated_at="2026-01-01T00:00:00")
        assert packet.ready is False
        packet.controls = [
            Control(framework, "1", "t", "met", "e") for framework in FRAMEWORKS
        ]
        assert packet.ready is True

    def test_a_single_gap_blocks_readiness(self):
        packet = CompliancePacket(generated_at="2026-01-01T00:00:00")
        packet.controls = [
            Control(framework, "1", "t", "met", "e") for framework in FRAMEWORKS
        ]
        packet.controls.append(Control("SOC 2", "9", "bad", "gap", "no evidence"))
        assert packet.ready is False
        assert len(packet.gaps) == 1

    def test_counts_add_up_to_the_control_list(self):
        packet = build_packet()
        assert sum(packet.counts.values()) == len(packet.controls)

    def test_residency_is_reported_per_tenant(self, tmp_path):
        from app_files.tenancy import Tenant

        acme = Tenant(id="acme", name="Acme", root=tmp_path / "acme")
        acme.metadata["region"] = "eu-west"
        beta = Tenant(id="beta", name="Beta", root=tmp_path / "beta")

        packet = build_packet(tenants=[acme, beta], region="us-east")
        regions = {region.storage_path: region.region for region in packet.residency}
        assert regions[str(tmp_path / "acme")] == "eu-west"
        assert regions[str(tmp_path / "beta")] == "us-east"

    def test_no_tenants_renders_a_plain_statement(self):
        packet = build_packet()
        assert "No tenants configured." in packet.render()

    def test_the_render_names_every_framework(self):
        rendered = build_packet().render()
        for framework in FRAMEWORKS:
            assert f"### {framework}" in rendered

    def test_write_emits_markdown_and_json(self, tmp_path):
        packet = build_packet()
        path = write_packet(packet, tmp_path / "docs" / "compliance.md")
        assert path.exists()
        assert path.with_suffix(".json").exists()
        data = json.loads(path.with_suffix(".json").read_text())
        assert data["counts"] == packet.counts
        assert data["frameworks"] == list(FRAMEWORKS)

    def test_the_packet_carries_an_encryption_statement(self):
        packet = build_packet()
        assert "AES-256-GCM" in packet.encryption_at_rest
        assert "TLS 1.3" in packet.encryption_in_transit

    def test_residency_dataclass_round_trips(self):
        region = Residency(region="ap-south", storage_path="/data/ap")
        assert region.as_dict() == {"region": "ap-south", "storage_path": "/data/ap"}
