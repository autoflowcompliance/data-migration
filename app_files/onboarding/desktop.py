"""Desktop launcher: start the tool without a terminal.

This is the module the packaged executable runs. It finds a free port, starts
the NiceGUI server in a subprocess, waits until the page answers, opens the
browser, and keeps running until the user closes it (or Ctrl-C).

It is a launcher, not a rewrite: the server it starts is exactly the one
``python main.py`` starts from the command line. That is what keeps the desktop
build honest — there is no second code path to drift, and a change to the web
UI reaches the packaged client without touching this file.

Everything here is importable and testable without packaging: the wait-for-page
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

# The launcher starts the same entry point a developer runs, so the desktop
# build and the hosted demo cannot disagree about which UI they are serving.
APP_ENTRY = Path("main.py")
DEFAULT_PORT = 8080
DEFAULT_HOST = "127.0.0.1"

# Marker the packaged app passes to itself to mean "become the web server".
# A frozen build has no ``python`` on disk to run main.py with, so it
# re-invokes its own executable and hands off to the server in the child.
UI_INTERNAL_FLAG = "--ui-run"


def project_root() -> Path:
    """The folder holding ``main.py`` and ``app_files/``.

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


def server_env(port: int, root: Path, base: dict[str, str] | None = None) -> dict[str, str]:
    """The environment the child server needs to bind the chosen port.

    ``DATAREADY_PORT`` (not ``PORT``) because the launcher wants a setting a
    developer's own ``PORT`` cannot silently override; ``resolve_port`` gives
    ``PORT`` precedence, which is right for a PaaS and wrong for a desktop app
    picking its own free port.

    ``DATAREADY_SHOW=0`` suppresses NiceGUI's own browser launch — this module
    opens the browser itself, once the page actually answers, so the user never
    stares at a connection error during startup.
    """
    env = dict(os.environ if base is None else base)
    env["DATAREADY_PORT"] = str(port)
    env["DATAREADY_HOST"] = DEFAULT_HOST
    env["DATAREADY_SHOW"] = "0"
    env["DATAREADY_RELOAD"] = "0"
    env.setdefault("PYTHONPATH", str(root))
    return env


def build_command(port: int, root: Path | None = None) -> list[str]:
    """The exact command that starts the web UI.

    From source this is ``python main.py``. When frozen, ``sys.executable`` is
    the application itself, so the launcher re-invokes it with an internal
    marker and hands off to the server in the child process (see
    :func:`run_server`). Without this, the child would re-enter this launcher
    and argparse would reject the launcher's own arguments.
    """
    root = root or project_root()
    if is_frozen():
        return [sys.executable, UI_INTERNAL_FLAG]
    return [sys.executable, str(app_path(root))]


def run_server(host: str, port: int) -> int:
    """Run the NiceGUI server in-process.

    Called from ``main.py`` for a normal launch and from the re-invoked child of
    a frozen build, so there is one server implementation rather than two.
    """
    try:
        from app_files.interface.web.main import run_server as serve
    except ImportError as exc:  # pragma: no cover - only when the bundle is broken
        raise RuntimeError(
            "The web interface is missing from this build, so the tool cannot start."
        ) from exc

    serve(host=host, port=port)
    return 0


def health_url(port: int, host: str = DEFAULT_HOST) -> str:
    return f"http://{host}:{port}/"


def wait_for_health(
    port: int,
    timeout: float = 60.0,
    interval: float = 0.5,
    host: str = DEFAULT_HOST,
) -> bool:
    """Block until the server returns the page, or ``timeout`` passes.

    NiceGUI exposes no dedicated health endpoint, so the readiness signal is a
    200 on the root page — which is exactly the request the browser is about to
    make, so "ready" means the first paint will succeed rather than merely that
    a socket is listening.
    """
    deadline = time.monotonic() + timeout
    url = health_url(port, host)
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
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
    env = server_env(chosen, root)

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
    if UI_INTERNAL_FLAG in raw:
        return run_server(DEFAULT_HOST, int(os.environ.get("DATAREADY_PORT", DEFAULT_PORT)))

    parser = argparse.ArgumentParser(description="Start the DataReady data migration tool.")
    parser.add_argument("--port", type=int, default=None, help="preferred port (default: first free from 8080)")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    parser.add_argument("--timeout", type=float, default=60.0, help="seconds to wait for startup")
    args = parser.parse_args(argv)

    print("Starting DataReady…")
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
