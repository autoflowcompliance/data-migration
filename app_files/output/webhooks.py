"""Fire an HTTP POST when a run completes or fails.

The last output destination is often another system, and polling for whether a
run finished is worse than being told. A webhook is a final output: it gets the
same run summary the report does.

Delivery is best-effort and never raises into the pipeline. A run that produced
correct output must not be failed because a notification endpoint was down, so
failures are returned in the result rather than thrown.

The transport is injectable, which is what lets the tests drive a real local
listener (and what lets a caller plug in an async client).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

#: ``(url, body_bytes, headers, timeout) -> status_code``
Transport = Callable[[str, bytes, dict[str, str], float], int]

#: The events a caller can subscribe to.
EVENTS = ("run.completed", "run.failed")


@dataclass
class WebhookPayload:
    """What gets POSTed. Small, stable, and useful without another call."""

    event: str
    run_id: str
    status: str
    quality_score: float = 0.0
    rows_in: int = 0
    rows_out: int = 0
    output_location: str | None = None
    error: str | None = None
    source: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "event": self.event,
            "run_id": self.run_id,
            "status": self.status,
            "quality_score": round(float(self.quality_score), 1),
            "rows_in": int(self.rows_in),
            "rows_out": int(self.rows_out),
            "output_location": self.output_location,
            "source": self.source,
        }
        if self.error:
            payload["error"] = self.error
        payload.update(self.extra)
        return payload


@dataclass
class DeliveryResult:
    delivered: bool
    status_code: int | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "delivered": self.delivered,
            "status_code": self.status_code,
            "error": self.error,
        }


def _urllib_transport(url: str, body: bytes, headers: dict[str, str], timeout: float) -> int:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:  # a 4xx/5xx is a delivery result, not a crash
        return int(exc.code)


@dataclass
class Webhook:
    """One subscriber."""

    url: str
    events: tuple[str, ...] = EVENTS
    timeout: float = 5.0
    secret: str | None = None
    """When set, sent as an ``X-DataFlow-Signature`` HMAC so the receiver can
    verify the payload came from this tool."""

    def accepts(self, event: str) -> bool:
        return event in self.events

    def build_headers(self, body: bytes) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "User-Agent": "DataFlow-Webhook/1"}
        if self.secret:
            import hashlib
            import hmac

            signature = hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
            headers["X-DataFlow-Signature"] = f"sha256={signature}"
        return headers


class WebhookDispatcher:
    """Sends payloads to every subscriber that wants the event."""

    def __init__(
        self,
        webhooks: list[Webhook] | None = None,
        transport: Transport | None = None,
    ):
        self.webhooks = list(webhooks or [])
        self._transport = transport or _urllib_transport

    def add(self, webhook: Webhook) -> None:
        self.webhooks.append(webhook)

    def dispatch(self, payload: WebhookPayload) -> list[DeliveryResult]:
        """Deliver to all matching subscribers. Never raises."""
        body = json.dumps(payload.as_dict()).encode("utf-8")
        results = []
        for webhook in self.webhooks:
            if not webhook.accepts(payload.event):
                continue
            results.append(self._deliver(webhook, body))
        return results

    def _deliver(self, webhook: Webhook, body: bytes) -> DeliveryResult:
        try:
            status = self._transport(
                webhook.url, body, webhook.build_headers(body), webhook.timeout
            )
        except Exception as exc:  # noqa: BLE001 - a failed notification is not a failed run
            return DeliveryResult(False, None, f"{type(exc).__name__}: {exc}")
        delivered = 200 <= status < 300
        return DeliveryResult(
            delivered, status, None if delivered else f"HTTP {status}"
        )


def notify_completion(
    run_id: str,
    summary: dict[str, Any],
    dispatcher: WebhookDispatcher,
    output_location: str | None = None,
    error: str | None = None,
    source: str | None = None,
) -> list[DeliveryResult]:
    """Build the payload from a run summary and dispatch it."""
    failed = bool(error)
    payload = WebhookPayload(
        event="run.failed" if failed else "run.completed",
        run_id=run_id,
        status="failed" if failed else "completed",
        quality_score=float(summary.get("quality_score", 0.0) or 0.0),
        rows_in=int(summary.get("rows_in", 0) or 0),
        rows_out=int(summary.get("rows_out", 0) or 0),
        output_location=output_location,
        error=error,
        source=source,
    )
    return dispatcher.dispatch(payload)
