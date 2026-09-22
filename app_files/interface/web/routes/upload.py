"""Route ``/upload`` — the primary action, plus a no-upload path for prospects.

Two job types share this page. A CRM export is one file through the pipeline; a
bank reconciliation is a statement plus a ledger. They differ only in what they
collect here — both hand a :class:`~app_files.interface.web.state.RunOutcome` to
``/results``, so the results page has one shape to render.

The sample button exists so a demo visitor sees a real result in seconds
without hunting for a file, which is the difference between a live link that
converts and one that gets closed. It deliberately does not count against the
demo's run allowance: a visitor who never uploads anything still needs to see
the output.
"""

from __future__ import annotations

from nicegui import ui

from app_files.ingestion import UnsupportedFormatError
from app_files.interface.web import components as c
from app_files.interface.web import session as session_store
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import (
    LimitExceededError,
    check_file_size,
    current_mode,
)
from app_files.settings import purchase_url

NAV = [
    ("Home", "/demo"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
]

# Build order must match the numbering supplied to the pipeline: the core
# pipeline runs clean, then map, then validate, then report.
PROCESS_STEPS = [
    "Reading the file",
    "Cleaning and de-duplicating",
    "Mapping to the target fields",
    "Validating and scoring",
]

CRM_JOB = "CRM export"
RECON_JOB = "Bank reconciliation"

# The user-facing workflow, distinct from PROCESS_STEPS (the pipeline's own
# internal phases shown as a live checklist beneath it).
WORKFLOW_STEPS = ["Upload", "Configure", "Process", "Review"]


@ui.page("/upload")
def upload_page() -> None:
    theme.inject_theme()
    licence, limits = current_mode()
    allowance = limits.max_runs_per_session
    buy_url = purchase_url()

    with page_shell(NAV, active="/upload"):
        c.page_header(
            "Upload your file",
            "CSV, Excel, JSON or a bank-statement PDF. Everything is processed "
            "in memory and, in client mode, on this machine.",
        )

        steps_slot = ui.column().classes("w-full")

        def show_steps(current: int) -> None:
            """Draw the workflow stepper at ``current`` (0-indexed).

            Redrawn rather than built once because the page stays mounted while
            the run happens: the marker has to move from Upload to Process in
            place, not on a fresh page load.
            """
            steps_slot.clear()
            with steps_slot:
                c.step_indicator(WORKFLOW_STEPS, current)

        show_steps(0)

        config_row = ui.row().classes("gap-4 items-end w-full")
        with config_row:
            template_select = c.select(
                state.templates_on_disk(),
                "Target config",
                value=_default_template(),
            ).classes("min-w-56")
            format_select = c.select(
                state.format_choices(limits),
                "Output format",
                value=state.format_choices(limits)[0],
            ).classes("min-w-40")

        status = ui.column().classes("w-full gap-1")
        checklist_slot = ui.column().classes("w-full")

        def start_run(outcome) -> None:
            """Store a finished outcome and move to the results page."""
            show_steps(3)
            session_store.set_outcome(outcome)
            session_store.session().template = template_select.value
            session_store.session().output_format = str(format_select.value).strip().lower()
            ui.notify(f"Processed {outcome.source_name}", type="positive")
            ui.navigate.to("/results")

        def claim_run() -> bool:
            """Consume one demo run, or explain why the run is blocked.

            Checked and consumed in one place, before any work happens, so a
            blocked 4th attempt cannot half-execute. Returns ``True`` when the
            caller may proceed.
            """
            if allowance is None:
                return True
            if session_store.runs_remaining(allowance) == 0:
                status.clear()
                with status:
                    c.runs_exhausted_note(buy_url, allowance)
                return False
            session_store.register_run()
            return True

        def run_crm(frame, source_name: str) -> None:
            show_steps(2)
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
                _show_failure(checklist_slot, status, source_name, exc)
                return
            status.clear()
            with status:
                summary = outcome.summary
                c.metric_row(
                    [
                        (summary.get("rows_in", len(frame)), "Rows in"),
                        (len(outcome.pipeline.clean_frame), "Rows out"),
                        (summary.get("errors", 0), "Errors", theme.BAD),
                        (summary.get("warnings", 0), "Warnings", theme.WARN),
                        (f"{outcome.score}%", "Quality score", theme.score_colour(outcome.score)),
                    ]
                )
            start_run(outcome)

        def run_reconciliation(bank, ledger, source_name: str) -> None:
            show_steps(2)
            checklist_slot.clear()
            with checklist_slot:
                c.section("Processing")
                c.progress_checklist(PROCESS_STEPS, current=0)
            try:
                outcome = state.run_reconciliation_migration(
                    bank, ledger, source_name=source_name, limits=limits
                )
            except Exception as exc:  # noqa: BLE001 - surfaced to the user
                _show_failure(checklist_slot, status, source_name, exc)
                return
            checklist_slot.clear()
            start_run(outcome)

        def handle_crm_upload(event) -> None:
            data, name = event.content.read(), event.name
            if not _accept(data, name, limits):
                return
            try:
                frame = state.read_upload(data, name)
            except (UnsupportedFormatError, ValueError) as exc:
                ui.notify(str(exc), type="negative", multi_line=True)
                return
            if claim_run():
                run_crm(frame, name)

        def handle_bank_upload(event) -> None:
            data, name = event.content.read(), event.name
            if not _accept(data, name, limits):
                return
            try:
                bank_state["frame"] = state.read_upload(data, name)
            except (UnsupportedFormatError, ValueError) as exc:
                ui.notify(str(exc), type="negative", multi_line=True)
                return
            bank_state["name"] = name
            _maybe_reconcile()

        def handle_ledger_upload(event) -> None:
            data, name = event.content.read(), event.name
            if not _accept(data, name, limits):
                return
            try:
                ledger_state["frame"] = state.read_upload(data, name)
            except (UnsupportedFormatError, ValueError) as exc:
                ui.notify(str(exc), type="negative", multi_line=True)
                return
            ledger_state["name"] = name
            _maybe_reconcile()

        bank_state: dict = {"frame": None, "name": ""}
        ledger_state: dict = {"frame": None, "name": ""}

        def _maybe_reconcile() -> None:
            if bank_state["frame"] is None or ledger_state["frame"] is None:
                return
            if claim_run():
                run_reconciliation(
                    bank_state["frame"], ledger_state["frame"],
                    bank_state["name"] or "reconciliation",
                )

        async def load_sample() -> None:
            """Process a bundled sample with no upload at all.

            Not counted against the allowance: this is the guided tour, not a
            real run, so it must work even after the allowance is spent.

            The sample follows the JOB TYPE, not the config selector — on the
            reconciliation tab the sample must be a statement/ledger pair, and
            picking by config would silently run a CRM migration instead.
            """
            entry = _sample_for(job_type.value, template_select.value)
            try:
                frame = state.load_sample(entry["file"])
            except Exception as exc:  # noqa: BLE001
                ui.notify(f"Could not read the sample: {exc}", type="negative")
                return
            template_select.value = entry["template"]
            if entry["template"] == "bank_reconciliation":
                # A reconciliation sample is one half of a pair; pick the file
                # by extension and pair it with its counterpart.
                ledger_name = _LEDGER_FOR.get(entry["file"])
                if ledger_name:
                    bank_frame, ledger_frame = (
                        (state.load_sample(ledger_name), frame)
                        if entry["file"] == "ledger.csv"
                        else (frame, state.load_sample(ledger_name))
                    )
                    outcome = state.run_reconciliation_migration(
                        bank_frame, ledger_frame,
                        source_name=entry["file"], limits=limits,
                    )
                    start_run(outcome)
                    return
            run_crm(frame, entry["file"])

        job_type = ui.radio(
            [CRM_JOB, RECON_JOB], value=CRM_JOB
        ).props("inline").classes("dr-radio")

        uploader_row = ui.column().classes("w-full gap-2")

        def render_uploader() -> None:
            """Swap the uploader and the config row to match the job type.

            A reconciliation PAIRS a statement with a ledger; a CRM export
            maps one file onto a target config. Showing the config selector for
            a reconciliation would invite the user to change something that
            has no effect on the run.
            """
            uploader_row.clear()
            config_row.set_visibility(job_type.value == CRM_JOB)
            with uploader_row:
                if job_type.value == CRM_JOB:
                    ui.upload(
                        on_upload=handle_crm_upload,
                        max_file_size=_max_bytes(limits),
                        auto_upload=True,
                        label="Drop a file here or click to choose",
                    ).classes("dropzone dr-dropzone w-full")
                else:
                    with ui.row().classes("w-full gap-4"):
                        with ui.column().classes("flex-1"):
                            ui.label("Bank statement").classes("text-sm font-semibold")
                            ui.upload(
                                on_upload=handle_bank_upload,
                                max_file_size=_max_bytes(limits),
                                auto_upload=True,
                                label="Bank statement (CSV or PDF)",
                            ).classes("dropzone dr-dropzone w-full")
                        with ui.column().classes("flex-1"):
                            ui.label("Your ledger").classes("text-sm font-semibold")
                            ui.upload(
                                on_upload=handle_ledger_upload,
                                max_file_size=_max_bytes(limits),
                                auto_upload=True,
                                label="Ledger (CSV or PDF)",
                            ).classes("dropzone dr-dropzone w-full")

        job_type.on_value_change(lambda _: render_uploader())
        render_uploader()

        ui.separator().classes("my-4")
        with ui.row().classes("items-center gap-3"):
            ui.label("No file handy?").classes("text-sm").style(f"color:{theme.SLATE}")
            theme.download_button(
                "Try it with sample data", on_click=load_sample
            ).mark("sample-button")

        if limits.demo:
            _run_allowance_note(allowance, buy_url)


def _default_template() -> str:
    templates = state.templates_on_disk()
    return "hubspot" if "hubspot" in templates else templates[0]


def _max_bytes(limits) -> int:
    """The uploader's own ceiling, generous when the mode sets none."""
    return int((limits.max_file_size_mb or 1024) * 1024 * 1024)


def _accept(data: bytes, name: str, limits) -> bool:
    """Apply the file-size rule. Returns ``False`` when the upload is rejected."""
    try:
        check_file_size(len(data), limits)
        return True
    except LimitExceededError as exc:
        ui.notify(str(exc), type="warning", multi_line=True)
        return False


def _show_failure(slot, status, source_name: str, exc: Exception) -> None:
    slot.clear()
    ui.notify(f"The migration failed: {exc}", type="negative", multi_line=True)
    status.clear()
    with status:
        ui.label(f"Could not process `{source_name}`.").classes("font-medium").style(
            f"color:{theme.DANGER}"
        )
        ui.label(str(exc)).classes("text-xs").style(f"color:{theme.SLATE}")


def _sample_for(job_type: str, template: str) -> dict[str, str]:
    """Pick the sample that best matches what the user is about to run.

    Two signals, in order: the job type decides the *kind* of sample (a CRM
    export vs a bank statement), and the config selector picks between samples
    of that kind. Honouring only the config selector sends the reconciliation
    tab a CRM sample, which then runs as a mapping job — a silent wrong answer.
    """
    samples = state.available_samples()
    wants_reconciliation = job_type == RECON_JOB
    for entry in samples:
        is_recon = entry["template"] == "bank_reconciliation"
        if is_recon == wants_reconciliation and (
            wants_reconciliation or entry["template"] == template
        ):
            return entry
    for entry in samples:
        if (entry["template"] == "bank_reconciliation") == wants_reconciliation:
            return entry
    return samples[0]


_LEDGER_FOR = {"bank_statement.pdf": "ledger.csv", "bank_statement.csv": "ledger.csv"}


def _run_allowance_note(allowance: int | None, buy_url: str) -> None:
    """A live count of the remaining demo runs, under the uploader."""
    if allowance is None:
        return
    remaining = session_store.runs_remaining(allowance)
    if remaining is None:
        return
    if remaining > 0:
        c.info_note(
            f"{remaining} of {allowance} demo runs left in this session. "
            "The licensed version has no limit."
        )
    else:
        c.runs_exhausted_note(buy_url, allowance)
