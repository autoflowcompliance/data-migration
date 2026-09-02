"""End-to-end orchestration: clean, map, validate, report."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.cleaners import CleaningConfig, CleaningResult, clean_data
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

    @property
    def clean_frame(self) -> pd.DataFrame:
        return self.mapping.frame

    def mapping_log(self) -> pd.DataFrame:
        return self.mapping.mapping_log()

    def cleaning_log(self) -> pd.DataFrame:
        return self.cleaning.actions_frame()

    def summary(self) -> dict[str, Any]:
        return {
            "rows_in": self.cleaning.rows_in,
            "rows_out": len(self.clean_frame),
            "duplicates_removed": self.cleaning.duplicates_removed,
            **self.validation.summary(),
        }


def run_pipeline(
    source: pd.DataFrame,
    crm: str,
    cleaning_config: CleaningConfig | None = None,
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
    run_structural_check: bool = True,
) -> PipelineResult:
    cleaning_config = cleaning_config or CleaningConfig()
    mapping_config = load_mapping_config(crm)

    cleaning = clean_data(source, cleaning_config)
    mapping = map_data(cleaning.frame, mapping_config)
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
    return PipelineResult(cleaning, mapping, validation, html, mapping_config)
