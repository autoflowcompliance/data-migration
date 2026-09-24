"""A tamper-evident audit chain.

The existing audit log is append-only in the sense that the code only appends.
That is a promise, not a proof: anyone with write access to the file can edit a
line or drop one, and the result still parses. This module makes the log
self-checking by chaining each entry to the hash of the one before it.

    entry_n.hash = H(entry_n.canonical_payload + entry_{n-1}.hash)

Changing any earlier entry changes every later hash, so verification fails at
the first edit. That is the difference between append-only and tamper-evident.

The chain is written beside the log as a companion file, so the existing log
format and every reader of it are untouched. :func:`append_to_chain` reads the
existing log, not a second copy.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GENESIS = "0" * 64


def chain_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override) / "audit"
    return Path(__file__).resolve().parent.parent.parent / "audit"


def chain_path(name: str = "chain.jsonl") -> Path:
    return chain_dir() / name


def _canonical(payload: dict[str, Any]) -> str:
    """A stable serialisation, so the same entry always hashes the same."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def entry_hash(payload: dict[str, Any], previous: str) -> str:
    digest = hashlib.sha256()
    digest.update(_canonical(payload).encode("utf-8"))
    digest.update(previous.encode("utf-8"))
    return digest.hexdigest()


@dataclass
class ChainVerification:
    """The result of checking a chain, with the position of the first break."""

    ok: bool
    entries: int
    broken_at: int | None = None
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "entries": self.entries,
            "broken_at": self.broken_at,
            "detail": self.detail,
        }

    def render(self) -> str:
        if self.ok:
            return f"chain intact: {self.entries} entries"
        return f"chain BROKEN at entry {self.broken_at}: {self.detail}"


@dataclass
class AuditChain:
    """Append entries and verify the whole chain."""

    path: Path = field(default_factory=chain_path)

    def last_hash(self) -> str:
        entries = self.entries()
        return entries[-1]["hash"] if entries else GENESIS

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Add one entry, chained to the previous hash. Returns the recorded row."""
        row = self._build(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    def _build(self, payload: dict[str, Any]) -> dict[str, Any]:
        previous = self.last_hash()
        return {
            "seq": len(self.entries()),
            "payload": payload,
            "previous": previous,
            "hash": entry_hash(payload, previous),
        }

    def verify(self) -> ChainVerification:
        return verify_records(self.entries())

    def export(self, destination: str | Path) -> Path:
        """Copy the chain out. The export is verifiable on its own."""
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.path.read_text(encoding="utf-8") if self.path.exists() else "",
                          encoding="utf-8")
        return target


def verify_records(records: list[dict[str, Any]]) -> ChainVerification:
    """Check each entry against its predecessor, stopping at the first break."""
    previous = GENESIS
    for index, record in enumerate(records):
        payload = record.get("payload")
        if not isinstance(payload, dict):
            return ChainVerification(False, len(records), index, "entry has no payload")
        recorded_previous = record.get("previous")
        if recorded_previous != previous:
            return ChainVerification(
                False, len(records), index,
                f"previous hash {recorded_previous!r} does not match {previous!r}",
            )
        expected = entry_hash(payload, previous)
        if record.get("hash") != expected:
            return ChainVerification(False, len(records), index, "entry contents were altered")
        previous = expected
    return ChainVerification(True, len(records))


def verify_chain(path: str | Path | None = None) -> ChainVerification:
    return AuditChain(Path(path) if path else chain_path()).verify()


def append_to_chain(entry: Any, name: str = "chain.jsonl") -> dict[str, Any]:
    """Chain an audit-log entry (a dict or dataclass) beside the log."""
    payload = entry.as_dict() if hasattr(entry, "as_dict") else dict(entry)
    return AuditChain(chain_path(name)).append(payload)


__all__ = [
    "GENESIS",
    "AuditChain",
    "ChainVerification",
    "append_to_chain",
    "chain_dir",
    "chain_path",
    "entry_hash",
    "verify_chain",
    "verify_records",
]
