"""Layer 15 — metrics, alerting and health checks."""

from __future__ import annotations

import json

import pytest

from app_files.observability import (
    Alert,
    AlertRule,
    AlertSeverity,
    AlertSink,
    Counter,
    EmailChannel,
    Gauge,
    HealthStatus,
    Histogram,
    MetricsRegistry,
    SlackChannel,
    TeamsChannel,
    WebhookChannel,
    build_alert,
    evaluate_alerts,
    liveness,
    notify_alert,
    readiness,
    record_run,
    render_prometheus,
)


class TestMetrics:
    def test_a_counter_only_goes_up(self):
        counter = Counter("hits")
        counter.inc()
        counter.inc(2)
        assert counter.value() == 3.0

    def test_a_counter_refuses_to_decrease(self):
        with pytest.raises(ValueError, match="cannot decrease"):
            Counter("hits").inc(-1)

    def test_a_counter_is_per_label_set(self):
        counter = Counter("runs")
        counter.inc(labels={"source": "crm"})
        assert counter.value({"source": "crm"}) == 1.0
        assert counter.value({"source": "bank"}) == 0.0

    def test_a_gauge_moves_both_ways(self):
        gauge = Gauge("temperature")
        gauge.set(10)
        gauge.inc(-3)
        assert gauge.value() == 7.0

    def test_a_histogram_counts_cumulatively(self):
        hist = Histogram("latency", buckets=(1.0, 5.0, 10.0))
        for value in (0.5, 3.0, 9.0):
            hist.observe(value)
        assert hist.bucket_counts(()) == [1, 2, 3]
        assert hist.count() == 3
        assert hist.total() == pytest.approx(12.5)

    def test_a_histogram_exposes_count_and_sum(self):
        hist = Histogram("latency", buckets=(1.0,))
        hist.observe(0.5)
        rendered = hist.render()
        assert "latency_count" in rendered
        assert "latency_sum" in rendered
        assert 'le="+Inf"' in rendered

    def test_the_registry_declares_the_run_metrics(self):
        registry = MetricsRegistry()
        for name in (
            "dataflow_runs_total",
            "dataflow_run_duration_seconds",
            "dataflow_run_failures_total",
            "dataflow_quality_score",
            "dataflow_rows_processed_total",
        ):
            assert name in registry.names

    def test_rendering_is_prometheus_text(self):
        registry = MetricsRegistry()
        record_run("crm", "ok", 1.5, registry=registry)
        rendered = render_prometheus(registry)
        assert "# TYPE dataflow_runs_total counter" in rendered
        assert 'dataflow_runs_total{source="crm",status="ok"} 1.0' in rendered

    def test_a_run_is_recorded_on_every_dimension(self):
        registry = MetricsRegistry()
        record_run("crm", "ok", 2.0, quality_score=93.5, rows=100, registry=registry)
        assert registry.counter("dataflow_runs_total").value({"source": "crm", "status": "ok"}) == 1
        assert registry.gauge("dataflow_quality_score").value({"source": "crm"}) == 93.5
        assert registry.counter("dataflow_rows_processed_total").value({"source": "crm"}) == 100
        assert registry.histogram("dataflow_run_duration_seconds").count({"source": "crm"}) == 1

    def test_a_failure_is_counted_with_its_reason(self):
        registry = MetricsRegistry()
        record_run("crm", "failed", 1.0, reason="bad_csv", registry=registry)
        failures = registry.counter("dataflow_run_failures_total")
        assert failures.value({"source": "crm", "reason": "bad_csv"}) == 1

    def test_a_success_is_not_counted_as_a_failure(self):
        registry = MetricsRegistry()
        record_run("crm", "ok", 1.0, registry=registry)
        assert registry.counter("dataflow_run_failures_total").values == {}

    def test_rendering_escapes_label_values(self):
        registry = MetricsRegistry()
        registry.counter("thing").inc(labels={"note": 'a"b'})
        assert 'note="a\\"b"' in render_prometheus(registry)

    def test_a_metric_can_be_re_declared_without_losing_data(self):
        registry = MetricsRegistry()
        registry.counter("dataflow_runs_total").inc()
        again = registry.counter("dataflow_runs_total")
        assert again.value() == 1.0

    def test_the_registry_exposes_a_default(self):
        from app_files.observability import default_registry

        assert isinstance(default_registry(), MetricsRegistry)

    def test_recording_against_the_default_does_not_raise(self):
        record_run("x", "ok", 0.1)


class TestAlertRules:
    def test_an_unknown_condition_is_rejected(self):
        with pytest.raises(ValueError, match="Unknown alert condition"):
            AlertRule("meteor_strike")

    def test_a_rule_defaults_its_name_to_its_condition(self):
        assert AlertRule("failure").name == "failure"

    def test_a_severity_string_is_coerced(self):
        assert AlertRule("failure", severity="critical").severity is AlertSeverity.CRITICAL

    def test_a_rule_round_trips_through_a_dict(self):
        rule = AlertRule("quality_drop", threshold=80.0, severity=AlertSeverity.CRITICAL)
        assert rule.as_dict()["threshold"] == 80.0
        assert rule.as_dict()["severity"] == "critical"


