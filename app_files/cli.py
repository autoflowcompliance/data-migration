"""Command line entry point: ``python -m data_migration_tool.cli``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .auditors import audit_import
from .cleaners import load_cleaning_config
from .mappers import available_crms
from .pipeline import run_pipeline
from .reporters import render_audit_report


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with encoding detection."""
    import chardet
    import io
    
    with open(path, 'rb') as f:
        raw = f.read()
        result = chardet.detect(raw)
        encoding = result['encoding'] or 'utf-8'
    
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding=encoding)


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


def main(argv: list[str] | None = None) -> int:
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
