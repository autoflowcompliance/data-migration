"""Command line entry point: ``python -m app_files.cli``.

Two modes: the flat flags below process a single file, and ``batch``
(``python -m app_files.cli batch --in … --template … --out …``) processes a
whole folder.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

from app_files.auditors import audit_import
from app_files.cleaners import load_cleaning_config
from app_files.mappers import available_crms
from app_files.pipeline import run_pipeline
from app_files.reporters import render_audit_report


class _UsageError(Exception):
    """A bad input the caller can fix. Printed as a message, never a traceback."""

    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


# Everything a malformed or incomplete config can throw while loading. The
# loader lives in the frozen core, so turning these into plain English is the
# CLI's job: a raw traceback reads as "the tool is broken" to a buyer.
_CONFIG_ERRORS = (yaml.YAMLError, FileNotFoundError, ValueError, TypeError, KeyError)


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with encoding detection.

    A missing, empty or headerless file is a user mistake, not a crash, so it
    is reported as a :class:`_UsageError` rather than a pandas traceback.
    """
    import chardet

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise _UsageError(f"Could not read {path}: {exc}") from exc

    if not raw.strip():
        raise _UsageError(f"{path} is empty — there is nothing to migrate.")

    encoding = chardet.detect(raw)['encoding'] or 'utf-8'
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding=encoding)
    except pd.errors.EmptyDataError as exc:
        raise _UsageError(
            f"{path} has no columns to parse — a migration needs a header row "
            f"and at least one data row."
        ) from exc
    except UnicodeDecodeError as exc:
        raise _UsageError(f"Could not decode {path} as {encoding}: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean, map and validate a CRM export.")
    parser.add_argument("-i", "--input", required=True, type=Path, help="source CSV")
    parser.add_argument(
        "-c",
        "--crm",
        required=True,
        help=f"target CRM or path to a mapping config ({', '.join(available_crms())})",
    )
    parser.add_argument("-o", "--outdir", default=Path("output"), type=Path)
    parser.add_argument("--cleaning-config", type=Path, default=None)
    parser.add_argument("--project", default="Data migration")
    parser.add_argument("--audit-export", type=Path, default=None, help="CRM export to audit")
    parser.add_argument("--audit-key", default=None, help="unique key column for the audit")
    parser.add_argument("--date-dayfirst", action="store_true", 
                       help="Parse dates with day first (DD/MM/YYYY instead of MM/DD/YYYY)")
    return parser


def build_batch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app_files.cli batch",
        description="Process every supported file in a folder in one pass.",
    )
    parser.add_argument("--in", dest="input_dir", required=True, type=Path,
                        help="folder of source files")
    parser.add_argument("--template", required=True,
                        help=f"target config ({', '.join(available_crms())})")
    parser.add_argument("--out", dest="output_dir", required=True, type=Path,
                        help="folder for per-file output, summary.csv and dashboard.html")
    parser.add_argument("--format", default="csv",
                        choices=["csv", "excel", "json", "sql"],
                        help="clean-data format for each file")
    parser.add_argument("--project", default="Batch run")
    return parser


def run_batch_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli batch …``.

    Imported at call time so the single-file path never pays for the batch
    layer's imports.
    """
    from app_files.batch import run_batch

    args = build_batch_parser().parse_args(argv)
    if not args.input_dir.is_dir():
        print(f"Input folder not found: {args.input_dir}", file=sys.stderr)
        return 2

    def report(index: int, total: int, name: str) -> None:
        print(f"[{index}/{total}] {name}")

    result = run_batch(
        args.input_dir,
        template=args.template,
        output_dir=args.output_dir,
        output_format=args.format,
        project_name=args.project,
        on_progress=report,
    )

    for item in result.items:
        if item.ok:
            print(
                f"  ok    {item.file}: {item.rows_in} in, {item.rows_out} out, "
                f"score {item.score}%"
            )
        else:
            print(f"  FAIL  {item.file}: {item.error}", file=sys.stderr)

    print(
        f"\n{result.succeeded} of {result.processed} file(s) processed, "
        f"average score {result.average_score}%"
    )
    print(f"Summary:   {Path(result.output_dir) / 'summary.csv'}")
    print(f"Dashboard: {Path(result.output_dir) / 'dashboard.html'}")
    return 1 if result.failed else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "batch":
        return run_batch_command(argv[1:])

    try:
        return _run_single_file(argv)
    except _UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code
    except _CONFIG_ERRORS as exc:
        # A config that will not load is a fixable input error, not a crash.
        print(
            f"error: could not load the mapping config: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2


def _run_single_file(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)

    # Load cleaning config and apply date_first preference
    cleaning_config = load_cleaning_config(args.cleaning_config)
    if args.date_dayfirst:
        cleaning_config.date_first = True

    result = run_pipeline(
        source=_read_csv(args.input),
        crm=args.crm,
        cleaning_config=cleaning_config,
        project_name=args.project,
        source_filename=args.input.name,
    )
    result.clean_frame.to_csv(args.outdir / "clean_data.csv", index=False)
    result.mapping_log().to_csv(args.outdir / "mapping_log.csv", index=False)
    result.cleaning_log().to_csv(args.outdir / "cleaning_log.csv", index=False)
    result.validation.issues_frame().to_csv(args.outdir / "issues.csv", index=False)
    (args.outdir / "qa_report.html").write_text(result.qa_report_html, encoding="utf-8")

    summary = result.summary()
    print(
        f"{summary['rows_in']} rows in, {summary['rows_out']} out, "
        f"quality score {summary['quality_score']}%, "
        f"{summary['errors']} errors, {summary['warnings']} warnings"
    )

    if args.audit_export:
        if not args.audit_key:
            print("--audit-key is required with --audit-export", file=sys.stderr)
            return 2
        audit = audit_import(
            expected=result.clean_frame,
            exported=_read_csv(args.audit_export),
            key=args.audit_key,
        )
        audit.mismatches.to_csv(args.outdir / "audit_mismatches.csv", index=False)
        (args.outdir / "audit_report.html").write_text(
            render_audit_report(audit.stats(), audit.mismatches, args.project),
            encoding="utf-8",
        )
        print(
            f"Audit: {len(audit.mismatches)} mismatched values, "
            f"{len(audit.missing_keys)} missing records"
        )

    print(f"Wrote deliverables to {args.outdir}")
    return 0 if result.validation.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