class TestAlertEvaluation:
    def test_a_failure_raises_a_critical_alert(self):
        alerts = evaluate_alerts({"status": "failed", "error": "bad csv"})
        assert alerts[0].condition == "failure"
        assert alerts[0].severity is AlertSeverity.CRITICAL
        assert "bad csv" in alerts[0].message

    def test_a_success_raises_nothing(self):
        assert evaluate_alerts({"status": "ok"}) == []

    def test_a_failure_rule_can_be_disabled_by_omitting_it(self):
        alerts = evaluate_alerts({"status": "failed"}, rules=[AlertRule("quality_drop", 80.0)])
        assert alerts == []

    def test_a_quality_drop_below_the_floor_fires(self):
        rules = [AlertRule("quality_drop", threshold=80.0)]
        alerts = evaluate_alerts({"status": "ok", "quality_score": 72.0}, rules)
        assert alerts[0].condition == "quality_drop"
        assert alerts[0].value == 72.0

    def test_a_quality_score_above_the_floor_is_quiet(self):
        rules = [AlertRule("quality_drop", threshold=80.0)]
        assert evaluate_alerts({"quality_score": 92.0}, rules) == []

    def test_a_quality_score_equal_to_the_floor_is_quiet(self):
        # The floor is a floor: at the threshold is still acceptable.
        rules = [AlertRule("quality_drop", threshold=80.0)]
        assert evaluate_alerts({"quality_score": 80.0}, rules) == []

    def test_a_sla_breach_above_the_ceiling_fires(self):
        rules = [AlertRule("sla_breach", threshold=10.0)]
        alerts = evaluate_alerts({"duration_seconds": 42.0}, rules)
        assert alerts[0].condition == "sla_breach"

    def test_a_duration_breach_above_the_budget_fires(self):
        rules = [AlertRule("duration_breach", threshold=30.0)]
        assert evaluate_alerts({"duration_seconds": 45.0}, rules)[0].condition == "duration_breach"

    def test_a_missing_value_does_not_fire(self):
        rules = [AlertRule("quality_drop", threshold=80.0)]
        assert evaluate_alerts({}, rules) == []

    def test_an_unparseable_value_does_not_fire(self):
        rules = [AlertRule("sla_breach", threshold=10.0)]
        assert evaluate_alerts({"duration_seconds": "not a number"}, rules) == []

    def test_the_source_and_run_id_are_carried_through(self):
        alert = evaluate_alerts({"status": "failed", "source": "crm", "run_id": "r-1"})[0]
        assert alert.source == "crm"
        assert alert.run_id == "r-1"

    def test_the_message_names_the_source(self):
        alert = evaluate_alerts({"status": "failed", "source": "crm"})[0]
        assert alert.message.startswith("crm:")

    def test_several_rules_can_fire_at_once(self):
        rules = [
            AlertRule("quality_drop", threshold=80.0),
            AlertRule("sla_breach", threshold=10.0),
        ]
        alerts = evaluate_alerts({"quality_score": 50.0, "duration_seconds": 90.0}, rules)
        assert {alert.condition for alert in alerts} == {"quality_drop", "sla_breach"}

    def test_build_alert_uses_the_given_message(self):
        alert = build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL, message="custom")
        assert alert.message.endswith("custom")


class TestAlertChannels:
    def test_a_webhook_channel_posts_json(self):
        calls = []

        def transport(url, body, headers, timeout):
            calls.append(json.loads(body))
            return 200

        channel = WebhookChannel("http://example.test/hook", transport=transport)
        assert channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL))
        assert calls[0]["condition"] == "failure"
        assert calls[0]["severity"] == "critical"

    def test_a_webhook_channel_signs_when_given_a_secret(self):
        seen = {}

        def transport(url, body, headers, timeout):
            seen.update(headers)
            return 200

        WebhookChannel("http://x", secret="s3cret", transport=transport).send(
            build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL)
        )
        assert seen["X-DataFlow-Signature"].startswith("sha256=")

    def test_a_rejected_webhook_is_reported_not_raised(self):
        channel = WebhookChannel("http://x", transport=lambda *a: 500)
        assert channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL)) is False

    def test_a_webhook_transport_error_is_swallowed(self):
        def transport(*args):
            raise OSError("no route")

        channel = WebhookChannel("http://x", transport=transport)
        assert channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL)) is False

    def test_a_slack_channel_sends_text(self):
        calls = []
        channel = SlackChannel("http://x", transport=lambda u, b, h, t: calls.append(json.loads(b)) or 200)
        channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL))
        assert "rotating_light" in calls[0]["text"]

    def test_a_slack_channel_marks_each_severity(self):
        calls = []
        channel = SlackChannel("http://x", transport=lambda u, b, h, t: calls.append(json.loads(b)) or 200)
        for severity in AlertSeverity:
            channel.send(build_alert("failure", 1.0, 0.0, severity))
        assert ":information_source:" in calls[0]["text"]
        assert ":warning:" in calls[1]["text"]

    def test_a_teams_channel_sends_a_message_card(self):
        calls = []
        channel = TeamsChannel("http://x", transport=lambda u, b, h, t: calls.append(json.loads(b)) or 200)
        channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.WARNING))
        assert calls[0]["@type"] == "MessageCard"
        assert calls[0]["themeColor"] == "FFA500"

    def test_an_email_channel_composes_without_sending(self):
        channel = EmailChannel()
        assert channel.send(build_alert("quality_drop", 50.0, 80.0, AlertSeverity.WARNING))
        assert "quality_drop" in channel.last_message[0]

    def test_an_email_channel_uses_the_injected_sender(self):
        sent = []
        channel = EmailChannel(sender=lambda subject, body: sent.append(subject) or True)
        channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL))
        assert sent

    def test_a_failing_email_sender_is_reported_not_raised(self):
        def bad_sender(subject, body):
            raise RuntimeError("smtp down")

        channel = EmailChannel(sender=bad_sender)
        assert channel.send(build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL)) is False


