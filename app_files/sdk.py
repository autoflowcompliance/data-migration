"""A small Python SDK over the pipeline.

The SDK exists so a buyer's own script does not have to know which module each
capability lives in. One object, ``Migration``, exposes the whole workflow that
the CLI and the web UI drive, and returns the artifacts rather than printing:

    from app_files.sdk import Migration

    run = Migration.from_file("contacts.csv", crm="hubspot")
    result = run.execute()
    result.clean_frame           # pandas DataFrame
    result.qa_report_html        # the HTML report
    result.summary()             # rows, quality score, issues

It is deliberately thin: every method calls the same functions the rest of the
tool calls, so the SDK cannot drift into a second implementation. The three
extra conveniences over calling those functions directly are:

* a single ``Migration`` object holding the common options,
* ``execute()`` returning one result object with every artifact attached,
* ``write()`` writing the full set of deliverables in one call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.cleaners import load_cleaning_config
from app_files.ingestion import read_any
from app_files.lineage import LineageTracker
from app_files.pipeline import PipelineResult, run_pipeline, write_deliverables


class SDKError(ValueError):
    """Raised for an SDK call the underlying pipeline cannot act on."""


@dataclass
class RunResult:
    """Everything one run produced, in one object."""

    result: PipelineResult
    tracker: LineageTracker | None = None
    written: dict[str, Path] = field(default_factory=dict)

    @property
    def clean_frame(self) -> pd.DataFrame:
        return self.result.clean_frame

    @property
    def qa_report_html(self) -> str:
        return self.result.qa_report_html

    @property
    def raw(self) -> PipelineResult:
        """The underlying pipeline result, for callers that want everything."""
        return self.result

    def mapping_log(self) -> pd.DataFrame:
        return self.result.mapping_log()

    def cleaning_log(self) -> pd.DataFrame:
        return self.result.cleaning_log()

    def issues(self) -> pd.DataFrame:
        return self.result.validation.issues_frame()

    def lineage_log(self) -> pd.DataFrame:
        return self.result.lineage_log()

    def summary(self) -> dict[str, Any]:
        return self.result.summary()

    @property
    def valid(self) -> bool:
        return self.result.validation.valid

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "valid": self.valid,
            "written": {name: str(path) for name, path in self.written.items()},
        }


class Migration:
    """A pipeline run, configured once and executed explicitly."""

    def __init__(
        self,
        source: pd.DataFrame,
        *,
        crm: str,
        cleaning_config: Any = None,
        project_name: str = "Data migration",
        source_filename: str = "",
        lineage: bool = False,
        output_format: str = "csv",
    ) -> None:
        if source is None:
            raise SDKError("A source frame is required.")
        if not crm:
            raise SDKError("A target config name (crm) is required.")
        self.source = source
        self.crm = crm
        self.cleaning_config = cleaning_config
        self.project_name = project_name
        self.source_filename = source_filename
        self.lineage = lineage
        self.output_format = output_format

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        *,
        crm: str,
        cleaning_config_path: str | Path | None = None,
        lineage: bool = False,
        output_format: str = "csv",
        **kwargs: Any,
    ) -> "Migration":
        """Read any supported file (CSV, Excel, PDF, JSON) and build a run."""
        source_path = Path(path)
        if not source_path.exists():
            raise SDKError(f"No such file: {source_path}.")
        frame = read_any(source_path)
        cleaning = load_cleaning_config(cleaning_config_path) if cleaning_config_path else None
        return cls(
            frame,
            crm=crm,
            cleaning_config=cleaning,
            source_filename=source_path.name,
            lineage=lineage,
            output_format=output_format,
            **kwargs,
        )

    def execute(self) -> RunResult:
        """Run the pipeline. Lineage is opt-in, matching the core function."""
        tracker = LineageTracker() if self.lineage else None
        result = run_pipeline(
            source=self.source,
            crm=self.crm,
            cleaning_config=self.cleaning_config,
            project_name=self.project_name,
            source_filename=self.source_filename,
            lineage_tracker=tracker,
        )
        return RunResult(result=result, tracker=tracker)

    def run_and_write(self, outdir: str | Path = "output") -> RunResult:
        """Run, then write every deliverable, in one call."""
        run = self.execute()
        run.written = write_deliverables(
            run.result, outdir=outdir, output_format=self.output_format
        )
        return run

    def dry_run(self) -> dict[str, Any]:
        """What a run would write, without running the pipeline for real."""
        from app_files.safety import dry_run as _dry_run

        plan = _dry_run(self.source, self.crm, output_format=self.output_format)
        return plan.as_dict()

    def privacy_report(self) -> dict[str, Any]:
        """The personal-data columns this source carries."""
        from app_files.privacy import detect_personal_data

        return detect_personal_data(self.source).as_dict()


class Client:
    """The entry point a script starts from.

    Holds defaults so a batch of runs does not repeat them:

        client = Client(crm="hubspot", lineage=True)
        for path in paths:
            print(client.migrate(path).summary())
    """

    def __init__(self, *, crm: str, lineage: bool = False, output_format: str = "csv",
                 project_name: str = "Data migration") -> None:
        self.crm = crm
        self.lineage = lineage
        self.output_format = output_format
        self.project_name = project_name

    def migrate(self, source: str | Path | pd.DataFrame, **kwargs: Any) -> RunResult:
        if isinstance(source, pd.DataFrame):
            run = Migration(
                source,
                crm=kwargs.pop("crm", self.crm),
                lineage=kwargs.pop("lineage", self.lineage),
                output_format=kwargs.pop("output_format", self.output_format),
                project_name=kwargs.pop("project_name", self.project_name),
                **kwargs,
            )
        else:
            run = Migration.from_file(
                source,
                crm=kwargs.pop("crm", self.crm),
                lineage=kwargs.pop("lineage", self.lineage),
                output_format=kwargs.pop("output_format", self.output_format),
                project_name=kwargs.pop("project_name", self.project_name),
                **kwargs,
            )
        return run.execute()

    def migrate_many(self, sources: list[Any], **kwargs: Any) -> list[RunResult]:
        return [self.migrate(source, **kwargs) for source in sources]