"""Structural validation of the output CSV via Frictionless."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from frictionless import validate


def frictionless_summary(csv_path: str | Path) -> dict[str, Any]:
    """Return a compact structural report (blank rows, ragged rows, encoding)."""
    report = validate(str(csv_path))
    return {
        "valid": report.valid,
        "errors": [
            {"type": error.type, "message": error.message}
            for task in report.tasks
            for error in task.errors
        ],
    }
