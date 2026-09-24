"""Alerting on failure, quality drop and SLA breach.

Rules are data. A rule names a condition, a threshold and a severity, and
:func:`evaluate_alerts` turns run summaries into alerts. Channels deliver them —
the same HTTP-payload shape the webhook layer already uses, so a receiver
written for run notifications can accept alerts too.

A channel that fails does not raise. A missed alert is bad; a failed run because
an alert could not be sent is worse.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

Transport = Callable[[str, bytes, dict[str, str], float], int]

FAILURE = "failure"
QUALITY_DROP = "quality_drop"
SLA_BREACH = "sla_breach"
DURATION_BREACH = "duration_breach"
CONDITIONS = (FAILURE, QUALITY_DROP, SLA_BREACH, DURATION_BREACH)


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """One thing an operator should know about."""

    condition: str
    severity: AlertSeverity
    message: str
    source: str | None = None
    run_id: str | None = None
    value: float | None = None
    threshold: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "condition": self.condition,
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "run_id": self.run_id,
            "value": self.value,
            "threshold": self.threshold,
        }


@dataclass
class AlertRule:
    """A condition worth being told about."""

    condition: str
    threshold: float = 0.0
    severity: AlertSeverity = AlertSeverity.WARNING
    name: str = ""

    def __post_init__(self) -> None:
        if self.condition not in CONDITIONS:
            raise ValueError(
                f"Unknown alert condition {self.condition!r}. Allowed: {', '.join(CONDITIONS)}"
            )
        if not isinstance(self.severity, AlertSeverity):
            self.severity = AlertSeverity(str(self.severity))
        if not self.name:
            self.name = self.condition

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "condition": self.condition,
            "threshold": self.threshold,
            "severity": self.severity.value,
        }


def build_alert(
    condition: str,
    value: float,
    threshold: float,
    severity: AlertSeverity,
    source: str | None = None,
    run_id: str | None = None,
    message: str | None = None,
) -> Alert:
    """One place that decides what an alert says, so wording cannot drift."""
    if condition == FAILURE:
        detail = message or "run failed"
    elif condition == QUALITY_DROP:
        detail = message or f"quality score {value:.1f} is below {threshold:.1f}"
    elif condition == DURATION_BREACH:
        detail = message or f"run took {value:.1f}s, over the {threshold:.1f}s budget"
    else:
        detail = message or f"SLA value {value:.1f} exceeds {threshold:.1f}"
    if source:
        detail = f"{source}: {detail}"
    return Alert(
        condition=condition,
        severity=severity,
        message=detail,
        source=source,
        run_id=run_id,
        value=value,
        threshold=threshold,
    )


def evaluate_alerts(
    summary: Mapping[str, Any],
    rules: list[AlertRule] | None = None,
) -> list[Alert]:
    """Turn one run summary into alerts.

    Reads only keys the run summary already carries, so nothing has to be
    threaded through the pipeline to make this work.
    """
    rules = rules if rules is not None else [AlertRule(FAILURE, severity=AlertSeverity.CRITICAL)]
    source = str(summary.get("source")) if summary.get("source") is not None else None
    run_id = str(summary.get("run_id")) if summary.get("run_id") is not None else None
    status = str(summary.get("status", "ok")).lower()

    alerts: list[Alert] = []
    for rule in rules:
        if rule.condition == FAILURE:
            if status in {"failed", "error"}:
                alerts.append(
                    build_alert(
                        FAILURE, 1.0, rule.threshold, rule.severity, source, run_id,
                        message=str(summary.get("error") or "run failed"),
                    )
                )
            continue

        value = _summary_value(summary, rule.condition)
        if value is None:
            continue
        if rule.condition == QUALITY_DROP:
            # A quality score is a floor: below the threshold is the problem.
            if value < rule.threshold:
                alerts.append(
                    build_alert(QUALITY_DROP, value, rule.threshold, rule.severity, source, run_id)
                )
        elif value > rule.threshold:
            alerts.append(
                build_alert(rule.condition, value, rule.threshold, rule.severity, source, run_id)
            )
    return alerts


def _summary_value(summary: Mapping[str, Any], condition: str) -> float | None:
    if condition == QUALITY_DROP:
        raw = summary.get("quality_score")
    else:
        raw = summary.get("duration_seconds")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


class AlertChannel(Protocol):
    name: str

    def send(self, alert: Alert) -> bool: ...


def _urllib_transport(url: str, body: bytes, headers: dict[str, str], timeout: float) -> int:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


@dataclass
class WebhookChannel:
    """POSTs the alert as JSON to any URL."""

    url: str
    name: str = "webhook"
    timeout: float = 5.0
    secret: str | None = None
    transport: Transport | None = None

    def send(self, alert: Alert) -> bool:
        body = json.dumps(alert.as_dict()).encode("utf-8")
        headers = {"Content-Type": "application/json", "User-Agent": "DataFlow-Alert/1"}
        if self.secret:
            import hashlib
            import hmac

            signature = hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
            headers["X-DataFlow-Signature"] = f"sha256={signature}"
        transport = self.transport or _urllib_transport
        try:
            status = transport(self.url, body, headers, self.timeout)
        except Exception:  # noqa: BLE001 - a failed alert must not fail the run
            return False
        return 200 <= status < 300


@dataclass
class SlackChannel:
    """Slack incoming webhook. The message text is the alert message."""

    url: str
    name: str = "slack"
    timeout: float = 5.0
    transport: Transport | None = None

    def send(self, alert: Alert) -> bool:
        icon = {"info": ":information_source:", "warning": ":warning:",
                "critical": ":rotating_light:"}.get(alert.severity.value, ":bell:")
        body = json.dumps({"text": f"{icon} [{alert.severity.value.upper()}] {alert.message}"})
        transport = self.transport or _urllib_transport
        try:
            status = transport(
                self.url, body.encode("utf-8"),
                {"Content-Type": "application/json"}, self.timeout,
            )
        except Exception:  # noqa: BLE001
            return False
        return 200 <= status < 300


@dataclass
class TeamsChannel:
    """Microsoft Teams incoming webhook (MessageCard shape)."""

    url: str
    name: str = "teams"
    timeout: float = 5.0
    transport: Transport | None = None

    def send(self, alert: Alert) -> bool:
        colour = {"info": "0076D7", "warning": "FFA500", "critical": "D93F0B"}.get(
            alert.severity.value, "808080"
        )
        body = json.dumps(
            {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": colour,
                "summary": alert.message,
                "title": f"DataFlow alert: {alert.condition}",
                "text": alert.message,
            }
        )
        transport = self.transport or _urllib_transport
        try:
            status = transport(
                self.url, body.encode("utf-8"),
                {"Content-Type": "application/json"}, self.timeout,
            )
        except Exception:  # noqa: BLE001
            return False
        return 200 <= status < 300


@dataclass
class EmailChannel:
    """Composes an email and hands it to a sender function.

    SMTP is environment-specific (host, port, credentials, TLS), so the sender
    is injected rather than configured here. The default records the message
    instead of sending, which is what a dry run wants.
    """

    sender: Callable[[str, str], bool] | None = None
    recipients: tuple[str, ...] = ()
    name: str = "email"

    def send(self, alert: Alert) -> bool:
        subject = f"[DataFlow {alert.severity.value}] {alert.condition}"
        body = alert.message
        for key, value in alert.as_dict().items():
            body += f"\n{key}: {value}"
        if self.sender is None:
            self.last_message = (subject, body)
            return True
        try:
            return bool(self.sender(subject, body))
        except Exception:  # noqa: BLE001
            return False


@dataclass
class AlertSink:
    """Fans an alert out to every channel. Never raises."""

    channels: list[Any] = field(default_factory=list)

    def add(self, channel: Any) -> None:
        self.channels.append(channel)

    def send(self, alerts: list[Alert]) -> dict[str, list[bool]]:
        results: dict[str, list[bool]] = {}
        for alert in alerts:
            for channel in self.channels:
                results.setdefault(getattr(channel, "name", "channel"), []).append(
                    bool(channel.send(alert))
                )
        return results


def notify_alert(
    summary: Mapping[str, Any],
    channels: list[Any] | None = None,
    rules: list[AlertRule] | None = None,
) -> list[Alert]:
    """Evaluate and deliver in one call. Returns the alerts that fired."""
    alerts = evaluate_alerts(summary, rules)
    if alerts and channels:
        AlertSink(list(channels)).send(alerts)
    return alerts


__all__ = [
    "CONDITIONS",
    "DURATION_BREACH",
    "FAILURE",
    "QUALITY_DROP",
    "SLA_BREACH",
    "Alert",
    "AlertChannel",
    "AlertRule",
    "AlertSeverity",
    "AlertSink",
    "EmailChannel",
    "SlackChannel",
    "TeamsChannel",
    "WebhookChannel",
    "build_alert",
    "evaluate_alerts",
    "notify_alert",
]
