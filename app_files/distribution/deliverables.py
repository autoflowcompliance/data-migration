"""Signed deliverables and push to a destination.

Two capabilities that turn a finished run into something a recipient can trust
and receive without a human in the middle.

* **Signing.** Each deliverable gets a detached ``.sig`` sidecar holding an
  HMAC-SHA256 over the file's bytes, plus a manifest listing every artifact and
  its digest. The recipient can verify that the clean file they were handed is
  the one this tool produced, and that nothing on disk changed afterwards.
  Reuses the license key machinery so there is one secret to manage, not two.

* **Push.** Send the deliverables to a destination — a directory, an S3 prefix,
  or an HTTP endpoint. The connector layer does the actual transport; this
  module plans which files go where and records what succeeded, so a partial
  push is visible rather than reported as success.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_files.licensing.signing import secret_key


class DeliveryError(RuntimeError):
    """Raised when a deliverable cannot be signed or pushed."""


class SignatureMismatch(DeliveryError):
    """Raised when a signature does not verify against the file."""


# ------------------------------------------------------------------- signing
def file_digest(path: str | Path) -> str:
    """SHA-256 of a file's bytes, hex encoded."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sign_file(path: str | Path, key: str | None = None) -> dict[str, Any]:
    """Sign one file and return the detached signature record.

    The signature covers the digest rather than the bytes, so the same record
    can be checked from a manifest without reading the file twice.
    """
    target = Path(path)
    if not target.exists():
        raise DeliveryError(f"Cannot sign missing file: {target}")
    digest = file_digest(target)
    signature = hmac.new(
        (key or secret_key()).encode(), digest.encode(), hashlib.sha256
    ).hexdigest()
    return {
        "file": target.name,
        "algorithm": "HMAC-SHA256",
        "digest": digest,
        "signature": signature,
        "signed_at": datetime.now(timezone.utc).isoformat(),
    }


def verify_file(path: str | Path, record: dict[str, Any], key: str | None = None) -> bool:
    """Check a signature record against the file's current bytes."""
    target = Path(path)
    if not target.exists():
        return False
    digest = file_digest(target)
    expected = hmac.new(
        (key or secret_key()).encode(), digest.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, str(record.get("signature", "")))


@dataclass
class SignedBundle:
    directory: Path
    manifest_path: Path | None = None
    records: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "directory": str(self.directory),
            "manifest": str(self.manifest_path) if self.manifest_path else "",
            "files": [record["file"] for record in self.records],
            "digests": {record["file"]: record["digest"] for record in self.records},
        }


def sign_deliverables(
    directory: str | Path,
    *,
    patterns: tuple[str, ...] = ("*.csv", "*.html", "*.json", "*.xlsx", "*.sql"),
    manifest_name: str = "manifest.json",
    key: str | None = None,
) -> SignedBundle:
    """Sign every deliverable in a directory and write a manifest.

    The signature sidecars and the manifest are excluded from signing, so
    re-running over a previously signed directory does not sign the signatures.
    """
    base = Path(directory)
    if not base.is_dir():
        raise DeliveryError(f"Not a directory: {base}")

    skip = {manifest_name, f"{manifest_name}.sig"}
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(base.glob(pattern)))
    files = [f for f in files if f.name not in skip and not f.name.endswith(".sig")]

    bundle = SignedBundle(directory=base)
    for target in files:
        record = sign_file(target, key=key)
        bundle.records.append(record)
        target.with_name(target.name + ".sig").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )

    manifest_path = base / manifest_name
    bundle.manifest_path = manifest_path
    manifest_path.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "algorithm": "HMAC-SHA256",
                "files": bundle.records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return bundle


def verify_bundle(directory: str | Path, *, key: str | None = None) -> dict[str, Any]:
    """Verify every file listed in the manifest against its signature.

    Returns the failures rather than raising, so a caller can report "3 of 12
    files failed to verify" instead of stopping at the first bad one.
    """
    base = Path(directory)
    manifest_path = base / "manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "reason": f"No manifest at {manifest_path}", "failures": []}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for record in manifest.get("files", []):
        target = base / record["file"]
        if not verify_file(target, record, key=key):
            failures.append(record["file"])
    return {
        "ok": not failures,
        "checked": len(manifest.get("files", [])),
        "failures": failures,
    }


# --------------------------------------------------------------------- push
@dataclass
class PushPlan:
    destination: str
    files: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"destination": self.destination, "files": list(self.files)}


def plan_push(
    directory: str | Path,
    *,
    include_signatures: bool = True,
    include_manifest: bool = True,
) -> PushPlan:
    """List what a push would send, before sending anything."""
    base = Path(directory)
    if not base.is_dir():
        raise DeliveryError(f"Not a directory: {base}")

    files = []
    for candidate in sorted(base.rglob("*")):
        if not candidate.is_file():
            continue
        name = candidate.name
        if name.endswith(".sig") and not include_signatures:
            continue
        if name == "manifest.json" and not include_manifest:
            continue
        files.append(str(candidate.relative_to(base)))
    return PushPlan(destination=str(base), files=files)


def push_deliverables(
    directory: str | Path,
    *,
    destination: str,
    transport: Any | None = None,
    include_signatures: bool = True,
) -> dict[str, Any]:
    """Send every deliverable to ``destination`` through a transport callable.

    ``transport`` is called as ``transport(source_path, destination, filename)``
    and returns truthy on success. It defaults to a local directory copy, so the
    push path is exercisable without a cloud account. A transport failure on one
    file is recorded and the push continues, so a partial upload is reported as
    partial rather than being swallowed.
    """
    base = Path(directory)
    plan = plan_push(base, include_signatures=include_signatures)

    if transport is None:
        transport = _local_copy

    sent, failed = [], []
    for relative in plan.files:
        source = base / relative
        try:
            ok = transport(source, destination, relative)
        except Exception as error:  # noqa: BLE001 - report, never abort the batch
            failed.append({"file": relative, "error": str(error)})
            continue
        if ok:
            sent.append(relative)
        else:
            failed.append({"file": relative, "error": "transport returned false"})

    return {
        "destination": destination,
        "sent": sent,
        "failed": failed,
        "ok": not failed,
        "pushed_at": datetime.now(timezone.utc).isoformat(),
    }


def _local_copy(source: Path, destination: str, relative: str) -> bool:
    target = Path(destination) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    return True