"""Extra API routes and the Python SDK (Layer 12)."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from app_files.distribution.api import create_app
from app_files.distribution.api_extras import register_extra_routes

CSV = (
    b"Email Address,Phone,Full Name\n"
    b"a@x.com,+14155552671,Jane Doe\n"
    b"b@x.com,+14155559999,John Smith\n"
)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return register_extra_routes(create_app())


@pytest.fixture
def client(app):
    return TestClient(app)


class TestRouteRegistration:
    def test_extra_routes_are_added(self, app):
        paths = {route.path for route in app.routes}
        assert {"/map", "/mask", "/lineage", "/audit", "/schedule"} <= paths

    def test_original_routes_are_untouched(self, app):
        paths = {route.path for route in app.routes}
        assert {"/health", "/validate", "/clean", "/profile", "/reconcile"} <= paths

    def test_registration_is_idempotent(self, app):
        before = len(app.routes)
        register_extra_routes(app)
        assert len(app.routes) == before


class TestMapEndpoint:
    def test_suggests_a_mapping(self, client):
        response = client.post(
            "/map", files={"file": ("c.csv", CSV, "text/csv")}, data={"crm": "hubspot"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["crm"].lower() == "hubspot"
        assert any(field["target_field"] == "email" for field in body["fields"])

    def test_first_file_is_not_learned(self, client):
        body = client.post(
            "/map", files={"file": ("c.csv", CSV, "text/csv")}, data={"crm": "hubspot"}
        ).json()
        assert body["learned"] is False

    def test_unknown_target_system_is_a_400(self, client):
        response = client.post(
            "/map",
            files={"file": ("c.csv", CSV, "text/csv")},
            data={"crm": "not-a-real-crm"},
        )
        assert response.status_code == 400


class TestMaskEndpoint:
    def test_detects_and_masks_pii(self, client):
        body = client.post("/mask", files={"file": ("c.csv", CSV, "text/csv")}).json()
        assert body["status"] == "ok"
        assert body["detections"] == 4
        assert body["by_kind"] == {"email": 2, "phone": 2}
        assert body["masked_values"] == 4

    def test_masked_output_contains_no_raw_pii(self, client):
        body = client.post("/mask", files={"file": ("c.csv", CSV, "text/csv")}).json()
        rendered = str(body["data"])
        assert "a@x.com" not in rendered
        assert "14155552671" not in rendered
        assert "[REDACTED]" in rendered

    def test_strategy_can_be_chosen(self, client):
        body = client.post(
            "/mask",
            files={"file": ("c.csv", CSV, "text/csv")},
            data={"strategy": "partial"},
        ).json()
        assert body["by_strategy"] == {"partial": 4}
        assert "2671" in str(body["data"])

    def test_specific_fields_can_be_targeted(self, client):
        body = client.post(
            "/mask",
            files={"file": ("c.csv", CSV, "text/csv")},
            data={"fields": "Email Address"},
        ).json()
        assert body["by_kind"] == {"email": 2}

    def test_missing_upload_is_a_400(self, client):
        assert client.post("/mask").status_code == 400


class TestLineageEndpoint:
    def test_returns_events_with_a_stable_shape(self, client):
        body = client.post(
            "/lineage", files={"file": ("c.csv", CSV, "text/csv")}, data={"crm": "hubspot"}
        ).json()
        assert body["status"] == "ok"
        assert body["events"] > 0
        assert set(body["columns"]) >= {"source_row", "output_row", "field", "before", "after"}


class TestScheduleEndpoint:
    def test_returns_next_fire_times(self, client):
        body = client.get("/schedule", params={"expression": "*/15 * * * *", "count": 3}).json()
        assert body["status"] == "ok"
        assert body["count"] == 3
        assert body["next"][0] < body["next"][1]

    def test_a_bad_expression_is_a_400(self, client):
        assert client.get("/schedule", params={"expression": "bogus"}).status_code == 400

    def test_a_missing_expression_is_a_400(self, client):
        assert client.get("/schedule").status_code == 400


class TestAuditEndpoint:
    def test_returns_the_log_shape(self, client):
        body = client.get("/audit").json()
        assert body["status"] == "ok"
        assert isinstance(body["data"], list)


class TestPythonSDK:
    def _session(self, client):
        from app_files.distribution.sdk import Response

        class TestClientSession:
            def post(self, path, **kwargs):
                headers = kwargs.get("headers", {})
                response = client.post(
                    path,
                    content=kwargs.get("body"),
                    headers={k: v for k, v in headers.items() if k != "Content-Length"},
                )
                return Response(response.status_code, response.json())

            def get(self, path, **kwargs):
                response = client.get(path)
                return Response(response.status_code, response.json())

        return TestClientSession()

    def test_clean_through_the_sdk_alone(self, client):
        from app_files.distribution.sdk import DataFlowClient

        sdk = DataFlowClient("http://test", session=self._session(client))
        result = sdk.clean(CSV, filename="c.csv")
        assert result.ok
        assert result.data["rows_in"] == 2

    def test_mask_through_the_sdk(self, client):
        from app_files.distribution.sdk import DataFlowClient

        sdk = DataFlowClient("http://test", session=self._session(client))
        result = sdk.mask(CSV, filename="c.csv")
        assert result.ok
        assert result.data["detections"] == 4

    def test_schedule_through_the_sdk(self, client):
        from app_files.distribution.sdk import DataFlowClient

        sdk = DataFlowClient("http://test", session=self._session(client))
        result = sdk.schedule("0 9 * * *", count=2)
        assert result.ok and result.data["count"] == 2

    def test_multipart_body_carries_the_filename(self):
        from app_files.distribution.sdk import _multipart

        body, headers = _multipart(b"data", "c.csv", {"crm": "hubspot"})
        assert b'filename="c.csv"' in body
        assert b"hubspot" in body
        assert "multipart/form-data" in headers["Content-Type"]

    def test_connect_returns_a_client(self):
        from app_files.distribution.sdk import connect

        assert connect("http://example").base_url == "http://example"


class TestSDKOverRealHTTP:
    """Drive the SDK through a real socket, not a fake session."""

    def test_full_workflow_over_http(self, app):
        import threading
        import time

        import uvicorn

        config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="error")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        for _ in range(100):
            if getattr(server, "started", False):
                break
            time.sleep(0.05)
        try:
            port = server.servers[0].sockets[0].getsockname()[1]
            from app_files.distribution.sdk import connect

            sdk = connect(f"http://127.0.0.1:{port}")
            healthy = sdk.health()
            assert healthy.ok
            masked = sdk.mask(CSV, filename="c.csv")
            assert masked.ok and masked.data["detections"] == 4
        finally:
            server.should_exit = True
            thread.join(timeout=5)
