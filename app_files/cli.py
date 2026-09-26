"""Command line entry point: ``python -m app_files.cli``.

Two modes: the flat flags below process a single file, and ``batch``
(``python -m app_files.cli batch --in … --template … --out …``) processes a
whole folder.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from app_files.auditors import audit_import
from app_files.cleaners import load_cleaning_config
from app_files.mappers import available_crms
from app_files.mappers.schema import CONFIG_DIR
from app_files.pipeline import run_pipeline
from app_files.reporters import render_audit_report


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with encoding detection."""

    import chardet
    
    with open(path, 'rb') as f:
        raw = f.read()
        result = chardet.detect(raw)
        encoding = result['encoding'] or 'utf-8'
    
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False, encoding=encoding)
    except pd.errors.EmptyDataError as exc:
        # pandas' own message ("No columns to parse from file") does not say
        # which file, and an empty upload is the most common first mistake.
        raise ValueError(
            f"{path} is empty — it has no header row, so there is nothing to map."
        ) from exc


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
    parser.add_argument("--record-quality", action="store_true",
                       help="Record this run's quality score in the source's history "
                            "and report the trend")
    parser.add_argument("--baseline", action="store_true",
                       help="Pin this run as the source's baseline (records it too)")
    parser.add_argument("--fail-on-regression", action="store_true",
                       help="Exit non-zero when a dimension falls past the baseline")
    parser.add_argument("--notify", action="store_true",
                       help="Fire the config's notifications: alerts and completion "
                            "webhooks for this run")
    parser.add_argument("--lineage", action="store_true",
                       help="Record row-level lineage and write lineage_report.csv, "
                            "lineage_report.html and lineage_openlineage.json")
    parser.add_argument("--diff", action="store_true",
                       help="Write diff_report.html — what changed, value by value")
    parser.add_argument("--profile-report", action="store_true",
                       help="Inject the five-dimension quality scorecard into the "
                            "QA report and write profile.json")
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
    parser.add_argument("--notify", action="store_true",
                        help="Fire the config's notifications: alerts and completion "
                             "webhooks for each file")
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
    from app_files.distribution.connectors import CONNECTORS, ConnectorError, get_connector

    args = build_pull_parser().parse_args(argv)
    supplied = {
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
    # Every option is offered for every provider, so an option that does not
    # apply (``--path`` on a database) used to reach the constructor and raise
    # TypeError. Pass only what the chosen connector accepts, and say what was
    # ignored rather than silently dropping a value the user typed.
    from inspect import signature

    connector_class = CONNECTORS[args.provider]
    accepted = set(signature(connector_class.__init__).parameters) - {"self"}
    connector_kwargs = {k: v for k, v in supplied.items() if k in accepted}
    ignored = sorted(set(supplied) - accepted)
    if ignored:
        print(
            f"Note: {args.provider} does not use "
            f"{', '.join('--' + k.replace('_', '-') for k in ignored)}; ignoring.",
            file=sys.stderr,
        )
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
    # A pulled dataset is a run like any other: it used to print "Wrote
    # deliverables" while writing none, so a scheduled pull produced an empty
    # output folder and no complaint.
    from app_files.pipeline import write_deliverables

    written = write_deliverables(result, args.outdir, include_lineage=False)
    print(f"Wrote {len(written)} deliverables to {args.outdir}")
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
    if args.notify:
        # A scheduled batch is exactly the unattended case the spec wants an
        # external system told about. One notification per file, from the same
        # config block the single-file run reads.
        from app_files.observability import NotificationConfigError, notify_run

        missed = 0
        for item in result.items:
            try:
                outcome = notify_run(
                    args.template,
                    {
                        "status": "ok" if item.ok else "failed",
                        "quality_score": item.score,
                        "rows_in": item.rows_in,
                        "rows_out": item.rows_out,
                        "errors": item.errors,
                        "warnings": item.warnings,
                        "source": Path(item.file).stem,
                        "run_id": Path(item.file).stem,
                    },
                    run_id=Path(item.file).stem,
                    output_location=item.output_dir,
                    error=item.error,
                    source=Path(item.file).stem,
                )
            except NotificationConfigError as exc:
                print(f"Invalid notifications configuration: {exc}", file=sys.stderr)
                return 2
            if outcome is not None and outcome.failed_deliveries:
                missed += outcome.failed_deliveries
        if missed:
            print(f"Notifications: {missed} delivery failure(s) across the batch")
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


def build_quality_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli quality …`` — read a source's score history."""
    parser = argparse.ArgumentParser(
        prog="app_files.cli quality",
        description=(
            "Show the recorded quality history for a source. Runs must have "
            "been recorded with --record-quality or --baseline first; this "
            "reads the trend store those write to."
        ),
    )
    parser.add_argument("source", nargs="?", default=None,
                        help="source name (as passed to --record-quality); omit to list sources")
    parser.add_argument("--html", type=Path, default=None,
                        help="write the trend table to this HTML file")
    parser.add_argument("-o", "--outdir", type=Path, default=None,
                        help="write <source>_quality_trend.html here")
    return parser


def run_quality_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli quality …``.

    The trend store was written by a run and readable only from Python, and
    ``render_trend_html`` — the dashboard the spec asks for — had no caller, so
    the history existed and nothing showed it. This surfaces both from one
    command a buyer can put in a cron job.
    """
    from app_files.profiling import TrendStore, render_trend_html

    args = build_quality_parser().parse_args(argv)
    store = TrendStore()
    sources = store.sources()

    from app_files.profiling.binding import source_key

    if args.source is None:
        if not sources:
            print("No quality history recorded yet. Run with --record-quality first.")
            return 0
        print(f"{len(sources)} source(s) with recorded runs:")
        for name in sources:
            points = store.trend(name)
            print(f"  {name}: {len(points)} run(s), {points[-1].overall:.1f} latest")
            _write_trend(render_trend_html(points, name), args, name)
        return 0

    name = source_key(args.source)
    points = store.trend(name)
    if not points:
        print(
            f"No recorded runs for {name!r}. "
            "Record one with --record-quality first.",
            file=sys.stderr,
        )
        return 1
    print(f"{name}: {len(points)} run(s)")
    for point in points:
        print(f"  {point.recorded_at[:19]}  {point.overall:.1f}  ({point.row_count} rows)")
    _write_trend(render_trend_html(points, name), args, name)
    return 0


def _write_trend(html: str, args: argparse.Namespace, name: str) -> None:
    target = args.html
    if target is None and args.outdir is not None:
        target = args.outdir / f"{name}_quality_trend.html"
    if target is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        print(f"Wrote trend dashboard to {target}")


def build_quality_check_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli quality check …`` — gate a run on its quality."""
    parser = argparse.ArgumentParser(
        prog="app_files.cli quality check",
        description=(
            "Judge a file against the quality: block in its config. The SLA "
            "floors and the regression action decide the exit code, so this is "
            "usable directly in a cron job or a CI step."
        ),
    )
    parser.add_argument("input", type=Path, help="the file to check")
    parser.add_argument("-c", "--config", required=True, type=Path,
                        help="config holding the quality: block")
    parser.add_argument("--baseline", action="store_true",
                        help="pin this run as the source's baseline (records it too)")
    parser.add_argument("--record", action="store_true",
                        help="record this run in the source's quality history")
    parser.add_argument("-o", "--outdir", type=Path, default=None,
                        help="write quality_report.json here")
    return parser


def run_quality_check_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli quality check …``.

    Exit codes: ``0`` the run met its SLA and did not regress past its action,
    ``1`` the run breached its SLA or regressed under block/quarantine, ``2``
    the config could not be read or the block was malformed. The distinction
    matters because a cron job wants to tell "the data is bad" from "the config
    is wrong".
    """
    args = build_quality_check_parser().parse_args(argv)

    if not args.config.exists():
        print(f"No config at {args.config}", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"No input file at {args.input}", file=sys.stderr)
        return 2

    import pandas as pd

    from app_files.core import ConfigError
    from app_files.ingestion import read_any
    from app_files.quality.binding import bind_quality, check_regression

    try:
        declared = _read_config(args.config)
    except Exception as exc:  # noqa: BLE001 - an unreadable config is reported
        print(f"Could not read {args.config}: {exc}", file=sys.stderr)
        return 2

    frame = read_any(args.input)

    try:
        binding = bind_quality(frame, declared)
    except ConfigError as exc:
        print(f"Invalid quality block: {exc}", file=sys.stderr)
        return 2

    if binding is None:
        print(
            "No quality: block declared in "
            f"{args.config}; nothing to check."
        )
        return 0

    history = None
    if args.baseline or args.record:
        from app_files.profiling import pin_baseline, record_quality

        if args.baseline:
            point = pin_baseline(args.input.name, binding.profile_result)
            print(
                f"Baseline pinned for {point.source} at "
                f"{point.overall:.1f}."
            )
        else:
            history = record_quality(args.input.name, binding.profile_result)

    print(binding.describe())

    if args.outdir is not None:
        import json

        args.outdir.mkdir(parents=True, exist_ok=True)
        target = args.outdir / "quality_report.json"
        target.write_text(
            json.dumps(binding.summary(), indent=2, default=str), encoding="utf-8"
        )
        print(f"Wrote quality report to {target}")

    if binding.breached:
        return 1

    # The regression check reads the stored baseline and writes nothing, so a
    # check never moves the baseline it is measuring against.
    decision = check_regression(args.input.name, binding)
    if decision.regressed:
        print(decision.summary())
        if not decision.proceed:
            return 1

    return 0


def _read_config(path: Path) -> dict[str, Any]:
    """Read a config file into a mapping, or raise if it is not one."""
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a config mapping")
    return data


def build_reconcile_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli reconcile …`` — match a statement to a ledger."""
    parser = argparse.ArgumentParser(
        prog="app_files.cli reconcile",
        description=(
            "Reconcile a bank statement against a ledger. Both files are read "
            "the same way the web page reads them. A config with a matching: "
            "block drives the comparison; without one the amount-and-date "
            "default runs."
        ),
    )
    parser.add_argument("--statement", required=True, type=Path, help="bank statement CSV/PDF")
    parser.add_argument("--ledger", required=True, type=Path, help="ledger CSV/PDF")
    parser.add_argument("-c", "--crm", default="bank_reconciliation",
                        help="config holding the matching: block (default bank_reconciliation)")
    parser.add_argument("-o", "--outdir", type=Path, default=Path("output"))
    parser.add_argument("--bank-date-col", default="Date")
    parser.add_argument("--bank-amount-col", default="Amount")
    parser.add_argument("--ledger-date-col", default=None)
    parser.add_argument("--ledger-amount-col", default=None)
    parser.add_argument("--tolerance", type=int, default=2)
    return parser


def run_reconcile_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli reconcile …``.

    Reconciliation was reachable from the web page and from Python only, so a
    scheduled or scripted run could not match a statement to a ledger. This
    entry point also reads the config's ``matching:`` block, which is what makes
    a YAML match strategy matter to anyone who never imports the package.
    """
    from app_files.services.bank_reconciliation.binding import (
        MatchStrategyConfigError,
        describe_match_strategy,
        load_match_strategy,
    )
    from app_files.services.bank_reconciliation.reconciler import (
        UnreadableStatementError,
        run_reconciliation,
    )

    args = build_reconcile_parser().parse_args(argv)
    try:
        strategy = load_match_strategy(args.crm)
    except MatchStrategyConfigError as exc:
        print(f"Invalid matching configuration: {exc}", file=sys.stderr)
        return 2

    ledger_date = args.ledger_date_col or args.bank_date_col
    ledger_amount = args.ledger_amount_col or args.bank_amount_col
    try:
        result = run_reconciliation(
            args.statement.read_bytes(),
            args.ledger.read_bytes(),
            bank_date_col=args.bank_date_col,
            bank_amount_col=args.bank_amount_col,
            ledger_date_col=ledger_date,
            ledger_amount_col=ledger_amount,
            date_tolerance_days=args.tolerance,
            strategy=strategy,
        )
    except UnreadableStatementError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except KeyError as exc:
        print(
            f"Column {exc} named by the matching strategy was not found in the "
            "statement or ledger.",
            file=sys.stderr,
        )
        return 1

    summary = result["summary"]
    print(f"Strategy: {describe_match_strategy(strategy)}")
    print(
        f"{summary['bank_transactions']} statement row(s), "
        f"{summary['ledger_transactions']} ledger row(s), "
        f"{summary['matched']} matched"
    )
    print(
        f"  missing from books: {summary['missing_from_books']}, "
        f"recorded but never cleared: {summary['recorded_but_never_cleared']}"
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    result["bank_only"].to_csv(args.outdir / "missing_from_books.csv", index=False)
    result["ledger_only"].to_csv(args.outdir / "recorded_but_never_cleared.csv", index=False)
    pd.DataFrame(result["matches"]).to_csv(args.outdir / "matched.csv", index=False)
    print(f"Wrote reconciliation outputs to {args.outdir}")
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

    from app_files.config_bindings import (
        apply_configured_bindings,
        write_bound_deliverables,
    )
    from app_files.pipeline import run_pipeline

    result = run_pipeline(
        frame,
        crm=args.crm,
        project_name=args.project,
        source_filename=args.input.name,
    )
    # The config's declared blocks apply on a committed migration exactly as
    # they do on the flat CLI and in batch. Skipping them wrote raw PII for a
    # config whose ``privacy:`` block says mask it, and omitted the declared
    # dedupe and normalization deliverables.
    from app_files.dedupe.engine import DedupeConfigError
    from app_files.normalization.binding import NormalizationConfigError
    from app_files.privacy.config import PrivacyConfigError

    try:
        bindings = apply_configured_bindings(
            result, args.crm, project_name=args.project, source_filename=args.input.name
        )
    except (PrivacyConfigError, NormalizationConfigError, DedupeConfigError) as exc:
        # Fail closed on a malformed block: a typo in ``privacy:`` must not let
        # unmasked PII through while the command reports success.
        print(f"Invalid configuration block: {exc}", file=sys.stderr)
        return 2
    result.clean_frame.to_csv(outdir / "clean_data.csv", index=False)
    write_bound_deliverables(bindings, outdir)
    if bindings.declared_rules:
        result.validation.issues_frame().to_csv(outdir / "issues.csv", index=False)
    summary = result.summary()
    print(
        f"\n{summary['rows_in']} rows in, {summary['rows_out']} out, "
        f"quality score {summary['quality_score']}%"
    )
    if bindings.privacy is not None:
        counts = bindings.privacy.summary()
        print(
            f"Privacy: {counts['detected']} value(s) detected, "
            f"{counts['masked']} masked in {', '.join(counts['columns']) or 'no columns'}"
        )
    print(f"Wrote deliverables to {outdir}")
    return 0


def _batch_job_handler(payload: dict) -> dict:
    """Run one batch folder from a job payload. Registered by ``jobs run``."""
    from app_files.batch import run_batch

    result = run_batch(
        input_dir=payload["input_dir"],
        template=payload["template"],
        output_dir=payload["output_dir"],
        output_format=payload.get("output_format", "csv"),
        project_name=payload.get("project_name", "Queued batch run"),
    )
    return result.as_dict()


def build_jobs_parser() -> argparse.ArgumentParser:
    """``python -m app_files.cli jobs …`` — the durable queue an operator drives.

    Layer 14 was library-only. This exposes submit / list / run, and registers
    the built-in ``batch`` handler so a submitted job actually does something
    without the operator writing Python.
    """
    parser = argparse.ArgumentParser(
        prog="app_files.cli jobs",
        description=(
            "Submit work to the durable job queue, inspect it, and drain it with "
            "workers. The queue lives under AUTOFLOW_HOME, so a crash loses "
            "neither a submission nor a state change."
        ),
    )
    sub = parser.add_subparsers(dest="action", required=True)

    submit = sub.add_parser("submit", help="add a job to the queue")
    submit.add_argument("--kind", default="batch",
                        help="job kind; only 'batch' has a built-in handler")
    submit.add_argument("--input-dir", type=Path, help="folder for a batch job")
    submit.add_argument("--template", help="config name for a batch job")
    submit.add_argument("--out", dest="output_dir", type=Path, help="output folder")
    submit.add_argument("--format", default="csv", help="output format for a batch job")
    submit.add_argument("--priority", choices=["low", "normal", "high"], default="normal")
    submit.add_argument("--depends-on", action="append", default=[],
                        help="a job id that must succeed first; repeatable")
    submit.add_argument("--max-attempts", type=int, default=1)

    sub.add_parser("list", help="show queued and finished jobs")

    run = sub.add_parser("run", help="drain the queue with workers")
    run.add_argument("--workers", type=int, default=1, help="number of workers")
    run.add_argument("--max-jobs", type=int, default=None,
                     help="stop after this many jobs in total")
    run.add_argument("--threads", action="store_true",
                     help="run the workers concurrently rather than in turn")
    return parser


def run_jobs_command(argv: list[str]) -> int:
    """Handle ``python -m app_files.cli jobs …``."""
    from app_files.orchestration import JobQueue, JobSpec, Priority, run_workers
    from app_files.orchestration.workers import register_handler

    args = build_jobs_parser().parse_args(argv)
    queue = JobQueue()

    if args.action == "submit":
        if args.kind == "batch":
            missing = [
                name for name, value in
                (("--input-dir", args.input_dir), ("--template", args.template),
                 ("--out", args.output_dir))
                if value is None
            ]
            if missing:
                print(
                    f"A batch job needs {', '.join(missing)}.",
                    file=sys.stderr,
                )
                return 2
            payload = {
                "input_dir": str(args.input_dir),
                "template": args.template,
                "output_dir": str(args.output_dir),
                "output_format": args.format,
            }
        else:
            print(f"No built-in handler for kind {args.kind!r}.", file=sys.stderr)
            return 2
        priority = {
            "low": Priority.LOW, "normal": Priority.NORMAL, "high": Priority.HIGH,
        }[args.priority]
        job = queue.submit(
            JobSpec(
                kind=args.kind,
                payload=payload,
                priority=priority,
                max_attempts=args.max_attempts,
                depends_on=list(args.depends_on),
            )
        )
        print(f"Submitted job {job.id} ({args.kind}, {args.priority} priority).")
        return 0

    if args.action == "list":
        print(queue.render())
        return 0

    # ``run``: the built-in handler is registered here rather than on import, so
    # importing the queue never mutates the global registry on a caller. The
    # registry is restored afterwards, because leaving ``batch`` behind would
    # change what other callers' own registrations mean.
    from app_files.orchestration.workers import HANDLERS

    snapshot = dict(HANDLERS)
    register_handler("batch", _batch_job_handler, override=True)
    try:
        reports = run_workers(
            queue, count=args.workers, max_jobs=args.max_jobs, threads=args.threads
        )
    finally:
        HANDLERS.clear()
        HANDLERS.update(snapshot)
    total_done = sum(report.succeeded for report in reports)
    total_failed = sum(report.failed for report in reports)
    for report in reports:
        print(f"worker {report.worker}: {report.succeeded} ok, {report.failed} failed")
    print(f"Jobs: {total_done} succeeded, {total_failed} failed")
    return 1 if total_failed else 0


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
    if argv and argv[0] == "reconcile":
        return run_reconcile_command(argv[1:])
    if argv and argv[0] == "quality":
        # ``quality check`` gates a file against its quality: block; the bare
        # ``quality <source>`` still reads a source's recorded history.
        if len(argv) > 1 and argv[1] == "check":
            return run_quality_check_command(argv[2:])
        return run_quality_command(argv[1:])
    if argv and argv[0] == "migrate":
        return run_migrate_command(argv[1:])
    if argv and argv[0] == "jobs":
        return run_jobs_command(argv[1:])

    args = build_parser().parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)

    # A config that cannot be parsed, or that declares no fields at all, used to
    # reach the pipeline as an empty mapping: every source column dropped and a
    # cheerful "quality score 100.0%". That is the worst possible failure for a
    # migration tool, so both are caught here and reported plainly. This lives
    # at the CLI boundary because the frozen mapper's loader is shared with the
    # web UI, which surfaces the same problems through its own error path.
    config_path = Path(args.crm)
    if not config_path.exists():
        config_path = CONFIG_DIR / f"{str(args.crm).strip().lower()}.yaml"
    if not config_path.exists():
        print(
            f"No mapping config for {args.crm!r}. Known CRMs: "
            f"{', '.join(available_crms())}",
            file=sys.stderr,
        )
        return 2
    import yaml

    try:
        declared = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"Invalid mapping config {config_path}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(declared, dict):
        print(
            f"Invalid mapping config {config_path}: expected a YAML mapping, "
            f"found {type(declared).__name__}",
            file=sys.stderr,
        )
        return 2
    # Validate each declared block before the fields guard below, so a config
    # that is wrong in two ways reports the more specific one. The bindings
    # raise their own config error, which is the message a buyer needs.
    from app_files.dedupe.binding import declared_dedupe_rules
    from app_files.dedupe.engine import DedupeConfigError
    from app_files.normalization.binding import (
        NormalizationConfigError,
        validate_normalization_block,
    )

    try:
        declared_dedupe_rules(config_path)
    except DedupeConfigError as exc:
        print(f"Invalid dedupe configuration: {exc}", file=sys.stderr)
        return 2
    try:
        validate_normalization_block(config_path)
    except NormalizationConfigError as exc:
        print(f"Invalid normalization configuration: {exc}", file=sys.stderr)
        return 2
    if not declared.get("fields"):
        print(
            f"Invalid mapping config {config_path}: it declares no 'fields', so "
            "every source column would be dropped. Add at least one field.",
            file=sys.stderr,
        )
        return 2
    # Load cleaning config and apply date_first preference
    cleaning_config = load_cleaning_config(args.cleaning_config)
    if args.date_dayfirst:
        cleaning_config.date_first = True

    from app_files.dedupe.binding import apply_configured_dedupe
    from app_files.dedupe.engine import DedupeConfigError
    from app_files.lineage import LineageTracker
    from app_files.normalization.binding import (
        NormalizationConfigError,
        apply_configured_normalization,
    )
    from app_files.privacy.binding import apply_configured_privacy
    from app_files.privacy.config import PrivacyConfigError
    from app_files.privacy.report import inject_pii_report
    from app_files.rules.binding import apply_configured_rules, failures_exceed

    try:
        source_frame = _read_csv(args.input)
    except (ValueError, pd.errors.ParserError) as exc:
        print(f"Cannot read {args.input}: {exc}", file=sys.stderr)
        return 2

    result = run_pipeline(
        source=source_frame,
        crm=args.crm,
        cleaning_config=cleaning_config,
        project_name=args.project,
        source_filename=args.input.name,
        lineage_tracker=LineageTracker() if args.lineage else None,
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
    # Layer 5's scorecard and Layer 6's two views were reachable only from the
    # web UI, so a scheduled run produced no scorecard and no lineage. Both are
    # opt-in: a run that does not ask for them writes exactly what it wrote
    # before, which keeps every prior golden file byte-identical.
    if args.profile_report:
        from app_files.profiling import profile
        from app_files.profiling.report import render_qa_report_with_profile

        profile_result = profile(result.clean_frame)
        qa_html = render_qa_report_with_profile(qa_html, result.clean_frame, profile_result)
        profile_dict = profile_result.as_dict()
        (args.outdir / "profile.json").write_text(
            json.dumps(profile_dict, indent=2), encoding="utf-8"
        )
        dimensions = {
            k: v
            for k, v in profile_dict.items()
            if k in {"completeness", "uniqueness", "validity", "consistency", "timeliness"}
        }
        print(
            f"Profile: overall {profile_dict['overall']:.1f} "
            f"({', '.join(f'{k} {v:.0f}' for k, v in dimensions.items())})"
        )
    (args.outdir / "qa_report.html").write_text(qa_html, encoding="utf-8")
    if args.lineage:
        from app_files.collaboration.comparison import (
            build_comparison,
            render_comparison_html,
        )
        from app_files.lineage import (
            render_lineage_html,
            to_openlineage,
            write_lineage_report,
            write_openlineage,
        )

        tracker = result.lineage
        write_lineage_report(tracker, args.outdir / "lineage_report.csv")
        (args.outdir / "lineage_report.html").write_text(
            render_lineage_html(tracker), encoding="utf-8"
        )
        write_openlineage(
            to_openlineage(tracker), args.outdir / "lineage_openlineage.json"
        )
        if args.diff:
            try:
                (args.outdir / "diff_report.html").write_text(
                    render_comparison_html(
                        build_comparison(_read_csv(args.input), tracker, result.clean_frame),
                        title=f"What changed — {args.input.stem}",
                    ),
                    encoding="utf-8",
                )
            except Exception as exc:  # noqa: BLE001 - a missing diff must not fail the run
                print(f"Diff report unavailable: {exc}", file=sys.stderr)

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
    quality_history = None
    if args.record_quality or args.baseline:
        # Layer 5's trend store and baseline comparison had no caller outside
        # the profiling package, so every run scored a source and forgot it.
        # Recording is opt-in so a run that never asked for history writes
        # nothing and stays byte-identical.
        from app_files.profiling import pin_baseline, profile, record_quality
        from app_files.profiling.binding import source_key

        current_profile = profile(result.clean_frame)
        if args.baseline:
            point = pin_baseline(args.input.name, current_profile)
            print(f"Baseline pinned for {source_key(args.input.name)} at {point.overall:.1f}.")
        else:
            quality_history = record_quality(args.input.name, current_profile)
            counts = quality_history.summary()
            print(
                f"Quality history: {counts['runs_recorded']} run(s) for "
                f"{counts['source']}, trend {counts['trend']}"
            )
            if quality_history.comparison is not None and quality_history.alerting:
                comparison = quality_history.comparison
                print(
                    f"  regression: {', '.join(comparison.regressed_dimensions)} "
                    f"fell past baseline ({comparison.overall_baseline} -> "
                    f"{comparison.overall_current})"
                )
            anomaly = quality_history.anomaly
            if anomaly is not None and not anomaly.clean:
                print(
                    f"  anomaly: {anomaly.status} outside the learned range for "
                    f"{', '.join(item.dimension for item in anomaly.anomalies)}"
                )
    if args.notify:
        # Layers 8's completion webhook and 15's alerting were both complete
        # and both unreachable from a run. This fires them from the config's
        # notifications: block; delivery is best-effort so a dead endpoint
        # cannot fail a run that produced correct output.
        from app_files.observability import NotificationConfigError, notify_run

        run_status = "ok" if core_valid else "failed"
        notify_summary = {
            **summary,
            "status": run_status,
            "source": args.input.stem,
            "run_id": args.input.stem,
        }
        try:
            notifications = notify_run(
                args.crm,
                notify_summary,
                run_id=args.input.stem,
                output_location=str(args.outdir),
                error=None if core_valid else f"{summary['errors']} validation error(s)",
                source=args.input.stem,
            )
        except NotificationConfigError as exc:
            print(f"Invalid notifications configuration: {exc}", file=sys.stderr)
            return 2
        if notifications is not None:
            print(
                f"Notifications: {len(notifications.alerts)} alert(s), "
                f"{notifications.summary()['webhooks_delivered']} webhook(s) delivered"
                + (
                    f", {notifications.failed_deliveries} delivery failure(s)"
                    if notifications.failed_deliveries
                    else ""
                )
            )
    if args.strict_rules and failures_exceed(built, max_failures=0):
        print(
            f"--strict-rules: {built.total_rule_failures} declared rule failure(s).",
            file=sys.stderr,
        )
        return 1
    if (
        args.fail_on_regression
        and quality_history is not None
        and quality_history.alerting
    ):
        print(
            "--fail-on-regression: the run fell past its baseline in "
            f"{', '.join(quality_history.comparison.regressed_dimensions)}.",
            file=sys.stderr,
        )
        return 1
    return 0 if core_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
