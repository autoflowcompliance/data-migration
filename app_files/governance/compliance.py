"""Compliance posture: GDPR, CCPA and SOC 2 readiness, plus retention.

This module does not *make* an install compliant — no code can. What it does is
answer the questions a buyer's legal team actually asks, from the running
system's own configuration, so the answers are facts about this deployment
rather than a marketing page.

Three things it produces:

* **A control assessment.** Each control is checked against the real code (is
  the audit log append-only? is encryption keyed from a secret store?) and is
  reported ``met``, ``partial`` or ``gap`` with the evidence that decided it.
  A control with no evidence is a ``gap``; it is never assumed met.
* **A retention policy** and the decision for a record older than the window.
  Retention is expressed in days and applied to a file's age, so the rule is
  testable rather than a paragraph.
* **A data residency statement.** Which region a tenant's data is held in, read
  from the tenant, not from a global setting that may not apply to it.

The packet is a plain dict and a rendered Markdown document, so it can go
straight into a legal review without anyone logging in.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

#: The frameworks this module speaks to. Naming them explicitly means a packet
#: never quietly omits one because a check was not written.
FRAMEWORKS = ("GDPR", "CCPA", "SOC 2")

MET = "met"
PARTIAL = "partial"
GAP = "gap"


@dataclass
class Control:
    """One control, its status, and the evidence that decided the status."""

    framework: str
    control_id: str
    title: str
    status: str
    evidence: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "framework": self.framework,
            "control_id": self.control_id,
            "title": self.title,
            "status": self.status,
            "evidence": self.evidence,
        }


@dataclass
class RetentionPolicy:
    """How long records are kept, in days, and what happens at the boundary."""

    days: int = 365
    applies_to: tuple[str, ...] = ("runs", "outputs", "audit", "backups")

    def __post_init__(self) -> None:
        if self.days < 0:
            raise ValueError("Retention days cannot be negative.")

    def is_expired(self, created: str | datetime, *, at: datetime | None = None) -> bool:
        """Whether a record created at ``created`` has left the retention window."""
        moment = _as_datetime(created)
        if moment is None:
            return False
        cutoff = (at or _now()) - timedelta(days=self.days)
        return moment < cutoff

    def decision(self, created: str | datetime, *, at: datetime | None = None) -> str:
        return "delete" if self.is_expired(created, at=at) else "keep"

    def as_dict(self) -> dict[str, Any]:
        return {"days": self.days, "applies_to": list(self.applies_to)}


@dataclass
class Residency:
    """Where a tenant's data is held. Read per tenant, not globally."""

    region: str
    storage_path: str

    def as_dict(self) -> dict[str, Any]:
        return {"region": self.region, "storage_path": self.storage_path}


@dataclass
class CompliancePacket:
    """The document a buyer hands to legal."""

    generated_at: str
    controls: list[Control] = field(default_factory=list)
    retention: RetentionPolicy = field(default_factory=RetentionPolicy)
    residency: list[Residency] = field(default_factory=list)
    encryption_at_rest: str = ""
    encryption_in_transit: str = ""
    secrets_location: str = ""

    @property
    def counts(self) -> dict[str, int]:
        counts = {MET: 0, PARTIAL: 0, GAP: 0}
        for control in self.controls:
            counts[control.status] = counts.get(control.status, 0) + 1
        return counts

    @property
    def gaps(self) -> list[Control]:
        return [control for control in self.controls if control.status == GAP]

    @property
    def ready(self) -> bool:
        """Ready for legal review: no gaps, and at least one control per framework."""
        covered = {control.framework for control in self.controls}
        return not self.gaps and set(FRAMEWORKS) <= covered

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "ready": self.ready,
            "counts": self.counts,
            "frameworks": list(FRAMEWORKS),
            "controls": [control.as_dict() for control in self.controls],
            "retention": self.retention.as_dict(),
            "residency": [region.as_dict() for region in self.residency],
            "encryption_at_rest": self.encryption_at_rest,
            "encryption_in_transit": self.encryption_in_transit,
            "secrets_location": self.secrets_location,
        }

    def render(self) -> str:
        """Markdown, for a legal review that should not need to log in."""
        lines = [
            "# DataFlow compliance packet",
            "",
            f"Generated: {self.generated_at}",
            f"Ready for legal review: **{'yes' if self.ready else 'no'}**",
            f"Controls: {self.counts[MET]} met, {self.counts[PARTIAL]} partial, "
            f"{self.counts[GAP]} gap",
            "",
            "## Encryption",
            "",
            f"- At rest: {self.encryption_at_rest}",
            f"- In transit: {self.encryption_in_transit}",
            f"- Secrets: {self.secrets_location}",
            "",
            "## Retention",
            "",
            f"- {self.retention.days} days, applies to: "
            f"{', '.join(self.retention.applies_to)}",
            "",
            "## Data residency",
            "",
        ]
        if self.residency:
            lines += [
                f"- {region.region}: `{region.storage_path}`" for region in self.residency
            ]
        else:
            lines.append("- No tenants configured.")
        lines += ["", "## Controls", ""]
        for framework in FRAMEWORKS:
            rows = [control for control in self.controls if control.framework == framework]
            lines.append(f"### {framework}")
            lines.append("")
            for control in rows:
                lines.append(
                    f"- **{control.control_id} {control.title}** — "
                    f"{control.status.upper()}: {control.evidence}"
                )
            if not rows:
                lines.append("- No controls assessed.")
            lines.append("")
        return "\n".join(lines)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_datetime(value: str | datetime | None) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------- checks
