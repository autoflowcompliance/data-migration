"""Route ``/batch`` — process a folder of files, client mode only.

Batch is a licensed feature: the page renders an upsell instead of the form
when the active limits forbid it, so an unlicensed install cannot accidentally
run an unbounded folder job on the hosted demo.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from app_files.batch import run_batch, supported_files
from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import current_mode
from app_files.settings import purchase_url

NAV = [
    ("Home", "/demo"),
    ("Upload", "/upload"),
    ("Batch", "/batch"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
]


@ui.page("/batch")
def batch_page() -> None:
    theme.inject_theme()
    _licence, limits = current_mode()

    with page_shell(NAV, active="/batch"):
        c.page_header(
            "Batch processing",
            "Point DataFlow at a folder and get one clean output per file, plus "
            "a combined summary and dashboard.",
        )

        if not limits.batch:
            c.empty_state(
                "lock",
                "Batch processing is not enabled in this mode",
                "Folder processing needs a licence. A licence also unlocks every "
                "output format and unbounded row counts.",
                "See the licence options",
                lambda: ui.navigate.to(purchase_url()),
            )
            return

        templates = state.templates_on_disk()
        input_state = {"dir": str(Path.cwd() / "samples")}
        allowance = limits.batch_max_files

        with ui.row().classes("gap-4 items-end w-full"):
            template_select = c.select(
                templates,
                "Target config",
                value="hubspot" if "hubspot" in templates else templates[0],
            ).classes("min-w-56")
            format_select = c.select(
                state.allowed_formats(limits), "Output format", value="csv"
            ).classes("min-w-40")

        dir_input = c.field("Input folder", value=input_state["dir"]).classes("w-full")
        out_input = c.field(
            "Output folder", value=str(Path.cwd() / "batch_output")
        ).classes("w-full")

        found = ui.label("").classes("text-sm").style(f"color:{theme.SLATE}")

        def refresh_count() -> None:
            files = supported_files(dir_input.value or "")
            if not files:
                found.text = "No supported files in that folder."
                return
            if allowance is not None and len(files) > allowance:
                # Say so up front rather than silently processing a subset and
                # leaving the user to notice.
                found.text = (
                    f"{len(files)} supported file(s) found — the demo processes "
                    f"the first {allowance}."
                )
            else:
                found.text = f"{len(files)} supported file(s) found."

        dir_input.on_value_change(lambda _: refresh_count())
        refresh_count()

        progress = ui.column().classes("w-full gap-1")

        def start_batch() -> None:
            files = supported_files(dir_input.value or "")
            if not files:
                ui.notify("That folder has no supported files.", type="warning")
                return
            if allowance is not None:
                files = files[:allowance]
            progress.clear()
            steps = [f"{path.name}" for path in files]

            def on_progress(index: int, total: int, name: str) -> None:
                progress.clear()
                with progress:
                    ui.label(f"Processing {index} of {total}: {name}").classes("text-sm")
                    c.progress_checklist(steps, current=index - 1)

            result = run_batch(
                dir_input.value,
                template=template_select.value,
                output_dir=out_input.value,
                output_format=str(format_select.value).lower(),
                files=files,
                on_progress=on_progress,
            )
            session_store.session().batch = result
            progress.clear()
            with progress:
                c.section("Batch complete")
                c.metric_row(
                    [
                        (result.processed, "Files"),
                        (result.succeeded, "Succeeded"),
                        (result.failed, "Failed", theme.BAD if result.failed else None),
                        (f"{result.total_rows_out:,}", "Rows out"),
                        (result.average_score, "Average score"),
                    ]
                )
                ui.label(f"Output written to {result.output_dir}").classes(
                    "text-sm"
                ).style(f"color:{theme.SLATE}")
                c.file_table(_summary_frame(result))

        theme.button("Run batch", on_click=start_batch).mark(
            "run-batch"
        )


def _summary_frame(result):
    from app_files.batch import summary_frame

    return summary_frame(result)