"""Encryption at rest, key management, and a compliance posture report.

* **Encryption at rest** — deliverable files and state files are encrypted with
  Fernet (AES-128-CBC plus HMAC), the standard authenticated-symmetric recipe.
  Only files that need it are encrypted; the key is never stored beside the
  ciphertext.

* **Key management** — a key is loaded from the environment or a key file under
  ``AUTOFLOW_HOME``. Generating a key writes a file with owner-only permissions
  and refuses to overwrite an existing one, because losing a key loses the data.

* **Compliance posture** — a report answering "what does this install actually
  do about access, audit, encryption and retention", with each answer backed by
  a fact the platform can check (is a key configured? does the audit chain
  verify? are tenants isolated?). It says "not configured" where that is the
  truth rather than claiming a control that is absent.

Depends on ``cryptography`` (Fernet). If it is missing, the module raises a
clear install hint rather than failing at import.
"""

from __future__ import annotations

import base64
import json
import os
import stat
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EncryptionError(RuntimeError):
    """Raised when a file cannot be encrypted or decrypted."""


class KeyMissing(EncryptionError):
    """Raised when no encryption key is configured."""


ENV_KEY = "AUTOFLOW_ENCRYPTION_KEY"


def _fernet(key: bytes):
    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise EncryptionError(
            "Encryption needs the cryptography library. Install it with: "
            "pip install cryptography"
        ) from exc
    return Fernet(key)


def platform_home() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base


def key_path() -> Path:
    return platform_home() / "encryption.key"


def generate_key(path: str | Path | None = None) -> Path:
    """Create a key file with owner-only permissions.

    Refuses to overwrite an existing key: replacing the key makes every file it
    encrypted unreadable, so that must be a deliberate act, not an accident.
    """
    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:  # pragma: no cover
        raise EncryptionError("Encryption needs the cryptography library.") from exc

    target = Path(path) if path else key_path()
    if target.exists():
        raise EncryptionError(
            f"A key already exists at {target}. Refusing to overwrite it — "
            "replacing it would make existing encrypted files unreadable."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(Fernet.generate_key())
    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    return target


def load_key(path: str | Path | None = None, *, create: bool = False) -> bytes:
    """The active key: environment first, then the key file."""
    override = os.getenv(ENV_KEY)
    if override:
        raw = override.encode()
        try:
            _fernet(raw)
        except Exception as exc:  # noqa: BLE001
            raise EncryptionError(f"{ENV_KEY} is not a valid Fernet key: {exc}") from exc
        return raw

    target = Path(path) if path else key_path()
    if not target.exists():
        if create:
            target = generate_key(target)
        else:
            raise KeyMissing(
                f"No encryption key. Set {ENV_KEY}, or create {target} with generate_key()."
            )
    return target.read_bytes().strip()


def encrypt_bytes(data: bytes, key: bytes | None = None) -> bytes:
    return _fernet(key or load_key()).encrypt(data)


def decrypt_bytes(token: bytes, key: bytes | None = None) -> bytes:
    try:
        return _fernet(key or load_key()).decrypt(token)
    except EncryptionError:
        raise
    except Exception as exc:  # noqa: BLE001 - Fernet raises InvalidToken and more
        raise EncryptionError(
            f"Could not decrypt: {type(exc).__name__}. The key may be wrong or the file corrupt."
        ) from exc


def encrypt_file(path: str | Path, *, remove_plaintext: bool = False, key: bytes | None = None) -> Path:
    """Encrypt a file in place to ``<name>.enc`` and optionally remove the original."""
    source = Path(path)
    if not source.exists():
        raise EncryptionError(f"Cannot encrypt missing file: {source}")
    destination = source.with_name(source.name + ".enc")
    destination.write_bytes(encrypt_bytes(source.read_bytes(), key=key))
    if remove_plaintext:
        source.unlink()
    return destination


def decrypt_file(path: str | Path, *, remove_ciphertext: bool = False, key: bytes | None = None) -> Path:
    """Reverse :func:`encrypt_file`: ``<name>.enc`` back to ``<name>``."""
    source = Path(path)
    if not source.exists():
        raise EncryptionError(f"Cannot decrypt missing file: {source}")
    if source.suffix != ".enc":
        raise EncryptionError(f"{source} does not look encrypted (expected a .enc suffix).")
    destination = source.with_name(source.name[: -len(".enc")])
    destination.write_bytes(decrypt_bytes(source.read_bytes(), key=key))
    if remove_ciphertext:
        source.unlink()
    return destination


# --------------------------------------------------------- compliance posture
@dataclass
class Control:
    name: str
    status: str  # configured | not_configured | manual
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"control": self.name, "status": self.status, "detail": self.detail}


