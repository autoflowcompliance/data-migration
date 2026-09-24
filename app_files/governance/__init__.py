"""Layer 13 — security and governance.

Role-based access control, a tamper-evident audit chain, and encryption for
data at rest.

The theme running through all three: the tool must be able to say what happened,
who did it, and prove the record has not been edited afterwards. A permission
model without a trustworthy log answers only half the question.

Nothing here changes an existing layer. The audit chain wraps the existing
append-only log without rewriting it, and encryption is a utility the caller
chooses to apply.
"""

from __future__ import annotations

from app_files.governance.audit_chain import (
    AuditChain,
    ChainVerification,
    append_to_chain,
    chain_path,
    verify_chain,
)
from app_files.governance.encryption import (
    Ciphertext,
    EncryptionError,
    SecretStore,
    decrypt_bytes,
    decrypt_file,
    decrypt_text,
    encrypt_bytes,
    encrypt_file,
    encrypt_text,
    resolve_key,
)
from app_files.governance.rbac import (
    ROLE_PERMISSIONS,
    AccessDenied,
    Permission,
    Principal,
    Role,
    UserRegistry,
    check,
    require,
    role_for,
)

__all__ = [
    "ROLE_PERMISSIONS",
    "AccessDenied",
    "AuditChain",
    "ChainVerification",
    "Ciphertext",
    "EncryptionError",
    "Permission",
    "Principal",
    "Role",
    "SecretStore",
    "UserRegistry",
    "append_to_chain",
    "chain_path",
    "check",
    "decrypt_bytes",
    "decrypt_file",
    "decrypt_text",
    "encrypt_bytes",
    "encrypt_file",
    "encrypt_text",
    "require",
    "resolve_key",
    "role_for",
    "verify_chain",
]
