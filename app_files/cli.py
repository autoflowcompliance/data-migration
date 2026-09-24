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

from app_files.auditors import audit_import
from app_files.cleaners import load_cleaning_config
from app_files.mappers import available_crms
from app_files.pipeline import run_pipeline
from app_files.reporters import render_audit_report


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with encoding detection."""

    import chardet
    
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
    parser.add_argument("--strict-rules", action="store_true",
                       help="Exit non-zero when a rule the config declares fails")
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
    parser.add_argument("--strict-rules", action="store_true",
                        help="Exit non-zero when a rule the config declares fails")
    return parser


def build_watch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app_files.cli watch",
        description="Process a file the moment it lands in a folder.",
    )
    parser.add_argument("--in", dest="input_dir", required=True, type=Path,
                        help="folder to watch")
    parser.add_argument("--template", required=True,
                        help=f"target config ({', '.join(available_crms())})")
    parser.add_argument("--out", dest="output_dir", required=True, type=Path,
                        help="folder for per-file output")
    parser.add_argument("--format", default="csv",
                        choices=["csv", "excel", "json", "sql"],
                        help="clean-data format for each file")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="seconds between polls")
    parser.add_argument("--settle", type=float, default=2.0,
                        help="seconds a file's size must hold steady before it is read")
    parser.add_argument("--once", action="store_true",
                        help="poll once and exit, for cron")
    parser.add_argument("--max-polls", type=int, default=None,
                        help="stop after this many polls")
    parser.add_argument("--project", default="Watch run")
    return parser


def build_pull_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli pull …`` — read from where the data lives."""
    from app_files.distribution.connectors import available_connectors

    parser = argparse.ArgumentParser(
        prog="app_files.cli pull",
        description="Fetch a dataset from a connector and run the pipeline on it.",
    )
    parser.add_argument("provider", choices=available_connectors())
    parser.add_argument("--table", default="", help="table name (database providers)")
    parser.add_argument("--query", default="", help="read-only SELECT (database providers)")
    parser.add_argument("--url", default="", help="database URL")
    parser.add_argument("--bucket", default="", help="S3 bucket")
    parser.add_argument("--key", default="", help="S3 key")
    parser.add_argument("--path", default="", help="remote path (SFTP/Dropbox/OneDrive)")
    parser.add_argument("--spreadsheet-id", default="", help="Google sheet id")
    parser.add_argument("--sheet-name", default="", help="Google sheet tab")
    parser.add_argument("--file-id", default="", help="Google Drive file id")
    parser.add_argument("-c", "--crm", default="hubspot")
    parser.add_argument("-o", "--outdir", type=Path, default=Path("output"))
    parser.add_argument(
        "--dry-run", action="store_true", help="fetch only, do not run the pipeline"
    )
    return parser


def run_pull_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli pull …``.

    Fetch through the connector, then hand the resulting DataFrame to the same
    ``run_pipeline`` every other entry point uses. The connector is a producer
    into the existing interface, not a second pipeline.
    """
    from app_files.distribution.connectors import ConnectorError, get_connector

    args = build_pull_parser().parse_args(argv)
    connector_kwargs = {
        key: value
        for key, value in {
            "url": args.url,
            "bucket": args.bucket,
            "path": args.path,
            "spreadsheet_id": args.spreadsheet_id,
            "sheet_name": args.sheet_name,
            "file_id": args.file_id,
        }.items()
        if value
    }
    fetch_kwargs = {
        key: value
        for key, value in {"table": args.table, "query": args.query, "key": args.key}.items()
        if value
    }
    try:
        connector = get_connector(args.provider, **connector_kwargs)
        payload = connector.fetch(**fetch_kwargs) if fetch_kwargs else connector.fetch()
    except (ConnectorError, ValueError) as exc:
        print(f"Could not read from {args.provider}: {exc}", file=sys.stderr)
        return 2

    frame = payload.as_frame()
    print(f"Pulled {len(frame)} rows from {payload.location or payload.name}")
    if args.dry_run:
        return 0

    args.outdir.mkdir(parents=True, exist_ok=True)
    result = run_pipeline(frame, crm=args.crm)
    summary = result.summary()
    print(
        f"{summary['rows_in']} rows in, {summary['rows_out']} out, "
        f"quality score {summary['quality_score']}%, {summary['errors']} errors, "
        f"{summary['warnings']} warnings"
    )
    print(f"Wrote deliverables to {args.outdir}")
    return 0


def run_watch_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli watch …``."""
    from app_files.batch import WatchFolder

    args = build_watch_parser().parse_args(argv)
    if not args.input_dir.is_dir():
        print(f"Input folder not found: {args.input_dir}", file=sys.stderr)
        return 2

    folder = WatchFolder(
        args.input_dir,
        args.template,
        args.output_dir,
        settle_seconds=args.settle,
        output_format=args.format,
        project_name=args.project,
    )

    def report(outcome) -> None:
        if outcome.ok:
            print(f"  ok    {outcome.file}: {outcome.item.rows_out} rows out, "
                  f"score {outcome.item.score}%")
        else:
            print(f"  FAIL  {outcome.file}: {outcome.reason}", file=sys.stderr)

    iterations = 1 if args.once else args.max_polls
    try:
        outcomes = folder.run(
            iterations=iterations,
            poll_interval=args.interval,
            on_progress=report,
        )
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 0
    return 1 if any(not outcome.ok for outcome in outcomes) else 0


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
            rule_note = (
                f", {item.rule_failures} rule failure(s)" if item.rule_failures else ""
            )
            print(
                f"  ok    {item.file}: {item.rows_in} in, {item.rows_out} out, "
                f"score {item.score}%{rule_note}"
            )
        else:
            print(f"  FAIL  {item.file}: {item.error}", file=sys.stderr)

    print(
        f"\n{result.succeeded} of {result.processed} file(s) processed, "
        f"average score {result.average_score}%"
    )
    print(f"Summary:   {Path(result.output_dir) / 'summary.csv'}")
    print(f"Dashboard: {Path(result.output_dir) / 'dashboard.html'}")
    if result.failed:
        return 1
    if args.strict_rules:
        offenders = [item.file for item in result.items if item.rule_failures]
        if offenders:
            print(
                f"--strict-rules: {len(offenders)} file(s) had declared rule failures: "
                f"{', '.join(offenders)}",
                file=sys.stderr,
            )
            return 1
    return 0


