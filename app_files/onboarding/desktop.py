"""Desktop launcher: start the tool without a terminal.

This is the module the packaged executable runs. It finds a free port, starts
the Streamlit server in a subprocess, waits until the health endpoint answers,
opens the browser, and keeps running until the user closes it (or Ctrl-C).

It is a launcher, not a rewrite: the app it starts is exactly the same
``app_files/interface/web/app.py`` a developer runs from the command line. That
is what keeps the desktop build honest — there is no second code path to drift.

Everything here is importable and testable without packaging: the wait-for-health
loop, the free-port search and the command construction are plain functions.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

APP_ENTRY = Path("app_files") / "interface" / "web" / "app.py"
DEFAULT_PORT = 8501
DEFAULT_HOST = "127.0.0.1"

# Marker the packaged app passes to itself to mean "become the Streamlit server".
STREAMLIT_INTERNAL_FLAG = "--streamlit-run"


def project_root() -> Path:
    """The folder holding ``app_files/``.

    Three cases:

    * frozen by PyInstaller — the bundled data lives in ``sys._MEIPASS`` (the
      ``--add-data`` destination root), not next to the executable. Getting this
      wrong is the classic packaged-app bug: the exe starts, then reports the
      app folder missing.
    * running ``run_desktop.py`` as a script — ``__file__`` is one level up.
    * running from source — walk up to the repository root.
    """
    if getattr(sys, "frozen", False):
        bundle = getattr(sys, "_MEIPASS", None)
        if bundle and (Path(bundle) / APP_ENTRY).exists():
            return Path(bundle)
        next_to_exe = Path(sys.executable).resolve().parent
        if (next_to_exe / APP_ENTRY).exists():
            return next_to_exe
        return Path(bundle) if bundle else next_to_exe
    return Path(__file__).resolve().parents[2]


def app_path(root: Path | None = None) -> Path:
    return (root or project_root()) / APP_ENTRY


def find_free_port(start: int = DEFAULT_PORT, attempts: int = 20) -> int:
    """First free port at or after ``start``.

    A buyer double-clicking an icon should never see "address already in use",
    so we scan rather than fail.
    """
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((DEFAULT_HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError(
        f"No free port found in {start}-{start + attempts - 1}. Close other apps and try again."
    )


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def build_command(port: int, root: Path | None = None) -> list[str]:
    """The exact command that starts the web UI.

    From source this is ``python -m streamlit`` rather than the ``streamlit``
    console script, because the script is not always on ``PATH``.

    When frozen, ``sys.executable`` is the application itself, so the launcher
    re-invokes itself with an internal marker and hands off to Streamlit in the
    child process (see :func:`run_streamlit`). Without this, the child would
    re-enter this launcher and argparse would reject Streamlit's arguments.
    """
    streamlit_args = [
        "run",
        str(app_path(root)),
        "--server.port",
        str(port),
        "--server.address",
        DEFAULT_HOST,
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    if is_frozen():
        return [sys.executable, STREAMLIT_INTERNAL_FLAG, *streamlit_args]
    return [sys.executable, "-m", "streamlit", *streamlit_args]


def run_streamlit(argv: list[str]) -> int:
    """Run Streamlit's CLI in-process, as ``python -m streamlit`` would.

    Called only in the re-invoked child of a frozen build.
    """
    try:
        from streamlit.web import cli as streamlit_cli
    except ImportError as exc:  # pragma: no cover - only when the bundle is broken
        raise RuntimeError(
            "Streamlit is missing from this build, so the tool cannot start."
        ) from exc

    sys.argv = ["streamlit", *argv]
    try:
        streamlit_cli.main()
    except SystemExit as exc:  # the CLI exits with a code of its own
        return int(exc.code or 0)
    return 0


def health_url(port: int, host: str = DEFAULT_HOST) -> str:
    return f"http://{host}:{port}/_stcore/health"


def wait_for_health(
    port: int,
    timeout: float = 60.0,
    interval: float = 0.5,
    host: str = DEFAULT_HOST,
) -> bool:
    """Block until the server answers its health check, or ``timeout`` passes."""
    deadline = time.monotonic() + timeout
    url = health_url(port, host)
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                body = response.read().decode("utf-8", errors="replace").strip()
                if response.status == 200 and body == "ok":
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(interval)
    return False


def launch(
    port: int | None = None,
    open_browser: bool = True,
    wait: bool = True,
    timeout: float = 60.0,
) -> dict[str, object]:
    """Start the app and return a description of what happened.

    Returns a dict rather than printing, so both the packaged launcher and the
    tests can assert on the outcome.
    """
    root = project_root()
    entry = app_path(root)
    if not entry.exists():
        raise FileNotFoundError(
            f"Could not find the application at {entry}. "
            "Re-download the tool; the app_files folder is missing."
        )

    chosen = port or find_free_port()
    command = build_command(chosen, root)
    env = dict(os.environ)
    env.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    env.setdefault("PYTHONPATH", str(root))
    # Streamlit treats a frozen bundle as a development install (there is no
    # __init__.py beside the script) and then refuses --server.port. A packaged
    # app is a production install, so say so.
    env.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")

    process = subprocess.Popen(command, cwd=str(root), env=env)

    ready = False
    if wait:
        ready = wait_for_health(chosen, timeout=timeout)
        if ready and open_browser:
            webbrowser.open(f"http://{DEFAULT_HOST}:{chosen}")

    return {
        "port": chosen,
        "url": f"http://{DEFAULT_HOST}:{chosen}",
        "pid": process.pid,
        "command": command,
        "ready": ready,
        "process": process,
    }


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - launcher shim
    raw = list(sys.argv[1:] if argv is None else argv)
    if STREAMLIT_INTERNAL_FLAG in raw:
        return run_streamlit(raw[raw.index(STREAMLIT_INTERNAL_FLAG) + 1:])

    parser = argparse.ArgumentParser(description="Start the AutoFlow data migration tool.")
    parser.add_argument("--port", type=int, default=None, help="preferred port (default: first free from 8501)")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    parser.add_argument("--timeout", type=float, default=60.0, help="seconds to wait for startup")
    args = parser.parse_args(argv)

    print("Starting AutoFlow…")
    try:
        result = launch(port=args.port, open_browser=not args.no_browser, timeout=args.timeout)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Could not start the tool: {exc}")
        return 2

    if result["ready"]:
        print(f"Ready. Opening {result['url']} — press Ctrl-C here to stop.")
    else:
        print(
            f"The server did not answer within {args.timeout:.0f}s.\n"
            f"It may still be starting. Try {result['url']} in your browser,\n"
            f"or run the install check: python -m app_files.onboarding.verifier"
        )

    process = result["process"]
    try:
        process.wait()
    except KeyboardInterrupt:  # pragma: no cover - interactive only
        print("\nStopping…")
        process.terminate()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())