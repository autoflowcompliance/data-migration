"""UI-independent run logic for DataFlow.

Streamlit pages are hard to unit-test, so every decision worth getting right
lives here as a plain function over plain data: reading an upload, running the
migration under the active licence limits, and reconciling a bank statement.

The migration path deliberately goes through
:func:`app_files.interface.web.state.run_migration` rather than calling
``run_pipeline`` directly. That function is where the demo limits are applied
(row cap, file size, CSV-only, watermark), so a page calling the pipeline
itself would quietly ignore the licence and hand back an unlimited,
unwatermarked result. One call site, one thing to audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.cleaners import CleaningConfig
from app_files.ingestion import available_extensions
from app_files.interface.web.state import read_upload, run_migration, sample_path
from app_files.licensing import Limits, check_file_size
from app_files.mappers import available_crms
from app_files.pipeline import PipelineResult

JOB_CRM = "CRM export"
JOB_BANK = "Bank reconciliation"
JOB_TYPES: tuple[str, ...] = (JOB_CRM, JOB_BANK)

STEPS: tuple[str, ...] = ("Upload", "Configure", "Process", "Review")


@dataclass(frozen=True)
class Sample:
    """A bundled file a visitor can run without having one of their own."""

    key: str
    label: str
    filename: str
    crm: str


# Only the CRM samples: the bank ones are a different job type with their own
# column contract, and this menu drives the "try a sample" shortcut in the CRM
# branch. The file names are resolved by
# :func:`app_files.interface.web.state.sample_path`, so both interfaces agree
# on where samples live.
SAMPLE_MENU: tuple[Sample, ...] = (
    Sample("messy_contacts", "Messy CRM contacts (CSV)", "messy_contacts.csv", "hubspot"),
    Sample("employee_records", "Employee records (CSV)", "employee_records.csv", "hubspot"),
    Sample("messy_contacts_json", "Contacts from a JSON export", "messy_contacts.json", "hubspot"),
    Sample("messy_contacts_xlsx", "Contacts from an Excel workbook", "messy_contacts.xlsx", "hubspot"),
)


def available_samples() -> list[Sample]:
    """The sample menu, filtered to files actually present on disk."""
    return [sample for sample in SAMPLE_MENU if sample_path(sample.filename).is_file()]


def sample_bytes(sample: Sample) -> bytes:
    """Read a bundled sample as bytes, so it takes the same path as an upload."""
    return sample_path(sample.filename).read_bytes()


DIMENSIONS: tuple[str, ...] = (
    "completeness",
    "uniqueness",
    "validity",
    "consistency",
    "timeliness",
)

# The bank reconciler is column-name driven, so the defaults have to match the
# bundled samples; a user with different headers overrides them in step 1.
DEFAULT_DATE_COLUMN = "Date"
DEFAULT_AMOUNT_COLUMN = "Amount"


@dataclass
class MigrationRun:
    """A finished CRM migration, ready to render."""

    result: PipelineResult
    summary: dict[str, Any]
    profile: Any
    source_name: str

    @property
    def rows_out(self) -> int:
        return int(self.summary.get("rows_out", 0))

    @property
    def quality_score(self) -> float:
        return float(self.summary.get("quality_score", 0.0))

    def dimension_scores(self) -> dict[str, float]:
        """The five quality dimensions, missing ones omitted rather than faked."""
        scores = getattr(self.profile, "scores", None) or {}
        return {name: float(scores[name]) for name in DIMENSIONS if name in scores}

    def downloads(self) -> list[tuple[str, str, bytes | str, str, str]]:
        """``(label, icon, payload, filename, mime)`` for each available artefact."""
        clean_csv = self.result.clean_frame.to_csv(index=False)
        artefacts: list[tuple[str, str, bytes | str, str, str]] = [
            ("Clean CSV", "📄", clean_csv, "clean_data.csv", "text/csv"),
            ("QA Report", "📊", self.result.qa_report_html, "qa_report.html", "text/html"),
            (
                "Mapping Log",
                "🗺️",
                self.result.mapping_log().to_csv(index=False),
                "mapping_log.csv",
                "text/csv",
            ),
        ]
        lineage = self.result.lineage_log()
        if not lineage.empty:
            artefacts.append(
                ("Lineage", "🧬", lineage.to_csv(index=False), "lineage.csv", "text/csv")
            )
        return artefacts


def supported_types() -> list[str]:
    """Extensions the file uploader should accept, without the leading dot."""
    return [extension.lstrip(".") for extension in available_extensions()]


def crm_choices() -> list[str]:
    """Target configs on disk, for the selector."""
    return available_crms()


def file_size(filename: str, data: bytes) -> tuple[int, str]:
    """A human-readable size for an upload, plus its extension label."""
    if len(data) < 1024:
        size = f"{len(data)} B"
    elif len(data) < 1024 * 1024:
        size = f"{len(data) / 1024:.0f} KB"
    else:
        size = f"{len(data) / (1024 * 1024):.1f} MB"
    return len(data), f"{Path(filename).name} · {size}"


def migration_error_message(exc: Exception) -> str:
    """Plain-language text for the failures a user can actually cause.

    A bad extension or an over-size file is the user's doing and deserves a
    sentence they can act on; anything else is a bug and keeps its own text.
    """
    if isinstance(exc, ValueError) and "not a supported file type" in str(exc):
        return str(exc)
    if type(exc).__name__ == "LimitExceededError":
        return str(exc)
    return f"Something went wrong while processing this file: {exc}"


def build_cleaning_config(
    remove_duplicates: bool = True,
    date_first: bool = False,
    default_region: str = "US",
) -> CleaningConfig:
    """The cleaning options exposed in step 1."""
    return CleaningConfig(
        remove_duplicates=bool(remove_duplicates),
        date_first=bool(date_first),
        default_region=(default_region or "US").upper(),
    )


def run_crm_migration(
    data: bytes,
    filename: str,
    crm: str,
    limits: Limits,
    cleaning_config: CleaningConfig | None = None,
) -> MigrationRun:
    """Ingest an upload and migrate it under ``limits``.

    The size check runs before ingestion, matching the NiceGUI upload route:
    reading a file we are about to reject is wasted work, and in demo mode it
    is work an anonymous visitor gets to trigger.

    Raises the ingestion/limit errors unchanged; callers turn them into
    messages with :func:`migration_error_message`.
    """
    check_file_size(len(data), limits)
    source = read_upload(data, filename)
    outcome = run_migration(
        source,
        source_name=filename,
        template=crm,
        limits=limits,
        enable_lineage=limits.lineage,
    )
    return MigrationRun(
        result=outcome.pipeline,
        summary=outcome.summary,
        profile=outcome.profile,
        source_name=filename,
    )


def run_bank_reconciliation(
    bank_data: bytes,
    ledger_data: bytes,
    limits: Limits,
    bank_date_col: str = DEFAULT_DATE_COLUMN,
    bank_amount_col: str = DEFAULT_AMOUNT_COLUMN,
    ledger_date_col: str = DEFAULT_DATE_COLUMN,
    ledger_amount_col: str = DEFAULT_AMOUNT_COLUMN,
    tolerance_days: int = 2,
) -> dict[str, Any]:
    """Reconcile a bank statement against a ledger.

    The demo file-size cap is enforced here. The row cap is not: the reconciler
    reads the uploaded bytes itself and returns frames rather than taking them,
    so there is no frame to truncate before matching — truncating mid-reconcile
    would invent missing transactions. Demo mode therefore bounds the upload
    size, which is what keeps a hosted demo cheap.

    The reconciler is imported lazily because it pulls in pdfplumber for PDF
    statements, and a CSV-only install should not pay for that on import.
    """
    from app_files.licensing import check_file_size  # noqa: PLC0415 — lazy by design
    from app_files.services.bank_reconciliation.reconciler import run_reconciliation

    check_file_size(len(bank_data), limits)
    check_file_size(len(ledger_data), limits)

    return run_reconciliation(
        bank_data,
        ledger_data,
        bank_date_col,
        bank_amount_col,
        ledger_date_col,
        ledger_amount_col,
        int(tolerance_days),
    )


def reconciliation_counts(result: dict[str, Any]) -> dict[str, int]:
    summary = result.get("summary", {})
    return {
        "matched": int(summary.get("matched", 0)),
        "missing_from_books": int(summary.get("missing_from_books", 0)),
        "never_cleared": int(summary.get("recorded_but_never_cleared", 0)),
    }


def reconciliation_downloads(
    result: dict[str, Any],
) -> list[tuple[str, str, bytes | str, str, str]]:
    """``(label, icon, payload, filename, mime)`` for the reconciliation output."""
    return [
        (
            "Missing from books",
            "🔍",
            result["bank_only"].to_csv(index=False),
            "missing_from_books.csv",
            "text/csv",
        ),
        (
            "Never cleared",
            "🔍",
            result["ledger_only"].to_csv(index=False),
            "never_cleared.csv",
            "text/csv",
        ),
    ]


def empty_frame_guard(value: Any) -> pd.DataFrame | None:
    """Return ``value`` when it is a non-empty frame, else ``None``."""
    if isinstance(value, pd.DataFrame) and not value.empty:
        return value
    return None