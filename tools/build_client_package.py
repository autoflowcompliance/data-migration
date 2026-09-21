"""Build the zip a buyer downloads.

Usage:
    python tools/build_client_package.py
    python tools/build_client_package.py --out dist --name DataReady-1.0

Copies the application, templates, samples and docs into a clean folder, writes
the per-platform launchers and a client config, and zips the result.

The portable Python runtime is intentionally not downloaded here. Bundling a
150 MB interpreter makes this script depend on three vendor URLs staying
available and on the build machine's network, which is a poor trade inside a
repository whose test suite must run offline. Pass ``--runtime`` to include a
runtime you have already unpacked; without it the launchers fall back to the
``python`` on the buyer's PATH and say so in the README.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INCLUDE = ["app_files", "configs", "site", "tools"]
"""``app_files`` already carries templates/, samples/ and docs/ inside it.
The top-level ``configs/`` holds demo.yaml and client.yaml, which the interface
reads to describe the active mode."""
INCLUDE_FILES = ["requirements.txt", "main.py", "LICENSE.md"]

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".git"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}

START_SH = """#!/usr/bin/env bash
# DataReady launcher (Linux/macOS)
cd "$(dirname "$0")"
PYTHON=python3
if [ -x "runtime/python/bin/python3" ]; then
  PYTHON="runtime/python/bin/python3"
fi
exec "$PYTHON" main.py
"""

START_COMMAND = """#!/usr/bin/env bash
# DataReady launcher (macOS, double-clickable)
cd "$(dirname "$0")"
PYTHON=python3
if [ -x "runtime/python/bin/python3" ]; then
  PYTHON="runtime/python/bin/python3"
fi
exec "$PYTHON" main.py
"""

START_BAT = """@echo off
REM DataReady launcher (Windows)
cd /d "%~dp0"
set PYTHON=python
if exist "runtime\\python\\python.exe" set PYTHON=runtime\\python\\python.exe
"%PYTHON%" main.py
pause
"""

CLIENT_README = """# DataReady

## Start the app

- Windows: double-click `start.bat`
- macOS:   double-click `start.command`
- Linux:   run `./start.sh`

Your browser opens at http://localhost:8080. Nothing leaves this computer.

## Activate your licence

1. Open the app and go to **Settings**.
2. Paste the licence JSON from your purchase email into **Activate a licence**.
3. Click **Activate**. The banner changes from Demo mode to your email address.

## Check the install

Run `python tools/verify_install.py` (or open the **Verify** page in the app).
Every line should say PASS.

## Batch processing

Open the **Batch** page, choose an input folder, a target config and an output
folder, then click **Run batch**. Each file gets its own output folder, and a
combined `summary.csv` and `dashboard.html` are written at the top level.

## Without a licence

The app runs in demo mode: three runs per browser session, with a watermarked QA
report. Lineage, batch processing, branding and every output format work, so you
can judge the real tool. Paste a licence in **Settings** to lift the run limit
and remove the watermark.
"""


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    return path.suffix in EXCLUDE_SUFFIXES


def copy_tree(source: Path, destination: Path) -> None:
    """Copy a tree, skipping caches and compiled files."""
    for item in source.rglob("*"):
        if should_skip(item.relative_to(source)):
            continue
        target = destination / item.relative_to(source)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def build(out_dir: Path, name: str, runtime: Path | None = None) -> Path:
    """Assemble the package folder and return the path to the zip."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    staging = out_dir / name
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    for folder in INCLUDE:
        source = ROOT / folder
        if source.is_dir():
            copy_tree(source, staging / folder)
    for filename in INCLUDE_FILES:
        source = ROOT / filename
        if source.is_file():
            shutil.copy2(source, staging / filename)

    # Launchers.
    for filename, content in (
        ("start.sh", START_SH),
        ("start.command", START_COMMAND),
        ("start.bat", START_BAT),
    ):
        path = staging / filename
        path.write_text(content, encoding="utf-8", newline="\n")
        path.chmod(0o755)

    (staging / "README.md").write_text(CLIENT_README, encoding="utf-8")

    if runtime is not None:
        destination = staging / "runtime" / "python"
        copy_tree(Path(runtime), destination)
    else:
        (staging / "runtime").mkdir(exist_ok=True)
        (staging / "runtime" / "README.md").write_text(
            "Place a portable Python here as runtime/python/ to make this package "
            "self-contained. Without it, start scripts use the system Python.\n",
            encoding="utf-8",
        )

    zip_path = out_dir / f"{name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(staging.rglob("*")):
            if item.is_file():
                archive.write(item, item.relative_to(out_dir))
    return zip_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the client zip.")
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    parser.add_argument("--name", default="DataReady-1.0")
    parser.add_argument("--runtime", type=Path, default=None,
                        help="path to an unpacked portable Python to bundle")
    parser.add_argument("--no-zip", action="store_true", help="leave the folder, skip the zip")
    args = parser.parse_args(argv)

    zip_path = build(args.out, args.name, args.runtime)
    if args.no_zip:
        zip_path.unlink(missing_ok=True)
        print(f"Built {args.out / args.name}")
        return 0
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Built {zip_path} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())