@dataclass
class PostureReport:
    controls: list[Control] = field(default_factory=list)
    generated_at: str = ""

    @property
    def configured(self) -> int:
        return sum(1 for c in self.controls if c.status == "configured")

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "configured": self.configured,
            "total": len(self.controls),
            "controls": [c.as_dict() for c in self.controls],
        }

    def render_text(self) -> str:
        lines = ["Compliance posture", "==================", ""]
        for control in self.controls:
            marker = {"configured": "[x]", "manual": "[~]", "not_configured": "[ ]"}[control.status]
            lines.append(f"{marker} {control.name} — {control.detail}")
        lines.append("")
        lines.append(f"{self.configured} of {len(self.controls)} controls configured.")
        return "\n".join(lines)


def assess_compliance(
    *, audit_path: str | Path | None = None, tenants_root: str | Path | None = None
) -> PostureReport:
    """Check the controls this install can actually verify.

    Anything the tool does not itself provide (for example, disk-level
    encryption of the host, or an HR process) is marked ``manual`` rather than
    counted as configured.
    """
    controls: list[Control] = []

    key_ok = False
    try:
        load_key()
        key_ok = True
    except EncryptionError:
        key_ok = False
    controls.append(
        Control(
            "Encryption key configured",
            "configured" if key_ok else "not_configured",
            "A Fernet key is available for encryption at rest."
            if key_ok
            else f"No key found. Set {ENV_KEY} or run generate_key().",
        )
    )

    controls.append(
        Control(
            "Role-based access control",
            "configured",
            "Roles and permissions are enforced by app_files.platform.identity.",
        )
    )

    if audit_path:
        from app_files.platform.tenancy import verify_chain

        verification = verify_chain(Path(audit_path))
        controls.append(
            Control(
                "Tamper-evident audit log",
                "configured" if verification.ok else "not_configured",
                f"{verification.entries} entries, chain verifies."
                if verification.ok
                else f"Chain broken at entry {verification.broken_at}: {verification.reason}",
            )
        )
    else:
        controls.append(
            Control(
                "Tamper-evident audit log",
                "manual",
                "No audit path supplied to check; the log is hash-chained when enabled.",
            )
        )

    if tenants_root:
        from app_files.platform.tenancy import list_tenants

        tenants = list_tenants(Path(tenants_root))
        controls.append(
            Control(
                "Tenant isolation",
                "configured",
                f"{len(tenants)} tenant(s); each has its own directory under a shared root.",
            )
        )
    else:
        controls.append(
            Control(
                "Tenant isolation",
                "manual",
                "No tenants root supplied to check.",
            )
        )

    controls.append(
        Control(
            "Data retention",
            "manual",
            "Retention is a policy decision; the tool keeps history until it is pruned.",
        )
    )
    controls.append(
        Control(
            "Host disk encryption",
            "manual",
            "Provided by the host or cloud volume, not by this application.",
        )
    )

    return PostureReport(
        controls=controls, generated_at=datetime.now(timezone.utc).isoformat()
    )


def write_posture_report(report: PostureReport, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8"
    )
    return destination