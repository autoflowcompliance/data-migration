"""Backup and restore for a tenant.

A backup is a copy plus a manifest of per-file digests. The manifest is the
part that earns its keep: without it, a restore cannot tell a complete archive
from one that lost a file in transit, and the difference only shows up when
someone opens a report a year later.

Restore verifies every digest *before* it writes, and reports mismatches rather
than overwriting good state with bad. That ordering is deliberate — restoring a
corrupt file over a healthy one is worse than refusing to restore.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app_files.tenancy.tenants import Tenant


class BackupError(RuntimeError):
    """Raised when a backup is missing, unreadable, or fails verification."""


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass
class BackupManifest:
    """What a backup contains, per file, with a digest each."""

    tenant: str
    created_at: str
    files: dict[str, str] = field(default_factory=dict)
    """Relative path -> sha256."""

    def as_dict(self) -> dict:
        return {"tenant": self.tenant, "created_at": self.created_at,
                "files": dict(sorted(self.files.items()))}

    @classmethod
    def from_dict(cls, data: dict) -> BackupManifest:
        return cls(
            tenant=str(data["tenant"]),
            created_at=str(data.get("created_at", "")),
            files=dict(data.get("files") or {}),
        )

    @property
    def file_count(self) -> int:
        return len(self.files)


@dataclass
class Backup:
    """A completed backup on disk."""

    tenant: str
    path: Path
    manifest: BackupManifest

    def as_dict(self) -> dict:
        return {
            "tenant": self.tenant,
            "path": str(self.path),
            "created_at": self.manifest.created_at,
            "files": self.manifest.file_count,
        }


@dataclass
class RestoreReport:
    """What a restore did, or refused to do."""

    tenant: str
    restored: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    mismatched: list[str] = field(default_factory=list)
    ok: bool = True

    def as_dict(self) -> dict:
        return {
            "tenant": self.tenant,
            "restored": list(self.restored),
            "missing": list(self.missing),
            "mismatched": list(self.mismatched),
            "ok": self.ok,
        }


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def create_backup(tenant: Tenant, destination: str | Path | None = None) -> Backup:
    """Archive a tenant's tree with a digest manifest beside it.

    The manifest lives *outside* the archive as well as inside it: the outer
    copy is what a verifier reads without unpacking, and the inner copy travels
    with the data so the archive is self-describing.
    """
    destination = Path(destination) if destination else tenant.root.parent / "backups"
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = destination / f"{tenant.id}-{stamp}.tar.gz"

    manifest = BackupManifest(
        tenant=tenant.id,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    files = _iter_files(tenant.root)
    for path in files:
        manifest.files[str(path.relative_to(tenant.root))] = _digest(path)

    with tempfile.TemporaryDirectory() as staging:
        manifest_path = Path(staging) / "backup-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with tarfile.open(archive, "w:gz") as tar:
            for path in files:
                tar.add(path, arcname=str(path.relative_to(tenant.root)))
            tar.add(manifest_path, arcname="backup-manifest.json")

    archive.with_suffix(archive.suffix + ".manifest.json").write_text(
        json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return Backup(tenant=tenant.id, path=archive, manifest=manifest)


def verify_backup(backup: Backup | str | Path) -> BackupManifest:
    """Check every archived file against the manifest. Returns the manifest.

    The authoritative manifest is the one *inside* the archive: it travels with
    the data, so an archive copied to another machine is self-describing. The
    manifest beside the archive is a convenience for reading without unpacking;
    when present it must agree, because two manifests that disagree mean one of
    them was edited and neither can be trusted.

    Raises :class:`BackupError` on a missing file or a digest mismatch, so a
    caller that ignores the return value still cannot miss a corrupt backup.
    """
    path = backup.path if isinstance(backup, Backup) else Path(backup)
    if not path.exists():
        raise BackupError(f"No backup at {path}")

    with tempfile.TemporaryDirectory() as staging:
        with tarfile.open(path, "r:gz") as tar:
            names = tar.getnames()
            if "backup-manifest.json" not in names:
                raise BackupError(f"Backup {path} has no embedded manifest")
            embedded = tar.extractfile("backup-manifest.json")
            if embedded is None:
                raise BackupError(f"Backup {path} has an unreadable manifest")
            manifest = BackupManifest.from_dict(
                json.loads(embedded.read().decode("utf-8"))
            )
            tar.extractall(staging, filter="data")

        outer_path = path.with_suffix(path.suffix + ".manifest.json")
        if outer_path.exists():
            outer = BackupManifest.from_dict(
                json.loads(outer_path.read_text(encoding="utf-8"))
            )
            if outer.files != manifest.files:
                raise BackupError(
                    f"Manifest for {path} does not match the archive's own manifest"
                )

        problems: list[str] = []
        root = Path(staging)
        for relative, expected in manifest.files.items():
            candidate = root / relative
            if not candidate.exists():
                problems.append(f"missing: {relative}")
            elif _digest(candidate) != expected:
                problems.append(f"mismatch: {relative}")
    if problems:
        raise BackupError("Backup failed verification: " + "; ".join(problems[:5]))
    return manifest


def _read_embedded_manifest(archive: Path) -> BackupManifest:
    with tarfile.open(archive, "r:gz") as tar:
        embedded = tar.extractfile("backup-manifest.json")
        if embedded is None:
            raise BackupError(f"Backup {archive} has no embedded manifest")
        return BackupManifest.from_dict(json.loads(embedded.read().decode("utf-8")))


def restore_backup(
    backup: Backup | str | Path,
    tenant: Tenant,
    verify: bool = True,
) -> RestoreReport:
    """Restore a backup into a tenant's root.

    Verification runs first, so a corrupt archive is refused before it can
    overwrite good state. ``verify=False`` is for a caller that has already
    verified and is restoring the same archive twice.
    """
    archive = backup.path if isinstance(backup, Backup) else Path(backup)
    if not archive.exists():
        raise BackupError(f"No backup at {archive}")
    manifest = _read_embedded_manifest(archive)

    if verify:
        verify_backup(archive)

    report = RestoreReport(tenant=tenant.id, ok=True)
    tenant.root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        members = {member.name: member for member in tar.getmembers()}
        for relative, expected in manifest.files.items():
            member = members.get(relative)
            if member is None:
                report.missing.append(relative)
                continue
            target = tenant.resolve_path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = tar.extractfile(member)
            if extracted is None:
                report.missing.append(relative)
                continue
            target.write_bytes(extracted.read())
            if _digest(target) != expected:
                report.mismatched.append(relative)
                continue
            report.restored.append(relative)

    report.ok = not (report.missing or report.mismatched)
    return report


def prune_backups(directory: str | Path, keep: int = 5) -> list[Path]:
    """Keep the newest ``keep`` archives in a directory, remove the rest."""
    directory = Path(directory)
    if not directory.exists():
        return []
    archives = sorted(directory.glob("*.tar.gz"))
    removed = []
    for archive in archives[:-keep] if keep > 0 else archives:
        manifest = archive.with_suffix(archive.suffix + ".manifest.json")
        archive.unlink()
        if manifest.exists():
            manifest.unlink()
        removed.append(archive)
    return removed


def latest_backup(tenant: str, directory: str | Path) -> Path | None:
    directory = Path(directory)
    matches = sorted(directory.glob(f"{tenant}-*.tar.gz"))
    return matches[-1] if matches else None


def copy_tree(source: Tenant | Path, destination: Path) -> int:
    """A plain copy, for a caller that does not want an archive."""
    root = source.root if isinstance(source, Tenant) else Path(source)
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(root, destination)
    return len(_iter_files(destination))


__all__ = [
    "Backup",
    "BackupError",
    "BackupManifest",
    "RestoreReport",
    "copy_tree",
    "create_backup",
    "latest_backup",
    "prune_backups",
    "restore_backup",
    "verify_backup",
]
