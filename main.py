"""Launch the DataFlow web UI. ``python main.py`` from the repo root.

One interface ships in this checkout:

* **DataFlow** — the NiceGUI web app under ``app_files/interface/web``.

The port comes from ``PORT`` (what a PaaS injects) then ``DATAREADY_PORT``,
then the default; see :func:`app_files.settings.resolve_port`.

Every launch path — this file, the container, and the packaged desktop
launcher — ends at :func:`app_files.interface.web.main.run_server`, so there is
one server implementation rather than one per entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_files.settings import resolve_host, resolve_port  # noqa: E402


def run_nicegui(host: str, port: int) -> None:
    """Start the DataFlow web UI."""
    from app_files.interface.web.main import run_server

    run_server(host=host, port=port)


def main() -> None:
    host = resolve_host()
    port = resolve_port()

    print(f"Starting the DataFlow interface on http://{host}:{port}")
    run_nicegui(host, port)


if __name__ in {"__main__", "__mp_main__"}:
    main()
