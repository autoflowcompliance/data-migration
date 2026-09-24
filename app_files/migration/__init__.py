"""Layer 18 — Migration safety: assess before, roll back after, rehearse first.

Four things a buyer asks before committing to a migration, answered without
touching the frozen pipeline:

- ``analyze_source`` profiles a source and reports what will bite. It is a
  standalone deliverable: no output is written, the pipeline is not modified.
- ``build_rollback`` captures the input exactly as it arrived, so a migration
  can be undone from the file itself.
- ``dry_run`` runs the real pipeline and reports what *would* be produced,
  writing nothing.
- ``generate_runbook`` writes the cutover steps from the actual configuration,
  not from a template someone forgot to update.

Each function calls the existing pipeline rather than reimplementing it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.mappers import load_mapping_config, suggest_mapping
from app_files.mappers.learning import MappingMemory
from app_files.pipeline import PipelineResult, run_pipeline
from app_files.profiling import profile

THIN_COLUMN_THRESHOLD = 0.6
LOW_CONFIDENCE_THRESHOLD = 0.6
LOW_QUALITY_FLOOR = 50.0
MEDIOCRE_QUALITY = 75.0


@dataclass
class SourceIssue:
    """One thing about the source that could complicate a migration."""

    kind: str
    column: str
    detail: str
    severity: str = "warning"

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "column": self.column,
            "detail": self.detail,
            "severity": self.severity,
        }


@dataclass
class PreMigrationReport:
    """What a source looks like before anyone commits to migrating it."""

    source_name: str
    rows: int
    columns: int
    quality: dict[str, Any]
    mapping_confidence: float
    issues: list[SourceIssue] = field(default_factory=list)
    field_map: dict[str, str] = field(default_factory=dict)
    unmapped_columns: list[str] = field(default_factory=list)

    @property
    def blocking(self) -> list[SourceIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def ready(self) -> bool:
        """A source is ready when nothing blocking was found."""
        return not self.blocking

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "rows": self.rows,
            "columns": self.columns,
            "quality": self.quality,
            "mapping_confidence": self.mapping_confidence,
            "ready": self.ready,
            "issues": [issue.as_dict() for issue in self.issues],
            "field_map": dict(self.field_map),
            "unmapped_columns": list(self.unmapped_columns),
        }

    def render(self) -> str:
        lines = [
            f"Pre-migration analysis: {self.source_name}",
            "=" * 60,
            f"Rows: {self.rows}   Columns: {self.columns}",
            f"Overall quality: {self.quality.get('overall', 'n/a')}",
            f"Mapping confidence: {self.mapping_confidence:.2f}",
            f"Ready to migrate: {'yes' if self.ready else 'no'}",
            "",
            "Issues",
            "-" * 60,
        ]
        if not self.issues:
            lines.append("None found.")
        for issue in self.issues:
            lines.append(
                f"[{issue.severity.upper()}] {issue.column}: {issue.detail} ({issue.kind})"
            )
        if self.unmapped_columns:
            lines += [
                "",
                "Projected columns with no target: " + ", ".join(self.unmapped_columns),
            ]
        return "\n".join(lines)


def analyze_source(
    frame: pd.DataFrame,
    crm: str,
    source_name: str = "upload.csv",
    memory: MappingMemory | None = None,
) -> PreMigrationReport:
    """Profile a source and report migration risk. Writes nothing."""
    config = load_mapping_config(crm)
    quality = profile(frame).as_dict()
    memory = memory if memory is not None else MappingMemory()
    suggestion = suggest_mapping(frame, config, memory)
    field_map = {
        entry.source_column: entry.target_field
        for entry in suggestion.fields
        if entry.source_column
    }

    issues: list[SourceIssue] = []
    overall = float(quality.get("overall", 0) or 0)
    if overall < LOW_QUALITY_FLOOR:
        issues.append(
            SourceIssue(
                "low_quality",
                "*",
                f"Overall quality {overall:.0f} is below the migration floor of "
                f"{LOW_QUALITY_FLOOR:.0f}",
                "error",
            )
        )
    elif overall < MEDIOCRE_QUALITY:
        issues.append(
            SourceIssue("low_quality", "*", f"Overall quality {overall:.0f} is mediocre")
        )

    for column in frame.columns:
        series = frame[column]
        name = str(column)
        present = series.notna() & (series.astype(str).str.strip() != "")
        coverage = float(present.mean()) if len(series) else 0.0
        if coverage < THIN_COLUMN_THRESHOLD:
            issues.append(
                SourceIssue(
                    "sparse_column",
                    name,
                    f"Only {coverage:.0%} of values present",
                )
            )
        duplicates = int(series[present].astype(str).duplicated().sum())
        if len(series) and duplicates > len(series) * 0.5:
            issues.append(
                SourceIssue(
                    "low_cardinality",
                    name,
                    f"{duplicates} repeated values; may not be a usable key",
                )
            )
        if name not in field_map:
            issues.append(
                SourceIssue("unmapped", name, "No target field claims this column", "error")
            )

    if suggestion.mean_confidence < LOW_CONFIDENCE_THRESHOLD:
        issues.append(
            SourceIssue(
                "weak_mapping",
                "*",
                f"Mean mapping confidence {suggestion.mean_confidence:.2f} is low",
            )
        )

    return PreMigrationReport(
        source_name=source_name,
        rows=int(len(frame)),
        columns=int(len(frame.columns)),
        quality=quality,
        mapping_confidence=float(suggestion.mean_confidence),
        issues=issues,
        field_map=field_map,
        unmapped_columns=[issue.column for issue in issues if issue.kind == "unmapped"],
    )


def write_pre_migration_report(report: PreMigrationReport, path: str | Path) -> Path:
    """Write the analysis as text and JSON: readable by a person, parseable by CI."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.render(), encoding="utf-8")
    path.with_suffix(".json").write_text(
        json.dumps(report.as_dict(), indent=2), encoding="utf-8"
    )
    return path


