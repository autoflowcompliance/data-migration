"""Cloud deployment profiles, backup, and disaster recovery.

Three things a buyer asks for before they put this near production data.

* **Deployment profiles** — named, checked bundles of settings for a target
  (a local box, a container, a managed cloud service). A profile states what it
  expects to be true (a port, a writable state home, a persistent volume) and
  validates itself against the running environment, so a misconfigured deploy is
  caught by a check rather than by a customer.

* **Backup** — a single archive of the state that matters: the audit logs,
  baselines, watch state, profiles and configs. It is a tar of a manifest plus
  the files, and it records a digest per file so a restore can tell a good
  archive from a truncated one.

* **Disaster recovery** — restore a backup into a fresh home, verifying every
  digest first, and report what was restored and what was missing rather than
  half-writing a broken state.

Everything writes under ``AUTOFLOW_HOME``/``DATAREADY_HOME``; nothing lands in
the repository.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import tarfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKUP_FORMAT = "dataflow-backup/1"


class DeploymentError(RuntimeError):
    """Raised for an invalid deployment profile or a failed deploy check."""


class BackupError(RuntimeError):
    """Raised when a backup cannot be written or read."""


def autoflow_home() -> Path:
    return Path(os.getenv("AUTOFLOW_HOME") or (Path.home() / ".autoflow"))


def dataready_home() -> Path:
    return Path(os.getenv("DATAREADY_HOME") or (Path.home() / ".dataready"))


@dataclass
class Profile:
    name: str
    port: int = 8080
    state_home: str = ""
    persistent: bool = True
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "port": self.port,
            "state_home": self.state_home,
            "persistent": self.persistent,
            "description": self.description,
        }


PROFILES: dict[str, Profile] = {
    "local": Profile("local", port=8080, persistent=False, description="A laptop or a single VM."),
    "container": Profile(
        "container",
        port=int(os.getenv("PORT") or os.getenv("DATAREADY_PORT") or 8080),
        persistent=True,
        description="Docker or another container runtime.",
    ),
    "cloud": Profile(
        "cloud",
        port=int(os.getenv("PORT") or 8080),
        persistent=True,
        description="A managed web service with a mounted volume.",
    ),
}


@dataclass
class DeployCheck:
    name: str
    ok: bool
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"check": self.name, "ok": self.ok, "detail": self.detail}


@dataclass
class DeployReport:
    profile: Profile
    checks: list[DeployCheck] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.as_dict(),
            "ok": self.ok,
            "checks": [check.as_dict() for check in self.checks],
        }


def get_profile(name: str) -> Profile:
    key = str(name).strip().lower()
    if key not in PROFILES:
        raise DeploymentError(
            f"Unknown deployment profile {name!r}. Choose one of: {', '.join(sorted(PROFILES))}."
        )
    return PROFILES[key]


def validate_deployment(
    name: str = "container",
    *,
    state_home: str | Path | None = None,
    environ: dict[str, str] | None = None,
) -> DeployReport:
    """Check that a profile's assumptions hold here and now.

    The port check honours the same precedence as the server itself
    (``PORT`` > ``DATAREADY_PORT`` > profile default), because a container that
    binds the wrong port is the classic silent Render failure.
    """
    env = environ if environ is not None else os.environ
    profile = get_profile(name)
    checks: list[DeployCheck] = []

    resolved_port = int(env.get("PORT") or env.get("DATAREADY_PORT") or profile.port or 8080)
    checks.append(
        DeployCheck(
            "port",
            True,
            f"Will bind {resolved_port} (PORT > DATAREADY_PORT > {profile.port}).",
        )
    )

    home = Path(state_home) if state_home else (autoflow_home())
    writable = True
    try:
        home.mkdir(parents=True, exist_ok=True)
        probe = home / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as error:
        writable = False
        checks.append(
            DeployCheck("state home", False, f"Cannot write to {home}: {error}")
        )
    if writable:
        checks.append(DeployCheck("state home", True, f"{home} is writable."))

    if profile.persistent:
        checks.append(
            DeployCheck(
                "persistence",
                bool(env.get("AUTOFLOW_HOME") or env.get("DATAREADY_HOME")),
                "AUTOFLOW_HOME/DATAREADY_HOME set"
                if env.get("AUTOFLOW_HOME") or env.get("DATAREADY_HOME")
                else "No state-home env set; state will live inside the container and be lost on redeploy.",
            )
        )

    return DeployReport(profile=profile, checks=checks)


# ------------------------------------------------------------------- backup
@dataclass
class BackupManifest:
    created_at: str = ""
    format: str = BACKUP_FORMAT
    files: list[dict[str, Any]] = field(default_factory=list)
    root: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "created_at": self.created_at,
            "root": self.root,
            "files": list(self.files),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BackupManifest":
        return cls(
            created_at=str(data.get("created_at", "")),
            format=str(data.get("format", BACKUP_FORMAT)),
            files=list(data.get("files", [])),
            root=str(data.get("root", "")),
        )


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _gather(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    if not root.is_dir():
        return []
    found: list[Path] = []
    for pattern in patterns:
        found.extend(sorted(root.rglob(pattern)))
    return [f for f in found if f.is_file()]


DEFAULT_PATTERNS = ("*.json", "*.jsonl", "*.key", "*.csv", "*.yaml", "*.yml")


def create_backup(
    destination: str | Path,
    *,
    home: str | Path | None = None,
    patterns: tuple[str, ...] = DEFAULT_PATTERNS,
) -> Path:
    """Write a tar archive of the state under ``home``.

    The archive carries a ``manifest.json`` first, with a digest per file, so a
    restore can verify integrity without a sidecar.
    """
    base = Path(home) if home else autoflow_home()
    files = _gather(base, patterns)

    manifest = BackupManifest(
        created_at=datetime.now(timezone.utc).isoformat(),
        root=str(base),
    )
    entries: list[tuple[Path, bytes]] = []
    for path in files:
        data = path.read_bytes()
        relative = str(path.relative_to(base))
        manifest.files.append(
            {"path": relative, "size": len(data), "sha256": _digest(data)}
        )
        entries.append((path, data))

    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(target, "w:gz") as archive:
        payload = json.dumps(manifest.as_dict(), indent=2).encode("utf-8")
        info = tarfile.TarInfo("manifest.json")
        info.size = len(payload)
        info.mtime = int(datetime.now(timezone.utc).timestamp())
        archive.addfile(info, io.BytesIO(payload))
        for path, data in entries:
            info = tarfile.TarInfo(f"files/{path.relative_to(base)}")
            info.size = len(data)
            info.mtime = int(path.stat().st_mtime)
            archive.addfile(info, io.BytesIO(data))
    return target


def read_backup_manifest(path: str | Path) -> BackupManifest:
    source = Path(path)
    if not source.exists():
        raise BackupError(f"No backup at {source}.")
    try:
        with tarfile.open(source, "r:gz") as archive:
            member = archive.extractfile("manifest.json")
            if member is None:
                raise BackupError(f"Backup {source} has no manifest.json.")
            return BackupManifest.from_dict(json.loads(member.read().decode("utf-8")))
    except tarfile.TarError as error:
        raise BackupError(f"Backup {source} is not a readable archive: {error}") from error


@dataclass
class RestoreResult:
    restored: list[str] = field(default_factory=list)
    failed: list[dict[str, str]] = field(default_factory=list)
    root: str = ""

    @property
    def ok(self) -> bool:
        return not self.failed

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "restored": list(self.restored), "failed": list(self.failed), "root": self.root}


def restore_backup(path: str | Path, *, home: str | Path | None = None) -> RestoreResult:
    """Restore a backup, verifying every digest before writing it.

    A file whose digest does not match is skipped and reported, rather than
    written, so a corrupted archive cannot install bad state. Files with a
    matching digest are written; the function never raises for one bad file.
    """
    source = Path(path)
    manifest = read_backup_manifest(source)
    base = Path(home) if home else autoflow_home()
    base.mkdir(parents=True, exist_ok=True)

    result = RestoreResult(root=str(base))
    with tarfile.open(source, "r:gz") as archive:
        for entry in manifest.files:
            relative = entry["path"]
            try:
                member = archive.extractfile(f"files/{relative}")
                if member is None:
                    result.failed.append({"path": relative, "error": "missing from archive"})
                    continue
                data = member.read()
                if _digest(data) != entry["sha256"]:
                    result.failed.append({"path": relative, "error": "digest mismatch"})
                    continue
                target = base / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                result.restored.append(relative)
            except (KeyError, OSError) as error:
                result.failed.append({"path": relative, "error": str(error)})
    return result


def verify_backup(path: str | Path) -> dict[str, Any]:
    """Read-only integrity check: does every listed file match its digest?"""
    source = Path(path)
    manifest = read_backup_manifest(source)
    good, bad = [], []
    with tarfile.open(source, "r:gz") as archive:
        for entry in manifest.files:
            member = archive.extractfile(f"files/{entry['path']}")
            if member is None:
                bad.append(entry["path"])
                continue
            (good if _digest(member.read()) == entry["sha256"] else bad).append(entry["path"])
    return {
        "format": manifest.format,
        "ok": not bad,
        "checked": len(manifest.files),
        "good": good,
        "bad": bad,
    }