def build_drift_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli drift …`` — gate a run on schema change."""
    parser = argparse.ArgumentParser(
        prog="app_files.cli drift",
        description=(
            "Compare a source file's schema to the last one seen for it, then "
            "run only if the change is safe. A blocked run stops and exits "
            "non-zero; re-run with --accept once a human has approved the drift."
        ),
    )
    parser.add_argument("-i", "--input", required=True, type=Path, help="source CSV")
    parser.add_argument("-c", "--crm", required=True,
                        help=f"target CRM or mapping config path ({', '.join(available_crms())})")
    parser.add_argument("-o", "--outdir", type=Path, default=Path("output"))
    parser.add_argument("--source", default=None,
                        help="name this source is remembered under (defaults to the filename)")
    parser.add_argument("--project", default="Drift-guarded run")
    parser.add_argument("--accept", action="store_true",
                        help="record the changed schema even when it would block")
    return parser


def run_drift_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli drift …``.

    On a blocked verdict the run does not happen and the process exits non-zero,
    so a scheduled job stops instead of quietly migrating a changed source.
    """
    from app_files.drift import WARN, DriftBlocked, DriftGate

    args = build_drift_parser().parse_args(argv)
    frame = _read_csv(args.input)
    source = args.source or args.input.name
    gate = DriftGate()

    if args.accept:
        # The human has looked at the drift and approved it; record the new
        # shape so the next run is judged against what was actually migrated.
        gate.remember(source, frame)
        print(f"Recorded the current schema for {source!r}.")

    try:
        result, decision = gate.guarded_run(
            source, frame, args.crm, source_filename=args.input.name,
            project_name=args.project,
        )
    except DriftBlocked as blocked:
        decision = blocked.decision
        print(decision.summary(), file=sys.stderr)
        print(
            "The run was stopped. Review the change, then re-run with --accept "
            "to record the new schema.",
            file=sys.stderr,
        )
        return 1

    if decision.verdict == WARN:
        print(f"Warning: {decision.summary()}")
    else:
        print(decision.summary())

    args.outdir.mkdir(parents=True, exist_ok=True)
    result.clean_frame.to_csv(args.outdir / "clean_data.csv", index=False)
    summary = result.summary()
    print(
        f"{summary['rows_in']} rows in, {summary['rows_out']} out, "
        f"quality score {summary['quality_score']}%"
    )
    print(f"Wrote deliverables to {args.outdir}")
    return 0


