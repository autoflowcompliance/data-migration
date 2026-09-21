"""Read and verify the offline license file.

A license lives at ``$DATAREADY_HOME/license.json`` (``~/.dataready`` by
default) and is a small JSON document signed with HMAC-SHA256. Verification is
purely local: no network call, no phone-home, which is what lets the tool run
on a machine with no internet connection at all.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app_files.licensing.signing import signature_matches

LICENSE_FILENAME = "license.json"


def config_home() -> Path:
    """The DataFlow config directory, overridable for tests and portable installs."""
    override = os.getenv("DATAREADY_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".dataready"


def license_path() -> Path:
    return config_home() / LICENSE_FILENAME


@dataclass
class License:
    """A verified license, or the absence of one."""

    valid: bool
    email: str | None = None
    issued: str | None = None
    version: str | None = None
    reason: str | None = None
    """Why the license was rejected, for the settings page. ``None`` when valid."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "email": self.email,
            "issued": self.issued,
            "version": self.version,
            "reason": self.reason,
        }


def verify_license(data: dict[str, Any] | None) -> License:
    """Check the signature on an already-parsed license document."""
    if not isinstance(data, dict):
        return License(valid=False, reason="License file is not a JSON object.")
    for key in ("email", "issued", "signature"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            return License(valid=False, reason=f"License is missing a valid '{key}'.")
    if not signature_matches(data["email"], data["issued"], data["signature"]):
        return License(valid=False, reason="License signature does not match this machine's key.")
    return License(
        valid=True,
        email=data["email"],
        issued=data["issued"],
        version=str(data.get("version", "1.0")),
    )


def load_license(path: str | Path | None = None) -> License:
    """Load and verify the license at ``path`` (default: the standard location).

    Never raises: a missing, unreadable or malformed file simply yields an
    invalid :class:`License`, which the caller turns into demo mode.
    """
    target = Path(path) if path else license_path()
    if not target.exists():
        return License(valid=False, reason="No license file found — running in demo mode.")
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return License(valid=False, reason=f"License file could not be read: {exc}")
    return verify_license(data)


def write_license(data: dict[str, Any], path: str | Path | None = None) -> Path:
    """Persist a license document, creating the config directory if needed."""
    target = Path(path) if path else license_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return target