"""Client workspaces: one folder per client, nothing crosses over.

A bookkeeper running twenty clients should not have twenty installs, and should
never mix one client's data with another's. A workspace is a folder::

    workspaces/<client>/
        config.yaml      # this client's mapping config (optional; a named
                         # config is used when absent)
        samples/         # files dropped in for this client
        output/          # everything this client's runs produced
        runs.jsonl       # append-only audit trail for this client

The rule that matters: every path handed back is rooted inside the workspace,
and ``resolve_path`` refuses to escape it. That is what stops a stray ``..`` in
a client name — or a crafted filename — from reading or writing another client's
data.

``AUTOFLOW_HOME`` relocates the ``workspaces/`` folder, matching the audit log
and the setup flag. Without it the folder would sit beside the code, which a
desktop install may not be able to write to, and a user copying a workspace to
another machine would not carry it along.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


class WorkspaceError(ValueError):
    """Raised on an invalid client name or an attempt to escape a workspace."""


def workspaces_dir() -> Path:
    """Where client workspaces live. ``AUTOFLOW_HOME`` overrides for portability."""
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override) / "workspaces"
    return Path(__file__).resolve().parent.parent.parent / "workspaces"


# Kept for callers that read module state rather than calling the function.
WORKSPACES_DIR = Path(__file__).resolve().parent.parent.parent / "workspaces"

_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]{0,63}$")


def _safe_client_name(name: str) -> str:
    cleaned = str(name).strip()
    if not cleaned:
        raise WorkspaceError("A workspace needs a client name.")
    if not _SAFE_NAME.match(cleaned) or ".." in cleaned:
        raise WorkspaceError(
            f"Invalid client name {name!r}. Use letters, digits, spaces, dot, "
            "dash or underscore (max 64 characters)."
        )
    return cleaned


@dataclass
class Workspace:
    """One client's folder."""

    client: str
    root: Path

    # ------------------------------------------------------------------ paths
    @property
    def samples_dir(self) -> Path:
        return self.root / "samples"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def config_path(self) -> Path:
        return self.root / "config.yaml"

    @property
    def runs_path(self) -> Path:
        return self.root / "runs.jsonl"

    def resolve_path(self, *parts: str) -> Path:
        """Join ``parts`` onto the workspace root, refusing to escape it."""
        candidate = (self.root.joinpath(*parts)).resolve()
        root = self.root.resolve()
        if candidate != root and root not in candidate.parents:
            raise WorkspaceError(
                f"Path {'/'.join(parts)!r} would leave the workspace for {self.client!r}."
            )
        return candidate

    def create(self) -> "Workspace":
        for folder in (self.root, self.samples_dir, self.output_dir):
            folder.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.config_path.write_text(
                "# Optional: this client's own mapping config.\n"
                "# Leave the file empty to use a named config such as 'hubspot'.\n",
                encoding="utf-8",
            )
        return self

    # ------------------------------------------------------------------ files
    def add_sample(self, source: str | Path, name: str | None = None) -> Path:
        """Copy a file into this client's ``samples/`` folder."""
        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f"No such file: {source}")
        target = self.resolve_path("samples", name or source.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        return target

    def samples(self) -> list[Path]:
        if not self.samples_dir.exists():
            return []
        return sorted(p for p in self.samples_dir.iterdir() if p.is_file())

    def outputs(self) -> list[Path]:
        if not self.output_dir.exists():
            return []
        return sorted(p for p in self.output_dir.iterdir() if p.is_file())

    def config_for_run(self, fallback: str = "hubspot") -> str:
        """The config path to use: the workspace's own, else the fallback name."""
        if self.config_path.exists() and _has_fields(self.config_path):
            return str(self.config_path)
        return fallback

    # ------------------------------------------------------------------ audit
    def record_run(
        self,
        input_name: str,
        config: str,
        rows_in: int,
        rows_out: int,
        quality_score: float,
        output_hash: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        """Append one run to this client's audit trail and return the entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "client": self.client,
            "input": input_name,
            "config": config,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "quality_score": quality_score,
            "output_hash": output_hash or "",
        }
        if extra:
            entry.update(extra)
        self.root.mkdir(parents=True, exist_ok=True)
        with open(self.runs_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
        return entry

    def run_history(self) -> list[dict]:
        if not self.runs_path.exists():
            return []
        entries = []
        for line in self.runs_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    # --------------------------------------------------------------- lifecycle
    def tree(self) -> list[str]:
        """Relative paths of everything in the workspace, sorted."""
        if not self.root.exists():
            return []
        return sorted(
            str(path.relative_to(self.root))
            for path in self.root.rglob("*")
            if path.is_file()
        )

    def delete(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)


def _has_fields(path: Path) -> bool:
    """True when the config file declares at least one field."""
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - a broken config falls back to the named one
        return False
    return bool(isinstance(data, dict) and data.get("fields"))


def list_workspaces() -> list[str]:
    base = workspaces_dir()
    if not base.exists():
        return []
    return sorted(
        folder.name
        for folder in base.iterdir()
        if folder.is_dir() and (folder / "output").exists()
    )


def get_workspace(client: str, create: bool = True) -> Workspace:
    """Return a workspace, creating its folders when ``create`` is true."""
    name = _safe_client_name(client)
    workspace = Workspace(client=name, root=workspaces_dir() / name)
    if create:
        workspace.create()
    elif not workspace.root.exists():
        raise FileNotFoundError(f"No workspace for client {name!r}.")
    return workspace


def create_workspace(client: str) -> Workspace:
    return get_workspace(client, create=True)


@dataclass
class WorkspaceRun:
    """Result of running one file inside a workspace."""

    client: str
    input_name: str
    output_paths: list[Path] = field(default_factory=list)
    rows_in: int = 0
    rows_out: int = 0
    quality_score: float = 0.0
    output_hash: str = ""
    audit_entry: dict = field(default_factory=dict)

    def summary(self) -> dict:
        return {
            "client": self.client,
            "input": self.input_name,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "quality_score": self.quality_score,
            "output_hash": self.output_hash,
            "outputs": [p.name for p in self.output_paths],
        }


def run_in_workspace(
    client: str,
    source: str | Path,
    config: str = "hubspot",
    output_format: str = "csv",
    lineage: bool = False,
) -> WorkspaceRun:
    """Run the pipeline for one client, writing every artefact into their folder.

    The output filename is prefixed with the client name, so even a user who
    later gathers files from several workspaces can tell them apart.
    """
    from app_files.collaboration.audit_trail import hash_file, write_audit_bundle
    from app_files.ingestion import read_any
    from app_files.lineage import LineageTracker
    from app_files.output import write_any
    from app_files.pipeline import run_pipeline

    workspace = get_workspace(client)
    source = Path(source)
    frame = read_any(source, filename=source.name)

    # Keep the input with the client's other files. Without this the workspace
    # records what was produced but not what it was produced from, so a run
    # could not be reproduced or a client's folder moved to another machine.
    workspace.add_sample(source)

    tracker = LineageTracker() if lineage else None
    result = run_pipeline(
        frame,
        crm=config if _looks_like_path(config) else workspace.config_for_run(config),
        lineage_tracker=tracker,
        source_filename=source.name,
        project_name=f"{workspace.client} — {source.stem}",
    )

    output_paths: list[Path] = []
    target = workspace.resolve_path("output", f"{workspace.client}_{source.stem}")
    output_paths.append(write_any(result.clean_frame, target, output_format))

    issues_csv = ""
    try:
        issues_csv = result.validation.issues_frame().to_csv(index=False)
    except Exception:  # noqa: BLE001 - a report must not break a run
        issues_csv = ""

    for name, payload, suffix in (
        ("qa_report", result.qa_report_html, ".html"),
        ("issues", issues_csv, ".csv"),
    ):
        if payload:
            path = workspace.resolve_path(
                "output", f"{workspace.client}_{source.stem}_{name}{suffix}"
            )
            path.write_text(payload, encoding="utf-8")
            output_paths.append(path)

    if tracker is not None and getattr(tracker, "events", None):
        lineage_path = workspace.resolve_path("output", f"{workspace.client}_{source.stem}_lineage.csv")
        tracker.to_frame().to_csv(lineage_path, index=False)
        output_paths.append(lineage_path)

    summary = result.summary()
    digest = hash_file(output_paths[0])
    entry = workspace.record_run(
        input_name=source.name,
        config=str(config),
        rows_in=summary["rows_in"],
        rows_out=summary["rows_out"],
        quality_score=summary["quality_score"],
        output_hash=digest,
    )
    write_audit_bundle(workspace, output_paths[0], entry)

    return WorkspaceRun(
        client=workspace.client,
        input_name=source.name,
        output_paths=output_paths,
        rows_in=summary["rows_in"],
        rows_out=summary["rows_out"],
        quality_score=summary["quality_score"],
        output_hash=digest,
        audit_entry=entry,
    )


def _looks_like_path(value: str) -> bool:
    return str(value).endswith((".yaml", ".yml")) or "/" in str(value) or "\\" in str(value)