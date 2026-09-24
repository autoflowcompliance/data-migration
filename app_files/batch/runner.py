"""Process a folder of files through the core pipeline, one at a time.

This layer is deliberately thin: it walks a directory, hands each supported
file to the frozen ``run_pipeline`` via ``read_any``, and records what
happened. A failure on one file is captured as a failed row in the summary
rather than aborting the run — a bookkeeper's inbox routinely contains one
unreadable scan, and losing the other forty results to it would make the
feature useless.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app_files.ingestion import available_extensions, read_any
from app_files.lineage import LineageTracker
from app_files.pipeline import run_pipeline, write_deliverables
from app_files.profiling import profile

ProgressCallback = Callable[[int, int, str], Any]
"""``(index, total, filename)`` — called before each file is processed."""


@dataclass
class BatchItem:
    """The outcome for a single file in the batch."""

    file: str
    status: str
    rows_in: int = 0
    rows_out: int = 0
    score: float = 0.0
    errors: int = 0
    warnings: int = 0
    rule_failures: int = 0
    rules_run: int = 0
    error: str | None = None
    output_dir: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    def as_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "status": self.status,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "score": self.score,
            "errors": self.errors,
            "warnings": self.warnings,
            "rule_failures": self.rule_failures,
            "rules_run": self.rules_run,
            "error": self.error or "",
            "output_dir": self.output_dir or "",
        }


@dataclass
class BatchResult:
    """Every item's outcome plus the totals the dashboard needs."""

    input_dir: str
    output_dir: str
    template: str
    items: list[BatchItem] = field(default_factory=list)

    @property
    def processed(self) -> int:
        return len(self.items)

    @property
    def succeeded(self) -> int:
        return sum(1 for item in self.items if item.ok)

    @property
    def failed(self) -> int:
        return self.processed - self.succeeded

    @property
    def total_rows_out(self) -> int:
        return sum(item.rows_out for item in self.items if item.ok)

    @property
    def average_score(self) -> float:
        scores = [item.score for item in self.items if item.ok]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 1)

    def as_dict(self) -> dict[str, Any]:
        return {
            "input_dir": self.input_dir,
            "output_dir": self.output_dir,
            "template": self.template,
            "processed": self.processed,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "total_rows_out": self.total_rows_out,
            "average_score": self.average_score,
            "results": [item.as_dict() for item in self.items],
        }


def supported_files(input_dir: str | Path) -> list[Path]:
    """Every supported file directly inside ``input_dir``, in stable order."""
    directory = Path(input_dir)
    if not directory.is_dir():
        return []
    extensions = set(available_extensions())
    is_supported = lambda path: path.is_file() and path.suffix.lower() in extensions  # noqa: E731
    return sorted((path for path in directory.iterdir() if is_supported(path)), key=lambda p: p.name.lower())


def process_one(
    path: Path,
    template: str,
    out_dir: Path,
    output_format: str = "csv",
    project_name: str = "Batch run",
) -> BatchItem:
    """Run one file through the pipeline and write its deliverables.

    Per-file directories keep a batch output readable: ``outbox/client_a/``
    holds that file's clean data and reports, and the combined summary sits at
    the top level.
    """
    try:
        source = read_any(path)
        if source.empty:
            # An empty or headerless file reads "successfully" into an empty
            # frame. Reporting that as ok would put a green tick next to a
            # file that produced nothing, which is worse than a red one.
            return BatchItem(
                file=path.name,
                status="failed",
                error="No rows could be read from this file.",
            )
        result = run_pipeline(
            source,
            crm=template,
            project_name=f"{project_name} — {path.stem}",
            source_filename=path.name,
            lineage_tracker=LineageTracker(),
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        write_deliverables(result, out_dir, output_format=output_format)

        from app_files.rules.binding import apply_configured_rules

        # Config rules were previously a UI-only step, so a batch run's issues
        # CSV and report omitted every rule failure. Apply them now and rewrite
        # the two artifacts rendered from the issue list, so a batch file shows
        # what the single-file CLI shows.
        built = apply_configured_rules(
            result, template,
            project_name=f"{project_name} — {path.stem}",
            source_filename=path.name,
        )
        if built.rules or built.cross_field_rules:
            (out_dir / "qa_report.html").write_text(built.qa_report_html, encoding="utf-8")
            result.validation.issues_frame().to_csv(out_dir / "issues.csv", index=False)

        summary = result.summary()
        return BatchItem(
            file=path.name,
            status="ok",
            rows_in=int(summary.get("rows_in", len(source))),
            rows_out=len(result.clean_frame),
            score=float(profile(result.clean_frame).overall),
            errors=int(summary.get("errors", 0)),
            warnings=int(summary.get("warnings", 0)),
            rule_failures=int(built.total_rule_failures),
            rules_run=int(built.total_rules_run),
            output_dir=str(out_dir),
        )
    except Exception as exc:  # noqa: BLE001 - one bad file must not sink the batch
        return BatchItem(file=path.name, status="failed", error=f"{type(exc).__name__}: {exc}")


def run_batch(
    input_dir: str | Path,
    template: str,
    output_dir: str | Path,
    output_format: str = "csv",
    project_name: str = "Batch run",
    files: Iterable[Path] | None = None,
    on_progress: ProgressCallback | None = None,
    write_summary_files: bool = True,
) -> BatchResult:
    """Process every supported file in ``input_dir``.

    Args:
        input_dir: folder to scan. Only its direct children are processed.
        template: config name for every file (``hubspot``, ``bank_reconciliation``…).
        output_dir: where per-file folders, ``summary.csv`` and ``dashboard.html`` go.
        output_format: clean-data format for each file.
        files: override the scan (used by tests and the UI's file picker).
        on_progress: called before each file with ``(index, total, filename)``.
        write_summary_files: set ``False`` to collect results without touching disk.
    """
    out_root = Path(output_dir)
    selected = list(files) if files is not None else supported_files(input_dir)
    result = BatchResult(
        input_dir=str(input_dir), output_dir=str(out_root), template=template
    )

    for index, path in enumerate(selected, start=1):
        if on_progress is not None:
            on_progress(index, len(selected), path.name)
        item = process_one(
            path,
            template=template,
            out_dir=out_root / path.stem,
            output_format=output_format,
            project_name=project_name,
        )
        result.items.append(item)

    if write_summary_files:
        from app_files.batch.dashboard import write_dashboard
        from app_files.batch.summary import write_summary

        write_summary(result, out_root / "summary.csv")
        write_dashboard(result, out_root / "dashboard.html")

    return result