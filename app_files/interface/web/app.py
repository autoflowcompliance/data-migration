"""AutoFlow web interface.

Upload a file, pick a config and an output format, run the migration, and
download the clean data, QA report, lineage report and issues CSV.

This is an additive layer: it calls the existing pipeline and the new
ingestion / rules / profiling / lineage / output layers. Nothing in
``app_files/core`` is imported for modification, only for use.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# `streamlit run app_files/interface/web/app.py` sets __package__ to "" — the
# repo root must be importable for `app_files...` imports to resolve.
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app_files.ingestion import read_any, UnsupportedFormatError
from app_files.interface.web.display import arrow_safe, show
from app_files.lineage import LineageTracker
from app_files.mappers import available_crms
from app_files.output import FORMATS
from app_files.output.inmemory import to_bytes
from app_files.pipeline import run_pipeline
from app_files.profiling import profile, render_qa_report_with_profile
from app_files.rules import RuleConfigError, run_rules_for


st.set_page_config(page_title="AutoFlow — Data Migration", page_icon="⇄", layout="wide")

SUPPORTED = ["csv", "tsv", "txt", "json", "xlsx", "xlsm", "xls", "pdf"]

st.title("AutoFlow — Data Migration & Reconciliation")
st.caption(
    "Ingest CSV, Excel, JSON or bank-statement PDF · clean · map · validate · "
    "profile · trace every change."
)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Configuration")
    crms = available_crms()
    crm = st.selectbox(
        "Target config", crms, index=crms.index("hubspot") if "hubspot" in crms else 0
    )
    output_format = st.selectbox(
        "Output format", sorted(FORMATS), format_func=str.title
    )
    run_structural = st.checkbox(
        "Run structural (Frictionless) check", value=True,
        help="Adds a file-structure section to the QA report.",
    )
    enable_lineage = st.checkbox(
        "Track lineage", value=True,
        help="Records every changed value so any output row can be traced to its source row.",
    )
    enable_rules = st.checkbox(
        "Apply config rules", value=True,
        help="Runs the 'rules:' block from the selected config and adds failures to the issues list.",
    )
    project_name = st.text_input("Project name", value="Data migration")
    st.divider()
    st.page_link(
        "pages/rules.py",
        label="Build validation rules",
        icon="✅",
        help="Turn dropdowns into rules — no YAML, no patterns, no network call.",
    )

uploaded = st.file_uploader(
    "Upload your source file",
    type=SUPPORTED,
    help="CSV, TSV, JSON, Excel or a bank-statement PDF.",
)

if uploaded is None:
    st.info("Upload a file to begin. Sample files live in `app_files/samples/`.")
    st.stop()

# ---------------------------------------------------------------- ingest
try:
    source = read_any(uploaded.getvalue(), filename=uploaded.name)
except UnsupportedFormatError as exc:
    st.error(f"Unsupported file type: {exc}")
    st.stop()
except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
    st.error(f"Could not read `{uploaded.name}`.")
    st.caption(f"Technical details: {exc}")
    st.stop()

st.success(f"Read **{len(source):,}** rows and **{len(source.columns)}** columns from `{uploaded.name}`.")
with st.expander("Preview source data", expanded=False):
    show(source.head(50))

if not st.button("Run migration", type="primary"):
    st.stop()

# ---------------------------------------------------------------- run
tracker = LineageTracker() if enable_lineage else None
try:
    with st.spinner("Cleaning, mapping and validating…"):
        result = run_pipeline(
            source,
            crm=crm,
            project_name=project_name,
            source_filename=uploaded.name,
            run_structural_check=run_structural,
            lineage_tracker=tracker,
        )
except KeyError as exc:
    st.error(f"Config references a missing column: {exc}")
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error("The migration failed on this file.")
    st.caption(f"Technical details: {exc}")
    st.stop()

# ---------------------------------------------------------------- rules
rule_result = None
if enable_rules:
    try:
        rule_result = run_rules_for(result.clean_frame, crm)
    except RuleConfigError as exc:
        st.warning(f"Rules in `{crm}.yaml` could not be loaded: {exc}")

# ---------------------------------------------------------------- summary
summary = result.summary()
st.subheader("Result")
cols = st.columns(5)
cols[0].metric("Rows in", summary.get("rows_in", len(source)))
cols[1].metric("Rows out", len(result.clean_frame))
cols[2].metric("Duplicates removed", summary.get("duplicates_removed", 0))
cols[3].metric("Issues", summary.get("errors", 0) + summary.get("warnings", 0))
cols[4].metric("Quality score", f"{summary.get('quality_score', 0)}%")

if rule_result is not None and rule_result.rules_run:
    if rule_result.total_failures:
        st.warning(
            f"{rule_result.total_failures} rule failure(s) across "
            f"{rule_result.rules_run} rule(s): "
            + ", ".join(f"{k} ({v})" for k, v in rule_result.failures_by_rule.items())
        )
    else:
        st.success(f"All {rule_result.rules_run} configured rule(s) passed.")

# ---------------------------------------------------------------- profile
profile_result = profile(result.clean_frame)
st.subheader("Quality scorecard")
st.caption(f"Overall **{profile_result.overall}%** across five dimensions.")
for name, score in profile_result.scores.items():
    st.progress(min(max(score / 100, 0.0), 1.0), text=f"{name.title()} — {score}")

# ---------------------------------------------------------------- tabs
tabs = st.tabs(
    ["Clean data", "QA report", "Lineage", "Issues", "Logs"]
)

with tabs[0]:
    show(result.clean_frame)

with tabs[1]:
    html = render_qa_report_with_profile(result.qa_report_html, result.clean_frame, profile_result)
    st.download_button("Download QA report (HTML)", html, file_name="qa_report.html", mime="text/html")
    st.html(html)

with tabs[2]:
    log = result.lineage_log()
    if log.empty:
        st.caption("Lineage tracking was disabled for this run.")
    else:
        st.caption(f"{len(log)} transformation events.")
        show(log)
        st.download_button(
            "Download lineage report (CSV)", log.to_csv(index=False),
            file_name="lineage_report.csv", mime="text/csv",
        )

with tabs[3]:
    issues = result.validation.issues_frame()
    if rule_result is not None and rule_result.issues:
        rule_rows = pd.DataFrame(
            [
                {
                    "row": issue.row, "field": issue.field, "check": issue.check,
                    "severity": issue.severity, "message": issue.message,
                }
                for issue in rule_result.issues
            ]
        )
        issues = pd.concat([issues, rule_rows], ignore_index=True) if not issues.empty else rule_rows
    if issues.empty:
        st.success("No issues found.")
    else:
        show(issues)
        st.download_button(
            "Download issues (CSV)", issues.to_csv(index=False),
            file_name="issues.csv", mime="text/csv",
        )

with tabs[4]:
    st.write("**Mapping log**")
    show(result.mapping_log())
    st.write("**Cleaning log**")
    show(result.cleaning_log())

# ---------------------------------------------------------------- downloads
st.subheader("Downloads")
stem = Path(uploaded.name).stem
payload = to_bytes(result.clean_frame, output_format, stem=f"{stem}_clean")
st.download_button(
    f"Download clean data ({output_format})",
    payload.data,
    file_name=payload.filename,
    mime=payload.mime,
    type="primary",
)