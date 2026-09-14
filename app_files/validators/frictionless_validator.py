"""Structural validation of the output CSV via Frictionless."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from frictionless import system, validate


def frictionless_summary(csv_path: str | Path) -> dict[str, Any]:
    """Return a compact structural report (blank rows, ragged rows, encoding).

    Uses system.use_context(trusted=True) because this function is only ever
    called on a file WE just wrote ourselves to a temp directory (see
    pipeline.py) — Frictionless flags absolute/temp paths as "not safe" by
    default as a security measure against validating arbitrary user-supplied
    paths, which doesn't apply here since we generated the file internally.
    use_context() scopes the trust to just this call and restores the
    previous setting afterward, rather than weakening it globally.
    """
    with system.use_context(trusted=True):
        report = validate(str(csv_path))
    return {
        "valid": report.valid,
        "errors": [
            {"type": error.type, "message": error.message}
            for task in report.tasks
            for error in task.errors
        ],
    }
