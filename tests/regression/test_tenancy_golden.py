"""Golden file for Layer 16 — a known tenant tree round-trips through backup.

The input is a tenant populated with known files. The expected output is the
backup manifest (relative path -> digest) and the restored tree listing. If a
change alters what gets backed up, or the digests, this fails.

The deployment manifests are pinned too: they are generated from the port
precedence in ``app_files.settings`` and the two state-home variables, so a
change there changes the files a buyer deploys with.

If a golden breaks, the change is guilty until proven innocent: revert it or fix
the bug. Do not regenerate the expected file to make the test green.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from app_files.tenancy import (
    TenantRegistry,
    create_backup,
    deployment_plan,
    restore_backup,
    verify_backup,
)

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "tenancy"


def test_backup_manifest_golden(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    expected = json.loads((GOLDEN / "expected_manifest.json").read_text())

    tenant = TenantRegistry().create("Acme", tenant_id="acme")
    # Known content, so the digests are stable. tenant.json carries a timestamp
    # that varies, so it is asserted by presence rather than by digest.
    tenant.resolve_path("data", "input.csv").write_text("email,amount\na@x.com,10\n")
    tenant.resolve_path("output", "clean.csv").write_text("email,amount\na@x.com,10\n")
    tenant.resolve_path("config", "config.yaml").write_text("fields:\n  - name: email\n")

    backup = create_backup(tenant, tmp_path / "backups")
    verify_backup(backup)

    stable = {
        path: digest
        for path, digest in backup.manifest.files.items()
        if path != "tenant.json"
    }
    assert stable == expected["digests"]
    assert "tenant.json" in backup.manifest.files
    assert backup.manifest.file_count == expected["file_count"]


def test_backup_restore_golden_tree(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    expected = json.loads((GOLDEN / "expected_manifest.json").read_text())

    tenant = TenantRegistry().create("Acme", tenant_id="acme")
    tenant.resolve_path("data", "input.csv").write_text("email,amount\na@x.com,10\n")
    tenant.resolve_path("output", "clean.csv").write_text("email,amount\na@x.com,10\n")
    tenant.resolve_path("config", "config.yaml").write_text("fields:\n  - name: email\n")
    backup = create_backup(tenant, tmp_path / "backups")

    tenant.delete()
    restored = TenantRegistry().get("acme", create=True)
    report = restore_backup(backup, restored)

    assert report.ok
    assert sorted(report.restored) == expected["restored"]
    assert restored.tree() == expected["tree"]


def test_deploy_manifests_golden(tmp_path):
    plan = deployment_plan("render", port=10000, image="dataflow:2.0")
    assert plan.files["render.yaml"] == (GOLDEN / "render.yaml").read_text()

    compose = deployment_plan("docker", port=10000, image="dataflow:2.0")
    assert compose.files["docker-compose.yml"] == (
        GOLDEN / "docker-compose.yml"
    ).read_text()

    k8s = deployment_plan("kubernetes", port=10000, image="dataflow:2.0")
    assert k8s.files["dataflow.yaml"] == (GOLDEN / "k8s.yaml").read_text()


def test_golden_manifests_still_obey_the_port_rule():
    """The goldens are only meaningful while PORT is left to the platform."""
    render = yaml.safe_load((GOLDEN / "render.yaml").read_text())
    env_keys = {var["key"] for var in render["services"][0]["envVars"]}
    assert "PORT" not in env_keys
    assert {"AUTOFLOW_HOME", "DATAREADY_HOME"} <= env_keys
