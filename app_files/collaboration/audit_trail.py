"""Audit trail: a durable record of every run, with a hash of every output.

If a client asks "what did you do to my data?", this answers with facts rather
than memory: the timestamp, the input file name and its hash, the config used,
the row counts, the quality score, and a SHA-256 of the output file. The hash is
the part that matters — it proves the file the client is holding is the file
this tool produced, not a later edit.

The trail is append-only JSONL, one entry per line, per workspace and globally.
Each run also gets a small ``audit_<stem>.html`` bundle that can be attached to
a client deliverable.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

def audit_dir() -> Path:
    """Where the global audit log lives. ``AUTOFLOW_HOME`` overrides for tests."""
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override) / "audit"
    return Path(__file__).resolve().parent.parent.parent / "audit"

CHUNK = 1024 * 1024


def hash_file(path: str | Path, algorithm: str = "sha256") -> str:
    """Hash a file's bytes, streaming so large outputs do not blow memory."""
    digest = hashlib.new(algorithm)
    with open(path, "rb") as handle:
        while chunk := handle.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, data).hexdigest()


def global_log_path() -> Path:
    return audit_dir() / "runs.jsonl"


@dataclass
class AuditEntry:
    """One immutable run record."""

    timestamp: str
    input_name: str
    input_hash: str
    config: str
    rows_in: int
    rows_out: int
    quality_score: float
    output_hash: str
    output_name: str = ""
    client: str = ""
    tool_version: str = "1.0"
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        payload = {
            "timestamp": self.timestamp,
            "client": self.client,
            "input": self.input_name,
            "input_hash": self.input_hash,
            "config": self.config,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "quality_score": self.quality_score,
            "output": self.output_name,
            "output_hash": self.output_hash,
            "tool_version": self.tool_version,
        }
        payload.update(self.extra)
        return payload


def build_entry(
    input_path: str | Path,
    output_path: str | Path,
    config: str,
    rows_in: int,
    rows_out: int,
    quality_score: float,
    client: str = "",
    extra: dict | None = None,
) -> AuditEntry:
    """Hash the input and output and assemble a log entry."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        input_name=input_path.name,
        input_hash=hash_file(input_path) if input_path.exists() else "",
        config=str(config),
        rows_in=int(rows_in),
        rows_out=int(rows_out),
        quality_score=float(quality_score),
        output_name=output_path.name,
        output_hash=hash_file(output_path) if output_path.exists() else "",
        client=client,
        extra=extra or {},
    )


def append_entry(entry: AuditEntry | dict, path: str | Path | None = None) -> Path:
    """Append one entry to a JSONL log (the global one by default)."""
    target = Path(path) if path else global_log_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = entry.as_dict() if isinstance(entry, AuditEntry) else dict(entry)
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
    return target


def read_log(path: str | Path | None = None) -> list[dict]:
    """Read a JSONL log, skipping unreadable lines rather than failing."""
    target = Path(path) if path else global_log_path()
    if not target.exists():
        return []
    entries = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def verify_output(path: str | Path, expected_hash: str) -> bool:
    """True when ``path`` still hashes to ``expected_hash``."""
    path = Path(path)
    if not path.exists() or not expected_hash:
        return False
    return hash_file(path) == expected_hash


def render_audit_html(entry: dict | AuditEntry, verified: bool | None = None) -> str:
    """A standalone audit note, safe to attach to a client deliverable."""
    data = entry.as_dict() if isinstance(entry, AuditEntry) else dict(entry)
    rows = "".join(
        f"<tr><th>{key}</th><td>{value}</td></tr>"
        for key, value in data.items()
    )
    if verified is None:
        verdict = ""
    else:
        colour = "#047857" if verified else "#b91c1c"
        verdict = (
            f"<p style='color:{colour};font-weight:600;'>"
            f"Output hash {'matches' if verified else 'does NOT match'} this record.</p>"
        )
    return (
        "<html><head><meta charset='utf-8'><title>Run audit record</title>"
        "<style>body{font-family:sans-serif;padding:24px;color:#111827;}"
        "table{border-collapse:collapse;}th,td{border-bottom:1px solid #e5e7eb;"
        "padding:6px 10px;text-align:left;font-size:13px;}th{background:#f3f4f6;}"
        "code{background:#f3f4f6;padding:1px 3px;}</style></head><body>"
        "<h1>Run audit record</h1>"
        f"{verdict}"
        f"<table>{rows}</table>"
        "<p style='font-size:12px;color:#6b7280;'>The output hash is a SHA-256 digest "
        "of the delivered file. Re-hashing the file and getting the same value proves "
        "it is unchanged since this run.</p>"
        "</body></html>"
    )


def write_audit_bundle(workspace, output_path: Path, entry: dict) -> Path:
    """Record the run in the global log and write the workspace audit note."""
    entry.setdefault("client", getattr(workspace, "client", ""))
    append_entry(entry)
    note = workspace.resolve_path("output", f"audit_{Path(output_path).stem}.html")
    note.write_text(render_audit_html(entry), encoding="utf-8")
    return note