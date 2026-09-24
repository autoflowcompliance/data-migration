"""Sign a deliverable with an HMAC and verify it on receipt.

A signature answers one question: did this file change after it was produced?
It does not answer "who produced it" — the key ships with the tool, so this
stops accidental corruption and casual edits, not a determined attacker. The
distinction matters, so it is stated here rather than implied.

    manifest = sign_file(output, key=secret_key())
    verify_file(output, manifest)      # True, or False after a tamper
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#: Read in chunks so a multi-gigabyte deliverable does not load into memory.
CHUNK = 1024 * 1024


class SignatureError(Exception):
    """Raised when a deliverable does not match its signature."""


@dataclass
class SignatureManifest:
    """The signature of one file plus what was signed."""

    filename: str
    sha256: str
    signature: str
    algorithm: str = "HMAC-SHA256"
    size: int = 0
    signed_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "sha256": self.sha256,
            "signature": self.signature,
            "algorithm": self.algorithm,
            "size": self.size,
            "signed_at": self.signed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SignatureManifest:
        required = ("filename", "sha256", "signature")
        missing = [key for key in required if key not in data]
        if missing:
            raise SignatureError(f"Manifest is missing: {', '.join(missing)}")
        return cls(
            filename=str(data["filename"]),
            sha256=str(data["sha256"]),
            signature=str(data["signature"]),
            algorithm=str(data.get("algorithm", "HMAC-SHA256")),
            size=int(data.get("size", 0)),
            signed_at=str(data.get("signed_at", "")),
        )


def digest_file(path: str | Path) -> str:
    """SHA-256 of a file's bytes, streamed."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(CHUNK):
            hasher.update(chunk)
    return hasher.hexdigest()


def sign_digest(digest: str, key: str) -> str:
    """HMAC-SHA256 of a hex digest."""
    return hmac.new(key.encode(), digest.encode(), hashlib.sha256).hexdigest()


def sign_file(
    path: str | Path,
    key: str,
    signed_at: datetime | None = None,
) -> SignatureManifest:
    """Produce a manifest for a deliverable, leaving the file untouched."""
    location = Path(path)
    if not location.exists():
        raise FileNotFoundError(f"Cannot sign missing file: {location}")
    digest = digest_file(location)
    moment = signed_at or datetime.now(timezone.utc)
    return SignatureManifest(
        filename=location.name,
        sha256=digest,
        signature=sign_digest(digest, key),
        size=location.stat().st_size,
        signed_at=moment.astimezone(timezone.utc).isoformat(),
    )


def sign_bytes(data: bytes, filename: str, key: str) -> SignatureManifest:
    """Sign an in-memory deliverable before it is written."""
    digest = hashlib.sha256(data).hexdigest()
    return SignatureManifest(
        filename=filename,
        sha256=digest,
        signature=sign_digest(digest, key),
        size=len(data),
        signed_at=datetime.now(timezone.utc).isoformat(),
    )


def verify_file(path: str | Path, manifest: SignatureManifest, key: str) -> bool:
    """True when the file still matches its manifest. Never raises on a mismatch."""
    location = Path(path)
    if not location.exists():
        return False
    digest = digest_file(location)
    if not hmac.compare_digest(digest, manifest.sha256):
        return False
    return hmac.compare_digest(sign_digest(digest, key), manifest.signature)


def verify_or_raise(path: str | Path, manifest: SignatureManifest, key: str) -> None:
    """As :func:`verify_file`, but raises a reason on failure."""
    location = Path(path)
    if not location.exists():
        raise SignatureError(f"Signed file is missing: {location}")
    actual = digest_file(location)
    if not hmac.compare_digest(actual, manifest.sha256):
        raise SignatureError(
            f"{location.name} changed after signing "
            f"(expected {manifest.sha256[:12]}..., found {actual[:12]}...)"
        )
    if not hmac.compare_digest(sign_digest(actual, key), manifest.signature):
        raise SignatureError(f"{location.name} signature is not valid for this key")


def write_manifest(manifest: SignatureManifest, path: str | Path) -> Path:
    location = Path(path)
    location.parent.mkdir(parents=True, exist_ok=True)
    location.write_text(json.dumps(manifest.as_dict(), indent=2), encoding="utf-8")
    return location


def read_manifest(path: str | Path) -> SignatureManifest:
    location = Path(path)
    return SignatureManifest.from_dict(json.loads(location.read_text(encoding="utf-8")))


@dataclass
class SignatureBundle:
    """Signatures for a set of deliverables, written as one sidecar."""

    manifests: list[SignatureManifest] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"files": [manifest.as_dict() for manifest in self.manifests]}

    def verify_all(self, directory: str | Path, key: str) -> dict[str, bool]:
        base = Path(directory)
        return {
            manifest.filename: verify_file(base / manifest.filename, manifest, key)
            for manifest in self.manifests
        }

    @property
    def all_valid(self) -> bool:
        return all(manifest.signature for manifest in self.manifests)


def sign_directory(directory: str | Path, key: str, pattern: str = "*") -> SignatureBundle:
    """Sign every matching file in a directory, skipping the manifest itself."""
    base = Path(directory)
    manifests = [
        sign_file(path, key)
        for path in sorted(base.glob(pattern))
        if path.is_file() and not path.name.endswith(".manifest.json")
    ]
    return SignatureBundle(manifests=manifests)
