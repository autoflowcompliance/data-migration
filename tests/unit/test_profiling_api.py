"""Interface tests for the profiling extension's API and SDK adapters.

Written before the implementation. ``POST /profile/columns`` returns the same
report the CLI writes; ``DataFlowClient.profile_columns`` reaches it.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from app_files.distribution.api import create_app
from app_files.distribution.api_extras import register_extra_routes
from app_files.distribution.sdk import DataFlowClient

CSV = (
    b"amount,who\n1,a@x.com\n2,b@y.org\n3,c@z.net\n4,d@w.io\n5,e@v.co\n1000,f@u.me\n"
)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return register_extra_routes(create_app())


@pytest.fixture
def client(app):
    return TestClient(app)


class TestProfileColumnsEndpoint:
    def test_it_returns_statistics_patterns_and_outliers(self, client):
        response = client.post(
            "/profile/columns",
            files={"file": ("d.csv", CSV, "text/csv")},
            data={"statistics": "true", "patterns": "true", "outliers": "true"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["statistics"]["amount"]["kind"] == "numeric"
        assert body["patterns"]["who"]["label"] == "email"
        assert body["outliers"]["amount"]["count"] == 1

    def test_a_numeric_string_form_value_is_accepted(self, client):
        # Form fields arrive as strings; "1.5" must not be rejected as a k.
        response = client.post(
            "/profile/columns",
            files={"file": ("d.csv", CSV, "text/csv")},
            data={"outliers": "true", "outlier_k": "1.5"},
        )
        assert response.status_code == 200
        assert response.json()["outliers"]["amount"]["k"] == 1.5

    def test_sections_default_to_off(self, client):
        response = client.post(
            "/profile/columns", files={"file": ("d.csv", CSV, "text/csv")}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["statistics"] == {}
        assert body["outliers"] == {}

    def test_an_unknown_method_is_a_400_not_a_500(self, client):
        response = client.post(
            "/profile/columns",
            files={"file": ("d.csv", CSV, "text/csv")},
            data={"outliers": "true", "outlier_method": "vibes"},
        )
        assert response.status_code == 400
        assert "method" in response.json()["error"]

    def test_a_bad_file_is_a_400(self, client):
        response = client.post(
            "/profile/columns", files={"file": ("d.csv", b"", "text/csv")}
        )
        assert response.status_code == 400

    def test_the_original_profile_endpoint_is_untouched(self, client):
        response = client.post(
            "/profile", files={"file": ("d.csv", CSV, "text/csv")}
        )
        assert response.status_code == 200
        assert "overall" in response.json()


class TestSDK:
    def test_the_sdk_reaches_the_endpoint(self, app):
        client = DataFlowClient(session=_TestClientSession(TestClient(app)))
        response = client.profile_columns(
            CSV, statistics=True, patterns=True, outliers=True
        )
        assert response.status_code == 200
        assert response.json()["outliers"]["amount"]["count"] == 1

    def test_the_sdk_sends_the_method(self, app):
        client = DataFlowClient(session=_TestClientSession(TestClient(app)))
        response = client.profile_columns(CSV, outliers=True, outlier_method="zscore")
        assert response.json()["outliers"]["amount"]["method"] == "zscore"


class _TestClientSession:
    """Adapt Starlette's TestClient to the SDK's Session protocol."""

    def __init__(self, test_client: TestClient):
        self._client = test_client

    def get(self, path: str):
        return self._client.get(path)

    def post(self, path: str, body: bytes, headers: dict):
        return self._client.post(path, content=body, headers=headers)
