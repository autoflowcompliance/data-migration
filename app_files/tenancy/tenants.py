"""Tenants: isolated roots for data, config, output and license.

A tenant has an immutable id and a mutable display name. That split matters: a
folder keyed on the name would move the moment someone renames a client, taking
their history with it, and two tenants called "Acme" would collide. The id is
assigned once and never reused.

Everything a tenant writes lives under ``tenants/<id>/``. ``resolve_path``
refuses to escape that root, which is the guarantee the isolation test asserts:
a crafted name or a stray ``..`` cannot read or write another tenant's data.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


class TenantError(ValueError):
    """Raised on an invalid tenant id/name, or an attempt to escape a tenant."""


_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def tenants_dir() -> Path:
    """Where tenants live. ``AUTOFLOW_HOME`` overrides for portability."""
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override) / "tenants"
    return Path(__file__).resolve().parent.parent.parent / "tenants"


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(text).strip().lower()).strip("-")
    return cleaned or uuid.uuid4().hex[:8]


def _check_id(tenant_id: str) -> str:
    cleaned = str(tenant_id).strip().lower()
    if not _ID.match(cleaned) or ".." in cleaned:
        raise TenantError(
            f"Invalid tenant id {tenant_id!r}. Use lowercase letters, digits, dash "
            "or underscore (max 64 characters)."
        )
    return cleaned


@dataclass
class Tenant:
    """One tenant's root and its metadata."""

    id: str
    name: str
    root: Path
    license_key: str = ""
    created_at: str = ""
    metadata: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ paths
    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def queue_file(self) -> Path:
        return self.root / "jobs.jsonl"

    @property
    def workspaces_dir(self) -> Path:
        return self.root / "workspaces"

    @property
    def meta_path(self) -> Path:
        return self.root / "tenant.json"

    def resolve_path(self, *parts: str) -> Path:
        """Join ``parts`` onto the tenant root, refusing to escape it."""
        candidate = self.root.joinpath(*parts).resolve()
        root = self.root.resolve()
        if candidate != root and root not in candidate.parents:
            raise TenantError(
                f"Path {'/'.join(parts)!r} would leave tenant {self.id!r}."
            )
        return candidate

    def create(self) -> Tenant:
        for folder in (self.root, self.config_dir, self.data_dir, self.output_dir,
                       self.workspaces_dir):
            folder.mkdir(parents=True, exist_ok=True)
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._write_meta()
        return self

    def _write_meta(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(
            json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "license_key": self.license_key,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict, root: Path) -> Tenant:
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", data["id"])),
            root=root,
            license_key=str(data.get("license_key", "")),
            created_at=str(data.get("created_at", "")),
            metadata=dict(data.get("metadata") or {}),
        )

    def rename(self, name: str) -> Tenant:
        """Change the display name. The id, and therefore the folder, does not move."""
        self.name = str(name)
        self._write_meta()
        return self

    def bind_license(self, key: str) -> Tenant:
        self.license_key = str(key)
        self._write_meta()
        return self

    def delete(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def tree(self) -> list[str]:
        """Relative paths of every file under this tenant, sorted."""
        if not self.root.exists():
            return []
        return sorted(
            str(path.relative_to(self.root))
            for path in self.root.rglob("*")
            if path.is_file()
        )

    def usage(self) -> dict:
        """Bytes on disk and file count, per subtree. What billing meters read."""
        breakdown: dict[str, dict] = {}
        total_bytes = 0
        total_files = 0
        for label, folder in (
            ("data", self.data_dir),
            ("output", self.output_dir),
            ("config", self.config_dir),
            ("workspaces", self.workspaces_dir),
        ):
            size = 0
            count = 0
            if folder.exists():
                for path in folder.rglob("*"):
                    if path.is_file():
                        size += path.stat().st_size
                        count += 1
            breakdown[label] = {"files": count, "bytes": size}
            total_bytes += size
            total_files += count
        return {
            "tenant": self.id,
            "files": total_files,
            "bytes": total_bytes,
            "breakdown": breakdown,
        }


class TenantRegistry:
    """The tenants under one root."""

    def __init__(self, base: Path | None = None):
        self.base = Path(base) if base else tenants_dir()

    def _tenant(self, tenant_id: str) -> Tenant:
        checked = _check_id(tenant_id)
        root = self.base / checked
        meta = root / "tenant.json"
        if meta.exists():
            return Tenant.from_dict(json.loads(meta.read_text(encoding="utf-8")), root)
        return Tenant(id=checked, name=checked, root=root)

    def create(
        self,
        name: str,
        tenant_id: str | None = None,
        license_key: str = "",
        metadata: dict | None = None,
    ) -> Tenant:
        chosen_id = _check_id(tenant_id) if tenant_id else _slug(name)
        if (self.base / chosen_id).exists():
            raise TenantError(f"Tenant {chosen_id!r} already exists.")
        tenant = Tenant(
            id=chosen_id,
            name=str(name),
            root=self.base / chosen_id,
            license_key=license_key,
            metadata=dict(metadata or {}),
        )
        tenant.create()
        return tenant

    def get(self, tenant_id: str, create: bool = False, name: str = "") -> Tenant:
        checked = _check_id(tenant_id)
        root = self.base / checked
        if not root.exists():
            if not create:
                raise TenantError(f"No tenant {checked!r}.")
            return self.create(name or checked, tenant_id=checked)
        return self._tenant(checked)

    def list(self) -> list[Tenant]:
        if not self.base.exists():
            return []
        found = []
        for folder in sorted(self.base.iterdir()):
            if folder.is_dir() and (folder / "tenant.json").exists():
                try:
                    found.append(self._tenant(folder.name))
                except (json.JSONDecodeError, KeyError):
                    continue
        return found

    def delete(self, tenant_id: str) -> None:
        self.get(tenant_id).delete()


def list_tenants() -> list[dict]:
    return [tenant.as_dict() for tenant in TenantRegistry().list()]


def get_tenant(tenant_id: str, create: bool = False, name: str = "") -> Tenant:
    return TenantRegistry().get(tenant_id, create=create, name=name)


def ensure_tenant(name: str, tenant_id: str | None = None) -> Tenant:
    """Return an existing tenant, or create one — the idempotent entry point."""
    registry = TenantRegistry()
    chosen_id = _check_id(tenant_id) if tenant_id else _slug(name)
    root = registry.base / chosen_id
    if root.exists():
        return registry.get(chosen_id)
    return registry.create(name, tenant_id=chosen_id)


__all__ = [
    "Tenant",
    "TenantError",
    "TenantRegistry",
    "ensure_tenant",
    "get_tenant",
    "list_tenants",
    "tenants_dir",
]
