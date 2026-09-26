"""Layer 15 end to end: the observability surface an operator actually touches.

Metrics scraped over HTTP, readiness and liveness probed the way a platform
probes them, and an alert delivered to a listening socket rather than to a mock.
"""

from __future__ import annotations

import http.server
import json
import threading

import pytest
from starlette.testclient import TestClient

from app_files.distribution.api import create_app
from app_files.distribution.api_extras import register_extra_routes
from app_files.observability import (
    AlertRule,
    AlertSeverity,
    MetricsRegistry,
    WebhookChannel,
    evaluate_alerts,
    notify_alert,
    record_run,
    render_prometheus,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return TestClient(register_extra_routes(create_app()))


class TestScrapeEndpoint:
    def test_metrics_are_served_as_plain_text(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")

    def test_the_declared_metrics_are_present(self, client):
        body = client.get("/metrics").text
        assert "# TYPE dataflow_runs_total counter" in body
        assert "# TYPE dataflow_quality_score gauge" in body

    def test_a_probe_can_be_parsed_by_a_scraper(self, client):
        """Every non-comment line must be 'name{labels} value'."""
        for line in client.get("/metrics").text.splitlines():
            if not line or line.startswith("#"):
                continue
            name, _, value = line.rpartition(" ")
            assert name
            float(value)

    def test_the_endpoint_is_read_only(self, client):
        assert client.post("/metrics").status_code == 405


class TestHealthEndpoints:
    def test_readiness_reports_ok(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_readiness_lists_its_checks(self, client):
        payload = client.get("/ready").json()
        assert payload["checks"][0]["name"] == "pandas"

    def test_liveness_reports_ok(self, client):
        response = client.get("/live")
        assert response.status_code == 200
        assert response.json()["kind"] == "liveness"

    def test_the_original_health_endpoint_still_works(self, client):
        """The observability layer must not move the existing endpoint."""
        assert client.get("/health").json()["status"] == "ok"

    def test_readiness_goes_503_when_a_required_check_fails(self, monkeypatch):
        from app_files.observability import health

        monkeypatch.setattr(health, "_builtins", lambda: health.CheckResult("pandas", False))
        report = health.readiness()
        assert report.http_status == 503
        assert report.status.value == "unhealthy"


class _Receiver:
    """A real listening socket, so the alert travels over HTTP for real."""

    def __init__(self):
        self.bodies: list[dict] = []
        self.headers: list[dict] = []
        self._server = None
        self.port = 0
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                outer.bodies.append(json.loads(self.rfile.read(length)))
                outer.headers.append(dict(self.headers))
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        self._handler = Handler

    def __enter__(self):
        self._server = http.server.HTTPServer(("127.0.0.1", 0), self._handler)
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        assert self._server is not None
        self._server.shutdown()
        self._server.server_close()


class TestAlertDeliveryOverHttp:
    def test_an_alert_reaches_a_listening_socket(self):
        with _Receiver() as receiver:
            channel = WebhookChannel(f"http://127.0.0.1:{receiver.port}/alert")
            delivered = notify_alert(
                {"status": "failed", "source": "crm", "run_id": "r-7"},
                channels=[channel],
            )
            assert delivered
            assert receiver.bodies[0]["condition"] == "failure"
            assert receiver.bodies[0]["run_id"] == "r-7"

    def test_a_webhook_secret_is_sent_over_the_wire(self):
        with _Receiver() as receiver:
            channel = WebhookChannel(
                f"http://127.0.0.1:{receiver.port}/alert", secret="top-secret"
            )
            notify_alert({"status": "failed"}, channels=[channel])
            signature = next(
                value for key, value in receiver.headers[0].items()
                if key.lower() == "x-dataflow-signature"
            )
            assert signature.startswith("sha256=")

    def test_a_run_that_succeeds_sends_nothing(self):
        with _Receiver() as receiver:
            channel = WebhookChannel(f"http://127.0.0.1:{receiver.port}/alert")
            alerts = notify_alert({"status": "ok"}, channels=[channel])
            assert alerts == []
            assert receiver.bodies == []

    def test_a_dead_endpoint_does_not_fail_the_run(self):
        channels = [WebhookChannel("http://127.0.0.1:1/alert")]
        alerts = notify_alert({"status": "failed"}, channels=channels)
        assert alerts[0].condition == "failure"


class TestMetricsFromARealRun:
    def test_a_run_records_and_the_endpoint_serves_it(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        registry = render_prometheus  # noqa: F841 - keep the import exercised
        local = MetricsRegistry()
        record_run("crm", "ok", 3.5, quality_score=88.0, rows=250, registry=local)
        body = render_prometheus(local)
        assert 'dataflow_runs_total{source="crm",status="ok"} 1.0' in body
        assert 'dataflow_quality_score{source="crm"} 88.0' in body
        assert 'dataflow_rows_processed_total{source="crm"} 250.0' in body

    def test_a_failure_lands_in_the_failure_counter(self):
        local = MetricsRegistry()
        record_run("bank", "failed", 1.2, reason="unreadable", registry=local)
        body = render_prometheus(local)
        assert 'dataflow_run_failures_total{reason="unreadable",source="bank"} 1.0' in body

    def test_a_degrading_quality_score_moves_the_gauge(self):
        local = MetricsRegistry()
        record_run("crm", "ok", 1.0, quality_score=95.0, registry=local)
        record_run("crm", "ok", 1.0, quality_score=61.0, registry=local)
        assert 'dataflow_quality_score{source="crm"} 61.0' in render_prometheus(local)


class TestAlertingOnARealRunSummary:
    def test_a_degraded_run_fires_both_a_quality_and_a_sla_alert(self):
        rules = [
            AlertRule("quality_drop", threshold=80.0, severity=AlertSeverity.CRITICAL),
            AlertRule("sla_breach", threshold=60.0),
        ]
        alerts = evaluate_alerts(
            {"status": "ok", "source": "acme", "quality_score": 55.0, "duration_seconds": 120.0},
            rules,
        )
        assert {alert.condition for alert in alerts} == {"quality_drop", "sla_breach"}
        assert all(alert.source == "acme" for alert in alerts)

    def test_a_quiet_run_fires_nothing_across_all_conditions(self):
        rules = [
            AlertRule("quality_drop", threshold=80.0),
            AlertRule("sla_breach", threshold=60.0),
            AlertRule("duration_breach", threshold=60.0),
        ]
        assert evaluate_alerts(
            {"status": "ok", "quality_score": 97.0, "duration_seconds": 4.0}, rules
        ) == []
