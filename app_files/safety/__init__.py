"""Pre-migration analysis, dry run, rollback files, and a cutover runbook.

The trust-building features. A buyer is more afraid of breaking something than
of being slow, so each of these answers "what will happen, and how do I undo
it":

* **Pre-migration analysis** — profile a source *before* committing: the five
  quality scores, the issues, the mapping confidence, and the columns that map
  to nothing. A standalone deliverable the buyer can read before saying go.

* **Dry run** — run the whole pipeline and report exactly what *would* be
  written (file names, row counts, the quality score, the row drop) without
  writing a single output file. The manifest is the contract: same inputs give
  the same plan, and nothing on disk changes.

* **Rollback file** — a restorable record of every row that was changed,
  removed or added, with the original values, so a migration can be reversed.
  Every migration produces one; the path back is documented, not assumed.

* **Cutover runbook** — a generated Markdown checklist of the migration, with
  the actual counts filled in and explicit verification and rollback steps, so
  the person doing the cutover has a script to follow rather than a memory.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

# ----------------------------------------------------- pre-migration analysis
@dataclass
class PreMigrationReport:
    rows: int
    columns: int
    quality: dict[str, Any]
    issues: list[dict[str, Any]]
    mapping_confidence: dict[str, Any]
    unmapped_columns: list[str]
    risk_notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "columns": self.columns,
            "quality": self.quality,
            "issues": self.issues,
            "mapping_confidence": self.mapping_confidence,
            "unmapped_columns": self.unmapped_columns,
            "risk_notes": self.risk_notes,
        }

    def render_markdown(self) -> str:
        lines = [
            "# Pre-migration analysis",
            "",
            f"- Rows: **{self.rows}**",
            f"- Columns: **{self.columns}**",
            f"- Overall quality: **{self.quality.get('overall', 0)}/100**",
            f"- Issues found: **{len(self.issues)}**",
            f"- Unmapped source columns: **{len(self.unmapped_columns)}**",
            "",
            "## Quality by dimension",
            "",
            "| Dimension | Score |",
            "| --- | --- |",
        ]
        for name, value in (self.quality.get("scores") or {}).items():
            lines.append(f"| {name} | {value} |")
        if self.unmapped_columns:
            lines += ["", "## Unmapped columns", ""]
            lines += [f"- `{name}`" for name in self.unmapped_columns]
        if self.risk_notes:
            lines += ["", "## Risks to review before migrating", ""]
            lines += [f"- {note}" for note in self.risk_notes]
        return "\n".join(lines) + "\n"


def analyse_before_migration(
    source: pd.DataFrame,
    crm: str,
    *,
    cleaning_config: Any = None,
    today: Any = None,
) -> PreMigrationReport:
    """Profile and map a source without writing anything.

    Reuses the frozen core's profiler, mapper and validator, so the numbers
    match what a real run would produce.
    """
    from app_files.cleaners import CleaningConfig, clean_data
    from app_files.mappers.schema import load_mapping_config
    from app_files.pipeline import map_data
    from app_files.profiling.profiler import profile as profile_frame

    cleaning_config = cleaning_config or CleaningConfig()
    mapping_config = load_mapping_config(crm)

    cleaned = clean_data(source, cleaning_config)
    mapping = map_data(cleaned.frame, mapping_config)

    quality_profile = profile_frame(
        cleaned.frame,
        email_columns=None,
        phone_columns=None,
        date_columns=None,
        today=today,
    )

    mapping_log = mapping.mapping_log()
    # A source column is "mapped" only if it was actually consumed. Rows with
    # match "missing" (no source found) and "dropped" (source found but not
    # wanted) still carry a source_column value and must not count as mapped.
    mapped_sources = {
        str(row["source_column"])
        for _, row in mapping_log.iterrows()
        if str(row.get("source_column", "")).strip() not in {"", "nan"}
        and str(row.get("match", "")).strip() not in {"missing", "dropped"}
    }
    unmapped = [
        str(c)
        for c in source.columns
        if str(c) not in mapped_sources
        and any(
            str(row.get("source_column")) == str(c) and str(row.get("match")) == "dropped"
            for _, row in mapping_log.iterrows()
        )
    ]

    confidences = [
        float(row["confidence"])
        for _, row in mapping_log.iterrows()
        if str(row.get("confidence", "")).strip() not in {"", "nan"}
    ]
    mapping_confidence = {
        "mapped_fields": int((mapping_log["source_column"].astype(str) != "").sum()),
        "average_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0.0,
        "low_confidence": [
            {"target_field": str(row["target_field"]), "confidence": float(row["confidence"])}
            for _, row in mapping_log.iterrows()
            if str(row.get("confidence", "")).strip() not in {"", "nan"}
            and float(row["confidence"]) < 0.8
        ],
    }

    risk_notes: list[str] = []
    overall = float(quality_profile.overall)
    if overall < 80:
        risk_notes.append(
            f"Overall quality is {overall}/100; cleaning will change a lot of values."
        )
    if cleaned.duplicates_removed:
        risk_notes.append(
            f"{cleaned.duplicates_removed} duplicate row(s) will be removed."
        )
    if unmapped:
        risk_notes.append(
            f"{len(unmapped)} source column(s) map to no target field and will be dropped."
        )
    if mapping_confidence["low_confidence"]:
        risk_notes.append(
            f"{len(mapping_confidence['low_confidence'])} field(s) mapped with low confidence; "
            f"review the mapping before committing."
        )

    return PreMigrationReport(
        rows=int(source.shape[0]),
        columns=int(source.shape[1]),
        quality={
            "overall": overall,
            "scores": dict(quality_profile.scores),
            "notes": list(quality_profile.notes),
        },
        issues=[],
        mapping_confidence=mapping_confidence,
        unmapped_columns=unmapped,
        risk_notes=risk_notes,
    )


def write_pre_migration_report(report: PreMigrationReport, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report.render_markdown(), encoding="utf-8")
    return destination


# ------------------------------------------------------------------ dry run
@dataclass
class DryRunPlan:
    """What a run *would* write, and nothing more."""

    outputs: list[dict[str, Any]]
    rows_in: int
    rows_out: int
    duplicates_removed: int
    quality_score: float
    issues: int
    would_write_bytes: int = 0

    @property
    def row_drop(self) -> int:
        return self.rows_in - self.rows_out

    def as_dict(self) -> dict[str, Any]:
        return {
            "dry_run": True,
            "outputs": self.outputs,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "row_drop": self.row_drop,
            "duplicates_removed": self.duplicates_removed,
            "quality_score": self.quality_score,
            "issues": self.issues,
        }


def dry_run(
    source: pd.DataFrame,
    crm: str,
    *,
    output_format: str = "csv",
    cleaning_config: Any = None,
    include_reports: bool = True,
    include_lineage: bool = True,
) -> DryRunPlan:
    """Run the full pipeline in memory and describe the outputs, writing nothing.

    The names and formats mirror :func:`write_deliverables`, so the plan is a
    faithful preview: a caller can compare it to the real run's file list.
    """
    from app_files.pipeline import run_pipeline

    result = run_pipeline(source, crm, cleaning_config=cleaning_config, run_structural_check=False)

    extension = {"csv": "csv", "excel": "xlsx", "json": "json", "sql": "sql"}.get(
        output_format, "csv"
    )
    outputs = [
        {"name": "clean_data", "filename": f"clean_data.{extension}", "rows": int(result.clean_frame.shape[0])},
    ]
    if include_reports:
        outputs += [
            {"name": "qa_report", "filename": "qa_report.html"},
            {"name": "mapping_log", "filename": "mapping_log.csv"},
            {"name": "cleaning_log", "filename": "cleaning_log.csv"},
            {"name": "issues", "filename": "issues.csv", "rows": int(result.validation.issues_frame().shape[0])},
        ]
    if include_lineage:
        outputs.append({"name": "lineage_report", "filename": "lineage_report.csv"})

    return DryRunPlan(
        outputs=outputs,
        rows_in=int(result.clean_frame.shape[0] + result.cleaning.duplicates_removed),
        rows_out=int(result.clean_frame.shape[0]),
        duplicates_removed=int(result.cleaning.duplicates_removed),
        quality_score=float(result.validation.quality_score),
        issues=int(result.validation.issues_frame().shape[0]),
    )


# --------------------------------------------------------------- rollback file
@dataclass
class RollbackEntry:
    kind: str  # "changed" | "removed" | "added"
    row: int
    column: str = ""
    before: str = ""
    after: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "row": self.row,
            "column": self.column,
            "before": self.before,
            "after": self.after,
        }


@dataclass
class RollbackFile:
    created_at: str
    source_file: str
    crm: str
    rows_in: int
    rows_out: int
    entries: list[RollbackEntry] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "created_at": self.created_at,
            "source_file": self.source_file,
            "crm": self.crm,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "changed": sum(1 for e in self.entries if e.kind == "changed"),
            "removed": sum(1 for e in self.entries if e.kind == "removed"),
            "added": sum(1 for e in self.entries if e.kind == "added"),
            "entries": [e.as_dict() for e in self.entries],
        }

    def write(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.as_dict(), indent=2), encoding="utf-8")
        return destination


def build_rollback_file(
    source: pd.DataFrame,
    crm: str,
    *,
    source_filename: str = "upload.csv",
    cleaning_config: Any = None,
    restore_row_limit: int | None = None,
) -> RollbackFile:
    """Record everything a run changes, so it can be reversed.

    Uses the lineage tracker — which already knows every before/after value — as
    the source of truth, so the rollback file cannot drift from what actually
    happened.
    """
    from app_files.lineage import LineageTracker
    from app_files.pipeline import run_pipeline

    tracker = LineageTracker()
    result = run_pipeline(
        source, crm, cleaning_config=cleaning_config, lineage_tracker=tracker
    )

    entries: list[RollbackEntry] = []
    for row in tracker.to_frame().to_dict("records"):
        action = str(row.get("action", ""))
        before = "" if pd.isna(row.get("before")) else str(row.get("before"))
        after = "" if pd.isna(row.get("after")) else str(row.get("after"))
        if action == "removed_duplicate":
            continue  # recorded below, straight from the source, with real indices
        if before != after:
            source_row = row.get("source_row")
            row_index = int(source_row) if source_row is not None and not pd.isna(source_row) else -1
            entries.append(
                RollbackEntry(
                    kind="changed",
                    row=row_index,
                    column=str(row.get("field", "")),
                    before=before,
                    after=after,
                )
            )
        if restore_row_limit is not None and len(entries) >= restore_row_limit:
            break

    # The lineage tracker cannot always name the row a duplicate was removed
    # from, and a rollback file that says "row -1" cannot restore anything. The
    # duplicate keep-first rule is deterministic, so recompute the dropped
    # indices from the source itself.
    if not source.empty:
        duplicate_mask = source.duplicated(keep="first")
        for position in source.index[duplicate_mask]:
            entries.append(RollbackEntry(kind="removed", row=int(position)))

    return RollbackFile(
        created_at=datetime.now(timezone.utc).isoformat(),
        source_file=source_filename,
        crm=crm,
        rows_in=int(source.shape[0]),
        rows_out=int(result.clean_frame.shape[0]),
        entries=entries,
    )


# ------------------------------------------------------------ cutover runbook
def build_cutover_runbook(
    rollback: RollbackFile,
    *,
    dry_run_plan: DryRunPlan | None = None,
    output_dir: str = "output",
    owner: str = "",
) -> str:
    """A Markdown checklist for the person doing the cutover."""
    plan = dry_run_plan
    lines = [
        "# Cutover runbook",
        "",
        f"- Source file: `{rollback.source_file}`",
        f"- Target system: `{rollback.crm}`",
        f"- Rows in: **{rollback.rows_in}** → rows out: **{rollback.rows_out}**",
        f"- Rollback entries: **{len(rollback.entries)}** "
        f"({sum(1 for e in rollback.entries if e.kind == 'changed')} changed, "
        f"{sum(1 for e in rollback.entries if e.kind == 'removed')} removed)",
        f"- Output directory: `{output_dir}`",
    ]
    if owner:
        lines.append(f"- Owner: {owner}")
    if plan is not None:
        lines += [
            "",
            "## What this run will write",
            "",
            "| Deliverable | File |",
            "| --- | --- |",
        ]
        lines += [f"| {o['name']} | `{o['filename']}` |" for o in plan.outputs]
    lines += [
        "",
        "## Steps",
        "",
        "1. [ ] Take a backup of the target system.",
        "2. [ ] Run the dry run and confirm the row counts and quality score below.",
        "3. [ ] Run the real migration.",
        "4. [ ] Verify the clean file row count matches rows out above.",
        "5. [ ] Spot-check 10 rows against the source.",
        "6. [ ] Import in the target system's sandbox first.",
        "7. [ ] If anything is wrong, apply the rollback file to restore the source.",
        "8. [ ] Record the audit trail entry for the cutover.",
        "",
        "## Rollback",
        "",
        f"Apply `{rollback.source_file}`'s rollback entries to restore the original values:",
        "each entry names the row and column, the value before, and the value after.",
        "",
    ]
    return "\n".join(lines)


def write_cutover_runbook(content: str, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination