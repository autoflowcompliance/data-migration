"""Build the desktop application (one file per platform) with PyInstaller.

Usage::

    python build_desktop.py              # build for the current platform
    python build_desktop.py --check      # report whether a build is possible

The resulting single executable starts the web UI and opens the browser; the
buyer never sees a terminal. It bundles ``app_files`` (configs, samples,
templates) so the app is complete on first launch.

PyInstaller is an *optional* build dependency: it is not needed to run the tool,
only to freeze it. The script says so plainly instead of raising an ImportError
traceback.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAUNCHER = ROOT / "run_desktop.py"
DIST = ROOT / "dist"
BUILD = ROOT / "build"

# Data files the app needs at runtime, as (source, destination-folder) pairs.
# The launcher starts main.py from disk, so it must be bundled alongside the
# package. `interface` holds the NiceGUI routes; the rest are the library
# folders the layers read at runtime.
#
# PyInstaller copies the *contents* of a source directory into the destination,
# so the destination must repeat the leaf folder name. Bundling
# "app_files/interface" into "app_files" would bury web/main.py at
# app_files/web/main.py, and the launcher would report the app folder missing.
DATA_DIRS = [
    ("main.py", "main.py"),
    ("app_files/configs", "app_files/configs"),
    ("app_files/samples", "app_files/samples"),
    ("app_files/template_library", "app_files/template_library"),
    ("app_files/contracts", "app_files/contracts"),
    ("app_files/rule_library", "app_files/rule_library"),
    ("app_files/docs", "app_files/docs"),
    ("app_files/interface", "app_files/interface"),
]

BUNDLED_MODULES = [
    "app_files",
    "app_files.onboarding",
    "app_files.ingestion",
    "app_files.rules",
    "app_files.profiling",
    "app_files.lineage",
    "app_files.output",
    "app_files.services.bank_reconciliation",
]

# Packages whose data files PyInstaller's import analysis does not pick up.
# NiceGUI serves its browser frontend and its Vue components from files reached
# by path at runtime rather than by import, so without --collect-all the server
# starts and then returns 404 for the assets the page needs.
COLLECT_ALL = [
    "nicegui",
]

# Packages that read their own version through importlib.metadata at import
# time. PyInstaller does not copy *.dist-info by default, so without these they
# raise "No package metadata was found for ..." inside the bundle even though
# the module itself imported fine.
COPY_METADATA = [
    "nicegui",
    "pandas",
    "numpy",
    "pyarrow",
]

PLATFORM_FORMAT = {"Windows": "win .exe", "Darwin": ".app bundle / .dmg", "Linux": "AppImage / .deb"}


def pyinstaller_available() -> bool:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        return False
    return True


def describe_target() -> dict[str, str]:
    system = platform.system()
    return {
        "system": system,
        "format": PLATFORM_FORMAT.get(system, "executable"),
        "python": platform.python_version(),
        "arch": platform.machine(),
        "pyinstaller": "available" if pyinstaller_available() else "missing",
    }


def build_command(onefile: bool = True) -> list[str]:
    """The PyInstaller invocation, as a list so it can be printed and asserted."""
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        "AutoFlow",
        "--onefile" if onefile else "--onedir",
    ]
    for module in BUNDLED_MODULES:
        command += ["--hidden-import", module]
    for package in COLLECT_ALL:
        command += ["--collect-all", package]
    for package in COPY_METADATA:
        command += ["--copy-metadata", package]
    for source, destination in DATA_DIRS:
        separator = ";" if platform.system() == "Windows" else ":"
        command += ["--add-data", f"{source}{separator}{destination}"]
    command.append(str(LAUNCHER))
    return command


def build(onefile: bool = True) -> Path | None:
    if not LAUNCHER.exists():
        raise FileNotFoundError(f"Launcher not found: {LAUNCHER}")
    if not pyinstaller_available():
        print(
            "PyInstaller is not installed, so the desktop app cannot be built.\n"
            "It is only needed for packaging, not for running the tool.\n"
            "Install it with:  pip install pyinstaller"
        )
        return None

    command = build_command(onefile)
    print("Building desktop app with:\n  " + " ".join(command) + "\n")
    result = subprocess.run(command, cwd=str(ROOT), check=False)
    if result.returncode != 0:
        print(f"PyInstaller exited with code {result.returncode}.")
        return None

    system = platform.system()
    if system == "Windows":
        artifact = DIST / "AutoFlow.exe"
    elif system == "Darwin":
        artifact = DIST / "AutoFlow.app"
    else:
        artifact = DIST / "AutoFlow"
    return artifact if artifact.exists() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the AutoFlow desktop application.")
    parser.add_argument("--check", action="store_true", help="report platform and build availability, then exit")
    parser.add_argument("--onedir", action="store_true", help="build a folder instead of a single file")
    args = parser.parse_args(argv)

    target = describe_target()
    print("Desktop build target:")
    for key, value in target.items():
        print(f"  {key:12} {value}")
    print(f"  artifact     {PLATFORM_FORMAT.get(target['system'], 'executable')}")
    print()

    if args.check:
        return 0

    artifact = build(onefile=not args.onedir)
    if artifact is None:
        return 1
    size = artifact.stat().st_size if artifact.is_file() else _dir_size(artifact)
    print(f"\nBuilt: {artifact}\nSize:  {size:,} bytes")
    return 0


def _dir_size(path: Path) -> int:
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


if __name__ == "__main__":
    raise SystemExit(main())