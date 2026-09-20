"""UI-independent run logic: everything the pages do that is worth testing.

NiceGUI pages are hard to unit-test and easy to make untestable. So each page
builds widgets, and every decision worth getting right — applying demo limits,
profiling, running rules, branding the report, deciding which formats are
offered — lives here as a plain function over plain data.

``apply_limits`` in the licensing layer answers "what may this install do?".
This module is the only place that answer is acted on for a single run, so
there is one path to audit rather than one per page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.branding import Branding, inject_branding, inject_demo_watermark
from app_files.ingestion import available_extensions, read_any
from app_files.licensing import (
    Limits,
    RowLimitResult,
    apply_row_limit,
    check_file_size,
)
from app_files.lineage import LineageTracker
from app_files.mappers import available_crms
from app_files.pipeline import PipelineResult, run_pipeline
from app_files.profiling import Profile, profile, render_qa_report_with_profile
from app_files.rules import RuleConfigError, RuleResult, run_rules_for

from app_files.interface.web.session import publish_report as store_report

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"

SAMPLE_MENU: tuple[dict[str, str], ...] = (
    {
        "key": "messy_contacts",
        "label": "Messy CRM contacts (CSV)",
        "file": "messy_contacts.csv",
        "template": "hubspot",
    },
    {
        "key": "employee_records",
        "label": "Employee records (CSV)",
        "file": "employee_records.csv",
        "template": "hubspot",
    },
    {
        "key": "messy_contacts_json",
        "label": "Contacts from a JSON export",
        "file": "messy_contacts.json",
        "template": "hubspot",
    },
    {
        "key": "bank_statement",
        "label": "Bank statement (PDF)",
        "file": "bank_statement.pdf",
        "template": "bank_reconciliation",
    },
    {
        "key": "ledger",
        "label": "General ledger (CSV)",
        "file": "ledger.csv",
        "template": "bank_reconciliation",
    },
)


@dataclass
class RunOutcome:
    """Everything a results page needs, computed in one go."""

    pipeline: PipelineResult
    profile: Profile
    limits: Limits
    row_limit: RowLimitResult
    qa_report_html: str
    rules: RuleResult | None = None
    rules_error: str | None = None
    source_name: str = "upload"
    notes: list[str] = field(default_factory=list)
    report_token: str | None = None
    """Address of the rendered report in the session store.

    The report is fetched over HTTP rather than embedded in the element tree,
    because a full QA report is far larger than a WebSocket message.
    """

    @property
    def summary(self) -> dict[str, Any]:
        return self.pipeline.summary()

    @property
    def score(self) -> float:
        return self.profile.overall

    @property
    def issues(self) -> pd.DataFrame:
        """Validation issues plus any rule failures, in one frame."""
        frame = self.pipeline.validation.issues_frame()
        if self.rules is None or not self.rules.issues:
            return frame
        rule_rows = pd.DataFrame(
            [
                {
                    "row": issue.row,
                    "field": issue.field,
                    "check": issue.check,
                    "severity": issue.severity,
                    "message": issue.message,
                }
                for issue in self.rules.issues
            ]
        )
        if frame.empty:
            return rule_rows
        return pd.concat([frame, rule_rows], ignore_index=True)

    def warnings(self) -> list[str]:
        notes: list[str] = []
        if self.row_limit.truncated:
            notes.append(self.row_limit.note)
        if self.limits.watermark:
            notes.append(
                "Demo mode: the report is watermarked and limited to CSV output. "
                "A licence removes these restrictions."
            )
        return notes


def sample_path(name: str) -> Path:
    """Resolve a sample file by its basename, or its key from :data:`SAMPLE_MENU`."""
    for entry in SAMPLE_MENU:
        if entry["key"] == name:
            return SAMPLES_DIR / entry["file"]
    return SAMPLES_DIR / name


def available_samples() -> list[dict[str, str]]:
    """The sample menu, filtered to files actually present on disk."""
    return [dict(entry) for entry in SAMPLE_MENU if sample_path(entry["file"]).is_file()]


def load_sample(name: str) -> pd.DataFrame:
    """Read one of the bundled sample files."""
    return read_any(sample_path(name))


def read_upload(data: bytes, filename: str) -> pd.DataFrame:
    """Read an upload, checking its extension before size is enforced."""
    extension = Path(filename).suffix.lower()
    if extension not in available_extensions():
        raise ValueError(
            f"'{extension or filename}' is not a supported file type. "
            f"Supported: {', '.join(available_extensions())}"
        )
    return read_any(data, filename=filename)


def run_migration(
    source: pd.DataFrame,
    source_name: str,
    template: str,
    limits: Limits,
    branding: Branding | None = None,
    enable_rules: bool = True,
    enable_lineage: bool | None = None,
    run_structural_check: bool = True,
) -> RunOutcome:
    """Run the core pipeline under the active limits and build the report.

    Args:
        source: the already-ingested frame.
        source_name: filename shown in the report.
        template: config name, e.g. ``hubspot``.
        limits: the active :class:`Limits`; demo restrictions are enforced here.
        branding: white-label settings; ignored when the limits forbid branding.
        enable_lineage: ``None`` uses the mode's default.
        run_structural_check: pass through to the pipeline.
    """
    row_limit = apply_row_limit(source, limits)
    track_lineage = limits.lineage if enable_lineage is None else enable_lineage
    tracker = LineageTracker() if track_lineage else None

    result = run_pipeline(
        row_limit.frame,
        crm=template,
        project_name=f"Migration — {Path(source_name).stem}",
        source_filename=source_name,
        run_structural_check=run_structural_check,
        lineage_tracker=tracker,
    )
    profile_result = profile(result.clean_frame)

    html = render_qa_report_with_profile(
        result.qa_report_html, result.clean_frame, profile_result
    )
    # Branding is a licensed feature; in demo mode the default branding is
    # applied anyway so no `{{BRAND_*}}` placeholder ever leaks into a
    # finished report as literal text.
    html = inject_branding(html, branding if limits.branding else Branding())
    if limits.watermark:
        html = inject_demo_watermark(html, row_limit.note)

    rules: RuleResult | None = None
    rules_error: str | None = None
    if enable_rules:
        try:
            rules = run_rules_for(result.clean_frame, template)
        except RuleConfigError as exc:
            rules_error = str(exc)

    outcome = RunOutcome(
        pipeline=result,
        profile=profile_result,
        limits=limits,
        row_limit=row_limit,
        qa_report_html=html,
        rules=rules,
        rules_error=rules_error,
        source_name=source_name,
    )
    outcome.report_token = store_report(html)
    outcome.notes.extend(outcome.warnings())
    if rules is not None and rules.total_failures:
        outcome.notes.append(
            f"{rules.total_failures} rule failure(s) across {rules.rules_run} rule(s)."
        )
    return outcome


def allowed_formats(limits: Limits) -> list[str]:
    """Output formats the current mode offers, in a stable display order."""
    order = ["csv", "excel", "json", "sql"]
    return [fmt for fmt in order if limits.allows_format(fmt)]


def format_choices(limits: Limits) -> list[str]:
    """Display labels for the format selector."""
    return [fmt.title() for fmt in allowed_formats(limits)]


def templates_on_disk() -> list[str]:
    """Every config the mapper can load, for the templates page."""
    return available_crms()