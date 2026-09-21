"""Server settings for the launcher.

Stdlib only, and no import of the web framework. The launcher must be able to
decide which port to bind before the framework is importable, so a checkout
mid-install still starts cleanly.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

DEFAULT_PORT = 8080
DEFAULT_HOST = "0.0.0.0"


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