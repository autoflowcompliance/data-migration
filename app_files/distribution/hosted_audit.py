"""Hosted audit service: a web form that takes a file and returns a report.

This is the no-install revenue path. The buyer uploads a file, the tool runs the
quality audit on it, and they get the report back — no Docker, no Python, no
desktop app.

The flow is deliberately split so each part is testable without a payment
provider or a live server:

* ``pricing_for(size_bytes)`` — the price tiers, pure arithmetic.
* ``create_order(...)`` — records an order and returns its status.
* ``PaymentProvider`` — an interface with a ``StubPaymentProvider`` (marks an
  order paid, no network) and a ``StripePaymentProvider`` that only constructs a
  Stripe Checkout session when ``STRIPE_API_KEY`` is set. Without the key it
  raises ``MissingCredentials`` naming the variable, rather than pretending.

Orders are stored as JSONL under ``audit_orders/`` so a run of the service has a
real, inspectable record — the same file a bookkeeper-operator would process.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def orders_dir() -> Path:
    """Where order records and reports live. ``AUTOFLOW_HOME`` overrides for tests."""
    override = os.getenv("AUTOFLOW_HOME")
    return (Path(override) if override else _REPO_ROOT) / "audit_orders"

# (max bytes, price in whole currency units, label)
TIERS: list[tuple[int, int, str]] = [
    (5 * 1024 * 1024, 99, "up to 5 MB"),
    (50 * 1024 * 1024, 249, "up to 50 MB"),
    (500 * 1024 * 1024, 499, "up to 500 MB"),
]
CURRENCY = "USD"


class PaymentError(RuntimeError):
    """Raised when a payment cannot be started."""


class MissingCredentials(PaymentError):
    def __init__(self, variable: str, purpose: str = "") -> None:
        detail = f" ({purpose})" if purpose else ""
        super().__init__(
            f"Stripe needs the environment variable {variable}{detail}. "
            "Set it, or run with the stub payment provider for a dry run."
        )


def pricing_for(size_bytes: int) -> dict[str, Any]:
    """The tier covering ``size_bytes``."""
    for limit, price, label in TIERS:
        if size_bytes <= limit:
            return {"price": price, "currency": CURRENCY, "tier": label, "max_bytes": limit}
    return {
        "price": 999,
        "currency": CURRENCY,
        "tier": "over 500 MB (manual quote)",
        "max_bytes": None,
    }


@dataclass
class Order:
    """One hosted-audit request."""

    order_id: str
    filename: str
    size_bytes: int
    price: int
    currency: str
    tier: str
    email: str = ""
    paid: bool = False
    status: str = "awaiting_payment"
    created_at: str = ""
    report_path: str = ""
    summary: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, filename: str, size_bytes: int, email: str = "") -> "Order":
        quote = pricing_for(size_bytes)
        return cls(
            order_id=uuid.uuid4().hex[:12],
            filename=filename,
            size_bytes=size_bytes,
            price=quote["price"],
            currency=quote["currency"],
            tier=quote["tier"],
            email=email,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class PaymentProvider(Protocol):
    def begin(self, order: Order) -> dict[str, Any]: ...


class StubPaymentProvider:
    """Marks an order paid immediately. For tests and offline demos."""

    name = "stub"

    def begin(self, order: Order) -> dict[str, Any]:
        order.paid = True
        order.status = "paid"
        return {"provider": self.name, "paid": True, "checkout_url": "", "order_id": order.order_id}


class StripePaymentProvider:
    """Real Stripe Checkout session, created only when a key is present."""

    name = "stripe"
    ENDPOINT = "https://api.stripe.com/v1/checkout/sessions"

    def __init__(
        self,
        api_key: str | None = None,
        success_url: str = "https://example.com/success",
        cancel_url: str = "https://example.com/cancel",
        transport=None,
    ) -> None:
        import os as _os

        self.api_key = api_key or _os.getenv("STRIPE_API_KEY") or _os.getenv("STRIPE_SECRET_KEY")
        self.success_url = success_url
        self.cancel_url = cancel_url
        self._transport = transport

    def transport(self):
        if self._transport is not None:
            return self._transport
        import requests

        def request(method, url, **kwargs):
            kwargs.setdefault("timeout", 60)
            return requests.request(method, url, **kwargs)

        return request

    def begin(self, order: Order) -> dict[str, Any]:
        if not self.api_key:
            raise MissingCredentials("STRIPE_API_KEY", "Stripe secret key")
        payload = {
            "mode": "payment",
            "success_url": self.success_url,
            "cancel_url": self.cancel_url,
            "line_items[0][quantity]": "1",
            "line_items[0][price_data][currency]": order.currency.lower(),
            "line_items[0][price_data][unit_amount]": str(order.price * 100),
            "line_items[0][price_data][product_data][name]": (
                f"Data quality audit — {order.filename} ({order.tier})"
            ),
            "client_reference_id": order.order_id,
        }
        response = self.transport()(
            "POST",
            self.ENDPOINT,
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        if getattr(response, "status_code", 0) != 200:
            raise PaymentError(
                f"Stripe rejected the checkout session with HTTP "
                f"{getattr(response, 'status_code', 'unknown')}."
            )
        body = response.json()
        order.status = "awaiting_payment"
        return {
            "provider": self.name,
            "paid": False,
            "checkout_url": body.get("url", ""),
            "session_id": body.get("id", ""),
            "order_id": order.order_id,
        }


def get_payment_provider(name: str | None = None, **kwargs: Any) -> PaymentProvider:
    """``stripe`` when a key is configured, otherwise the stub."""
    chosen = (name or os.getenv("AUTOFLOW_PAYMENT_PROVIDER") or "").strip().lower()
    if chosen == "stripe":
        return StripePaymentProvider(**kwargs)
    if chosen == "stub" or chosen == "":
        if chosen == "" and (os.getenv("STRIPE_API_KEY") or os.getenv("STRIPE_SECRET_KEY")):
            return StripePaymentProvider(**kwargs)
        return StubPaymentProvider()
    raise PaymentError(f"Unknown payment provider {name!r}. Use 'stripe' or 'stub'.")


def orders_path() -> Path:
    return orders_dir() / "orders.jsonl"


def save_order(order: Order) -> Path:
    path = orders_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(order.as_dict()) + "\n")
    return path


def read_orders() -> list[dict[str, Any]]:
    path = orders_path()
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def orders_frame() -> pd.DataFrame:
    entries = read_orders()
    columns = [
        "order_id", "created_at", "filename", "size_bytes", "tier", "price",
        "currency", "email", "paid", "status", "quality_score", "rows",
    ]
    if not entries:
        return pd.DataFrame(columns=columns)
    rows = []
    for entry in entries:
        summary = entry.get("summary") or {}
        rows.append(
            {
                "order_id": entry.get("order_id", ""),
                "created_at": entry.get("created_at", ""),
                "filename": entry.get("filename", ""),
                "size_bytes": entry.get("size_bytes", 0),
                "tier": entry.get("tier", ""),
                "price": entry.get("price", 0),
                "currency": entry.get("currency", ""),
                "email": entry.get("email", ""),
                "paid": entry.get("paid", False),
                "status": entry.get("status", ""),
                "quality_score": summary.get("quality_score", ""),
                "rows": summary.get("rows", ""),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def audit_bytes(data: bytes, filename: str) -> dict[str, Any]:
    """Run the quality audit a hosted order pays for.

    Uses the same ingestion and profiling the rest of the tool uses, so the
    report a hosted customer receives matches what an installed customer sees.
    """
    from app_files.ingestion import read_any
    from app_files.profiling import profile

    frame = read_any(data, filename=filename)
    prof = profile(frame)
    return {
        "rows": prof.row_count,
        "columns": prof.column_count,
        "quality_score": round(prof.overall, 1),
        "scores": {k: round(v, 1) for k, v in prof.scores.items()},
        "notes": list(prof.notes),
    }


def process_order(
    order: Order,
    data: bytes,
    provider: PaymentProvider | None = None,
) -> dict[str, Any]:
    """Run an order end to end: payment, audit, report on disk.

    With the stub provider the audit runs immediately. With Stripe the audit is
    held until payment is confirmed, because auditing before payment would give
    the work away.
    """
    provider = provider or get_payment_provider()
    payment = provider.begin(order)

    result: dict[str, Any] = {"order": order.as_dict(), "payment": payment}
    if not order.paid:
        save_order(order)
        result["message"] = (
            "Order recorded. The audit runs once payment is confirmed at the "
            "checkout URL."
        )
        return result

    summary = audit_bytes(data, order.filename)
    order.summary = summary
    order.status = "completed"
    report = orders_dir() / f"{order.order_id}_report.html"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_order_report(order, summary), encoding="utf-8")
    order.report_path = str(report)
    save_order(order)

    result["summary"] = summary
    result["report_path"] = str(report)
    result["message"] = f"Audit complete. Report written to {report}"
    return result


def render_order_report(order: Order, summary: dict[str, Any]) -> str:
    """The report a hosted customer downloads. Standalone, no external resources."""
    scores = "".join(
        f"<tr><th>{key}</th><td>{value}</td></tr>" for key, value in summary.get("scores", {}).items()
    )
    notes = "".join(f"<li>{note}</li>" for note in summary.get("notes", []))
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Data quality audit</title>"
        "<style>body{font-family:sans-serif;padding:24px;color:#111827;}"
        ".score{font-size:44px;font-weight:700;color:#C97A2E;}"
        "table{border-collapse:collapse;}th,td{border-bottom:1px solid #e5e7eb;"
        "padding:6px 10px;text-align:left;}" 
        "th{background:#f3f4f6;}</style></head><body>"
        "<h1>Data quality audit</h1>"
        f"<p>File: <strong>{order.filename}</strong> · {order.size_bytes:,} bytes · tier {order.tier}</p>"
        f"<p class='score'>{summary.get('quality_score', 0)}%</p>"
        f"<p>{summary.get('rows', 0)} rows · {summary.get('columns', 0)} columns</p>"
        f"<table>{scores}</table>"
        f"<h2>What we noticed</h2><ul>{notes}</ul>"
        f"<p style='font-size:12px;color:#6b7280;'>Order {order.order_id}.</p>"
        "</body></html>"
    )


def payment_is_wired() -> dict[str, Any]:
    """Whether a real payment provider is configured. Used by the UI and tests."""
    key_present = bool(os.getenv("STRIPE_API_KEY") or os.getenv("STRIPE_SECRET_KEY"))
    return {
        "provider": "stripe" if key_present else "stub",
        "stripe_key_present": key_present,
        "blocker": "" if key_present else "STRIPE_API_KEY is not set",
        "live_payments": key_present,
    }