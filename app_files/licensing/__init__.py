"""Licensing layer: offline license verification and demo-mode limits.

Additive layer — it reads a signed JSON file from the user's config directory
and exposes a :class:`Limits` object. It never modifies the pipeline; the
interface asks this layer what it is allowed to do and passes the answer down.
"""

from app_files.licensing.limits import (
    DEMO_BATCH_MAX_FILES,
    DEMO_LIMITS,
    DEMO_RUNS_PER_SESSION,
    FULL_LIMITS,
    LimitExceededError,
    Limits,
    RowLimitResult,
    apply_limits,
    apply_row_limit,
    check_file_size,
    resolve_limits,
)
from app_files.licensing.loader import (
    License,
    config_home,
    license_path,
    load_license,
    verify_license,
    write_license,
)
from app_files.licensing.signing import SECRET_KEY, secret_key, sign, signature_matches

__all__ = [
    "DEMO_BATCH_MAX_FILES",
    "DEMO_LIMITS",
    "DEMO_RUNS_PER_SESSION",
    "FULL_LIMITS",
    "SECRET_KEY",
    "License",
    "LimitExceededError",
    "Limits",
    "RowLimitResult",
    "apply_limits",
    "apply_row_limit",
    "check_file_size",
    "config_home",
    "license_path",
    "load_license",
    "resolve_limits",
    "secret_key",
    "sign",
    "signature_matches",
    "verify_license",
    "write_license",
]


def current_mode() -> tuple[License, Limits]:
    """Read the license from disk and resolve the matching :class:`Limits`.

    A single call site keeps the UI from re-deriving "am I licensed?" in a
    dozen slightly different ways.
    """
    license_result = load_license()
    return license_result, resolve_limits(license_result.valid)