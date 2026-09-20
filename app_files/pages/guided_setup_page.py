"""Guided setup — templates, a five-step wizard, and the install check.

Lives in ``app_files/pages/``, so Streamlit's native multipage navigation
discovers it automatically. Independent of the CRM tool: it calls the onboarding
layer and the frozen core, and cannot break either.

Three things live here:

* the template library — pick a pack, read what it does, run it on its own sample
* the five-step wizard — upload, template, preview, run, download
* the install check — confirm the machine can run the tool
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app_files.ingestion import UnsupportedFormatError, read_any
from app_files.onboarding.templates import (
    all_templates,
    available_templates,
    load_template,
    render_template_result,
    run_template,
)
from app_files.onboarding.verifier import run_checks
from app_files.onboarding.wizard import (
    STEP_COUNT,
    WizardState,
    restart_wizard,
    should_show_wizard,
    steps_text,
)

st.set_page_config(page_title="Guided setup", page_icon="◆", layout="wide")


def _start_new_run() -> None:
    """Clear the wizard's own progress and show step one again.

    Distinct from the sidebar's "Restart wizard": this is what you press when
    you want to clean another file without leaving the page.
    """
    state = WizardState.load()
    state.step = 0
    state.completed = False
    state.run_summary = None
    state.save()
    for key in ("wizard_file", "wizard_template", "wizard_source", "wizard_result"):
        st.session_state.pop(key, None)


def _execute_migration(state: WizardState) -> str | None:
    """Run the wizard's file through the chosen template; return an error, if any.

    Shared by the preview and run steps so both paths produce the same result.
    The file is read from ``wizard_source`` rather than the uploader widget,
    because Streamlit discards a widget's state once that widget stops being
    rendered — which is exactly what happens on every step after the first.
    """
    source = st.session_state.get("wizard_source")
    if not source:
        if state.source_filename:
            return "Please re-upload your file — the upload is not kept between steps."
        return "Upload a file first."
    try:
        data = source["data"]
        frame = read_any(data, filename=source["name"])
        if state.template and state.template in available_templates():
            result = run_template(state.template, source=frame)
        else:
            from app_files.pipeline import run_pipeline

            result = run_pipeline(frame, crm="hubspot", source_filename=source["name"])
        st.session_state["wizard_result"] = result
        state.run_summary = result.summary()
        state.save()
    except UnsupportedFormatError as exc:
        return f"Unsupported file type: {exc}"
    except Exception as exc:  # noqa: BLE001 - the UI must never crash
        return f"Could not run that file: {exc}"
    return None


# --------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Setup")
    if st.button("Restart wizard", key="restart_wizard_button"):
        restart_wizard()
        for key in ("wizard_file", "wizard_template", "wizard_source", "wizard_result"):
            st.session_state.pop(key, None)
        st.rerun()
    st.caption("Shows the five-step setup again from the beginning.")

wizard_state = WizardState.load()
show_wizard = should_show_wizard()

st.html(
    """
    <div style="background:#14181F; border-radius:10px; padding:24px 28px; margin-bottom:16px;">
        <div style="color:#F7F6F3; font-size:1.3rem; font-weight:600;">Guided setup</div>
        <div style="color:#AEB6C2; font-size:.92rem; margin-top:4px;">
            Pick a template, run it, and download the results. No configuration files.
        </div>
    </div>
    """
)

_wizard_tab, _templates_tab, _install_tab = st.tabs(
    ["Wizard", "Template library", "Install check"]
)


# =============================================================== wizard
with _wizard_tab:
    if not show_wizard and st.session_state.get("wizard_file") is None:
        st.success(
            "Setup is complete. You can clean another file any time — "
            "press **Restart wizard** in the sidebar, or use the form below."
        )
        if st.button("Clean another file"):
            _start_new_run()
            st.rerun()

    if show_wizard or st.session_state.get("wizard_file") is not None:
        state = WizardState.load()
        if state.completed and not show_wizard:
            state = state.restart()
            state.save()

        # Progress rail
        st.progress((state.step + 1) / STEP_COUNT)
        st.caption(f"Step {state.step + 1} of {STEP_COUNT} — {state.step_name}")

        _steps = steps_text()

        # ---------------------------------------------------- step 1: upload
        if state.step == 0:
            st.subheader(state.step_name)
            st.write(_steps[0]["instruction"])
            uploaded = st.file_uploader(
                "Your file",
                type=["csv", "tsv", "txt", "json", "xlsx", "xlsm", "xls", "pdf"],
                key="wizard_file",
            )
            if uploaded is not None:
                state.source_filename = uploaded.name
                state.save()
                # Keep the bytes in session state: the uploader widget itself is
                # gone from the next step onward, and with it any way to re-read
                # the file.
                st.session_state["wizard_source"] = {
                    "name": uploaded.name,
                    "data": uploaded.getvalue(),
                }
                st.success(f"Loaded {uploaded.name}.")
            elif state.source_filename:
                st.info(f"Using {state.source_filename}.")

        # -------------------------------------------------- step 2: template
        elif state.step == 1:
            st.subheader(state.step_name)
            st.write(_steps[1]["instruction"])
            options = available_templates()
            index = options.index(state.template) if state.template in options else 0
            chosen = st.selectbox("Template", options, index=index, key="wizard_template")
            if chosen:
                pack = load_template(chosen)
                state.template = chosen
                state.save()
                st.markdown(f"**{pack.title}**")
                st.write(pack.readme())
                if st.checkbox("Preview sample input"):
                    st.dataframe(pd.read_csv(pack.sample_path), use_container_width=True)

        # --------------------------------------------------- step 3: preview
        elif state.step == 2:
            st.subheader(state.step_name)
            st.write(_steps[2]["instruction"])
            summary = state.run_summary
            if summary is None:
                # The preview has nothing to show until the run happens, so the
                # run happens here rather than stranding the user on a gate they
                # cannot open from this step.
                with st.spinner("Running the migration…"):
                    error = _execute_migration(state)
                summary = state.run_summary
                if error:
                    st.error(error)
            if summary is not None:
                columns = st.columns(3)
                columns[0].metric("Rows in", summary.get("rows_in"))
                columns[1].metric("Rows out", summary.get("rows_out"))
                columns[2].metric("Quality score", f"{summary.get('quality_score')}%")
                st.caption(
                    f"{summary.get('duplicates_removed')} duplicate rows removed · "
                    f"{summary.get('errors')} errors · {summary.get('warnings')} warnings"
                )
                result = st.session_state.get("wizard_result")
                if result is not None:
                    st.dataframe(result.clean_frame.head(20), use_container_width=True)

        # ------------------------------------------------------- step 4: run
        elif state.step == 3:
            st.subheader(state.step_name)
            st.write(_steps[3]["instruction"])
            st.caption(
                "Running uses the template you chose, or the raw file when no template applies."
            )
            if state.run_summary is not None:
                st.info("This run is ready — continue to step 5 to download.")
            if st.button("Run it again", type="primary"):
                error = _execute_migration(state)
                if error:
                    st.error(error)
                else:
                    st.success("Done. Continue to step 5 to download.")

        # -------------------------------------------------- step 5: download
        elif state.step == 4:
            st.subheader(state.step_name)
            st.write(_steps[4]["instruction"])
            result = st.session_state.get("wizard_result")
            if result is None:
                st.warning("Run the migration first (step 4).")
            else:
                from app_files.output.inmemory import to_bytes
                from app_files.utilities.fix_summary import render_summary_markdown, write_summary

                try:
                    fix = write_summary(result)
                    st.success(fix.paragraph())
                except Exception:  # noqa: BLE001 - the summary is a bonus, not a blocker
                    pass
                columns = st.columns(3)
                for column, (fmt, label) in zip(
                    columns, [("csv", "Clean data (CSV)"), ("excel", "Clean data (Excel)"), ("json", "Clean data (JSON)")]
                ):
                    payload = to_bytes(result.clean_frame, fmt)
                    column.download_button(
                        label, payload.data, file_name=payload.filename, mime=payload.mime
                    )
                st.download_button(
                    "QA report (HTML)",
                    result.qa_report_html.encode("utf-8"),
                    file_name="qa_report.html",
                    mime="text/html",
                )
                with st.expander("Plain-English summary"):
                    st.markdown(render_summary_markdown(fix))

        # ------------------------------------------------------- navigation
        st.divider()
        left, middle, right = st.columns([1, 1, 2])
        with left:
            if not state.is_first and st.button("Back"):
                state.back()
                state.completed = True if state.step >= STEP_COUNT - 1 else state.completed
                state.save()
                st.rerun()
        with middle:
            if not state.is_last:
                allowed, reason = state.can_advance()
                if st.button("Next", disabled=not allowed):
                    state.next()
                    state.save()
                    st.rerun()
                if not allowed:
                    st.caption(reason)
            else:
                if st.button("Finish", type="primary"):
                    state.finish()
                    st.session_state.pop("wizard_file", None)
                    st.rerun()


# ============================================================ templates
with _templates_tab:
    st.subheader("Template library")
    st.caption("Pre-built configurations. Pick one, see what it does, run it on its own sample.")
    names = available_templates()
    st.markdown(f"**{len(names)} templates available:** " + ", ".join(names))
    selected = st.selectbox("Choose a template", names, key="templates_selector")
    if selected:
        pack = load_template(selected)
        st.markdown(f"### {pack.title}")
        missing = pack.missing_files()
        if missing:
            st.error("Incomplete pack — missing: " + ", ".join(missing))
        else:
            st.success("Pack is complete: config, readme, sample and expected output all present.")
        st.markdown(pack.readme())
        st.markdown("**Sample input**")
        st.dataframe(pd.read_csv(pack.sample_path), use_container_width=True)
        if st.button("Preview sample", key="preview_sample_button"):
            try:
                actual = render_template_result(selected)
                expected = pd.read_csv(pack.expected_path, dtype=str, keep_default_na=False)
                st.markdown("**What the template produces**")
                st.dataframe(actual, use_container_width=True)
                if pack.expected_path.exists():
                    same = actual.astype(str).reset_index(drop=True).equals(
                        expected.astype(str).reset_index(drop=True)
                    )
                    (st.success if same else st.warning)(
                        "Matches expected_output.csv."
                        if same
                        else "Differs from expected_output.csv — see the regression suite."
                    )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not run that template: {exc}")


# ========================================================= install check
with _install_tab:
    st.subheader("Install check")
    st.caption("Confirms this machine has everything the tool needs.")
    if st.button("Run the install check", type="primary", key="install_check_button"):
        report = run_checks()
        for check in report.checks:
            (st.success if check.passed else st.error)(f"{check.name}: {check.detail}")
        summary = report.summary()
        if summary["ok"]:
            st.markdown(
                f"**All clear — {summary['passed']} of {summary['total']} checks passed.**"
            )
        else:
            st.markdown(
                f"**{len(summary['failed'])} check(s) failed: {', '.join(summary['failed'])}**"
            )