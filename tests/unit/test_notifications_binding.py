"""The binding that makes a config's ``notifications:`` block real (Layer 8 + 15).

Exercised against real YAML files on disk, with the transport injected at the
seam the webhook layer already exposes — so "delivered" means a payload was
actually produced and offered to a transport, not that a stub was called.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app_files.observability import (
    AlertSink,
    NotificationConfigError,
    WebhookChannel,
    notify_run,
)
from app_files.observability.binding import declared_alert_rules, notifications_block


def _config(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "crm.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def _collector():
    """A transport that records each body and returns 200."""
    bodies = []

    def transport(url, body, headers, timeout):
        bodies.append(json.loads(body))
        return 200

    return transport, bodies


def _alert_sink(url="http://x"):
    seen = []
    sink = AlertSink(
        [WebhookChannel(url, transport=lambda u, b, h, t: seen.append(json.loads(b)) or 200)]
    )
    return sink, seen


GOOD_RUN = {"status": "ok", "quality_score": 95.0, "rows_in": 10, "rows_out": 10}
BAD_RUN = {"status": "failed", "error": "bad csv", "quality_score": 20.0}
CHANNEL_BLOCK = "  channels:\n    - type: webhook\n      url: http://x\n"


class TestReadingTheBlock:
    def test_no_block_reads_as_none(self, tmp_path):
        config = _config(tmp_path, "crm: X\nfields: []\n")
        assert notifications_block(config) is None

    def test_a_block_is_found(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  alerts: []\n")
        assert notifications_block(config) is not None

    def test_an_unknown_config_name_reads_as_none(self):
        assert notifications_block("definitely-not-a-crm") is None

    def test_no_alerts_key_defaults_to_a_failure_alert(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  channels: []\n")
        assert [rule.condition for rule in declared_alert_rules(config)] == ["failure"]

    def test_an_explicit_empty_alerts_list_opts_out(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  alerts: []\n")
        assert declared_alert_rules(config) == []

    def test_a_single_alert_mapping_is_accepted(self, tmp_path):
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  alerts:\n    condition: quality_drop\n"
            "    threshold: 80\n",
        )
        rules = declared_alert_rules(config)
        assert len(rules) == 1
        assert rules[0].condition == "quality_drop"

    def test_an_unknown_condition_is_rejected(self, tmp_path):
        config = _config(
            tmp_path, "crm: X\nnotifications:\n  alerts:\n    - condition: meteor_strike\n"
        )
        with pytest.raises(NotificationConfigError, match="Unknown alert condition"):
            declared_alert_rules(config)

    def test_an_alert_without_a_condition_is_rejected(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  alerts:\n    - threshold: 1\n")
        with pytest.raises(NotificationConfigError, match="no condition"):
            declared_alert_rules(config)

    def test_an_unknown_severity_is_rejected(self, tmp_path):
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  alerts:\n    - condition: failure\n"
            "      severity: apocalyptic\n",
        )
        with pytest.raises(NotificationConfigError, match="Unknown alert severity"):
            declared_alert_rules(config)


class TestNoBlock:
    def test_a_config_without_the_block_is_untouched(self, tmp_path):
        config = _config(tmp_path, "crm: X\nfields: []\n")
        assert notify_run(config, GOOD_RUN, run_id="r-1") is None

    def test_configured_and_clean_is_not_none(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  alerts: []\n")
        outcome = notify_run(config, GOOD_RUN, run_id="r-1")
        assert outcome is not None
        assert outcome.alerted is False


class TestAlerts:
    def test_a_failure_fires_the_default_alert(self, tmp_path):
        config = _config(tmp_path, f"crm: X\nnotifications:\n{CHANNEL_BLOCK}")
        sink, seen = _alert_sink()
        outcome = notify_run(config, BAD_RUN, run_id="r-1", sink=sink)
        assert outcome.alerted is True
        assert seen[0]["condition"] == "failure"

    def test_a_successful_run_does_not_fire_the_default_alert(self, tmp_path):
        config = _config(tmp_path, f"crm: X\nnotifications:\n{CHANNEL_BLOCK}")
        sink, seen = _alert_sink()
        outcome = notify_run(config, GOOD_RUN, run_id="r-1", sink=sink)
        assert outcome.alerted is False
        assert seen == []

    def test_a_declared_quality_floor_fires_on_a_drop(self, tmp_path):
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  alerts:\n    - condition: quality_drop\n"
            f"      threshold: 80\n{CHANNEL_BLOCK}",
        )
        sink, seen = _alert_sink()
        outcome = notify_run(
            config, {"status": "ok", "quality_score": 72.0}, run_id="r-1", sink=sink
        )
        assert outcome.alerted is True
        assert seen[0]["condition"] == "quality_drop"

    def test_a_quality_score_above_the_floor_is_quiet(self, tmp_path):
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  alerts:\n    - condition: quality_drop\n"
            f"      threshold: 80\n{CHANNEL_BLOCK}",
        )
        sink, seen = _alert_sink()
        outcome = notify_run(
            config, {"status": "ok", "quality_score": 92.0}, run_id="r-1", sink=sink
        )
        assert outcome.alerted is False
        assert seen == []


class TestCompletionWebhooks:
    def test_a_successful_run_posts_completed(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url: http://hook\n")
        transport, bodies = _collector()
        outcome = notify_run(
            config, GOOD_RUN, run_id="r-1", output_location="out", transport=transport
        )
        assert outcome.delivered is True
        assert bodies[0]["event"] == "run.completed"
        assert bodies[0]["output_location"] == "out"
        assert bodies[0]["quality_score"] == 95.0

    def test_a_failed_run_posts_failed(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url: http://hook\n")
        transport, bodies = _collector()
        notify_run(config, BAD_RUN, run_id="r-1", error="bad csv", transport=transport)
        assert bodies[0]["event"] == "run.failed"
        assert bodies[0]["error"] == "bad csv"

    def test_a_dead_endpoint_is_reported_not_raised(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url: http://dead\n")
        outcome = notify_run(config, GOOD_RUN, run_id="r-1", transport=lambda u, b, h, t: 500)
        assert outcome.delivered is False
        assert outcome.failed_deliveries == 1

    def test_a_transport_error_is_swallowed(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url: http://dead\n")

        def boom(*args):
            raise OSError("no route")

        outcome = notify_run(config, GOOD_RUN, run_id="r-1", transport=boom)
        assert outcome.delivered is False

    def test_an_event_filter_is_honoured(self, tmp_path):
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  webhooks:\n    - url: http://hook\n"
            "      events: [run.failed]\n",
        )
        transport, bodies = _collector()
        outcome = notify_run(config, GOOD_RUN, run_id="r-1", transport=transport)
        assert bodies == []
        assert outcome.deliveries == []


class TestSecrets:
    def test_a_missing_url_env_fails_closed(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_HOOK", raising=False)
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url_env: MY_HOOK\n")
        with pytest.raises(NotificationConfigError, match="MY_HOOK"):
            notify_run(config, GOOD_RUN, run_id="r-1")

    def test_a_url_env_is_read(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MY_HOOK", "http://from-env")
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url_env: MY_HOOK\n")
        seen = {}

        def transport(url, body, headers, timeout):
            seen["url"] = url
            return 200

        notify_run(config, GOOD_RUN, run_id="r-1", transport=transport)
        assert seen["url"] == "http://from-env"

    def test_a_secret_env_signs_the_payload(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOOK_SECRET", "s3cret")
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  webhooks:\n    - url: http://hook\n"
            "      secret_env: HOOK_SECRET\n",
        )
        seen = {}

        def transport(url, body, headers, timeout):
            seen["headers"] = headers
            return 200

        notify_run(config, GOOD_RUN, run_id="r-1", transport=transport)
        assert seen["headers"]["X-DataFlow-Signature"].startswith("sha256=")

    def test_no_secret_means_no_signature(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url: http://hook\n")
        seen = {}

        def transport(url, body, headers, timeout):
            seen["headers"] = headers
            return 200

        notify_run(config, GOOD_RUN, run_id="r-1", transport=transport)
        assert "X-DataFlow-Signature" not in seen["headers"]


class TestChannelValidation:
    def test_an_unknown_channel_type_is_rejected(self, tmp_path):
        config = _config(
            tmp_path,
            "crm: X\nnotifications:\n  alerts: []\n  channels:\n"
            "    - type: carrier_pigeon\n      url: http://x\n",
        )
        with pytest.raises(NotificationConfigError, match="Unknown channel type"):
            notify_run(config, GOOD_RUN, run_id="r-1")

    def test_a_channel_without_a_url_is_rejected(self, tmp_path):
        config = _config(
            tmp_path, "crm: X\nnotifications:\n  alerts: []\n  channels:\n    - type: slack\n"
        )
        with pytest.raises(NotificationConfigError, match="url or a url_env"):
            notify_run(config, GOOD_RUN, run_id="r-1")


class TestSummary:
    def test_the_summary_reports_what_was_delivered(self, tmp_path):
        config = _config(tmp_path, "crm: X\nnotifications:\n  webhooks:\n    - url: http://hook\n")
        outcome = notify_run(config, GOOD_RUN, run_id="r-1", transport=lambda u, b, h, t: 200)
        assert outcome.summary()["webhooks_delivered"] == 1
        assert outcome.summary()["webhooks_failed"] == 0
