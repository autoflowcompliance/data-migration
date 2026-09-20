"""Route ``/results`` — score, summary, issue list and downloads.

Reads the last run out of the session store. With no run in the session it
shows an empty state rather than an error, because a demo visitor landing here
directly is a normal thing to do.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.interface.web.reports import report_url
from app_files.output import to_bytes
from app_files.licensing import current_mode

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
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
            with ui.expansion("How these were scored").classes("w-full"):
                for note in outcome.profile.notes:
                    ui.label(f"• {note}").classes("text-sm text-gray-500")

        if outcome.rules_error:
            ui.label(f"Rules could not be loaded: {outcome.rules_error}").classes(
                "text-amber-600 text-sm"
            )
        elif outcome.rules is not None and outcome.rules.rules_run:
            if outcome.rules.total_failures:
                ui.label(
                    f"{outcome.rules.total_failures} rule failure(s) across "
                    f"{outcome.rules.rules_run} rule(s)."
                ).classes("text-amber-600 text-sm")
            else:
                ui.label(f"All {outcome.rules.rules_run} configured rule(s) passed.").classes(
                    "text-green-700 text-sm"
                )

        c.section("Downloads")
        stem = Path(outcome.source_name).stem

        def download_html_report() -> None:
            if outcome.report_token:
                ui.download(report_url(outcome.report_token), filename=f"{stem}_qa_report.html")
            else:
                ui.download(
                    outcome.qa_report_html.encode("utf-8"),
                    filename=f"{stem}_qa_report.html",
                    media_type="text/html",
                )

        c.download_card(
            "QA report (HTML)",
            "description",
            download_html_report,
            "Quality scores, checks and every issue in one file.",
        )

        offered = state.allowed_formats(limits)
        if chosen_format not in offered:
            chosen_format = offered[0]

        for fmt in offered:
            payload = to_bytes(
                outcome.pipeline.clean_frame, fmt, stem=f"{stem}_clean"
            )
            c.download_card(
                f"Clean data ({fmt.upper()})",
                "table_view",
                lambda p=payload: ui.download(p.data, filename=p.filename, media_type=p.mime),
            )

        issues = outcome.issues
        if not issues.empty:
            c.download_card(
                "Issues (CSV)",
                "report",
                lambda: ui.download(
                    issues.to_csv(index=False).encode("utf-8"),
                    filename=f"{stem}_issues.csv",
                    media_type="text/csv",
                ),
                f"{len(issues)} row(s) flagged for review.",
            )

        lineage = outcome.pipeline.lineage_log()
        if not lineage.empty:
            c.download_card(
                "Lineage (CSV)",
                "account_tree",
                lambda: ui.download(
                    lineage.to_csv(index=False).encode("utf-8"),
                    filename=f"{stem}_lineage.csv",
                    media_type="text/csv",
                ),
                f"{len(lineage)} recorded transformations.",
            )
        elif limits.lineage is False:
            ui.label("Lineage tracking is a licensed feature.").classes(
                "text-xs text-gray-500"
            )

        with ui.tabs().classes("w-full mt-6") as tabs:
            clean_tab = ui.tab("Clean data")
            issues_tab = ui.tab("Issues")
            report_tab = ui.tab("QA report")
            logs_tab = ui.tab("Logs")

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
            with ui.tab_panel(report_tab):
                # An iframe, not ``ui.html``: a full report runs to hundreds of
                # kilobytes, which exceeds the WebSocket message limit and
                # drops the connection. Fetching it over HTTP keeps the socket
                # alive.
                if outcome.report_token:
                    ui.element("iframe").props(
                        f'src="{report_url(outcome.report_token)}"'
                    ).classes("w-full border rounded-lg bg-white").style(
                        "height:75vh"
                    )
                else:
                    # No token means the report was not published; embed
                    # nothing and offer the file instead of risking the socket.
                    c.download_card(
                        "QA report (HTML)",
                        "description",
                        download_html_report,
                        "Open the report directly in a new tab.",
                    )
            with ui.tab_panel(logs_tab):
                ui.label("Mapping log").classes("font-semibold")
                c.file_table(outcome.pipeline.mapping_log())
                ui.label("Cleaning log").classes("font-semibold mt-4")
                c.file_table(outcome.pipeline.cleaning_log())