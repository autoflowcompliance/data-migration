"""Route ``/upload`` — the primary action, plus a no-upload path for prospects.

The sample button exists so a demo visitor sees a real result in seconds
without hunting for a file, which is the difference between a live link that
converts and one that gets closed.
"""

from __future__ import annotations

from nicegui import ui

from app_files.ingestion import UnsupportedFormatError
from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import LimitExceededError, check_file_size, current_mode

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
]

# Build order must match the numbering supplied to the pipeline: the core
# pipeline runs clean, then map, then validate, then report.
PROCESS_STEPS = [
    "Reading the file",
    "Cleaning and de-duplicating",
    "Mapping to the target fields",
    "Validating and scoring",
]


@ui.page("/upload")
def upload_page() -> None:
    theme.inject_theme()
    licence, limits = current_mode()

    with page_shell(NAV, active="/upload"):
        c.page_header(
            "Upload your file",
            "CSV, Excel, JSON or a bank-statement PDF. Everything is processed "
            "in memory and, in client mode, on this machine.",
        )

        templates = state.templates_on_disk()

        with ui.row().classes("gap-4 items-end w-full"):
            template_select = ui.select(
                templates, value="hubspot" if "hubspot" in templates else templates[0],
                label="Target config",
            ).classes("min-w-56").props("outlined dense")
            format_select = ui.select(
                state.format_choices(limits), value=state.format_choices(limits)[0],
                label="Output format",
            ).classes("min-w-40").props("outlined dense")

        status = ui.column().classes("w-full gap-1")
        checklist_slot = ui.column().classes("w-full")

        def choose_format(value: str) -> str:
            return value.strip().lower()

        def start_run(frame, source_name: str) -> None:
            """Apply limits, run the pipeline and hand off to the results page."""
            checklist_slot.clear()
            with checklist_slot:
                c.section("Processing")
                c.progress_checklist(PROCESS_STEPS, current=0)
            try:
                outcome = state.run_migration(
                    frame,
                    source_name=source_name,
                    template=template_select.value,
                    limits=limits,
                    branding=None,
                )
            except Exception as exc:  # noqa: BLE001 - surfaced to the user
                checklist_slot.clear()
                ui.notify(f"The migration failed: {exc}", type="negative", multi_line=True)
                status.clear()
                with status:
                    ui.label(f"Could not process `{source_name}`.").classes(
                        "text-red-600 font-medium"
                    )
                    ui.label(str(exc)).classes("text-xs text-gray-500")
                return

            session_store.set_outcome(outcome)
            session_store.session().template = template_select.value
            session_store.session().output_format = choose_format(format_select.value)
            status.clear()
            with status:
                c.metric_row(
                    [
                        (outcome.summary.get("rows_in", len(frame)), "Rows in"),
                        (len(outcome.pipeline.clean_frame), "Rows out"),
                        (outcome.summary.get("errors", 0), "Errors", theme.BAD),
                        (outcome.summary.get("warnings", 0), "Warnings", theme.WARN),
                        (f"{outcome.score}%", "Quality score", theme.score_colour(outcome.score)),
                    ]
                )
            ui.notify(f"Processed {source_name}", type="positive")
            ui.navigate.to("/results")

        def handle_upload(event) -> None:
            data = event.content.read()
            name = event.name
            try:
                check_file_size(len(data), limits)
            except LimitExceededError as exc:
                ui.notify(str(exc), type="warning", multi_line=True)
                return
            try:
                frame = state.read_upload(data, name)
            except (UnsupportedFormatError, ValueError) as exc:
                ui.notify(str(exc), type="negative", multi_line=True)
                return
            start_run(frame, name)

        async def load_sample() -> None:
            """Process a bundled sample with no upload at all."""
            entry = _sample_for(template_select.value)
            try:
                frame = state.load_sample(entry["file"])
            except Exception as exc:  # noqa: BLE001
                ui.notify(f"Could not read the sample: {exc}", type="negative")
                return
            template_select.value = entry["template"]
            start_run(frame, entry["file"])

        with ui.row().classes("w-full items-center"):
            ui.upload(
                on_upload=handle_upload,
                max_file_size=int((limits.max_file_size_mb or 1024) * 1024 * 1024),
                auto_upload=True,
                label="Drop a file here or click to choose",
            ).classes("dr-dropzone w-full")

        ui.separator().classes("my-4")
        with ui.row().classes("items-center gap-3"):
            ui.label("No file handy?").classes("text-sm text-gray-500")
            theme.download_button(
                "Try it with sample data", on_click=load_sample
            ).mark("sample-button")

        if limits.demo:
            ui.html(
                '<div class="dr-trust">Demo mode: files are limited to '
                f"{limits.max_file_size_mb:g} MB and {limits.max_rows:,} rows, and the "
                "report is watermarked. Everything else works exactly as it does "
                "in the full tool.</div>"
            )


def _sample_for(template: str) -> dict[str, str]:
    """Pick the sample that best matches the currently selected config."""
    samples = state.available_samples()
    for entry in samples:
        if entry["template"] == template:
            return entry
    return samples[0]