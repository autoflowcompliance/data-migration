"""DataFlow — the web UI.

Upload a messy file, get a clean one back. Four steps: upload, configure,
process, review.

Run it with ``python -m streamlit run app_files/dataflow/app.py``, or via
``python main.py`` (the Docker/Render entrypoint) with
``DATAREADY_UI=dataflow``.

This module is the page: it builds widgets and delegates every decision to
:mod:`app_files.dataflow.state`. Keep it thin — the logic there is tested, and
logic added here is not.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# `streamlit run app_files/dataflow/app.py` sets __package__ to "" — the repo
# root must be importable for `app_files...` imports to resolve.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app_files.dataflow import state  # noqa: E402
from app_files.dataflow.components import (  # noqa: E402
    download_card,
    empty_state,
    metric_card,
    score_badge,
    step_indicator,
    unavailable_note,
)
from app_files.dataflow.theme import inject_theme  # noqa: E402
from app_files.licensing import current_mode  # noqa: E402

st.set_page_config(page_title="DataFlow", page_icon="🗂️", layout="wide")
inject_theme()

licence, limits = current_mode()

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
_DEFAULTS: dict[str, object] = {
    "df_step": 0,
    "df_job_type": state.JOB_CRM,
    "df_history": [],
    "df_crm": "hubspot",
    "df_remove_dupes": True,
    "df_date_first": False,
    "df_region": "US",
    "df_tolerance": 2,
    "df_bank_date_col": state.DEFAULT_DATE_COLUMN,
    "df_bank_amount_col": state.DEFAULT_AMOUNT_COLUMN,
    "df_ledger_date_col": state.DEFAULT_DATE_COLUMN,
    "df_ledger_amount_col": state.DEFAULT_AMOUNT_COLUMN,
}
for _key, _value in _DEFAULTS.items():
    st.session_state.setdefault(_key, _value)


def go_to(step: int) -> None:
    st.session_state.df_step = step
    st.rerun()


def start_over() -> None:
    """Clear the run, keeping the dashboard counters."""
    for key in list(st.session_state.keys()):
        if key.startswith("df_") and key != "df_history":
            del st.session_state[key]
    st.session_state.df_step = 0
    st.rerun()


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.html(
    """
    <div style="background:var(--ink); border-radius:4px 4px 10px 10px; padding:28px 32px;
                margin-bottom:24px; border-top:8px solid var(--amber);">
        <div style="font-family:'Fraunces', serif; color:var(--surface); font-size:1.6rem; font-weight:600;">
            DataFlow
        </div>
        <div style="color:#C7BEAE; font-size:.95rem; margin-top:4px;">
            Upload a messy file, get a clean one back.
        </div>
    </div>
    """
)

if limits.demo:
    st.caption(
        "Demo mode: up to 500 rows, 5 MB, CSV output, watermarked report. "
        "A licence removes these limits."
    )


# --------------------------------------------------------------------------
# Dashboard metrics
# --------------------------------------------------------------------------
history = st.session_state.df_history
configs = state.crm_choices()

dcols = st.columns(3)
with dcols[0]:
    metric_card(len(history), "Files run this session")
with dcols[1]:
    average = round(sum(entry["quality"] for entry in history) / len(history), 1) if history else "—"
    metric_card(average, "Avg quality score")
with dcols[2]:
    metric_card(len(configs), "Target configs available")

st.write("")
step_indicator(list(state.STEPS), st.session_state.df_step)


# --------------------------------------------------------------------------
# Step 0 — Upload
# --------------------------------------------------------------------------
if st.session_state.df_step == 0:
    st.subheader("Upload your file")
    job_type = st.radio(
        "What are you cleaning?", list(state.JOB_TYPES), horizontal=True, key="df_job_type"
    )

    if job_type == state.JOB_CRM:
        uploaded = st.file_uploader("Data file", type=state.supported_types(), key="df_upload")
        if uploaded is not None:
            st.session_state.df_source_bytes = uploaded.getvalue()
            st.session_state.df_source_name = uploaded.name
            st.session_state.df_source_label = state.file_size(uploaded.name, uploaded.getvalue())[1]

        samples = state.available_samples()
        if samples:
            # A hosted demo is often opened by someone with no export on hand,
            # so a sample is the difference between "try it" and "come back
            # later". It loads bytes and takes the same path as an upload.
            with st.expander("No file handy? Try a sample"):
                labels = [sample.label for sample in samples]
                chosen = st.selectbox("Sample file", labels, key="df_sample_choice")
                if st.button("Load sample"):
                    sample = samples[labels.index(chosen)]
                    st.session_state.df_crm = sample.crm
                    st.session_state.df_source_bytes = state.sample_bytes(sample)
                    st.session_state.df_source_name = sample.filename
                    st.session_state.df_source_label = state.file_size(
                        sample.filename, st.session_state.df_source_bytes
                    )[1]
                    go_to(1)

        label = st.session_state.get("df_source_label")
        if label:
            st.caption(f"Loaded {label}")
    else:
        bank_column, ledger_column = st.columns(2)
        with bank_column:
            bank_file = st.file_uploader(
                "Bank statement", type=state.supported_types(), key="df_bank_file"
            )
        with ledger_column:
            ledger_file = st.file_uploader(
                "Your ledger", type=state.supported_types(), key="df_ledger_file"
            )

    if st.button("Next: Configure →", type="primary"):
        go_to(1)


# --------------------------------------------------------------------------
# Step 1 — Configure
# --------------------------------------------------------------------------
elif st.session_state.df_step == 1:
    st.subheader("Configure")

    if st.session_state.df_job_type == state.JOB_CRM:
        if not configs:
            unavailable_note("Live config list")
        else:
            index = configs.index(st.session_state.df_crm) if st.session_state.df_crm in configs else 0
            st.session_state.df_crm = st.selectbox(
                "Target config", configs, index=index, format_func=lambda name: name.replace("_", " ").title()
            )
        with st.expander("Cleaning options"):
            st.checkbox("Remove duplicates", key="df_remove_dupes")
            st.checkbox("Parse dates day-first", key="df_date_first")
            st.text_input("Default phone region", key="df_region", max_chars=2)
    else:
        st.slider("Date matching tolerance (days)", 0, 7, key="df_tolerance")
        with st.expander("Column names"):
            st.caption("Default to the bundled samples' headers. Override for your own files.")
            st.text_input("Bank date column", key="df_bank_date_col")
            st.text_input("Bank amount column", key="df_bank_amount_col")
            st.text_input("Ledger date column", key="df_ledger_date_col")
            st.text_input("Ledger amount column", key="df_ledger_amount_col")

    back, forward = st.columns(2)
    with back:
        if st.button("← Back"):
            go_to(0)
    with forward:
        if st.button("Next: Process →", type="primary"):
            go_to(2)


# --------------------------------------------------------------------------
# Step 2 — Process
# --------------------------------------------------------------------------
elif st.session_state.df_step == 2:
    st.subheader("Processing")
    job_type = st.session_state.df_job_type

    try:
        with st.spinner("Working…"):
            if job_type == state.JOB_CRM:
                source_bytes = st.session_state.get("df_source_bytes")
                source_name = st.session_state.get("df_source_name")
                if source_bytes is None:
                    st.warning("No file to process. Start again and choose a file.")
                    go_to(0)
                else:
                    cleaning = state.build_cleaning_config(
                        st.session_state.df_remove_dupes,
                        st.session_state.df_date_first,
                        st.session_state.df_region,
                    )
                    st.session_state.df_run = state.run_crm_migration(
                        source_bytes,
                        source_name,
                        st.session_state.df_crm,
                        limits,
                        cleaning,
                    )
            else:
                bank_file = st.session_state.get("df_bank_file")
                ledger_file = st.session_state.get("df_ledger_file")
                if bank_file is None or ledger_file is None:
                    st.warning("Both files are needed. Start again and choose them.")
                    go_to(0)
                else:
                    st.session_state.df_recon = state.run_bank_reconciliation(
                        bank_file.getvalue(),
                        ledger_file.getvalue(),
                        limits,
                        st.session_state.df_bank_date_col,
                        st.session_state.df_bank_amount_col,
                        st.session_state.df_ledger_date_col,
                        st.session_state.df_ledger_amount_col,
                        st.session_state.df_tolerance,
                    )
        go_to(3)
    except Exception as exc:  # noqa: BLE001 — the page must never hard-crash
        st.error(state.migration_error_message(exc))
        if st.button("← Back to start"):
            start_over()


# --------------------------------------------------------------------------
# Step 3 — Review
# --------------------------------------------------------------------------
elif st.session_state.df_step == 3:
    st.subheader("Done")

    run = st.session_state.get("df_run")
    recon = st.session_state.get("df_recon")

    if run is not None:
        st.success(f"{run.rows_out} clean rows ready to download.")

        summary_columns = st.columns(4)
        summary_columns[0].metric("Quality score", f"{run.quality_score}%")
        summary_columns[1].metric("Rows out", run.rows_out)
        summary_columns[2].metric("Duplicates removed", run.summary.get("duplicates_removed", "—"))
        summary_columns[3].metric("Errors", run.summary.get("errors", "—"))

        dimensions = run.dimension_scores()
        if dimensions:
            st.write("")
            st.markdown("**Quality breakdown**")
            score_columns = st.columns(len(dimensions))
            for column, (name, value) in zip(score_columns, dimensions.items()):
                with column:
                    st.html(
                        f'<div style="text-align:center; font-size:.8rem; color:var(--slate);">'
                        f'{name.title()}<br>{score_badge(value)}</div>'
                    )
        else:
            unavailable_note("Quality breakdown (profiling)")

        download_columns = st.columns(len(run.downloads()))
        for column, (label, icon, payload, file_name, mime) in zip(download_columns, run.downloads()):
            with column:
                download_card(label, icon, payload, file_name, mime)

        # Count each finished run once. Streamlit re-runs this script on every
        # interaction, so the counter is keyed to the run that produced it.
        run_key = f"{run.source_name}:{run.rows_out}:{run.quality_score}"
        if st.session_state.get("df_counted_run") != run_key:
            st.session_state.df_counted_run = run_key
            st.session_state.df_history.append(
                {"file": run.source_name, "quality": run.quality_score}
            )

    elif recon is not None:
        counts = state.reconciliation_counts(recon)
        st.success(
            f"{counts['matched']} matched · {counts['missing_from_books']} missing from books · "
            f"{counts['never_cleared']} recorded but never cleared."
        )
        artefacts = state.reconciliation_downloads(recon)
        download_columns = st.columns(len(artefacts))
        for column, (label, icon, payload, file_name, mime) in zip(download_columns, artefacts):
            with column:
                download_card(label, icon, payload, file_name, mime)

    else:
        empty_state("🗂️", "Nothing to show", "The run finished without producing a result.")

    if st.button("← Run another file"):
        start_over()


if not history and st.session_state.df_step == 0:
    st.write("")
    empty_state("🗂️", "No runs yet", "Upload a file above to see it cleaned in seconds.")