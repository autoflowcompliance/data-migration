"""Route ``/results`` — score, summary, every report, and every download.

Reads the last run out of the session store. With no run in the session it
shows an empty state rather than an error, because a demo visitor landing here
directly is a normal thing to do.

Everything the run produced is surfaced here rather than behind a menu: the QA
report, the before/after diff, the row-level lineage, all four output formats
and — for a bank-reconciliation job — the reconciliation dashboard. A buyer
deciding whether the tool is worth paying for should not have to hunt for the
thing that proves it.
"""

from __future__ import annotations

import base64
from pathlib import Path

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.interface.web.reports import report_url
from app_files.licensing import current_mode
from app_files.output import to_bytes
from app_files.settings import purchase_url
from app_files.utilities.reconciliation_dashboard import render_dashboard_html

NAV = [
    ("Home", "/demo"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
]


@ui.page("/results")
def results_page() -> None:
    theme.inject_theme()
    _licence, limits = current_mode()
    outcome = session_store.get_outcome()
    chosen_format = session_store.session().output_format

    with page_shell(NAV, active="/results"):
        c.page_header("Results", "Your clean data, the QA report and every issue found.")

        if outcome is None:
            c.empty_state(
                "upload_file",
                "No migration run yet",
                "Upload a file or try one of the samples, and the results will appear here.",
                "Go to upload",
                lambda: ui.navigate.to("/upload"),
            )
            return

        if outcome.reconciliation is not None:
            _render_reconciliation(outcome)
        else:
            _render_migration(outcome, limits, chosen_format)

        _render_run_countdown(limits)


# ------------------------------------------------------------ migration path
def _render_migration(outcome, limits, chosen_format: str) -> None:
    for note in outcome.notes:
        ui.html(f'<div class="dr-trust">{note}</div>').classes("mb-2")

    summary = outcome.summary
    c.metric_row(
        [
            (summary.get("rows_in", 0), "Rows in"),
            (len(outcome.pipeline.clean_frame), "Rows out"),
            (summary.get("duplicates_removed", 0), "Duplicates removed"),
            (len(outcome.issues), "Issues"),
            (f"{outcome.score}%", "Quality score", theme.score_colour(outcome.score)),
        ]
    )

    c.section("Quality scorecard", f"Overall {outcome.score}% across five dimensions.")
    c.scorecard(outcome.profile.scores)
    if outcome.profile.notes:
        with c.expansion("How these were scored"):
            for note in outcome.profile.notes:
                ui.label(f"• {note}").classes("text-sm").style(f"color:{theme.SLATE}")

    if outcome.rules_error:
        ui.label(f"Rules could not be loaded: {outcome.rules_error}").classes(
            "text-sm"
        ).style(f"color:{theme.WARN}")
    elif outcome.rules is not None and outcome.rules.rules_run:
        text = (
            f"{outcome.rules.total_failures} rule failure(s) across "
            f"{outcome.rules.rules_run} rule(s)."
            if outcome.rules.total_failures
            else f"All {outcome.rules.rules_run} configured rule(s) passed."
        )
        colour = theme.WARN if outcome.rules.total_failures else theme.TEAL
        ui.label(text).classes("text-sm").style(f"color:{colour}")

    stem = Path(outcome.source_name).stem
    offered = state.allowed_formats(limits)
    if chosen_format not in offered:
        chosen_format = offered[0]

    c.section("Downloads", "Every format the run produced.")
    with ui.row().classes("w-full items-stretch gap-3"):
        with ui.column().classes("flex-1 min-w-40"):
            c.download_card(
                "QA report",
                "description",
                lambda: _download_report(outcome, stem),
                "Scores, checks and every issue.",
            )
        for fmt in offered:
            payload = to_bytes(outcome.pipeline.clean_frame, fmt, stem=f"{stem}_clean")
            with ui.column().classes("flex-1 min-w-40"):
                c.download_card(
                    f"Clean {fmt.upper()}",
                    "table_view",
                    lambda p=payload: ui.download(p.data, filename=p.filename, media_type=p.mime),
                )
        if outcome.diff_report_html:
            with ui.column().classes("flex-1 min-w-40"):
                c.download_card(
                    "Diff report",
                    "difference",
                    lambda: ui.download(
                        outcome.diff_report_html.encode("utf-8"),
                        filename=f"{stem}_diff.html",
                        media_type="text/html",
                    ),
                )
        if outcome.lineage_report_html:
            with ui.column().classes("flex-1 min-w-40"):
                c.download_card(
                    "Lineage",
                    "account_tree",
                    lambda: ui.download(
                        outcome.lineage_report_html.encode("utf-8"),
                        filename=f"{stem}_lineage.html",
                        media_type="text/html",
                    ),
                )

    # Every report is embedded, so nothing needs a second click to be seen.
    if outcome.report_token:
        c.section("QA report")
        c.report_embed(outcome.report_token)

    if outcome.diff_report_html:
        c.section("What changed", "Before and after, with changed cells highlighted.")
        _embed_html(outcome.diff_report_html, height="70vh")

    if outcome.lineage_report_html:
        c.section("Lineage", "Row-level provenance for every value.")
        _embed_html(outcome.lineage_report_html, height="60vh")

    issues = outcome.issues
    lineage = outcome.pipeline.lineage_log()
    with c.tabs(["Clean data", "Issues", "Logs"]) as (tabs, (clean_tab, issues_tab, logs_tab)):
        with ui.tab_panels(tabs, value=clean_tab).classes("w-full"):
            with ui.tab_panel(clean_tab):
                if outcome.pipeline.clean_frame.empty:
                    c.empty_state("inbox", "No rows came through", "Nothing to show.")
                else:
                    c.file_table(outcome.pipeline.clean_frame)
            with ui.tab_panel(issues_tab):
                if issues.empty:
                    c.empty_state(
                        "check_circle", "No issues found",
                        "Every check passed on this file.",
                    )
                else:
                    c.file_table(issues)
            with ui.tab_panel(logs_tab):
                ui.label("Mapping log").classes("font-semibold")
                c.file_table(outcome.pipeline.mapping_log())
                ui.label("Cleaning log").classes("font-semibold mt-4")
                c.file_table(outcome.pipeline.cleaning_log())
                if not lineage.empty:
                    ui.label("Lineage events").classes("font-semibold mt-4")
                    c.file_table(lineage)


def _download_report(outcome, stem: str) -> None:
    if outcome.report_token:
        ui.download(report_url(outcome.report_token), filename=f"{stem}_qa_report.html")
    else:
        ui.download(
            outcome.qa_report_html.encode("utf-8"),
            filename=f"{stem}_qa_report.html",
            media_type="text/html",
        )


# ------------------------------------------------------- reconciliation path
def _render_reconciliation(outcome) -> None:
    """The bank-reconciliation dashboard: the numbers a bookkeeper reads first."""
    dashboard = outcome.reconciliation
    summary = dashboard.summary
    differences = dashboard.status() == "differences found"

    for note in outcome.notes:
        ui.html(f'<div class="dr-trust">{note}</div>').classes("mb-2")

    c.metric_row(
        [
            (summary.matched, "Matched"),
            (summary.missing_from_books, "Missing from books",
             theme.BAD if summary.missing_from_books else None),
            (summary.never_cleared, "Never cleared",
             theme.BAD if summary.never_cleared else None),
            (summary.date_drift, "Date drift"),
            (f"{summary.total_variance:,.2f}", "Total variance",
             theme.WARN if differences else theme.TEAL),
        ]
    )
    ui.label(
        f"{dashboard.status()} · match rate {summary.match_rate:.1f}% · "
        f"{summary.bank_transactions} bank lines vs {summary.ledger_transactions} ledger lines · "
        f"±{summary.tolerance_days} day tolerance"
    ).classes("text-sm").style(f"color:{theme.SLATE}")

    stem = Path(outcome.source_name).stem
    dashboard_html = render_dashboard_html(dashboard, title=f"Reconciliation — {stem}")

    c.section("Downloads", "The exception lists, plus the full dashboard.")
    with ui.row().classes("w-full items-stretch gap-3"):
        with ui.column().classes("flex-1 min-w-40"):
            c.download_card(
                "Dashboard (HTML)",
                "dashboard",
                lambda: ui.download(
                    dashboard_html.encode("utf-8"),
                    filename=f"{stem}_reconciliation.html",
                    media_type="text/html",
                ),
                "Every number on one page.",
            )
        for label, frame, suffix in (
            ("Missing from books", dashboard.missing_from_books, "missing_from_books"),
            ("Never cleared", dashboard.never_cleared, "never_cleared"),
            ("Matched pairs", dashboard.matched_pairs, "matched_pairs"),
        ):
            if frame is None or frame.empty:
                continue
            payload = frame.to_csv(index=False).encode("utf-8")
            with ui.column().classes("flex-1 min-w-40"):
                c.download_card(
                    label,
                    "table_view",
                    lambda p=payload, s=suffix: ui.download(
                        p, filename=f"{stem}_{s}.csv", media_type="text/csv"
                    ),
                )

    c.section("Dashboard")
    _embed_html(dashboard_html, height="70vh")

    c.section("Exceptions")
    with c.tabs(["Missing from books", "Never cleared", "Matched pairs"]) as (
        tabs,
        (missing_tab, never_tab, pairs_tab),
    ):
        with ui.tab_panels(tabs, value=missing_tab).classes("w-full"):
            with ui.tab_panel(missing_tab):
                if dashboard.missing_from_books.empty:
                    c.empty_state("check_circle", "Nothing missing", "Every bank line is in the books.")
                else:
                    c.file_table(dashboard.missing_from_books)
            with ui.tab_panel(never_tab):
                if dashboard.never_cleared.empty:
                    c.empty_state("check_circle", "All cleared", "No uncleared ledger entries.")
                else:
                    c.file_table(dashboard.never_cleared)
            with ui.tab_panel(pairs_tab):
                if dashboard.matched_pairs.empty:
                    c.empty_state("inbox", "No matches", "Nothing paired up.")
                else:
                    c.file_table(dashboard.matched_pairs)


# ------------------------------------------------------------------ helpers
def _embed_html(html: str, height: str = "70vh") -> None:
    """Embed a standalone report in an iframe, via a data URL.

    A document, not ``ui.html``: a rendered report is far larger than a
    WebSocket message, and pushing it through the element tree drops the
    connection. The data URL keeps this self-contained — no extra route, no
    token to expire.
    """
    encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
    ui.element("iframe").props(f'src="data:text/html;base64,{encoded}"').classes(
        "w-full rounded-lg"
    ).style(f"height:{height};background:var(--surface);border:1px solid var(--line)")


def _render_run_countdown(limits) -> None:
    """Remaining demo runs, so the allowance is never a surprise.

    Silent until a run has actually been spent, matching the uploader. The
    results page is reachable from the sample button, which does not consume a
    run — showing "3 of 3 left" there would announce a limit to a visitor who
    has used none.
    """
    if limits.max_runs_per_session is None:
        return
    if session_store.runs_used() == 0:
        return
    remaining = session_store.runs_remaining(limits.max_runs_per_session)
    if remaining is None:
        return
    if remaining > 0:
        c.info_note(
            f"{remaining} of {limits.max_runs_per_session} demo runs left in this session. "
            "The licensed version has no limit."
        )
    else:
        c.runs_exhausted_note(purchase_url(), limits.max_runs_per_session)