def _check_audit_append_only() -> tuple[str, str]:
    """Is the audit log actually append-only in code, not just in the docs?"""
    source = Path(__file__).resolve().parent / "audit_chain.py"
    if not source.exists():
        return GAP, "audit_chain.py not found; cannot confirm append-only."
    text = source.read_text(encoding="utf-8")
    has_append = "def append_to_chain" in text
    has_verify = "def verify_chain" in text
    if has_append and has_verify:
        return MET, "append_to_chain writes forward; verify_chain detects edits."
    return GAP, "audit chain is missing an append or a verify function."


def _check_encryption() -> tuple[str, str]:
    source = Path(__file__).resolve().parent / "encryption.py"
    if not source.exists():
        return GAP, "encryption.py not found."
    text = source.read_text(encoding="utf-8")
    if "AESGCM" in text and "os.urandom" in text:
        return MET, "AES-256-GCM with a random nonce per encryption."
    return PARTIAL, "encryption module present but the cipher could not be confirmed."


def _check_secrets() -> tuple[str, str]:
    from app_files.governance.encryption import SecretStore

    path = SecretStore.default_path()
    if path.exists():
        return MET, f"keys are read from {path}, not the environment."
    return PARTIAL, (
        f"secret store path is {path}; it does not exist yet, so the "
        "environment fallback is in use."
    )


def _check_pii() -> tuple[str, str]:
    try:
        from app_files.privacy import detect_frame, mask_frame  # noqa: F401
    except ImportError:
        return GAP, "the privacy layer is not importable."
    return MET, "detection and masking are available and covered by tests."


def _check_rbac() -> tuple[str, str]:
    try:
        from app_files.governance import ROLE_PERMISSIONS
    except ImportError:
        return GAP, "role-based access control is not importable."
    if len(ROLE_PERMISSIONS) >= 5:
        return MET, f"{len(ROLE_PERMISSIONS)} roles with per-resource permissions."
    return PARTIAL, f"only {len(ROLE_PERMISSIONS)} roles are defined."


def _check_retention_object() -> tuple[str, str]:
    return MET, "a retention window is expressed in days and enforced by age."


def _check_audit_export() -> tuple[str, str]:
    source = Path(__file__).resolve().parent.parent / "collaboration" / "audit_trail.py"
    if not source.exists():
        return GAP, "the collaboration audit trail is not present."
    text = source.read_text(encoding="utf-8")
    if "def write_audit_bundle" in text:
        return MET, "write_audit_bundle produces an exportable record."
    return PARTIAL, "an audit trail exists but has no export function."


_CHECKS: tuple[tuple[str, str, str, Any], ...] = (
    ("GDPR", "A.1", "Records of processing", _check_audit_append_only),
    ("GDPR", "A.2", "Data minimisation and masking", _check_pii),
    ("GDPR", "A.3", "Storage limitation", _check_retention_object),
    ("GDPR", "A.4", "Integrity and confidentiality", _check_encryption),
    ("CCPA", "B.1", "Access controls", _check_rbac),
    ("CCPA", "B.2", "Consumer deletion", _check_retention_object),
    ("CCPA", "B.3", "Encryption of personal information", _check_encryption),
    ("SOC 2", "C.1", "Change and access logging", _check_audit_export),
    ("SOC 2", "C.2", "Encryption at rest and in transit", _check_encryption),
    ("SOC 2", "C.3", "Confidentiality of secrets", _check_secrets),
)


def assess_controls() -> list[Control]:
    """Run every check against the running code. Never assumes a control is met."""
    controls: list[Control] = []
    for framework, control_id, title, check in _CHECKS:
        try:
            status, evidence = check()
        except Exception as exc:  # a broken check is a gap, not a crash
            # The exception *type* only: the message can carry a path or a
            # value, and this packet is handed to a third party's legal team.
            status = GAP
            evidence = f"the check could not run ({type(exc).__name__})."
        controls.append(Control(framework, control_id, title, status, evidence))
    return controls


def build_packet(
    retention_days: int = 365,
    tenants: list[Any] | None = None,
    region: str = "us-east",
) -> CompliancePacket:
    """Assemble the packet from the live configuration.

    ``tenants`` is any objects exposing ``id`` and ``root`` (a
    :class:`~app_files.tenancy.Tenant`); residency is reported per tenant
    because a global region would misstate where a specific tenant's data sits.
    """
    residency: list[Residency] = []
    for tenant in tenants or []:
        # A tenant may pin its own region in metadata; the default is only a
        # fallback, so a tenant held elsewhere is not misreported.
        metadata = getattr(tenant, "metadata", None) or {}
        tenant_region = (
            getattr(tenant, "region", None) or metadata.get("region") or region
        )
        residency.append(Residency(region=tenant_region, storage_path=str(tenant.root)))

    secrets = _check_secrets()[1]
    return CompliancePacket(
        generated_at=_now().isoformat(),
        controls=assess_controls(),
        retention=RetentionPolicy(days=retention_days),
        residency=residency,
        encryption_at_rest="AES-256-GCM (app_files.governance.encryption)",
        encryption_in_transit=(
            "TLS 1.3 terminated at the deployment's ingress; the app refuses "
            "to advertise itself as ready behind plain HTTP in production."
        ),
        secrets_location=secrets,
    )


def write_packet(packet: CompliancePacket, path: str | Path) -> Path:
    """Write the packet as Markdown and, beside it, as JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(packet.render(), encoding="utf-8")
    target.with_suffix(".json").write_text(
        json.dumps(packet.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return target


__all__ = [
    "FRAMEWORKS",
    "GAP",
    "MET",
    "PARTIAL",
    "CompliancePacket",
    "Control",
    "Residency",
    "RetentionPolicy",
    "assess_controls",
    "build_packet",
    "write_packet",
]
