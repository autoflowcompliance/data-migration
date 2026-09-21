"""Route ``/`` — what this does, and one obvious way to start."""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from app_files.branding import load_branding
from app_files.interface.web import components as c
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
]


@ui.page("/")
def home_page() -> None:
    theme.inject_theme()
    with page_shell(NAV, active="/"):
        branding = load_branding()
        with ui.column().classes("dr-hero gap-0"):
            ui.html(
                f'<h1>{branding.company_name}: your data, ready for '
                "whatever comes next.</h1>"
            )
            ui.html(
                "<p>Clean, map, validate and profile CRM exports, bank statements, "
                "ledgers and invoices. One tool, any format, and it runs on your "
                "own machine.</p>"
            )
            with ui.row().classes("gap-3"):
                theme.button(
                    "Upload a file", on_click=lambda: ui.navigate.to("/upload")
                ).props("size=lg")
                theme.download_button(
                    "Try the samples", on_click=lambda: ui.navigate.to("/upload")
                ).props("size=lg")

        c.section("What you get")
        with ui.element("div").classes("dr-feature-grid"):
            for icon_name, title, body in _FEATURES:
                with ui.element("div").classes("dr-card"):
                    ui.icon(icon_name).classes("text-2xl").style(f"color:{theme.AMBER}")
                    ui.label(title).classes("font-semibold mt-1")
                    ui.label(body).classes("text-sm").style(f"color:{theme.SLATE}")

        c.section("How it works")
        c.progress_checklist(
            [
                "Ingest — CSV, Excel, JSON or a bank-statement PDF",
                "Clean — trim whitespace, normalise casing, remove duplicates",
                "Map — match source columns onto the target system's fields",
                "Validate — required fields, types, uniqueness, custom rules",
                "Profile — five independent quality scores",
                "Deliver — clean data, QA report, issue list, full lineage",
            ],
            current=-1,
        )

        ui.html(
            '<div class="dr-trust"><strong>Your data never leaves your computer.</strong> '
            "In client mode the whole pipeline runs locally. Nothing is uploaded "
            "anywhere.</div>"
        )


_FEATURES = [
    (
        "cleaning_services",
        "Cleaning that says what it did",
        "Every trimmed space, normalised phone number and dropped duplicate is "
        "recorded in a log you can hand to a client.",
    ),
    (
        "account_tree",
        "Row-level lineage",
        "Any value in the output can be traced back to the exact source row and "
        "the transform that produced it.",
    ),
    (
        "fact_check",
        "Validation with an opinion",
        "Required fields, unique keys, types, ranges and list membership — plus "
        "your own YAML rules per target system.",
    ),
    (
        "speed",
        "Five quality scores",
        "Completeness, uniqueness, validity, consistency and timeliness, each "
        "scored independently and honestly.",
    ),
    (
        "description",
        "Reports clients understand",
        "A QA report, an issue list and a clean file — branded with your own "
        "company name and logo.",
    ),
    (
        "folder_copy",
        "Whole folders at once",
        "Point it at an inbox and get one clean folder plus a combined dashboard "
        "per file.",
    ),
]  # : tuple of (icon, title, body)