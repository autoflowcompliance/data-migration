"""Multiple brand profiles, custom domain, and a client portal.

An agency running this for several clients needs more than one branding file:
each client gets their own name, colour, and logo, and the deliverable must be
skinned with the right one. This keeps a *set* of profiles, names one as
active default, and can re-skin a report for a specific profile on demand.

The portal is the client-facing view: a page listing the files a client was
delivered, with their branding, hosted at their own domain. It is rendered
offline — a static HTML page an agency can upload — so no server or DNS
configuration is needed to hand a client their results.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from app_files.branding.injector import inject_branding
from app_files.branding.settings import Branding, branding_path, load_branding
from app_files.licensing.loader import config_home

PROFILES_FILENAME = "brand_profiles.json"


class ProfileError(ValueError):
    """Raised for an unknown or malformed brand profile."""


@dataclass
class BrandProfile:
    slug: str
    branding: Branding
    domain: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "domain": self.domain,
            "branding": self.branding.as_dict(),
        }


@dataclass
class ProfileSet:
    profiles: dict[str, BrandProfile] = field(default_factory=dict)
    active: str = ""

    def add(self, profile: BrandProfile) -> None:
        self.profiles[profile.slug] = profile
        if not self.active:
            self.active = profile.slug

    def get(self, slug: str | None = None) -> BrandProfile:
        target = slug or self.active
        if target not in self.profiles:
            known = ", ".join(sorted(self.profiles)) or "none"
            raise ProfileError(f"Unknown brand profile {target!r}. Known profiles: {known}.")
        return self.profiles[target]

    def as_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "profiles": {slug: p.as_dict() for slug, p in self.profiles.items()},
        }


def profiles_path(path: str | Path | None = None) -> Path:
    if path:
        return Path(path)
    return config_home() / PROFILES_FILENAME


def load_profiles(path: str | Path | None = None) -> ProfileSet:
    """Load the profile set, falling back to the single default branding.

    A bare install has no profile file; rather than error, it presents the
    existing default branding as a single "default" profile so every caller
    has the same shape to work with.
    """
    target = profiles_path(path)
    if not target.exists():
        profiles = ProfileSet()
        profiles.add(BrandProfile(slug="default", branding=load_branding()))
        return profiles

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError(f"Could not read brand profiles at {target}: {error}") from error

    profiles = ProfileSet(active=str(data.get("active", "")))
    for slug, raw in (data.get("profiles") or {}).items():
        profiles.add(
            BrandProfile(
                slug=slug,
                branding=Branding.from_dict(raw.get("branding", raw)),
                domain=str(raw.get("domain", "")),
            )
        )
    if not profiles.profiles:
        profiles.add(BrandProfile(slug="default", branding=load_branding()))
    return profiles


def save_profiles(profile_set: ProfileSet, path: str | Path | None = None) -> Path:
    target = profiles_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(profile_set.as_dict(), indent=2) + "\n", encoding="utf-8")
    return target


def apply_profile_to_report(html: str, profile: BrandProfile) -> str:
    """Re-skin a rendered report with a profile's branding."""
    return inject_branding(html, profile.branding)


# --------------------------------------------------------------- the portal
@dataclass
class PortalEntry:
    filename: str
    label: str
    size_bytes: int = 0
    delivered_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "label": self.label,
            "size_bytes": self.size_bytes,
            "delivered_at": self.delivered_at,
        }


def build_portal(
    profile: BrandProfile,
    entries: list[PortalEntry],
    *,
    title: str = "Your data migration results",
) -> str:
    """A static, branded page listing a client's deliverables.

    Links are relative filenames, so the page works wherever the agency drops
    the folder — their own host, a shared drive, or the client's intranet.
    """
    brand = profile.branding
    accent = brand.accent_color
    rows = "".join(
        "<li style='margin:6px 0;'>"
        f"<a href='{escape(entry.filename)}' style='color:{accent};"
        f"text-decoration:none;font-weight:600;'>{escape(entry.label)}</a>"
        f"<span style='color:#7A6F5F;font-size:12px;'> &middot; "
        f"{escape(entry.filename)}"
        + (f" &middot; {entry.size_bytes} bytes" if entry.size_bytes else "")
        + "</span></li>"
        for entry in entries
    )
    contact = " &middot; ".join(
        part
        for part in (
            escape(brand.contact_email) if brand.contact_email else "",
            escape(brand.website) if brand.website else "",
        )
        if part
    )
    domain_note = (
        f"<p style='color:#7A6F5F;font-size:12px;'>Served for {escape(profile.domain)}</p>"
        if profile.domain
        else ""
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{escape(title)}</title></head>"
        "<body style='font-family:-apple-system,Segoe UI,Roboto,sans-serif;"
        "background:#F5F0E6;color:#2B2420;margin:0;padding:32px;'>"
        "<div style='max-width:720px;margin:0 auto;background:#FDFBF7;"
        "border:1px solid #E4DCC8;border-radius:10px;padding:28px;'>"
        f"<h1 style='font-family:Georgia,serif;color:{accent};margin-top:0;'>"
        f"{escape(brand.company_name)}</h1>"
        f"<h2 style='font-size:16px;'>{escape(title)}</h2>"
        f"{domain_note}"
        f"<ul style='padding-left:18px;'>{rows}</ul>"
        + (f"<p style='color:#7A6F5F;font-size:12px;'>{contact}</p>" if contact else "")
        + "</div></body></html>"
    )


def portal_entries_from_directory(directory: str | Path) -> list[PortalEntry]:
    """Build portal entries from the files in a deliverable directory."""
    base = Path(directory)
    entries = []
    for candidate in sorted(base.iterdir()):
        if not candidate.is_file() or candidate.name.endswith(".sig"):
            continue
        if candidate.name == "manifest.json":
            continue
        entries.append(
            PortalEntry(
                filename=candidate.name,
                label=candidate.stem.replace("_", " ").title(),
                size_bytes=candidate.stat().st_size,
                delivered_at=datetime.fromtimestamp(
                    candidate.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            )
        )
    return entries