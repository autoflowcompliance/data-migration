"""Read and write white-label branding settings.

Branding is stored beside the license at ``$DATAREADY_HOME/branding.json`` so
an agency can hand a client a pre-configured folder. Every key is optional; a
missing or partial file merges over :data:`DEFAULT_BRANDING` rather than
replacing it, so an old file that predates a new key still loads.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

from app_files.licensing.loader import config_home

BRANDING_FILENAME = "branding.json"

HEX_COLOUR_LENGTH = 7


@dataclass
class Branding:
    """Everything the report injector needs to re-skin a deliverable."""

    company_name: str = "DataReady"
    logo_path: str | None = None
    contact_email: str | None = None
    website: str | None = None
    accent_color: str = "#4F46E5"
    show_powered_by: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Branding:
        """Merge ``data`` over the defaults, ignoring unknown keys.

        Unknown keys are ignored rather than fatal: a branding file written by
        a newer build should still load in an older one.
        """
        known = {f.name for f in fields(cls)}
        clean = {k: v for k, v in (data or {}).items() if k in known}
        clean["show_powered_by"] = bool(clean.get("show_powered_by", True))
        if "accent_color" in clean:
            clean["accent_color"] = normalise_colour(clean["accent_color"])
        return cls(**clean)


def normalise_colour(value: Any) -> str:
    """Accept ``#4f46e5``, ``4f46e5`` or a nonsense string; always return a valid hex."""
    text = str(value or "").strip()
    if not text:
        return Branding.accent_color
    if not text.startswith("#"):
        text = f"#{text}"
    if len(text) != HEX_COLOUR_LENGTH:
        return Branding.accent_color
    try:
        int(text[1:], 16)
    except ValueError:
        return Branding.accent_color
    return text.upper()


def branding_path() -> Path:
    return config_home() / BRANDING_FILENAME


def load_branding(path: str | Path | None = None) -> Branding:
    """Load branding, falling back to the defaults when there is no file."""
    target = Path(path) if path else branding_path()
    if not target.exists():
        return Branding()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Branding()
    return Branding.from_dict(data)


def save_branding(branding: Branding | dict[str, Any], path: str | Path | None = None) -> Path:
    """Persist branding settings."""
    target = Path(path) if path else branding_path()
    payload = branding.as_dict() if isinstance(branding, Branding) else Branding.from_dict(branding).as_dict()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target