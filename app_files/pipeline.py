"""End-to-end orchestration: clean, map, validate, report."""

from __future__ import annotations

import dataclasses
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.cleaners import CleaningConfig, CleaningResult, clean_data
from app_files.lineage.tracker import (
    LINEAGE_ID,
    LineageTracker,
    attach_lineage_ids,
    strip_lineage_ids,
)
from app_files.mappers import MappingConfig, MappingResult, load_mapping_config, map_data
from app_files.reporters import render_qa_report
from app_files.validators import ValidationReport, frictionless_summary, validate_data


@dataclass
class PipelineResult:
    cleaning: CleaningResult
    mapping: MappingResult
    validation: ValidationReport
    qa_report_html: str
    mapping_config: MappingConfig
    lineage: LineageTracker | None = None
    """Populated only when ``run_pipeline(..., lineage_tracker=...)`` is passed."""

    @property
    def clean_frame(self) -> pd.DataFrame:
        return self.mapping.frame

    def mapping_log(self) -> pd.DataFrame:
        return self.mapping.mapping_log()

    def cleaning_log(self) -> pd.DataFrame:
        return self.cleaning.actions_frame()

    def lineage_log(self) -> pd.DataFrame:
        """The transformation log; empty when lineage tracking was not enabled."""
        if self.lineage is None:
            return pd.DataFrame(
                columns=["source_row", "output_row", "field", "before", "after", "action"]
            )
        return self.lineage.to_frame()

    def summary(self) -> dict[str, Any]:
        return {
            "rows_in": self.cleaning.rows_in,
            "rows_out": len(self.clean_frame),
            "duplicates_removed": self.cleaning.duplicates_removed,
            **self.validation.summary(),
        }


def _trace_cleaning(
    tracker: LineageTracker, source: pd.DataFrame, cleaned: pd.DataFrame
) -> None:
    """Record every cell the cleaner changed, plus every row it dropped."""
    if LINEAGE_ID not in cleaned.columns:
        return
    for column in source.columns:
        if column not in cleaned.columns:
            continue
        tracker.record_frame_diff(
            source, cleaned, field_name=column, action="clean", id_column=LINEAGE_ID
        )
    removed = sorted(set(source[LINEAGE_ID]) - set(cleaned[LINEAGE_ID]))
    if removed:
        tracker.record_removed_rows(
            source[source[LINEAGE_ID].isin(removed)], removed, action="removed_duplicate"
        )


def _trace_mapping(
    tracker: LineageTracker, cleaned: pd.DataFrame, mapping: MappingResult
) -> None:
    """Record every value the mapper wrote, linked back to its source row."""
    ids = cleaned[LINEAGE_ID] if LINEAGE_ID in cleaned.columns else pd.Series(cleaned.index)
    for entry in mapping.mappings:
        target = str(entry.get("target_field") or "")
        origin = entry.get("source_column") or ""
        transform = entry.get("transform") or "map"
        if not target or target not in mapping.frame.columns:
            continue
        before_series = (
            cleaned[origin]
            if origin in cleaned.columns
            else pd.Series([""] * len(cleaned), index=cleaned.index)
        )
        for index in mapping.frame.index:
            tracker.record(
                field_name=target,
                before=before_series.get(index, ""),
                after=mapping.frame.at[index, target],
                action=f"map:{transform}",
                source_row=int(ids.get(index, index)),
                output_row=int(index),
            )


def run_pipeline(
    source: pd.DataFrame,
    crm: str,
    cleaning_config: CleaningConfig | None = None,
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
    run_structural_check: bool = True,
    lineage_tracker: LineageTracker | None = None,
) -> PipelineResult:
    """Run clean -> map -> validate -> report.

    Passing ``lineage_tracker`` enables per-value lineage logging. When it is
    omitted — the default, and how the existing CLI and web UI call this — the
    pipeline behaves exactly as it always has.
    """
    cleaning_config = cleaning_config or CleaningConfig()
    mapping_config = load_mapping_config(crm)

    working = source
    if lineage_tracker is not None:
        working = attach_lineage_ids(source)
        # Duplicate detection must ignore the synthetic lineage column, or every
        # row would look unique and no duplicate would ever be removed.
        cleaning_config = dataclasses.replace(
            cleaning_config, duplicate_subset=list(source.columns)
        )

    cleaning = clean_data(working, cleaning_config)
    mapping = map_data(cleaning.frame, mapping_config)

    if lineage_tracker is not None:
        _trace_cleaning(lineage_tracker, working, cleaning.frame)
        _trace_mapping(lineage_tracker, cleaning.frame, mapping)
        # Never leak the helper column into downstream consumers.
        cleaning.frame = strip_lineage_ids(cleaning.frame)

    validation = validate_data(
        mapping.frame, mapping_config, cleaning_config.date_format, cleaning_config.default_region
    )

    structural: dict[str, Any] | None = None
    if run_structural_check:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapped.csv"
            mapping.frame.to_csv(path, index=False)
            structural = frictionless_summary(path)

    html = render_qa_report(
        report=validation,
        mapping_log=mapping.mapping_log(),
        cleaning_log=cleaning.actions_frame(),
        mapped=mapping.frame,
        project_name=project_name,
        source_filename=source_filename,
        crm=mapping_config.crm,
        structural=structural,
    )
    return PipelineResult(
        cleaning, mapping, validation, html, mapping_config, lineage=lineage_tracker
    )


def write_deliverables(
    result: PipelineResult,
    outdir: str | Path = "output",
    output_format: str = "csv",
    include_reports: bool = True,
    include_lineage: bool = True,
) -> dict[str, Path]:
    """Write a run's outputs, honouring the ``output_format`` choice.

    The clean data is written in the requested format; the logs, issues CSV and
    HTML reports are always written as CSV/HTML because they are meant to be
    read, not re-imported. Returns a mapping of deliverable name to path.
    """
    from app_files.output import write_any

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    written["clean_data"] = write_any(
        result.clean_frame, outdir / "clean_data", output_format
    )
    if include_reports:
        written["qa_report"] = _write_text(outdir / "qa_report.html", result.qa_report_html)
        written["mapping_log"] = _write_text_csv(outdir / "mapping_log.csv", result.mapping_log())
        written["cleaning_log"] = _write_text_csv(
            outdir / "cleaning_log.csv", result.cleaning_log()
        )
        written["issues"] = _write_text_csv(
            outdir / "issues.csv", result.validation.issues_frame()
        )
    if include_lineage:
        from app_files.lineage import write_lineage_report

        written["lineage_report"] = write_lineage_report(
            result.lineage if result.lineage is not None else LineageTracker(enabled=False),
            outdir / "lineage_report.csv",
        )
    return written


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_text_csv(path: Path, frame: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def run_pipeline_traced(
    source: pd.DataFrame, crm: str, **kwargs: Any
) -> tuple[PipelineResult, pd.DataFrame]:
    """Run the pipeline with lineage enabled and return ``(result, lineage_log)``."""
    tracker = LineageTracker()
    result = run_pipeline(source, crm, lineage_tracker=tracker, **kwargs)
    return result, tracker.to_frame()