def build_migrate_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli migrate …`` — rehearse, then run, a migration.

    Layer 18 was library-only: a buyer could import it, but nothing they could
    actually run reached it. This exposes the four safety steps on one command:
    analyse the source, take a rollback copy, dry-run, write the runbook, then
    migrate -- each step skipped unless asked for.
    """
    parser = argparse.ArgumentParser(
        prog="app_files.cli migrate",
        description=(
            "Rehearse a migration before committing to it: pre-migration "
            "analysis, a rollback copy, a dry run, and a generated runbook. "
            "Pass --commit to actually run the migration and write output."
        ),
    )
    parser.add_argument("-i", "--input", required=True, type=Path, help="source CSV")
    parser.add_argument("-c", "--crm", required=True,
                        help=f"target CRM or mapping config path ({', '.join(available_crms())})")
    parser.add_argument("-o", "--outdir", type=Path, default=Path("output"))
    parser.add_argument("--project", default="Data migration")
    parser.add_argument("--schedule", default=None,
                        help="cron expression to name in the runbook, if any")
    parser.add_argument("--commit", action="store_true",
                        help="run the migration and write output; without it, "
                             "nothing is written and a blocking issue exits non-zero")
    return parser


def run_migrate_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli migrate …``.

    The default is a rehearsal: analysis, rollback copy, dry run and runbook
    are written, but the migration itself is not. ``--commit`` runs it. A
    blocking issue found in analysis stops before anything is written unless
    ``--commit`` is passed, and then only with the issue printed.
    """
    from app_files.migration import (
        analyze_source,
        build_rollback,
        dry_run,
        generate_runbook,
        write_pre_migration_report,
    )

    args = build_migrate_parser().parse_args(argv)
    frame = _read_csv(args.input)
    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    analysis = analyze_source(frame, args.crm, source_name=args.input.name)
    write_pre_migration_report(analysis, outdir / "pre_migration.txt")
    print(analysis.render())

    rollback = build_rollback(frame, outdir / "rollback", source_name=args.input.name)
    print(
        f"\nRollback copy: {rollback.path} "
        f"({rollback.rows} rows, sha256 {rollback.checksum[:12]}…)"
    )

    rehearsal = dry_run(
        frame, args.crm, project_name=args.project, source_filename=args.input.name
    )
    print("\n" + rehearsal.render())

    runbook = generate_runbook(
        args.crm, project_name=args.project, source_name=args.input.name,
        output_path=str(outdir), schedule=args.schedule,
    )
    runbook.write(outdir / "runbook.txt")
    print(f"\nRunbook written to {outdir / 'runbook.txt'}")

    if not args.commit:
        if not analysis.ready:
            print(
                "\nBlocking issues found. Fix them or re-run with --commit to "
                "migrate anyway.",
                file=sys.stderr,
            )
            return 1
        print(
            "\nRehearsal complete, nothing was migrated. Re-run with --commit "
            "to run the migration."
        )
        return 0

    from app_files.pipeline import run_pipeline

    result = run_pipeline(
        frame,
        crm=args.crm,
        project_name=args.project,
        source_filename=args.input.name,
    )
    result.clean_frame.to_csv(outdir / "clean_data.csv", index=False)
    summary = result.summary()
    print(
        f"\n{summary['rows_in']} rows in, {summary['rows_out']} out, "
        f"quality score {summary['quality_score']}%"
    )
    print(f"Wrote deliverables to {outdir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "batch":
        return run_batch_command(argv[1:])
    if argv and argv[0] == "watch":
        return run_watch_command(argv[1:])
    if argv and argv[0] == "pull":
        return run_pull_command(argv[1:])
    if argv and argv[0] == "drift":
        return run_drift_command(argv[1:])
    if argv and argv[0] == "migrate":
        return run_migrate_command(argv[1:])

    args = build_parser().parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)

    # Load cleaning config and apply date_first preference
    cleaning_config = load_cleaning_config(args.cleaning_config)
    if args.date_dayfirst:
        cleaning_config.date_first = True

    from app_files.dedupe.binding import apply_configured_dedupe
    from app_files.dedupe.engine import DedupeConfigError
    from app_files.normalization.binding import (
        NormalizationConfigError,
        apply_configured_normalization,
    )
    from app_files.privacy.binding import apply_configured_privacy
    from app_files.privacy.config import PrivacyConfigError
    from app_files.privacy.report import inject_pii_report
    from app_files.rules.binding import apply_configured_rules, failures_exceed

    result = run_pipeline(
        source=_read_csv(args.input),
        crm=args.crm,
        cleaning_config=cleaning_config,
        project_name=args.project,
        source_filename=args.input.name,
    )
    # Layer 4's config rules used to run only in the web UI, so an unattended
    # run's issues.csv and score omitted them entirely. Apply them here on top
    # of the result we already have (never re-running the pipeline, which would
    # drop the cleaning config above).
    #
    # The exit code is decided by the *core* validation captured here, before
    # the rules merge. A merged error-severity rule issue would otherwise flip
    # ``validation.valid`` and make an advisory rule fail the run, contradicting
    # the documented contract and the batch engine's own exit logic.
    core_valid = result.validation.valid
    built = apply_configured_rules(
        result, args.crm, project_name=args.project, source_filename=args.input.name
    )
    result.clean_frame.to_csv(args.outdir / "clean_data.csv", index=False)
    result.mapping_log().to_csv(args.outdir / "mapping_log.csv", index=False)
    result.cleaning_log().to_csv(args.outdir / "cleaning_log.csv", index=False)
    result.validation.issues_frame().to_csv(args.outdir / "issues.csv", index=False)
    qa_html = built.qa_report_html
    # A config-declared ``privacy:`` block is the buyer saying PII must not
    # reach a destination. Mask the frame the pipeline produced and write the
    # masked copy and its card beside the original; a config without the block
    # writes nothing extra and its output is byte-identical to before.
    try:
        privacy = apply_configured_privacy(result.clean_frame, args.crm)
    except PrivacyConfigError as exc:
        # Fail closed, not silent: a typo in a privacy block must stop the run
        # rather than let unmasked PII through while reporting success.
        print(f"Invalid privacy configuration: {exc}", file=sys.stderr)
        return 2
    if privacy is not None:
        privacy.masked_frame.to_csv(args.outdir / "masked_data.csv", index=False)
        (args.outdir / "privacy_report.html").write_text(
            privacy.report_html, encoding="utf-8"
        )
        qa_html = inject_pii_report(qa_html, privacy.report, privacy.mask_result.summary())
    # A config-declared ``normalization:`` block canonicalises addresses and
    # converts currencies on a copy. The pipeline's own clean_data.csv is left
    # as-is, so a config without the block is byte-identical to before.
    try:
        normalization = apply_configured_normalization(result.clean_frame, args.crm)
    except NormalizationConfigError as exc:
        print(f"Invalid normalization configuration: {exc}", file=sys.stderr)
        return 2
    if normalization is not None:
        normalization.frame.to_csv(args.outdir / "normalized_data.csv", index=False)
        conversions = normalization.conversions_frame()
        if not conversions.empty:
            conversions.to_csv(args.outdir / "currency_conversions.csv", index=False)
    # A config-declared ``dedupe:`` block folds near-duplicate rows out of a
    # copy. The pipeline's own clean_data.csv (and the normalised copy) is left
    # as-is, so a config without the block is byte-identical to before.
    try:
        dedupe = apply_configured_dedupe(result.clean_frame, args.crm)
    except DedupeConfigError as exc:
        print(f"Invalid dedupe configuration: {exc}", file=sys.stderr)
        return 2
    if dedupe is not None:
        dedupe.frame.to_csv(args.outdir / "deduped_data.csv", index=False)
        merges = dedupe.merges_frame()
        if not merges.empty:
            merges.to_csv(args.outdir / "duplicates_removed.csv", index=False)
    (args.outdir / "qa_report.html").write_text(qa_html, encoding="utf-8")

    summary = result.summary()
    print(
        f"{summary['rows_in']} rows in, {summary['rows_out']} out, "
        f"quality score {summary['quality_score']}%, "
        f"{summary['errors']} errors, {summary['warnings']} warnings"
    )
    declared_rules = len(built.rules) + len(built.cross_field_rules)
    if declared_rules:
        unmatched = built.unmatched_rules + built.unmatched_cross_field
        print(
            f"Rules: {built.total_rules_run} of {declared_rules} run, "
            f"{built.total_rule_failures} failure(s)"
        )
        if unmatched:
            print(f"  unmatched rules: {', '.join(unmatched)}")
    if privacy is not None:
        counts = privacy.summary()
        print(
            f"Privacy: {counts['detected']} value(s) detected, "
            f"{counts['masked']} masked in {', '.join(counts['columns']) or 'no columns'}"
        )
    if normalization is not None:
        counts = normalization.summary()
        print(
            f"Normalization: {counts['addresses_normalised']} address(es) canonicalised, "
            f"{counts['amounts_converted']} amount(s) converted"
            + (f", {counts['amounts_failed']} unconverted" if counts["amounts_failed"] else "")
        )
    if dedupe is not None:
        print(
            f"Dedupe: {dedupe.duplicates_removed} near-duplicate row(s) removed "
            f"from {dedupe.summary()['rows_in']}"
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
    if args.strict_rules and failures_exceed(built, max_failures=0):
        print(
            f"--strict-rules: {built.total_rule_failures} declared rule failure(s).",
            file=sys.stderr,
        )
        return 1
    return 0 if core_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