class TestAlertSink:
    def test_every_alert_reaches_every_channel(self):
        seen = []
        sink = AlertSink([WebhookChannel("http://x", transport=lambda u, b, h, t: seen.append(b) or 200)])
        sink.send([build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL),
                   build_alert("quality_drop", 1.0, 2.0, AlertSeverity.WARNING)])
        assert len(seen) == 2

    def test_the_sink_reports_per_channel_results(self):
        sink = AlertSink([WebhookChannel("http://x", transport=lambda u, b, h, t: 200)])
        results = sink.send([build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL)])
        assert results["webhook"] == [True]

    def test_notify_alert_evaluates_and_delivers(self):
        seen = []
        notify_alert(
            {"status": "failed"},
            channels=[WebhookChannel("http://x", transport=lambda u, b, h, t: seen.append(b) or 200)],
        )
        assert len(seen) == 1

    def test_notify_alert_returns_the_alerts(self):
        alerts = notify_alert({"status": "failed"}, channels=[])
        assert alerts[0].condition == "failure"

    def test_a_channel_with_no_name_is_still_counted(self):
        class Anonymous:
            def send(self, alert):
                return True

        results = AlertSink([Anonymous()]).send(
            [build_alert("failure", 1.0, 0.0, AlertSeverity.CRITICAL)]
        )
        assert results["channel"] == [True]


class TestHealth:
    def test_liveness_is_ok_with_no_dependencies(self):
        assert liveness().status is HealthStatus.OK

    def test_liveness_reports_200(self):
        assert liveness().http_status == 200

    def test_readiness_is_ok_when_no_check_fails(self):
        assert readiness().status is HealthStatus.OK

    def test_a_failing_required_check_is_unhealthy(self):
        report = readiness([("db", lambda: False)])
        assert report.status is HealthStatus.UNHEALTHY
        assert report.http_status == 503

    def test_a_failing_optional_check_is_degraded(self):
        report = readiness([("cache", lambda: False, False)])
        assert report.status is HealthStatus.DEGRADED
        assert report.http_status == 200

    def test_a_passing_check_keeps_readiness_ok(self):
        assert readiness([("db", lambda: True)]).status is HealthStatus.OK

    def test_a_raising_check_becomes_an_unhealthy_result(self):
        def blow_up():
            raise ConnectionError("refused")

        report = readiness([("db", blow_up)])
        assert report.status is HealthStatus.UNHEALTHY
        assert "ConnectionError" in report.checks[-1].detail

    def test_a_check_returning_a_message_is_unhealthy(self):
        report = readiness([("db", lambda: "disk full")])
        assert report.status is HealthStatus.UNHEALTHY
        assert report.checks[-1].detail == "disk full"

    def test_a_check_can_return_its_own_result(self):
        from app_files.observability import CheckResult

        report = readiness([("db", lambda: CheckResult("db", False, "down"))])
        assert report.checks[-1].detail == "down"

    def test_the_report_serialises(self):
        payload = readiness([("db", lambda: False)]).as_dict()
        assert payload["status"] == "unhealthy"
        assert payload["checks"][-1]["name"] == "db"

    def test_the_report_renders_a_readable_line_per_check(self):
        text = readiness([("db", lambda: False)]).render()
        assert "[FAIL] db" in text

    def test_an_optional_failure_is_marked_optional(self):
        assert "(optional)" in readiness([("cache", lambda: False, False)]).render()


class TestAlertSerialisation:
    def test_an_alert_round_trips_through_json(self):
        alert = Alert("failure", AlertSeverity.CRITICAL, "boom", source="crm", run_id="r1")
        assert json.loads(json.dumps(alert.as_dict()))["severity"] == "critical"
