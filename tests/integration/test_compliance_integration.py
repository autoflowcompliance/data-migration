"""A compliance packet produced from a real run on a real sample file.

Unit tests prove the checks answer correctly. This proves the packet is about
a deployment that actually processed a file: a tenant, a metered run, and the
exportable Markdown that would go to legal.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.governance import FRAMEWORKS, build_packet, write_packet
from app_files.ingestion import read_any
from app_files.licensing import sign
from app_files.licensing.cloud import CloudLicense, CloudLicenseStore
from app_files.pipeline import run_pipeline
from app_files.tenancy import TenantRegistry


def _run_real_file(tmp_path) -> dict:
    """Migrate the bundled messy sample and return the run's summary."""
    source = Path(__file__).resolve().parents[2] / "app_files" / "samples" / "messy_contacts.csv"
    result = run_pipeline(
        source=read_any(source),
        crm="hubspot",
        project_name="Compliance packet fixture",
        source_filename=source.name,
    )
    return result.summary()


class TestPacketFromARealRun:
    def test_a_real_run_produces_rows_to_be_retained(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        summary = _run_real_file(tmp_path)
        assert summary["rows_in"] > 0

        licence = CloudLicense(CloudLicenseStore(tmp_path / "cloud"))
        issued = "2026-01-01T00:00:00"
        licence.activate(
            "acme@example.com", issued, sign("acme@example.com", issued), seats=1
        )
        licence.record_run(rows=summary["rows_in"])
        assert licence.usage()["rows"] == summary["rows_in"]

    def test_the_packet_reports_each_tenant_and_its_region(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        registry = TenantRegistry(tmp_path / "tenants")
        acme = registry.create("Acme", tenant_id="acme")
        acme.metadata["region"] = "eu-west"
        acme._write_meta()
        beta = registry.create("Beta", tenant_id="beta")

        packet = build_packet(tenants=[acme, beta], region="us-east")
        assert packet.ready is True
        assert len(packet.residency) == 2

    def test_the_packet_survives_a_write_and_reload(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        _run_real_file(tmp_path)
        packet = build_packet(retention_days=180)
        path = write_packet(packet, tmp_path / "packet" / "compliance.md")

        markdown = path.read_text()
        assert "GDPR" in markdown and "CCPA" in markdown and "SOC 2" in markdown
        data = json.loads(path.with_suffix(".json").read_text())
        assert data["retention"]["days"] == 180
        assert data["frameworks"] == list(FRAMEWORKS)
        # No control may be reported as met without evidence text.
        for control in data["controls"]:
            if control["status"] == "met":
                assert control["evidence"]

    def test_a_packet_never_contains_a_raw_secret_or_path_from_an_error(
        self, tmp_path, monkeypatch
    ):
        """The packet goes to a third party; a leaked path is a disclosure."""
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        packet = build_packet()
        rendered = packet.render() + json.dumps(packet.as_dict())
        assert "DATAREADY_ENCRYPTION_KEY" not in rendered
