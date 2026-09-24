"""Layer 13 end to end: authorization on a served route, and a chain that
proves an audit record was not edited after the fact.
"""

from __future__ import annotations

import json

import pytest
from starlette.testclient import TestClient

from app_files.collaboration.audit_trail import AuditEntry
from app_files.distribution.api import create_app
from app_files.distribution.api_extras import register_extra_routes
from app_files.governance import (
    AuditChain,
    Principal,
    Role,
    SecretStore,
    append_to_chain,
    decrypt_text,
    encrypt_text,
    verify_chain,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return TestClient(register_extra_routes(create_app()))


class TestRoleEnforcementOnTheApi:
    def test_a_viewer_is_refused_an_admin_read(self, client):
        response = client.get("/users", headers={"X-DataFlow-Role": "viewer"})
        assert response.status_code == 403
        assert response.json()["status"] == "denied"

    def test_the_default_role_is_the_least_privileged(self, client):
        assert client.get("/users").status_code == 403

    def test_an_admin_cannot_manage_users(self, client):
        # Managing users is owner-only; an admin runs the system but does not
        # hand out access to it.
        assert client.get("/users", headers={"X-DataFlow-Role": "admin"}).status_code == 403

    def test_an_owner_is_allowed(self, client):
        response = client.get("/users", headers={"X-DataFlow-Role": "owner"})
        assert response.status_code == 200
        assert response.json()["caller"]["role"] == "owner"

    def test_an_operator_is_still_refused_managing_users(self, client):
        assert client.get("/users", headers={"X-DataFlow-Role": "operator"}).status_code == 403

    def test_an_unknown_role_does_not_grant_access(self, client):
        assert client.get("/users", headers={"X-DataFlow-Role": "superuser"}).status_code == 403

    def test_the_refusal_names_the_role(self, client):
        body = client.get("/users", headers={"X-DataFlow-Role": "viewer"}).json()
        assert "viewer" in body["error"]

    def test_the_role_list_is_exposed_to_an_owner(self, client):
        roles = client.get("/users", headers={"X-DataFlow-Role": "owner"}).json()["roles"]
        assert set(roles) == {"owner", "admin", "operator", "viewer", "client"}


class TestAuditChainEndToEnd:
    def _entry(self, **overrides) -> AuditEntry:
        fields = {
            "timestamp": "2024-05-01T10:00:00+00:00",
            "input_name": "contacts.csv",
            "input_hash": "a" * 64,
            "config": "hubspot",
            "rows_in": 120,
            "rows_out": 120,
            "quality_score": 98.0,
            "output_hash": "b" * 64,
            "client": "acme",
        }
        fields.update(overrides)
        return AuditEntry(**fields)

    def test_a_series_of_runs_produces_a_verifiable_chain(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        for index in range(10):
            append_to_chain(self._entry(rows_in=index))
        report = verify_chain()
        assert report.ok
        assert report.entries == 10

    def test_every_chained_entry_is_traceable_to_its_actor(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        append_to_chain(self._entry(client="acme"))
        chain = AuditChain(tmp_path / "audit" / "chain.jsonl")
        first = chain.entries()[0]
        assert first["payload"]["client"] == "acme"
        assert first["payload"]["timestamp"] == "2024-05-01T10:00:00+00:00"

    def test_editing_a_chained_record_is_detected(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        for index in range(3):
            append_to_chain(self._entry(rows_in=index))
        path = tmp_path / "audit" / "chain.jsonl"
        lines = path.read_text().splitlines()
        record = json.loads(lines[1])
        record["payload"]["quality_score"] = 100.0
        lines[1] = json.dumps(record)
        path.write_text("\n".join(lines) + "\n")
        report = verify_chain(path)
        assert not report.ok
        assert report.broken_at == 1

    def test_the_chain_lives_under_autoflow_home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        append_to_chain(self._entry())
        assert (tmp_path / "audit" / "chain.jsonl").exists()


class TestEncryptedStateAtRest:
    def test_a_key_persisted_under_autoflow_home_round_trips(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        store = SecretStore()
        store.set("default", SecretStore.generate_key(), persist=True)
        sealed = encrypt_text('{"client": "acme"}', SecretStore().get("default"))
        assert decrypt_text(sealed, SecretStore().get("default")) == '{"client": "acme"}'

    def test_a_state_file_on_disk_does_not_hold_the_plaintext(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        store = SecretStore()
        store.set("default", SecretStore.generate_key(), persist=True)
        secret = "4111 1111 1111 1111"
        blob = encrypt_text(secret, store.get("default"))
        artifact = tmp_path / "state.enc"
        artifact.write_text(blob)
        assert secret not in artifact.read_text()


class TestRoleScoping:
    def test_a_client_principal_reads_only_its_own_workspace(self):
        principal = Principal("acme-portal", Role.CLIENT, scope="acme")
        from app_files.governance import check

        assert check(principal, "read_reports", client="acme")
        assert not check(principal, "read_reports", client="globex")
