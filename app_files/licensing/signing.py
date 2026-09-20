"""HMAC helpers shared by the license loader and the license generator.

The secret is read from ``DATAREADY_SECRET_KEY`` when set, and falls back to a
built-in default so a client install works out of the box. This is an offline
signature check, not a tamper-proof scheme: the key ships with the client
package and a determined user could extract it. It exists to stop casual
sharing of a license file, not to withstand a reverse engineer.
"""

from __future__ import annotations

import hashlib
import hmac
import os

SECRET_KEY = "dataready-offline-license-v1-8f2c41a9"
"""Default signing key. Override with ``DATAREADY_SECRET_KEY`` to rotate."""


def secret_key() -> str:
    """The active signing key: environment override, else the built-in default."""
    return os.getenv("DATAREADY_SECRET_KEY") or SECRET_KEY


def license_payload(email: str, issued: str) -> str:
    """The exact string that gets signed. Both sides must build it identically."""
    return f"{email}|{issued}"


def sign(email: str, issued: str, key: str | None = None) -> str:
    """Hex HMAC-SHA256 of ``email|issued``."""
    payload = license_payload(email, issued).encode()
    return hmac.new((key or secret_key()).encode(), payload, hashlib.sha256).hexdigest()


def signature_matches(email: str, issued: str, signature: str, key: str | None = None) -> bool:
    """Constant-time comparison so a wrong signature cannot be probed byte by byte."""
    if not isinstance(signature, str):
        return False
    return hmac.compare_digest(sign(email, issued, key), signature)