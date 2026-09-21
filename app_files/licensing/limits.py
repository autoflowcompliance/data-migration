"""Demo-mode limits, and the one place that decides which features are on.

The demo is a sales tool, so it does **not** hide features. An earlier revision
capped rows at 500, files at 5 MB, output to CSV and switched off lineage,
batch and branding — which meant a prospect evaluating the product saw a
crippled tool rather than the one being sold. What the demo limits instead is
*volume of use*: :data:`DEMO_RUNS_PER_SESSION` runs per browser session.

Everything else is identical to the licensed build. The one genuine difference
is the report watermark, which marks an unlicensed output rather than removing
a capability.

A licensed install resolves to :data:`FULL_LIMITS`. Nothing else in the
codebase should hard-code "if demo" checks — call :func:`resolve_limits` and
read the resulting :class:`Limits`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

DEMO_RUNS_PER_SESSION = 3
"""Runs an unlicensed visitor may start before the demo asks them to buy."""

DEMO_BATCH_MAX_FILES: int | None = None
"""No cap on a demo batch.

An earlier revision stopped a demo folder run after three files, which meant a
prospect with a twenty-client inbox could not judge the feature on their own
data — the moment they would otherwise decide to buy. The per-session run
allowance already bounds demo use, so the folder job is left whole.
"""

DEMO_LIMITS: dict[str, Any] = {
    "max_rows": None,
    "max_file_size_mb": None,
    "output_formats": ["csv", "excel", "json", "sql"],
    "watermark": True,
    "lineage": True,
    "batch": True,
    "batch_max_files": DEMO_BATCH_MAX_FILES,
    "branding": True,
    "max_runs_per_session": DEMO_RUNS_PER_SESSION,
}

FULL_LIMITS: dict[str, Any] = {
    "max_rows": None,
    "max_file_size_mb": None,
    "output_formats": ["csv", "excel", "json", "sql"],
    "watermark": False,
    "lineage": True,
    "batch": True,
    "batch_max_files": None,
    "branding": True,
    "max_runs_per_session": None,
}


class LimitExceededError(ValueError):
    """Raised when an upload is larger than the active mode allows."""


@dataclass(frozen=True)
class Limits:
    """The resolved feature set for the current run."""

    demo: bool
    max_rows: int | None
    max_file_size_mb: float | None
    output_formats: tuple[str, ...]
    watermark: bool
    lineage: bool
    batch: bool
    branding: bool
    batch_max_files: int | None = None
    max_runs_per_session: int | None = None

    def allows_format(self, output_format: str) -> bool:
        return str(output_format).strip().lower() in self.output_formats

    def as_dict(self) -> dict[str, Any]:
        return {
            "demo": self.demo,
            "max_rows": self.max_rows,
            "max_file_size_mb": self.max_file_size_mb,
            "output_formats": list(self.output_formats),
            "watermark": self.watermark,
            "lineage": self.lineage,
            "batch": self.batch,
            "batch_max_files": self.batch_max_files,
            "branding": self.branding,
            "max_runs_per_session": self.max_runs_per_session,
        }


def _to_limits(raw: dict[str, Any], demo: bool) -> Limits:
    return Limits(
        demo=demo,
        max_rows=raw["max_rows"],
        max_file_size_mb=raw["max_file_size_mb"],
        output_formats=tuple(raw["output_formats"]),
        watermark=raw["watermark"],
        lineage=raw["lineage"],
        batch=raw["batch"],
        branding=raw["branding"],
        # Read with a default so a config written before these keys existed
        # still resolves rather than raising a KeyError.
        batch_max_files=raw.get("batch_max_files"),
        max_runs_per_session=raw.get("max_runs_per_session"),
    )


def resolve_limits(license_valid: bool) -> Limits:
    """Full features when licensed, demo restrictions otherwise."""
    return _to_limits(FULL_LIMITS if license_valid else DEMO_LIMITS, demo=not license_valid)


def apply_limits(config: dict[str, Any], license_valid: bool) -> dict[str, Any]:
    """Overlay the demo restrictions onto a config dict.

    Licensed installs get ``config`` back untouched, so this is safe to call
    on every config load.
    """
    if license_valid:
        return config
    return {**config, **DEMO_LIMITS}


def check_file_size(size_bytes: int, limits: Limits) -> None:
    """Raise :class:`LimitExceededError` when an upload is too large for this mode."""
    if limits.max_file_size_mb is None:
        return
    limit = limits.max_file_size_mb * 1024 * 1024
    if size_bytes > limit:
        actual = size_bytes / (1024 * 1024)
        raise LimitExceededError(
            f"This file is {actual:.1f} MB. The demo accepts files up to "
            f"{limits.max_file_size_mb:g} MB."
        )


@dataclass
class RowLimitResult:
    """The frame to process, plus a note when rows were dropped."""

    frame: pd.DataFrame
    original_rows: int
    processed_rows: int

    @property
    def truncated(self) -> bool:
        return self.processed_rows < self.original_rows

    @property
    def note(self) -> str:
        if not self.truncated:
            return ""
        return (
            f"Demo mode processed the first {self.processed_rows:,} of "
            f"{self.original_rows:,} rows."
        )


def apply_row_limit(frame: pd.DataFrame, limits: Limits) -> RowLimitResult:
    """Trim ``frame`` to the mode's row allowance.

    No current mode sets a row cap, so this is a no-op in practice; it stays
    because it is the single place a cap would be enforced, and because
    licensed readers of ``Limits`` can still set one.
    """
    original = len(frame)
    if limits.max_rows is None or original <= limits.max_rows:
        return RowLimitResult(frame, original, original)
    return RowLimitResult(frame.head(limits.max_rows).copy(), original, limits.max_rows)
