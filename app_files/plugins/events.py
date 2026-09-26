"""Lifecycle events.

The output layer already fires a webhook when a run completes. This is the same
idea one level down: an in-process bus that any subscriber can attach to, so an
external system reacts to a lifecycle point by registering a handler rather than
by polling or by editing the layer that reached the point.

A handler that raises does not raise into the emitter. The reasoning is the same
as for an alert channel: a correct run must not fail because an observer did.
The failure is reported in the receipt, where the caller can see it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LifecycleEvent(str, Enum):
    """The points a subscriber can attach to."""

    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    OUTPUT_WRITTEN = "output.written"
    JOB_SUBMITTED = "job.submitted"
    JOB_FINISHED = "job.finished"
    RECONCILIATION_DONE = "reconciliation.done"
    PLUGIN_LOADED = "plugin.loaded"


@dataclass
class EventReceipt:
    """One handler's outcome for one event."""

    event: str
    handler: str
    ok: bool
    detail: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "handler": self.handler,
            "ok": self.ok,
            "detail": self.detail,
        }


def _event_key(event: LifecycleEvent | str) -> str:
    return event.value if isinstance(event, LifecycleEvent) else str(event)


@dataclass
class EventBus:
    """Register handlers per event and emit to them.

    ``subscribe`` with a wildcard ``"*"`` receives every event. That is what a
    generic forwarder or a test recorder wants, and spelling it as a literal
    keeps the matching rule obvious.
    """

    handlers: dict[str, list[tuple[str, Callable[[str, dict[str, Any]], Any]]]] = field(
        default_factory=dict
    )

    def subscribe(
        self,
        event: LifecycleEvent | str,
        handler: Callable[[str, dict[str, Any]], Any],
        name: str = "",
    ) -> str:
        if not callable(handler):
            raise ValueError(f"Handler must be callable, got {type(handler).__name__}")
        key = _event_key(event)
        label = name or getattr(handler, "__name__", "handler")
        self.handlers.setdefault(key, []).append((label, handler))
        return label

    def unsubscribe(self, event: LifecycleEvent | str, name: str) -> bool:
        key = _event_key(event)
        entries = self.handlers.get(key, [])
        kept = [entry for entry in entries if entry[0] != name]
        removed = len(kept) != len(entries)
        if kept:
            self.handlers[key] = kept
        else:
            self.handlers.pop(key, None)
        return removed

    def subscribers(self, event: LifecycleEvent | str) -> list[str]:
        key = _event_key(event)
        exact = [name for name, _ in self.handlers.get(key, [])]
        wildcard = [name for name, _ in self.handlers.get("*", [])]
        return exact + wildcard

    def emit(
        self,
        event: LifecycleEvent | str,
        payload: dict[str, Any] | None = None,
    ) -> list[EventReceipt]:
        """Deliver to every matching handler. Never raises."""
        key = _event_key(event)
        data = dict(payload or {})
        receipts: list[EventReceipt] = []
        for source in (key, "*"):
            for name, handler in list(self.handlers.get(source, [])):
                try:
                    handler(key, data)
                except Exception as exc:  # noqa: BLE001 - an observer must not fail a run
                    receipts.append(
                        EventReceipt(key, name, False, f"{type(exc).__name__}: {exc}")
                    )
                else:
                    receipts.append(EventReceipt(key, name, True, None))
        return receipts


_BUS = EventBus()


def bus() -> EventBus:
    return _BUS


def subscribe(
    event: LifecycleEvent | str,
    handler: Callable[[str, dict[str, Any]], Any],
    name: str = "",
) -> str:
    return _BUS.subscribe(event, handler, name)


def emit(event: LifecycleEvent | str, payload: dict[str, Any] | None = None) -> list[EventReceipt]:
    return _BUS.emit(event, payload)


__all__ = [
    "EventBus",
    "EventReceipt",
    "LifecycleEvent",
    "bus",
    "emit",
    "subscribe",
]
