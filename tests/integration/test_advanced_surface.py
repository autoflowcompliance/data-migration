"""The advanced surface, exercised through the interfaces a buyer touches.

These go over HTTP and the CLI rather than calling the modules directly, because
"the function works" and "the endpoint answers" are different claims. The API is
driven with a real in-process ASGI client, and the CLI is driven for real, with
the working directory moved so the ``no files were written`` claim is checked
against an empty directory.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app_files.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES = REPO_ROOT / "app_files" / "samples"
MESSY = SAMPLES / "messy_contacts.csv"


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app_files.distribution.api import create_app

    return TestClient(create_app())


def _upload(path: Path):
    return {"file": (path.name, path.read_bytes(), "text/csv")}


# ------------------------------------------------------------------ new routes
def test_health_deep_reports_its_checks(client):
    response = client.get("/health/deep")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert {c["name"] for c in body["checks"]} == {"liveness", "readiness"}


def test_metrics_are_scrapable_prometheus_text(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# TYPE dataflow_runs_total counter" in response.text


def test_connectors_endpoint_lists_providers_and_readiness(client):
    providers = {c["provider"] for c in client.get("/connectors").json()["connectors"]}
    assert {"s3", "gcs", "azure_blob", "slack", "hubspot", "salesforce"} <= providers


def test_dry_run_endpoint_plans_without_writing(client, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = client.post(
        "/dry-run", files=_upload(MESSY), data={"crm": "hubspot", "format": "csv"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["rows_in"] > 0
    assert {o["name"] for o in body["outputs"]} >= {"clean_data", "qa_report", "issues"}
    assert list(tmp_path.iterdir()) == []


def test_dry_run_rejects_an_empty_upload(client):
    response = client.post(
        "/dry-run", files={"file": ("empty.csv", b"", "text/csv")}, data={"crm": "hubspot"}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["error"].lower()


def test_alerts_endpoint_flags_a_bad_run(client):
    response = client.post(
        "/alerts",
        json={"summary": {"status": "failed", "quality_score": 40, "duration": 500}},
    )
    assert response.status_code == 200
    rules = {a["rule"] for a in response.json()["alerts"]}
    assert rules == {"run-failed", "low-quality", "slow-run"}


def test_alerts_endpoint_can_take_custom_rules(client):
    response = client.post(
        "/alerts",
        json={
            "summary": {"status": "succeeded", "quality_score": 95},
            "rules": [{"name": "only-quality", "kind": "quality_below", "threshold": 99}],
        },
    )
    assert [a["rule"] for a in response.json()["alerts"]] == ["only-quality"]


# ------------------------------------------------------------------- CLI paths
def test_cli_dry_run_prints_a_plan_and_writes_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    code = main(["-i", str(MESSY), "-c", "hubspot", "--dry-run"])
    out = capsys.readouterr().out
    assert code == 0
    assert "DRY RUN" in out
    assert "No files were written." in out
    assert list(tmp_path.iterdir()) == []


def test_cli_writes_a_rollback_file_and_runbook(tmp_path, capsys):
    clean = tmp_path / "clean.csv"
    clean.write_text(
        "First Name,Last Name,Email Address,Phone\n"
        "Ann,Lee,ann@x.com,5551234567\n"
        "Bob,Ray,bob@x.com,5559876543\n"
    )
    rollback = tmp_path / "rollback.json"
    runbook = tmp_path / "RUNBOOK.md"
    code = main(
        [
            "-i", str(clean),
            "-c", "hubspot",
            "-o", str(tmp_path / "out"),
            "--rollback", str(rollback),
            "--runbook", str(runbook),
        ]
    )
    assert code == 0
    payload = json.loads(rollback.read_text())
    assert payload["rows_in"] == 2
    assert runbook.read_text().startswith("# Cutover runbook")
    assert "Rollback file:" in capsys.readouterr().out

# ------------------------------------------------- newer endpoints (advanced)
def test_formats_endpoint_lists_builtins_and_plugins(client):
    body = client.get("/formats").json()
    assert {"csv", "excel", "json", "sql"} <= set(body["builtin"])
    assert body["plugins"] == []
    assert set(body["available"]) >= {"csv", "excel", "json", "sql"}


def test_compliance_endpoint_reports_a_posture(client):
    body = client.get("/compliance").json()
    assert "controls" in body
    assert isinstance(body["controls"], list)


def test_deployment_endpoint_validates_a_profile(client):
    body = client.get("/deployment?profile=container").json()
    assert body["profile"]["name"] == "container"
    assert any(c["check"] == "port" for c in body["checks"])


def test_deployment_endpoint_rejects_an_unknown_profile(client):
    response = client.get("/deployment?profile=mars")
    assert response.status_code == 400
    assert "Unknown deployment profile" in response.json()["error"]


def test_privacy_endpoint_detects_personal_data(client):
    response = client.post("/privacy", files=_upload(MESSY))
    assert response.status_code == 200
    body = response.json()
    assert "email" in body["report"]["by_class"]


def test_privacy_endpoint_masks_when_asked(client):
    response = client.post(
        "/privacy",
        files=_upload(MESSY),
        data={"mask": json.dumps({"modes": {"email": "hash"}})},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["masked"]["columns"]


def test_privacy_endpoint_rejects_bad_mask_json(client):
    response = client.post("/privacy", files=_upload(MESSY), data={"mask": "not json"})
    assert response.status_code == 400
    assert "not valid JSON" in response.json()["error"]


def test_admin_endpoint_presents_a_snapshot(client):
    body = client.get("/admin").json()
    assert set(body) == {"runs", "trend", "tenants", "formats", "connectors", "health"}
    assert {"csv", "excel", "json", "sql"} <= set(body["formats"]["builtin"])
