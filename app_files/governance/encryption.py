"""Encryption for data at rest, and a place for secrets that is not the shell.

Two things, both about keys rather than business logic.

Data at rest is encrypted with AES-256-GCM, which authenticates as well as
encrypts: a tampered ciphertext fails to decrypt rather than returning garbage.
The key comes from a :class:`SecretStore`, which reads a file with restrictive
permissions or an injected mapping — never a bare environment variable, because
an env var leaks into process listings, crash dumps and child processes.

The privacy layer already has a small keyed cipher for reversible masking. That
one is for values inside a dataset; this one is for files on disk. They are
deliberately separate, and neither is a substitute for the other.
"""

from __future__ import annotations

import base64
import json
import os
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # the cryptography package is installed for this feature
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _HAVE_CRYPTO = True
except Exception:  # pragma: no cover - only when the dependency is absent
    _HAVE_CRYPTO = False
    InvalidTag = Exception  # type: ignore[assignment,misc]

KEY_BYTES = 32
NONCE_BYTES = 12

_MAGIC = b"DFENC1"


class EncryptionError(RuntimeError):
    """Raised when a key is missing, malformed, or a ciphertext will not open."""


def _require_crypto() -> None:
    if not _HAVE_CRYPTO:
        raise EncryptionError(
            "Encryption needs the 'cryptography' package. Install it with "
            "`pip install cryptography`."
        )


@dataclass
class Ciphertext:
    """A blob with the parameters needed to open it again."""

    nonce: bytes
    body: bytes

    def to_bytes(self) -> bytes:
        return _MAGIC + base64.b64encode(self.nonce + self.body)

    def to_text(self) -> str:
        return self.to_bytes().decode("ascii")

    @classmethod
    def from_bytes(cls, blob: bytes) -> Ciphertext:
        if not blob.startswith(_MAGIC):
            raise EncryptionError("Not a DataFlow ciphertext")
        raw = base64.b64decode(blob[len(_MAGIC):])
        if len(raw) < NONCE_BYTES:
            raise EncryptionError("Ciphertext is too short to contain a nonce")
        return cls(raw[:NONCE_BYTES], raw[NONCE_BYTES:])


def _key_bytes(key: str | bytes) -> bytes:
    if isinstance(key, bytes):
        material = key
    else:
        try:
            material = base64.b64decode(key, validate=True)
        except Exception as exc:  # noqa: BLE001 - any decode failure is a bad key
            raise EncryptionError(
                "Encryption key must be base64. Generate one with "
                "`SecretStore.generate_key()`."
            ) from exc
    if len(material) != KEY_BYTES:
        raise EncryptionError(
            f"Encryption key must decode to {KEY_BYTES} bytes, got {len(material)}"
        )
    return material


def encrypt_bytes(plaintext: bytes, key: str | bytes) -> Ciphertext:
    _require_crypto()
    nonce = os.urandom(NONCE_BYTES)
    body = AESGCM(_key_bytes(key)).encrypt(nonce, plaintext, None)
    return Ciphertext(nonce, body)


def decrypt_bytes(blob: bytes | Ciphertext, key: str | bytes) -> bytes:
    _require_crypto()
    ciphertext = blob if isinstance(blob, Ciphertext) else Ciphertext.from_bytes(blob)
    try:
        return AESGCM(_key_bytes(key)).decrypt(ciphertext.nonce, ciphertext.body, None)
    except InvalidTag as exc:
        raise EncryptionError(
            "Ciphertext failed authentication: wrong key or the data was altered"
        ) from exc


def encrypt_text(text: str, key: str | bytes) -> str:
    return encrypt_bytes(text.encode("utf-8"), key).to_text()


def decrypt_text(blob: str | bytes, key: str | bytes) -> str:
    raw = blob if isinstance(blob, bytes) else blob.encode("ascii")
    return decrypt_bytes(raw, key).decode("utf-8")


def encrypt_file(source: str | Path, destination: str | Path, key: str | bytes) -> Path:
    """Encrypt a file in place-ish: read source, write ciphertext to destination."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(encrypt_bytes(Path(source).read_bytes(), key).to_bytes())
    return target


def decrypt_file(source: str | Path, destination: str | Path, key: str | bytes) -> Path:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(decrypt_bytes(Path(source).read_bytes(), key))
    return target


class SecretStore:
    """Keys held in one place, not scattered across the environment.

    Precedence is an injected mapping, then a file, then a single env var for
    the one key ``DATAREADY_ENCRYPTION_KEY``. The env fallback exists because a
    container needs some way in, but the file is preferred and is what the docs
    steer to.
    """

    ENV_KEY = "DATAREADY_ENCRYPTION_KEY"

    def __init__(
        self,
        values: Mapping[str, str] | None = None,
        path: str | Path | None = None,
    ) -> None:
        self._values: dict[str, str] = dict(values or {})
        self.path = Path(path) if path else self.default_path()
        if not self._values and self.path.exists():
            self._values.update(self._read_file())

    @staticmethod
    def default_path() -> Path:
        override = os.getenv("AUTOFLOW_HOME") or os.getenv("DATAREADY_HOME")
        root = Path(override) if override else Path(__file__).resolve().parent.parent.parent
        return root / "secrets" / "keys.json"

    @staticmethod
    def generate_key() -> str:
        """A fresh AES-256 key, base64-encoded for storage."""
        return base64.b64encode(os.urandom(KEY_BYTES)).decode("ascii")

    def _read_file(self) -> dict[str, str]:
        if os.name == "posix":
            mode = stat.S_IMODE(self.path.stat().st_mode)
            if mode & 0o077:
                raise EncryptionError(
                    f"{self.path} is readable by other users (mode {mode:o}). "
                    "Run `chmod 600` on it."
                )
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise EncryptionError(f"{self.path} is not valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise EncryptionError(f"{self.path} must hold a JSON object of key names")
        return {str(k): str(v) for k, v in data.items()}

    def get(self, name: str = "default") -> str:
        if name in self._values:
            return self._values[name]
        env = os.getenv(self.ENV_KEY)
        if env and name == "default":
            return env
        raise EncryptionError(
            f"No key named {name!r}. Add it to {self.path} or inject it."
        )

    def has(self, name: str) -> bool:
        return name in self._values

    def names(self) -> list[str]:
        return sorted(self._values)

    def set(self, name: str, value: str, persist: bool = False) -> None:
        _key_bytes(value)  # reject a malformed key at the point it is stored
        self._values[name] = value
        if persist:
            self.save()

    def save(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._values, indent=2, sort_keys=True), encoding="utf-8")
        if os.name == "posix":
            os.chmod(self.path, 0o600)
        return self.path

    def as_dict(self, reveal: bool = False) -> dict[str, Any]:
        """Never prints key material unless explicitly asked."""
        return {
            "path": str(self.path),
            "keys": {
                name: (value if reveal else "(set)") for name, value in self._values.items()
            },
        }


def resolve_key(store: SecretStore | None = None, name: str = "default") -> str:
    return (store or SecretStore()).get(name)


__all__ = [
    "KEY_BYTES",
    "NONCE_BYTES",
    "Ciphertext",
    "EncryptionError",
    "SecretStore",
    "decrypt_bytes",
    "decrypt_file",
    "decrypt_text",
    "encrypt_bytes",
    "encrypt_file",
    "encrypt_text",
    "resolve_key",
]
