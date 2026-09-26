"""Bind a config's ``notifications:`` block into a run.

Two layers were complete and tested with no caller in an actual run. The
completion webhook (Layer 8) knew how to POST a run summary and could not,
because nothing built a dispatcher from configuration. The alerting layer
(Layer 15) knew how to turn a run summary into alerts on failure, quality drop
and SLA breach, and could not, for the same reason. The spec asks for both "so
an external system is notified of every run without polling" and "no failure is
silent" — and neither happened.

This binds them the way :mod:`app_files.rules.binding` binds rules and
:mod:`app_files.privacy.binding` binds masking: nothing runs unless the config
declares a ``notifications:`` block, so a config without one is byte-identical
to before and pays for none of this.

Delivery is best-effort. A run that produced correct output is never failed
because an alert endpoint was down; the outcome reports what was delivered so
the caller can decide what to print.

Secrets are named, not committed: ``url_env`` and ``secret_env`` read a URL or
an HMAC key from the environment, so a webhook endpoint and its signing key do
not live in the YAML.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from app_files.mappers.schema import CONFIG_DIR
from app_files.observability.alerting import (
    FAILURE,
    Alert,
    AlertRule,
    AlertSeverity,
    AlertSink,
    SlackChannel,
    TeamsChannel,
    WebhookChannel,
    evaluate_alerts,
)
from app_files.output.webhooks import (
    DeliveryResult,
    Webhook,
    WebhookDispatcher,
    notify_completion,
)


class NotificationConfigError(ValueError):
    """A ``notifications:`` block that cannot be honoured. Fail closed."""


def _config_path(crm: str | Path) -> Path | None:
    path = Path(crm)
    if not path.exists():
        path = CONFIG_DIR / f"{str(crm).strip().lower()}.yaml"
    return path if path.exists() else None


def notifications_block(crm: str | Path) -> dict[str, Any] | None:
    """The raw ``notifications:`` mapping a config declares, or None."""
    path = _config_path(crm)
    if path is None:
        return None
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    block = data.get("notifications") if isinstance(data, dict) else None
    return block if isinstance(block, dict) else None


def _resolve(value: Any, *, env: str | None, what: str) -> str:
    if env:
        resolved = os.getenv(env, "")
        if not resolved:
            raise NotificationConfigError(
                f"{what} names environment variable {env!r}, which is not set."
            )
        return resolved
    if not value:
        raise NotificationConfigError(f"{what} needs a url or a url_env.")
    return str(value)


def _severity(raw: Any) -> AlertSeverity:
    try:
        return AlertSeverity(str(raw or "warning").lower())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in AlertSeverity)
        raise NotificationConfigError(
            f"Unknown alert severity {raw!r}. Allowed: {allowed}"
        ) from exc


def declared_alert_rules(crm: str | Path) -> list[AlertRule]:
    """The alert rules a config declares. Empty when it declares none.

    A ``notifications:`` block that omits ``alerts:`` entirely gets the built-in
    default, a critical alert on failure: a buyer who configured a channel did
    so to be told when a run goes wrong, and a failure going unannounced is the
    one alert nobody wants to opt into. An explicit ``alerts: []`` means "no
    alerts", so opting out stays possible.
    """
    block = notifications_block(crm)
    if block is None:
        return []
    if "alerts" not in block:
        return [AlertRule(FAILURE, severity=AlertSeverity.CRITICAL)]
    raw = block.get("alerts") or []
    if isinstance(raw, dict):
        raw = [raw]
    rules = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise NotificationConfigError(f"Alert {index} must be a mapping.")
        condition = item.get("condition")
        if not condition:
            raise NotificationConfigError(f"Alert {index} has no condition.")
        try:
            rules.append(
                AlertRule(
                    condition=str(condition),
                    threshold=float(item.get("threshold", 0.0)),
                    severity=_severity(item.get("severity")),
                    name=str(item.get("name") or condition),
                )
            )
        except ValueError as exc:
            raise NotificationConfigError(str(exc)) from exc
    return rules


def _declared_channels(block: dict[str, Any]) -> list[Any]:
    raw = block.get("channels") or []
    if isinstance(raw, dict):
        raw = [raw]
    channels: list[Any] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise NotificationConfigError(f"Channel {index} must be a mapping.")
        kind = str(item.get("type") or "").strip().lower()
        url = _resolve(
            item.get("url"), env=item.get("url_env"), what=f"Channel {index} ({kind or '?'})"
        )
        if kind == "slack":
            channels.append(SlackChannel(url=url))
        elif kind == "teams":
            channels.append(TeamsChannel(url=url))
        elif kind == "webhook":
            channels.append(WebhookChannel(url=url))
        else:
            raise NotificationConfigError(
                f"Unknown channel type {kind!r}. Allowed: webhook, slack, teams"
            )
    return channels


def _declared_webhooks(block: dict[str, Any]) -> list[Webhook]:
    raw = block.get("webhooks") or []
    if isinstance(raw, dict):
        raw = [raw]
    webhooks: list[Webhook] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise NotificationConfigError(f"Webhook {index} must be a mapping.")
        url = _resolve(
            item.get("url"), env=item.get("url_env"), what=f"Webhook {index}"
        )
        secret = None
        if item.get("secret_env"):
            secret = os.getenv(str(item["secret_env"])) or None
        events = item.get("events")
        webhooks.append(
            Webhook(
                url=url,
                events=tuple(events) if events else Webhook.events,
                timeout=float(item.get("timeout", 5.0)),
                secret=secret,
            )
        )
    return webhooks


@dataclass
class NotificationOutcome:
    """What one run told the outside world, and how it went."""

    alerts: list[Alert] = field(default_factory=list)
    channel_results: dict[str, list[bool]] = field(default_factory=dict)
    deliveries: list[DeliveryResult] = field(default_factory=list)

    @property
    def alerted(self) -> bool:
        return bool(self.alerts)

    @property
    def delivered(self) -> bool:
        return all(result.delivered for result in self.deliveries)

    @property
    def failed_deliveries(self) -> int:
        return sum(1 for result in self.deliveries if not result.delivered)

    def summary(self) -> dict[str, Any]:
        return {
            "alerts": [alert.as_dict() for alert in self.alerts],
            "channels": self.channel_results,
            "webhooks_delivered": sum(
                1 for result in self.deliveries if result.delivered
            ),
            "webhooks_failed": self.failed_deliveries,
        }


def notify_run(
    crm: str | Path,
    summary: dict[str, Any],
    *,
    run_id: str,
    output_location: str | None = None,
    error: str | None = None,
    source: str | None = None,
    transport: Any = None,
    sink: AlertSink | None = None,
) -> NotificationOutcome | None:
    """Evaluate alerts and fire completion webhooks for one run.

    Returns None when the config declares no ``notifications:`` block, so the
    caller can tell "nothing configured" from "configured and clean". Never
    raises for a delivery problem; an invalid block raises
    :class:`NotificationConfigError` so a typo fails loudly.

    ``transport`` is the seam the webhook layer already exposes
    (``(url, body, headers, timeout) -> status``), so a caller can drive a real
    local listener or an async client.
    """
    block = notifications_block(crm)
    if block is None:
        return None

    rules = declared_alert_rules(crm)
    channels = _declared_channels(block)
    webhooks = _declared_webhooks(block)

    alerts = evaluate_alerts(summary, rules)
    results: dict[str, list[bool]] = {}
    if alerts and channels:
        results = (sink or AlertSink(channels)).send(alerts)

    deliveries: list[DeliveryResult] = []
    if webhooks:
        dispatcher = WebhookDispatcher(webhooks, transport=transport)
        deliveries = notify_completion(
            run_id,
            summary,
            dispatcher,
            output_location=output_location,
            error=error,
            source=source,
        )
    return NotificationOutcome(
        alerts=alerts, channel_results=results, deliveries=deliveries
    )
