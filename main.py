"""Launch a UI. ``python main.py`` from the repo root.

Two interfaces ship in this checkout:

* **DataFlow** — the current web UI (Streamlit). The default.
* **DataReady** — the NiceGUI interface, still fully runnable.

Pick one with ``DATAREADY_UI=dataflow`` (default) or ``DATAREADY_UI=nicegui``.
The port comes from ``PORT`` (what a PaaS injects) then ``DATAREADY_PORT``;
see :func:`app_files.settings.resolve_port`.

The framework for the *chosen* interface is imported inside its branch, so a
checkout that installed only one framework still starts its own UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_files.settings import (  # noqa: E402
    DATAFLOW_UI,
    resolve_host,
    resolve_port,
    resolve_ui,
)


def run_dataflow(host: str, port: int) -> None:
    """Start the DataFlow (Streamlit) UI.

    Streamlit owns its own server and blocking loop, so ``host``/``port`` are
    passed as its CLI flags. ``sys.argv`` is rebuilt because Streamlit reads
    its flags from there, not from arguments.

    The theme colours are passed as flags rather than left to
    ``.streamlit/config.toml``: Streamlit resolves that file relative to the
    working directory, and the container does not ship one, so without these
    the widget accents (radios, sliders, upload buttons) would fall back to
    Streamlit's stock palette against DataFlow's amber-and-paper page.
    """
    from streamlit.web import cli as streamlit_cli

    from app_files.licensing import current_mode

    script = Path(__file__).resolve().parent / "app_files" / "dataflow" / "app.py"
    _, limits = current_mode()
    # Streamlit advertises its own upload cap in the dropzone. Left at the
    # default it promises 200 MB and then the page rejects anything over the
    # demo's 5 MB, which reads as a broken app rather than a licence limit.
    max_upload_mb = int(limits.max_file_size_mb) if limits.max_file_size_mb else 200
    sys.argv = [
        "streamlit",
        "run",
        str(script),
        f"--server.port={port}",
        f"--server.address={host}",
        f"--server.maxUploadSize={max_upload_mb}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        # Must match TOKENS in app_files/dataflow/theme.py.
        "--theme.primaryColor=#C97A2E",
        "--theme.backgroundColor=#F5F0E6",
        "--theme.secondaryBackgroundColor=#FDFBF7",
        "--theme.textColor=#2B2420",
    ]
    streamlit_cli.main()


def run_nicegui(host: str, port: int) -> None:
    """Start the NiceGUI interface."""
    from app_files.interface.web.main import run_server

    run_server(host=host, port=port)


def main() -> None:
    host = resolve_host()
    port = resolve_port()
    interface = resolve_ui()

    print(f"Starting the {interface} interface on http://{host}:{port}")
    if interface == DATAFLOW_UI:
        run_dataflow(host, port)
    else:
        run_nicegui(host, port)


if __name__ in {"__main__", "__mp_main__"}:
    main()