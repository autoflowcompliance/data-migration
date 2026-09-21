"""Server settings shared by every UI.

Stdlib only, and no import of either UI framework. The launcher must be able
to decide which interface to start — and on which port — before either
framework is importable, so a checkout that installed just one of them still
starts cleanly.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

DEFAULT_PORT = 8080
DEFAULT_HOST = "0.0.0.0"

NICEGUI_UI = "nicegui"
DATAFLOW_UI = "dataflow"
DEFAULT_UI = DATAFLOW_UI
AVAILABLE_UIS = (DATAFLOW_UI, NICEGUI_UI)


def resolve_port(env: Mapping[str, str] | None = None) -> int:
    """The TCP port to bind, in precedence order.

    ``PORT`` first, because PaaS platforms (Render, Heroku, Fly via its
    fallback) inject it and route traffic only to that port — ignoring it
    makes the platform fail the deploy with "no open ports detected". Then
    ``DATAREADY_PORT`` for an explicit local/container setting, then the
    built-in default.
    """
    env = os.environ if env is None else env
    raw = env.get("PORT") or env.get("DATAREADY_PORT") or ""
    try:
        return int(raw)
    except (TypeError, ValueError):
        return DEFAULT_PORT


def resolve_host(env: Mapping[str, str] | None = None) -> str:
    env = os.environ if env is None else env
    return env.get("DATAREADY_HOST") or DEFAULT_HOST


def resolve_ui(env: Mapping[str, str] | None = None) -> str:
    """Which interface to launch.

    Defaults to DataFlow. An unrecognised value falls back to the default
    rather than failing the boot — a typo in DATAREADY_UI should not take a
    hosted demo down.
    """
    env = os.environ if env is None else env
    requested = (env.get("DATAREADY_UI") or "").strip().lower()
    return requested if requested in AVAILABLE_UIS else DEFAULT_UI