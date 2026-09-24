"""Immutable audit log and tenant isolation.

Two foundations a SaaS buyer checks before signing:

* **An append-only audit log** where each entry carries the hash of the entry
  before it, so the chain can be verified and any edit or deletion in the middle
  is detectable. Entries record timestamp, actor, action, target, IP and a
  detail payload. The log is per tenant (``tenants/<tenant>/audit.jsonl``) and
  the whole chain can be exported as one JSON document for a compliance review.

* **Tenant isolation by construction.** A tenant owns exactly one directory
  tree under ``AUTOFLOW_HOME``, and every path handed back goes through
  :func:`Tenant.resolve`, which refuses to escape the root. Returning the wrong
  tenant's data is not "unlikely"; the only way to reach another tenant's file
  is to name that tenant explicitly, and a crafted ``..`` cannot do it.

Both follow the repository rule that runtime state lives under ``AUTOFLOW_HOME``
(never under the repo root), matching the audit trail and workspaces.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENESIS = "0" * 64

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")


class TenantError(RuntimeError):
    """Raised for an invalid tenant, path, or audit-chain problem."""


# ------------------------------------------------------------ path resolution
def platform_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override) / "platform"
    return Path(__file__).resolve().parent.parent.parent / "platform_state"


def tenants_dir() -> Path:
    return platform_dir() / "tenants"


def canonical_slug(value: str) -> str:
    """Lower-case, dash-separated, safe for a directory name."""
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower()).strip("-")
    if not slug or not _SLUG_RE.match(slug):
        raise TenantError(
            f"{value!r} does not make a valid tenant id. Use letters, digits, "
            f"'.', '_' or '-' (max 63 characters)."
        )
    return slug


def _is_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


@dataclass
class Tenant:
    """One customer: a directory tree that nothing else can reach into."""

    id: str
    name: str = ""
    created_at: str = ""

    @classmethod
    def create(cls, name: str, *, root: Path | None = None) -> "Tenant":
        tenant = cls(
            id=canonical_slug(name),
            name=name,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        base = tenant.root(root)
        for sub in ("config", "samples", "output", "audit"):
            (base / sub).mkdir(parents=True, exist_ok=True)
        tenant.audit_log_path(root).touch(exist_ok=True)
        return tenant

    def root(self, root: Path | None = None) -> Path:
        return (root or tenants_dir()) / self.id

    def resolve(self, *parts: str, root: Path | None = None) -> Path:
        """Resolve a path inside this tenant, refusing to escape it.

        This is the whole isolation guarantee: ``..`` and absolute paths are
        rejected, so no input can name another tenant's file.
        """
        base = self.root(root)
        candidate = base.joinpath(*parts)
        if not _is_within(base, candidate):
            raise TenantError(
                f"Path {parts!r} escapes tenant {self.id!r}. Isolation refused the read."
            )
        return candidate

    def audit_log_path(self, root: Path | None = None) -> Path:
        return self.resolve("audit", "audit.jsonl", root=root)

    def record(
        self,
        action: str,
        *,
        actor: str,
        target: str = "",
        ip: str = "",
        detail: dict[str, Any] | None = None,
        root: Path | None = None,
    ) -> "AuditRecord":
        """Append one entry to this tenant's hash-chained audit log."""
        path = self.audit_log_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        previous = previous_hash(path)
        record = AuditRecord.build(
            tenant=self.id,
            action=action,
            actor=actor,
            target=target,
            ip=ip,
            detail=detail or {},
            previous_hash=previous,
        )
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.as_dict(), sort_keys=True) + "\n")
        return record


def list_tenants(root: Path | None = None) -> list[str]:
    base = root or tenants_dir()
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir())


def get_tenant(name: str, root: Path | None = None) -> Tenant:
    slug = canonical_slug(name)
    if slug not in list_tenants(root):
        raise TenantError(f"No tenant {slug!r}. Create it first.")
    return Tenant(id=slug, name=slug)


# ------------------------------------------------------------------ audit log
@dataclass
class AuditRecord:
    tenant: str
    action: str
    actor: str
    target: str
    ip: str
    timestamp: str
    detail: dict[str, Any]
    previous_hash: str
    entry_hash: str

    @classmethod
    def build(
        cls,
        *,
        tenant: str,
        action: str,
        actor: str,
        target: str,
        ip: str,
        detail: dict[str, Any],
        previous_hash: str,
        timestamp: str | None = None,
    ) -> "AuditRecord":
        stamp = timestamp or datetime.now(timezone.utc).isoformat()
        entry = cls(
            tenant=tenant,
            action=action,
            actor=actor,
            target=target,
            ip=ip,
            timestamp=stamp,
            detail=detail,
            previous_hash=previous_hash,
            entry_hash="",
        )
        entry.entry_hash = entry.compute_hash()
        return entry

    def _hashable(self) -> dict[str, Any]:
        return {
            "tenant": self.tenant,
            "action": self.action,
            "actor": self.actor,
            "target": self.target,
            "ip": self.ip,
            "timestamp": self.timestamp,
            "detail": self.detail,
            "previous_hash": self.previous_hash,
        }

    def compute_hash(self) -> str:
        canonical = json.dumps(self._hashable(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        payload = self._hashable()
        payload["entry_hash"] = self.entry_hash
        return payload


def previous_hash(path: Path) -> str:
    """The hash of the last line, or the genesis hash for an empty log."""
    if not path.exists():
        return GENESIS
    last = ""
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = line
    if not last:
        return GENESIS
    try:
        return str(json.loads(last)["entry_hash"])
    except (json.JSONDecodeError, KeyError) as exc:
        raise TenantError(f"Audit log {path} is corrupt: {exc}") from exc


def read_audit(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise TenantError(f"Audit log line {number} is not JSON: {exc}") from exc
    return records


@dataclass
class ChainVerification:
    ok: bool
    entries: int
    broken_at: int | None = None
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "entries": self.entries,
            "broken_at": self.broken_at,
            "reason": self.reason,
        }


def verify_chain(path: Path) -> ChainVerification:
    """Recompute every hash and confirm the links. Detects edits and deletions."""
    records = read_audit(path)
    expected_previous = GENESIS
    for index, record in enumerate(records):
        rebuilt = AuditRecord(
            tenant=record.get("tenant", ""),
            action=record.get("action", ""),
            actor=record.get("actor", ""),
            target=record.get("target", ""),
            ip=record.get("ip", ""),
            timestamp=record.get("timestamp", ""),
            detail=record.get("detail", {}),
            previous_hash=record.get("previous_hash", ""),
            entry_hash=record.get("entry_hash", ""),
        )
        if rebuilt.previous_hash != expected_previous:
            return ChainVerification(
                ok=False,
                entries=len(records),
                broken_at=index,
                reason="previous_hash does not match the prior entry (an entry was changed or removed).",
            )
        if rebuilt.compute_hash() != rebuilt.entry_hash:
            return ChainVerification(
                ok=False,
                entries=len(records),
                broken_at=index,
                reason="entry_hash does not match the entry contents (the entry was edited).",
            )
        expected_previous = rebuilt.entry_hash
    return ChainVerification(ok=True, entries=len(records))


def export_audit(path: Path) -> dict[str, Any]:
    """One JSON document for a compliance review: entries plus chain status."""
    verification = verify_chain(path)
    return {
        "entries": read_audit(path),
        "verification": verification.as_dict(),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }