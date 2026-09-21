"""Per-browser-session storage for the most recent run.

NiceGUI pages are rebuilt per request, so the results page cannot receive the
run outcome as an argument — it has to be stashed somewhere keyed by client
and read back. A module-level dict is enough here: the app is a single-process
local tool or a small hosted demo, and entries are bounded by dropping the
oldest when the store grows past :data:`MAX_SESSIONS`.
"""

from __future__ import annotations

import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

MAX_SESSIONS = 64


@dataclass
class SessionData:
    """What a single browser session is holding onto between pages."""

    outcome: Any = None
    """The last :class:`~app_files.interface.web.state.RunOutcome`, if any."""
    template: str = "hubspot"
    output_format: str = "csv"
    batch: Any = None
    """The last :class:`~app_files.batch.runner.BatchResult`, if any."""
    runs_used: int = 0
    """Completed demo runs in this session, for the run allowance.

    Stored on the session rather than in ``app.storage.browser`` directly
    because that storage is a plain dict that only accepts simple values, and
    because this keeps the counter next to the rest of the per-client state.
    The session itself is keyed on the browser cookie, so the count survives
    every page navigation and resets when the cookie does.
    """
    extras: dict[str, Any] = field(default_factory=dict)


_sessions: "OrderedDict[str, SessionData]" = OrderedDict()


def current_key() -> str:
    """The key for the browser making this request, or a shared fallback.

    NiceGUI builds a page *before* the client's WebSocket handshake, so
    ``client.tab_id`` and ``client.id`` are both unusable here: the tab id is
    still unset, and the client id is freshly generated for every full-page
    navigation. Keying on the client id loses the run the moment the user
    lands on the results page, which is exactly the bug this avoids.

    ``app.storage.browser`` is cookie-backed, so it is stable across
    navigations and reloads. The trade-off is that it is shared between tabs
    of the same browser — acceptable, and arguably right, for a single-user
    local tool or a demo session.

    The fallback keeps the helpers usable outside a request context, which is
    what lets the test suite exercise them without a running server.
    """
    try:
        from nicegui import app, context

        if context.client is not None:
            return str(app.storage.browser["id"])
    except Exception:  # noqa: BLE001 - no request context is a normal case
        pass

    return "__global__"


def session(key: str | None = None) -> SessionData:
    """Get (creating if needed) the session for ``key``."""
    resolved = key or current_key()
    if resolved not in _sessions:
        _sessions[resolved] = SessionData()
    _sessions.move_to_end(resolved)
    while len(_sessions) > MAX_SESSIONS:
        _sessions.popitem(last=False)
    return _sessions[resolved]


def set_outcome(outcome: Any, key: str | None = None) -> None:
    session(key).outcome = outcome


def get_outcome(key: str | None = None) -> Any:
    return session(key).outcome


def clear(key: str | None = None) -> None:
    resolved = key or current_key()
    _sessions.pop(resolved, None)


def reset_all() -> None:
    """Drop every session. Used by tests to keep them independent."""
    _sessions.clear()


# -------------------------------------------------------- demo run allowance
# The demo allows a fixed number of runs per browser session. The count lives
# on the cookie-keyed session so it survives navigation, and is checked and
# incremented in one place from the upload route.

def runs_used(key: str | None = None) -> int:
    """How many runs this session has already started."""
    return session(key).runs_used


def runs_remaining(allowance: int | None, key: str | None = None) -> int | None:
    """Runs left, or ``None`` when the mode has no allowance."""
    if allowance is None:
        return None
    return max(0, allowance - runs_used(key))


def register_run(key: str | None = None) -> int:
    """Record a started run and return the new count."""
    target = session(key)
    target.runs_used += 1
    return target.runs_used


def reset_runs(key: str | None = None) -> None:
    session(key).runs_used = 0


# --------------------------------------------------------------- report route
# A QA report runs to hundreds of kilobytes. Pushing that through NiceGUI's
# element tree as ``ui.html`` content exceeds the WebSocket message limit and
# drops the connection, so reports are served over HTTP instead and the results
# page embeds them in an iframe.

_reports: "OrderedDict[str, str]" = OrderedDict()
MAX_REPORTS = 64


def publish_report(html: str) -> str:
    """Store a rendered report and return the token that addresses it."""
    token = uuid.uuid4().hex
    _reports[token] = html
    while len(_reports) > MAX_REPORTS:
        _reports.popitem(last=False)
    return token


def get_report(token: str) -> str | None:
    return _reports.get(token)