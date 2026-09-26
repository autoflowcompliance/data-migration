"""Golden: a configured ``notifications:`` block produces a known outcome.

The input is a real config file; the transports are deterministic, so the
outcome — which alert fires, its exact message, and what was delivered — must
be byte-for-byte what the fixture records. If a change alters the alert
message or the delivery shape, this fails rather than quietly drifting.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.observability import AlertSink, WebhookChannel, notify_run

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "notifications"


def _run():
    config = GOLDEN / "crm.yaml"
    alert_bodies: list[dict] = []
    sink = AlertSink(
        [
            WebhookChannel(
                "http://hook",
                transport=lambda u, b, h, t: alert_bodies.append(json.loads(b)) or 200,
            )
        ]
    )
    outcome = notify_run(
        config,
        {
            "status": "ok",
            "quality_score": 71.5,
            "source": "contacts",
            "run_id": "run-7",
        },
        run_id="run-7",
        source="contacts",
        transport=lambda u, b, h, t: 200,
        sink=sink,
    )
    assert outcome is not None
    return outcome


def test_the_notification_outcome_matches_the_golden_file():
    outcome = _run()
    expected = json.loads((GOLDEN / "expected_summary.json").read_text(encoding="utf-8"))
    assert outcome.summary() == expected


def test_the_golden_input_is_the_config_the_test_reads():
    # Guards against the fixture being edited to match a changed outcome.
    text = (GOLDEN / "crm.yaml").read_text(encoding="utf-8")
    assert "quality_drop" in text
    assert "threshold: 90" in text


def test_the_alert_message_is_stable():
    outcome = _run()
    assert outcome.alerts[0].message == "contacts: quality score 71.5 is below 90.0"