@dataclass
class RollbackFile:
    """The original rows, hashed, so a migration can be undone."""

    source_name: str
    path: Path
    rows: int
    columns: int
    checksum: str
    dtypes: dict[str, str] = field(default_factory=dict)
    nulls_path: Path | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "path": str(self.path),
            "rows": self.rows,
            "columns": self.columns,
            "checksum": self.checksum,
            "dtypes": dict(self.dtypes),
            "nulls_path": str(self.nulls_path) if self.nulls_path else None,
        }


def build_rollback(
    frame: pd.DataFrame, directory: str | Path, source_name: str = "source"
) -> RollbackFile:
    """Write a restore file for a migration, with a checksum of its contents.

    CSV cannot tell an empty string from a missing value, so the cells that
    were null are also recorded in a small sidecar. Without it, a source that
    distinguishes "blank" from "absent" cannot be restored faithfully.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = Path(source_name).stem
    target = directory / f"{stem}.rollback.csv"
    nulls = directory / f"{stem}.rollback.nulls.json"
    frame.to_csv(target, index=False)
    null_cells = {
        str(column): [index for index, value in enumerate(frame[column]) if pd.isna(value)]
        for column in frame.columns
        if frame[column].isna().any()
    }
    nulls.write_text(json.dumps({"null_cells": null_cells}), encoding="utf-8")
    return RollbackFile(
        source_name,
        target,
        int(len(frame)),
        int(len(frame.columns)),
        hashlib.sha256(target.read_bytes()).hexdigest(),
        {str(column): str(frame[column].dtype) for column in frame.columns},
        nulls,
    )


def restore_rollback(rollback: RollbackFile) -> pd.DataFrame:
    """Read a rollback file back. Refuses bytes that no longer match.

    Dtypes are reapplied so ``+14155552671`` does not come back as an integer,
    and the null sidecar is reapplied so a missing value does not come back as
    an empty string.
    """
    if not rollback.path.exists():
        raise FileNotFoundError(f"Rollback file is missing: {rollback.path}")
    current = hashlib.sha256(rollback.path.read_bytes()).hexdigest()
    if current != rollback.checksum:
        raise ValueError(
            f"Rollback file {rollback.path.name} has changed since it was written; "
            "refusing to restore from it"
        )
    # Read everything as text without any NA coercion, so nothing is
    # reinterpreted: a phone number keeps its leading +, a blank stays blank,
    # and a boolean string stays a string. Nulls and dtypes are then reapplied
    # from the sidecar and the recorded dtypes.
    restored = pd.read_csv(rollback.path, dtype=str, keep_default_na=False)
    restored = restored[[column for column in rollback.dtypes if column in restored.columns]]

    if rollback.nulls_path and rollback.nulls_path.exists():
        recorded = json.loads(rollback.nulls_path.read_text(encoding="utf-8"))
        for column, indexes in recorded.get("null_cells", {}).items():
            if column in restored.columns:
                restored.loc[indexes, column] = None

    for column, dtype in rollback.dtypes.items():
        if column not in restored.columns or dtype == "object":
            continue
        restored[column] = _restore_dtype(restored[column], dtype)
    return restored


def _restore_dtype(series: pd.Series, dtype: str) -> pd.Series:
    """Cast a text series back to its recorded dtype, preserving nulls.

    ``dtype`` is a string captured at write time, so the ``astype`` overloads
    cannot be resolved statically; the caller has already matched it by prefix.
    """
    nulls = series.isna()
    if dtype.startswith("bool"):
        cast = series.map({"True": True, "False": False})
        return cast.where(~nulls, other=None).astype(dtype)  # type: ignore[call-overload]
    if dtype.startswith("int") or dtype.startswith("uint"):
        numeric = pd.to_numeric(series, errors="coerce")
        return numeric.astype("Int64" if nulls.any() else dtype)  # type: ignore[call-overload]
    if dtype.startswith("float"):
        return pd.to_numeric(series, errors="coerce")
    if dtype.startswith("datetime"):
        return pd.to_datetime(series, errors="coerce")
    return series


@dataclass
class DryRunReport:
    """What a real run would produce, without producing it."""

    would_rename: dict[str, str]
    rows_in: int
    rows_out: int
    duplicates_removed: int
    issues_found: int
    quality_score: float | None
    columns_out: list[str]
    written: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "would_rename": dict(self.would_rename),
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "duplicates_removed": self.duplicates_removed,
            "issues_found": self.issues_found,
            "quality_score": self.quality_score,
            "columns_out": list(self.columns_out),
            "written": self.written,
        }

    def render(self) -> str:
        lines = [
            "Dry run",
            "=" * 60,
            f"Rows in:  {self.rows_in}",
            f"Rows out: {self.rows_out}",
            f"Duplicates removed: {self.duplicates_removed}",
            f"Validation issues: {self.issues_found}",
            f"Quality score: {self.quality_score if self.quality_score is not None else 'n/a'}",
            "",
            "Columns renamed:",
        ]
        if not self.would_rename:
            lines.append("  (none)")
        for source, target in sorted(self.would_rename.items()):
            lines.append(f"  {source} -> {target}")
        lines += ["", "No files were written."]
        return "\n".join(lines)


def dry_run(
    frame: pd.DataFrame,
    crm: str,
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
) -> DryRunReport:
    """Run the real pipeline in memory and report the outcome. Writes nothing."""
    result: PipelineResult = run_pipeline(
        frame,
        crm=crm,
        project_name=project_name,
        source_filename=source_filename,
        run_structural_check=False,
    )
    summary = result.summary()
    return DryRunReport(
        would_rename=_rename_map(result),
        rows_in=int(summary.get("rows_in", len(frame))),
        rows_out=int(summary.get("rows_out", len(result.clean_frame))),
        duplicates_removed=int(summary.get("duplicates_removed", 0)),
        issues_found=len(result.validation.issues),
        quality_score=_quality_score(result),
        columns_out=[str(column) for column in result.mapping.frame.columns],
        written=False,
    )


def _rename_map(result: PipelineResult) -> dict[str, str]:
    renames: dict[str, str] = {}
    for entry in result.mapping.mappings:
        source = str(entry.get("source_column", "") or "")
        target = str(entry.get("target_field", "") or "")
        if source and target and source != target:
            renames[source] = target
    return renames


def _quality_score(result: PipelineResult) -> float | None:
    try:
        return float(result.validation.quality_score)
    except Exception:  # noqa: BLE001 - a missing score is not a failed dry run
        return None


@dataclass
class Runbook:
    """Cutover steps generated from the actual configuration."""

    project_name: str
    crm: str
    steps: list[str]
    source_name: str = "upload.csv"
    output_path: str = "output/"
    schedule: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "crm": self.crm,
            "source_name": self.source_name,
            "output_path": self.output_path,
            "schedule": self.schedule,
            "steps": list(self.steps),
        }

    def render(self) -> str:
        numbered = [f"{index}. {step}" for index, step in enumerate(self.steps, 1)]
        return "\n".join([f"Cutover runbook: {self.project_name}", "=" * 60, *numbered])

    def write(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path


def generate_runbook(
    crm: str,
    project_name: str = "Data migration",
    source_name: str = "upload.csv",
    output_path: str = "output/",
    schedule: str | None = None,
) -> Runbook:
    """Generate the cutover steps from the real config, not a static template."""
    config = load_mapping_config(crm)
    target_fields = [target.name for target in config.fields]
    steps = [
        f"Confirm the source file is {source_name} and matches the expected schema.",
        "Run the pre-migration analysis and confirm no blocking issues remain.",
        f"Take a rollback copy of {source_name} before any write.",
        "Run the dry run and check the row counts and rename list.",
        f"Migrate {source_name} into {config.crm} ({crm}).",
        f"Confirm the {len(target_fields)} target fields below are populated:",
    ]
    steps += [f"   - {name}" for name in target_fields]
    steps += [
        f"Write deliverables to {output_path}.",
        "Verify each deliverable against its signature manifest.",
    ]
    if schedule:
        steps.append(f"Confirm the recurring job is registered for {schedule}.")
    steps += [
        "Record the run ID in the audit log.",
        f"If anything is wrong, restore {source_name} from the rollback copy and stop.",
    ]
    return Runbook(
        project_name=project_name,
        crm=config.crm,
        steps=steps,
        source_name=source_name,
        output_path=output_path,
        schedule=schedule,
    )
