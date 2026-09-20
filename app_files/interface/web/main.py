"""NiceGUI entry point: ``python main.py`` or ``python -m app_files.interface.web.main``.

One codebase, three ways to run. The mode is decided by the licence file on
disk — a hosted demo and an unlicensed client install are the same thing here,
which is why there is no separate "demo build" to keep in sync.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nicegui import ui  # noqa: E402

from app_files.interface.web import routes  # noqa: E402,F401  (registers the routes)
from app_files.interface.web.reports import register_report_route  # noqa: E402
from app_files.licensing import current_mode  # noqa: E402

FAVICON = Path(__file__).resolve().parent / "assets" / "favicon.png"

DEFAULT_PORT = 8080


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


def main() -> None:
    """Start the server, honouring the environment the deployment provides."""
    register_report_route()
    licence, limits = current_mode()
    host = os.getenv("DATAREADY_HOST", "0.0.0.0")
    port = resolve_port()
    reload_enabled = os.getenv("DATAREADY_RELOAD", "0") == "1"
    show = os.getenv("DATAREADY_SHOW", "1") == "1"

    mode = "full" if not limits.demo else "demo"
    print(f"DataReady starting in {mode} mode on http://{host}:{port}")
    if licence.valid:
        print(f"Licensed to {licence.email} (issued {licence.issued})")
    else:
        print(f"No licence: {licence.reason}")

    ui.run(
        host=host,
        port=port,
        title="DataReady",
        favicon=FAVICON if FAVICON.is_file() else "⇄",
        reload=reload_enabled,
        show=show,
        uvicorn_logging_level="info",
        dark=False,
        storage_secret=os.getenv("DATAREADY_STORAGE_SECRET", "dataready-local-session"),
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()