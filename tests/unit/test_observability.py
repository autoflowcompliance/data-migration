"""Observability: metrics, alerts, health, and the quality trend.

The Prometheus output is asserted by parsing it back with a tiny parser, so the
test checks the exposition format rather than a substring. Alert routing is
tested with a fake sender, including the case where one channel is down.
"""

from __future__ import annotations

import re

import pytest

from app_files.observability import (
    AlertRule,
    MetricsRegistry,
    TrendSummary,
    deliver_alerts,
    evaluate_alerts,
    full_health,
    liveness,
    readiness,
    read_trend,
    record_trend,
    route_channels,
    summarise_trend,
    trend_path,
)


# ------------------------------------------------------------------- metrics
def _parse_exposition(text: str) -> dict[str, float]:
    samples: dict[str, float] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^(?P<name>[a-zA-Z_:][\w:]*)(?P<labels>\{[^}]*\})?\s+(?P<value>.+)$", line)
        assert match, f"unparseable exposition line: {line!r}"
        samples[match.group("name") + (match.group("labels") or "")] = float(match.group("value"))
    return samples


def test_metrics_render_valid_prometheus_text():
    registry = MetricsRegistry()
    registry.record_run(status="succeeded", rows=120, quality=92.5, duration=3.2, config="hubspot")
    text = registry.render()

    assert "# TYPE dataflow_runs_total counter" in text
    assert "# TYPE dataflow_run_duration_seconds histogram" in text
    samples = _parse_exposition(text)
    assert samples['dataflow_runs_total{config="hubspot",status="succeeded",tenant=""}'] == 1
    assert samples['dataflow_rows_processed_total{config="hubspot",tenant=""}'] == 120
    assert samples['dataflow_quality_score{config="hubspot",tenant=""}'] == 92.5
    assert samples['dataflow_run_duration_seconds_count{config="hubspot",tenant=""}'] == 1


def test_failures_are_counted_by_status():
    registry = MetricsRegistry()
    registry.record_run(status="failed", config="hubspot")
    registry.record_run(status="succeeded", config="hubspot")
    samples = _parse_exposition(registry.render())
    assert samples['dataflow_failures_total{config="hubspot",tenant=""}'] == 1
    assert samples['dataflow_runs_total{config="hubspot",status="failed",tenant=""}'] == 1


def test_histogram_buckets_are_cumulative():
    registry = MetricsRegistry()
    registry.record_run(status="succeeded", duration=0.3)
    registry.record_run(status="succeeded", duration=7.0)
    samples = _parse_exposition(registry.render())
    # 0.3 falls in the <=0.5 bucket; both fall in <=15.
    assert samples['dataflow_run_duration_seconds_bucket{config="",le="0.5",tenant=""}'] == 1
    assert samples['dataflow_run_duration_seconds_bucket{config="",le="15",tenant=""}'] == 2
    assert samples['dataflow_run_duration_seconds_bucket{config="",le="+Inf",tenant=""}'] == 2


def test_metric_labels_are_escaped():
    registry = MetricsRegistry()
    registry.record_run(status="succeeded", config='weird"name')
    text = registry.render()
    assert '\\"name' in text
    _parse_exposition(text)  # still parses


# ------------------------------------------------------------------- alerting
def test_failure_rule_raises_a_critical_alert():
    rule = AlertRule(name="run-failed", kind="failure", severity="critical")
    alert = rule.evaluate({"status": "failed", "error": "unreadable input"})
    assert alert is not None
    assert alert.severity == "critical"
    assert "unreadable input" in alert.message


def test_quality_and_duration_rules():
    quality = AlertRule(name="low-quality", kind="quality_below", threshold=80)
    assert quality.evaluate({"quality_score": 70}) is not None
    assert quality.evaluate({"quality_score": 90}) is None

    slow = AlertRule(name="slow", kind="duration_above", threshold=30)
    assert slow.evaluate({"duration": 45}) is not None
    assert slow.evaluate({"duration": 10}) is None


def test_successful_run_raises_nothing():
    rules = [
        AlertRule(name="f", kind="failure"),
        AlertRule(name="q", kind="quality_below", threshold=80),
        AlertRule(name="d", kind="duration_above", threshold=30),
    ]
    assert evaluate_alerts(rules, {"status": "succeeded", "quality_score": 95, "duration": 4}) == []


def test_routing_falls_back_to_severity_default():
    from app_files.observability import Alert

    critical = Alert(rule="r", severity="critical", message="m")
    assert "email" in route_channels(critical)
    custom = Alert(rule="r", severity="critical", message="m", channels=["webhook"])
    assert route_channels(custom) == ["webhook"]


def test_delivery_reports_each_channel_and_survives_one_failure():
    from app_files.observability import Alert

    alerts = [Alert(rule="r", severity="critical", message="m")]
    calls = []

    def sender(channel, alert):
        calls.append(channel)
        if channel == "slack":
            raise RuntimeError("webhook is dead")

    results = deliver_alerts(alerts, sender)
    assert {r["channel"] for r in results} == {"email", "slack", "teams", "webhook"}
    slack = next(r for r in results if r["channel"] == "slack")
    assert slack["delivered"] is False
    email = next(r for r in results if r["channel"] == "email")
    assert email["delivered"] is True


# --------------------------------------------------------------------- health
def test_liveness_is_always_ok():
    assert liveness().ok is True


def test_readiness_passes_on_a_working_install(tmp_path):
    status = readiness(output_dir=tmp_path / "out")
    assert status.ok is True, status.detail


def test_readiness_fails_when_configs_are_missing(tmp_path):
    status = readiness(output_dir=tmp_path / "out", configs_dir=tmp_path / "nope")
    assert status.ok is False
    assert "missing" in status.detail


def test_readiness_fails_when_a_config_does_not_load(tmp_path):
    configs = tmp_path / "configs"
    configs.mkdir()
    (configs / "broken.yaml").write_text("target: [unclosed\n")
    status = readiness(output_dir=tmp_path / "out", configs_dir=configs)
    assert status.ok is False
    assert "does not load" in status.detail


def test_full_health_aggregates_checks(tmp_path):
    report = full_health(output_dir=tmp_path / "out")
    assert set(report) == {"ok", "checks", "checked_at"}
    assert report["ok"] is True
    assert {c["name"] for c in report["checks"]} == {"liveness", "readiness"}


# ----------------------------------------------------------------- trend
@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return tmp_path


def test_trend_records_and_summarises_a_rise(home):
    record_trend(80, rows_in=100, rows_out=95, config="hubspot")
    record_trend(90, rows_in=100, rows_out=98, config="hubspot")
    summary = summarise_trend(read_trend())
    assert summary.entries == 2
    assert summary.latest == 90
    assert summary.delta == 10
    assert summary.direction == "improving"


def test_trend_direction_declining_and_baseline(home):
    assert summarise_trend([]).direction == "no data"
    record_trend(70)
    assert summarise_trend(read_trend()).direction == "baseline"
    record_trend(60)
    assert summarise_trend(read_trend()).direction == "declining"


def test_trends_are_per_tenant(home):
    record_trend(90, tenant="acme")
    record_trend(50, tenant="beta")
    assert summarise_trend(read_trend("acme")).latest == 90
    assert summarise_trend(read_trend("beta")).latest == 50
    assert trend_path("acme") != trend_path("beta")


def test_trend_state_honours_autoflow_home(home):
    record_trend(88)
    assert str(trend_path()).startswith(str(home))