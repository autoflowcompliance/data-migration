"""NiceGUI entry point: ``python main.py`` or ``python -m app_files.interface.web.main``.

One codebase, three ways to run. The mode is decided by the licence file on
disk — a hosted demo and an unlicensed client install are the same thing here,
which is why there is no separate "demo build" to keep in sync.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nicegui import ui  # noqa: E402

from app_files.interface.web import routes  # noqa: E402,F401  (registers the routes)
from app_files.interface.web.reports import register_report_route  # noqa: E402
from app_files.licensing import current_mode  # noqa: E402
from app_files.settings import resolve_host, resolve_port  # noqa: E402

FAVICON = Path(__file__).resolve().parent / "assets" / "favicon.png"


def run_server(host: str | None = None, port: int | None = None) -> None:
    """Start the NiceGUI server on the resolved host and port.

    The host/port can be supplied by the launcher; anything omitted is
    resolved from the environment via :mod:`app_files.settings`, so this stays
    runnable directly for the NiceGUI-only workflow.
    """
    register_report_route()
    licence, limits = current_mode()
    host = host or resolve_host()
    port = port if port is not None else resolve_port()
    reload_enabled = os.getenv("DATAREADY_RELOAD", "0") == "1"
    show = os.getenv("DATAREADY_SHOW", "1") == "1"

    mode = "full" if not limits.demo else "demo"
    print(f"DataFlow starting in {mode} mode on http://{host}:{port}")
    if licence.valid:
        print(f"Licensed to {licence.email} (issued {licence.issued})")
    else:
        print(f"No licence: {licence.reason}")

    ui.run(
        host=host,
        port=port,
        title="DataFlow",
        favicon=FAVICON if FAVICON.is_file() else "⇄",
        reload=reload_enabled,
        show=show,
        uvicorn_logging_level="info",
        dark=False,
        storage_secret=os.getenv("DATAREADY_STORAGE_SECRET", "dataready-local-session"),
    )


def main() -> None:
    """Start the server, honouring the environment the deployment provides."""
    run_server()


if __name__ in {"__main__", "__mp_main__"}:
    main()