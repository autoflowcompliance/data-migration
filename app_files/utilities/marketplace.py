"""Template marketplace: browse, inspect and install template packs.

Onboarding templates ship with the tool. The marketplace adds the part that
makes the library extensible: installing a pack from a folder or a zip that
someone else produced, listing what is installed with a price/provenance badge,
and removing one.

It reuses the loader in ``app_files.onboarding.templates`` for discovery and
execution, so a pack behaves identically whether it shipped with the tool or was
installed afterwards. Nothing here writes to the frozen core; an installed pack
lands in ``app_files/template_library/``, which is where the loader already
looks.

Installing from a zip refuses paths that would escape the target directory
(``../`` or an absolute entry), because a template pack is untrusted input.
"""

from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from app_files.onboarding.templates import (
    LIBRARY_DIR,
    Template,
    all_templates,
    available_templates,
    load_template,
)


class InstallError(ValueError):
    """Raised when a pack cannot be installed safely."""


@dataclass
class CatalogEntry:
    """A template pack as the marketplace shows it."""

    name: str
    title: str
    description: str = ""
    free: bool = True
    price: float = 0.0
    installed: bool = True
    missing_files: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "price": "Free" if self.free else f"${self.price:.0f}",
            "installed": self.installed,
            "missing_files": self.missing_files,
            "description": self.description,
        }


# Packs that ship with the tool are free. A price attached here is what a
# marketplace listing would charge; installing is local either way.
_PRICES: dict[str, float] = {
    "bank_reconciliation": 0.0,
    "hubspot_contact_cleanup": 0.0,
    "salesforce_lead_cleanup": 49.0,
    "invoice_data_extraction": 49.0,
    "ecommerce_product_cleanup": 49.0,
    "google_sheets_contact_cleanup": 0.0,
    "ai_readiness_audit": 0.0,
}


def _first_paragraph(text: str) -> str:
    """The first non-heading, non-empty chunk of a README, for the catalogue."""
    import re

    for block in text.split("\n\n"):
        cleaned = " ".join(block.strip().split())
        if not cleaned or cleaned.startswith("#"):
            continue
        # READMEs are written for people; the catalogue shows one clean line.
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"[*_`]", "", cleaned)
        return cleaned
    return ""


def catalog() -> list[CatalogEntry]:
    """Everything installed, described well enough to display."""
    entries = []
    for template in all_templates():
        price = _PRICES.get(template.name, 0.0)
        entries.append(
            CatalogEntry(
                name=template.name,
                title=template.title,
                description=_first_paragraph(template.readme()),
                free=price == 0.0,
                price=price,
                installed=True,
                missing_files=template.missing_files(),
            )
        )
    return entries


def catalog_frame():
    import pandas as pd

    rows = [entry.as_dict() for entry in catalog()]
    columns = ["name", "title", "price", "installed", "description", "missing_files"]
    return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)


def install_from_folder(source: str | Path, name: str | None = None, overwrite: bool = False) -> Template:
    """Install a template pack from a directory."""
    source = Path(source)
    if not source.is_dir():
        raise InstallError(f"{source} is not a folder.")
    if not (source / "config.yaml").exists():
        raise InstallError(
            f"{source} has no config.yaml, so it is not a template pack."
        )
    target_name = name or source.name
    target = LIBRARY_DIR / target_name
    if target.exists() and not overwrite:
        raise InstallError(
            f"A template named {target_name!r} is already installed. "
            "Pass overwrite=True to replace it."
        )
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return load_template(target_name)


def _safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    """Extract, refusing entries that would land outside ``destination``.

    A zip entry named ``../../etc/passwd`` is a real attack, not a hypothetical
    one, so every member is resolved and checked before anything is written.
    """
    destination = destination.resolve()
    for member in archive.namelist():
        if member.endswith("/"):
            continue
        resolved = (destination / member).resolve()
        if resolved != destination and destination not in resolved.parents:
            raise InstallError(
                f"The archive contains an unsafe path ({member!r}); refusing to install it."
            )
    archive.extractall(destination)


def install_from_zip(source: str | Path, name: str | None = None, overwrite: bool = False) -> Template:
    """Install a template pack from a zip archive.

    The archive may either contain the pack at its root, or wrap it in a single
    top-level folder — both are common when someone zips a directory.
    """
    source = Path(source)
    if not source.is_file():
        raise InstallError(f"{source} is not a file.")
    import tempfile

    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        try:
            with zipfile.ZipFile(source) as archive:
                _safe_extract(archive, staging)
        except zipfile.BadZipFile as exc:
            raise InstallError(f"{source} is not a readable zip archive.") from exc

        root = _find_pack_root(staging)
        if root is None:
            raise InstallError(
                "The archive contains no config.yaml, so it is not a template pack."
            )
        return install_from_folder(root, name=name or root.name, overwrite=overwrite)


def _find_pack_root(staging: Path) -> Path | None:
    if (staging / "config.yaml").exists():
        return staging
    candidates = [
        folder for folder in staging.iterdir()
        if folder.is_dir() and (folder / "config.yaml").exists()
    ]
    return candidates[0] if len(candidates) == 1 else None


def uninstall(name: str) -> bool:
    """Remove an installed pack. Returns True when something was removed."""
    target = LIBRARY_DIR / name
    if not target.exists():
        return False
    shutil.rmtree(target)
    return True


def installed_names() -> list[str]:
    return available_templates()


def marketplace_summary() -> dict:
    entries = catalog()
    return {
        "installed": len(entries),
        "free": sum(1 for e in entries if e.free),
        "paid": sum(1 for e in entries if not e.free),
        "incomplete": [e.name for e in entries if e.missing_files],
        "directory": str(LIBRARY_DIR),
    }