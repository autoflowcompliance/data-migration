"""Multiple branding profiles: one install, many brands.

The single-brand path in :mod:`app_files.branding.settings` is unchanged: a
``branding.json`` in the config home, merged over defaults. This module adds a
named set of profiles beside it, so an agency can hold a brand per client and
pick one per run.

Two rules keep it from surprising anyone:

* **The default profile is the existing single-brand settings.** An install that
  never creates a profile resolves exactly as it does today, so this is opt-in
  and cannot change an existing output.
* **A profile is selected by name, and an unknown name is an error, not a
  silent fallback.** Falling back to the default would brand a client's report
  with another client's name — a mistake that ships to their customer.

Profiles live at ``$DATAREADY_HOME/branding_profiles.json``; the active name is
chosen per run by the caller, so two runs in one process can carry two brands.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.branding.settings import Branding, branding_path
from app_files.licensing.loader import config_home

PROFILES_FILENAME = "branding_profiles.json"


class BrandProfileError(ValueError):
    """Raised on a missing profile, or a profile that does not read as branding."""


def profiles_path() -> Path:
    return config_home() / PROFILES_FILENAME


def load_profiles(path: str | Path | None = None) -> dict[str, Branding]:
    """Every saved profile, keyed by name. Empty when none are saved."""
    target = Path(path) if path else profiles_path()
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    profiles: dict[str, Branding] = {}
    for name, payload in data.items():
        if isinstance(payload, dict):
            profiles[str(name)] = Branding.from_dict(payload)
        elif isinstance(payload, str):
            # A profile may be a path to a branding.json file.
            profiles[str(name)] = load_branding_file(Path(payload))
    return profiles


def load_branding_file(path: Path) -> Branding:
    try:
        return Branding.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return Branding()


def save_profile(name: str, branding: Branding, path: str | Path | None = None) -> Path:
    target = Path(path) if path else profiles_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    current = {}
    if target.exists():
        try:
            current = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            current = {}
    if not isinstance(current, dict):
        current = {}
    current[str(name)] = branding.as_dict()
    target.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def delete_profile(name: str, path: str | Path | None = None) -> bool:
    target = Path(path) if path else profiles_path()
    if not target.exists():
        return False
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(current, dict) or name not in current:
        return False
    del current[name]
    target.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return True


def resolve_profile(
    name: str | None = None,
    *,
    path: str | Path | None = None,
    profiles: dict[str, Branding] | None = None,
) -> Branding:
    """The branding for a run.

    ``None`` or ``"default"`` is the install's single-brand settings — the
    existing behaviour, unchanged. Any other name must exist, because falling
    back would put one client's brand on another client's report.
    """
    if name in (None, "", "default", "Default"):
        if branding_path().exists():
            try:
                return Branding.from_dict(
                    json.loads(branding_path().read_text(encoding="utf-8"))
                )
            except (OSError, json.JSONDecodeError):
                return Branding()
        return Branding()

    available = profiles if profiles is not None else load_profiles(path)
    if name not in available:
        known = ", ".join(sorted(available)) or "none"
        raise BrandProfileError(
            f"No brand profile named {name!r}. Available: {known}."
        )
    return available[name]


def profile_names(path: str | Path | None = None) -> list[str]:
    return sorted(load_profiles(path))


__all__ = [
    "PROFILES_FILENAME",
    "BrandProfileError",
    "delete_profile",
    "load_profiles",
    "profile_names",
    "profiles_path",
    "resolve_profile",
    "save_profile",
]
