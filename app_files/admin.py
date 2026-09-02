"""Admin Dashboard - Private Client Delivery System

Personal backend for processing paid client files locally.
Run on your own machine only — never deploy this publicly.

Usage: streamlit run admin.py
"""
from __future__ import annotations

import dataclasses
import datetime
import io
import re
import sys
import zipfile
from pathlib import Path

import chardet
import pandas as pd
import streamlit as st

if __package__ in (None, ""):  # allow `streamlit run admin.py` 
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_files.auditors import audit_import
from app_files.cleaners import CleaningConfig
from app_files.mappers import available_crms
from app_files.pipeline import run_pipeline
from app_files.reporters import render_audit_report


def build_cleaning_config(
    *, remove_duplicates, standardize_dates, standardize_phones, fix_scientific_notation,
    normalize_unicode, missing_value_strategy, default_region, date_first,
) -> CleaningConfig:
    """Build CleaningConfig against the confirmed real dataclass fields.

    date_format and date_first are two SEPARATE real fields (confirmed from
    cleaners/config.py source) — date_format is the strftime output pattern
    (default "%Y-%m-%d", left untouched here), date_first is the day-first
    input-parsing toggle. An earlier version of this function incorrectly
    treated them as alternates for the same concept and overwrote
    date_format with "DMY"/"MDY", which is wrong. Fixed now that the real
    field names are confirmed.
    """
    return CleaningConfig(
        remove_duplicates=remove_duplicates,
        standardize_dates=standardize_dates,
        date_first=date_first,
        standardize_phones=standardize_phones,
        fix_scientific_notation=fix_scientific_notation,
        normalize_unicode=normalize_unicode,
        missing_value_strategy=missing_value_strategy,
        default_region=default_region,
    )


def safe_get(d: dict, key: str, default="N/A"):
    """Read a summary dict key without crashing if the real key name differs."""
    return d.get(key, default)

st.set_page_config(page_title="Admin - Client Delivery", page_icon="🧑‍💻", layout="wide")

# --------------------------------------------------------------------------
# Local storage: deliveries archive + order log
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DELIVERIES_DIR = BASE_DIR / "deliveries"
ORDERS_LOG = BASE_DIR / "orders_log.csv"
DELIVERIES_DIR.mkdir(exist_ok=True)

LOG_COLUMNS = [
    "timestamp", "client_name", "client_email", "tier", "price",
    "target_crm", "rows_in", "rows_out", "quality_score", "errors",
    "warnings", "guarantee_met", "zip_filename",
]

TIER_PRICING = {
    "Starter (< 1,000 rows) — $600": ("Starter", 600),
    "Standard (1,000–10,000 rows) — $1,500": ("Standard", 1500),
    "Premium (10,000+ rows) — $2,000": ("Premium", 2000),
}

TIER_DELIVERABLES = {
    # (clean_csv, mapping_log, cleaning_log, issues, qa_report)
    "Starter": {"clean_csv"},
    "Standard": {"clean_csv", "mapping_log", "cleaning_log", "issues", "qa_report"},
    "Premium": {"clean_csv", "mapping_log", "cleaning_log", "issues", "qa_report"},
}

GUARANTEE_MAX_ERRORS = 0  # errors above this = flag before sending


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", name).strip("_") or "client"


def append_order_log(row: dict) -> None:
    df_row = pd.DataFrame([row], columns=LOG_COLUMNS)
    if ORDERS_LOG.exists():
        df_row.to_csv(ORDERS_LOG, mode="a", header=False, index=False)
    else:
        df_row.to_csv(ORDERS_LOG, mode="w", header=True, index=False)


st.title("Client Job Processor")
st.caption("Runs locally. No row limits. Generates the delivery package for a paid job.")
st.info(
    "🔒 Local-only tool — files are processed on this machine and never uploaded elsewhere. "
    "Delivered zips are also saved to the `deliveries/` folder here so you keep a record "
    "even after cleaning up client files."
)

tab_process, tab_audit, tab_log = st.tabs(["Process new job", "Post-import audit", "Job log"])

# ==========================================================================
# TAB 1 — Process a new job
# ==========================================================================
with tab_process:
    with st.sidebar:
        st.header("Job details")
        client_name = st.text_input("Client / project name", value="")
        client_email = st.text_input("Client email", value="")
        tier_label = st.selectbox("Package tier", list(TIER_PRICING.keys()))
        tier, suggested_price = TIER_PRICING[tier_label]
        price = st.number_input("Price ($)", min_value=0, value=suggested_price, step=50)
        target_crm = st.selectbox("Target CRM", available_crms())

        st.divider()
        st.header("Processing settings")
        remove_duplicates = st.checkbox("Remove duplicates", value=True)
        standardize_dates = st.checkbox("Standardize dates", value=True)
        date_first = st.checkbox(
            "Parse dates day-first (DD/MM/YYYY)", value=False,
            help="Enable for European date formats. Disable for US (MM/DD/YYYY).",
        )
        standardize_phones = st.checkbox("Standardize phones (E.164)", value=True)
        fix_scientific = st.checkbox("Fix Excel scientific notation", value=True)
        normalize_unicode = st.checkbox("Fold accents to ASCII", value=False)
        missing_strategy = st.selectbox("Missing values", ["flag", "auto", "drop"])
        region = st.text_input("Phone region", value="US")

        st.divider()
        st.header("Report branding")
        brand_name = st.text_input("Brand name", value="Your Business Name")
        tool_name = st.text_input("Tool name", value="Data Migration Tool")

    uploaded_file = st.file_uploader("Upload the full client CSV (no row limit)", type=["csv"], key="main_upload")

    if uploaded_file is not None:
        uploaded_file.seek(0)  # fixes the reread-after-rerun bug: pointer may be at EOF from a prior run
        with st.spinner("Reading file…"):
            try:
                raw_data = uploaded_file.read()
                if not raw_data:
                    st.error("The file appears empty on read. Re-select it in the uploader and try again.")
                    st.stop()
                encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
                source = pd.read_csv(io.BytesIO(raw_data), dtype=str, encoding=encoding, keep_default_na=False)
                st.success(f"File loaded: {len(source)} rows, {len(source.columns)} columns.")
            except UnicodeDecodeError as e:
                st.error("Encoding issue reading this file.")
                st.exception(e)
                st.stop()
            except pd.errors.EmptyDataError:
                st.error("The file has no parsable data.")
                st.stop()
            except pd.errors.ParserError as e:
                st.error("CSV format looks malformed.")
                st.exception(e)
                st.stop()

        # Gentle tier sanity-check against actual row count — you decide, this just flags it
        if tier == "Starter" and len(source) >= 1000:
            st.warning(f"This file has {len(source)} rows — outside the Starter range. Consider re-pricing before delivery.")
        elif tier == "Standard" and len(source) >= 10000:
            st.warning(f"This file has {len(source)} rows — Premium range. Consider re-pricing before delivery.")

        if not client_name.strip():
            st.warning("Add a client / project name in the sidebar before processing.")

        process_clicked = st.button("Process full file", type="primary", disabled=not client_name.strip())

        if process_clicked:
            progress_bar = st.progress(0, text="Starting pipeline…")
            try:
                config = build_cleaning_config(
                    remove_duplicates=remove_duplicates,
                    standardize_dates=standardize_dates,
                    date_first=date_first,
                    standardize_phones=standardize_phones,
                    fix_scientific_notation=fix_scientific,
                    normalize_unicode=normalize_unicode,
                    missing_value_strategy=missing_strategy,
                    default_region=region.upper() or "US",
                )

                progress_bar.progress(30, text="Cleaning, mapping, and validating…")

                # NOTE: brand/tool name still travel via os.environ here, matching the existing
                # reporters.py contract. Low risk for a single local admin session (no concurrent
                # users), but worth asking your coder to accept these as explicit run_pipeline /
                # render_* arguments instead of env globals — the same pattern is riskier on the
                # public demo, which does have concurrent users.
                import os
                os.environ["BRAND_NAME"] = brand_name
                os.environ["TOOL_NAME"] = tool_name

                result = run_pipeline(
                    source=source,
                    crm=target_crm,
                    cleaning_config=config,
                    project_name=client_name,
                    source_filename=uploaded_file.name,
                )

                progress_bar.progress(80, text="Checking against guarantee…")
                summary = result.summary()
                errors_val = safe_get(summary, "errors", 0)
                guarantee_met = isinstance(errors_val, (int, float)) and errors_val <= GUARANTEE_MAX_ERRORS

                progress_bar.progress(100, text="Done.")

                st.subheader("Delivery summary")
                cols = st.columns(4)
                cols[0].metric("Quality score", f"{safe_get(summary, 'quality_score')}%")
                cols[1].metric("Records out", safe_get(summary, "rows_out"))
                cols[2].metric("Duplicates removed", safe_get(summary, "duplicates_removed"))
                cols[3].metric("Errors", errors_val)

                if guarantee_met:
                    st.success("✅ Meets your delivery guarantee (no unresolved errors). Safe to send.")
                else:
                    st.error(
                        f"⚠️ {errors_val} unresolved error(s) — this does NOT currently meet "
                        f"your guarantee. Review the issues below before sending anything to the client."
                    )

                issues = result.validation.issues_frame()
                if not issues.empty:
                    st.dataframe(issues.head(15), use_container_width=True)

                # Build the zip with only what this tier is supposed to include
                include = TIER_DELIVERABLES[tier]
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    if "clean_csv" in include:
                        zf.writestr("clean_data.csv", result.clean_frame.to_csv(index=False))
                    if "mapping_log" in include:
                        zf.writestr("mapping_log.csv", result.mapping_log().to_csv(index=False))
                    if "cleaning_log" in include:
                        zf.writestr("cleaning_log.csv", result.cleaning_log().to_csv(index=False))
                    if "issues" in include:
                        zf.writestr("issues.csv", issues.to_csv(index=False))
                    if "qa_report" in include:
                        zf.writestr("qa_report.html", result.qa_report_html)
                zip_buffer.seek(0)

                safe_client = sanitize_filename(client_name)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"{safe_client}_{target_crm}_{timestamp}.zip"

                # Persist a copy locally so you have a record even after deleting client source files
                archive_path = DELIVERIES_DIR / zip_filename
                archive_path.write_bytes(zip_buffer.getvalue())
                zip_buffer.seek(0)

                append_order_log({
                    "timestamp": timestamp,
                    "client_name": client_name,
                    "client_email": client_email,
                    "tier": tier,
                    "price": price,
                    "target_crm": target_crm,
                    "rows_in": safe_get(summary, "rows_in"),
                    "rows_out": safe_get(summary, "rows_out"),
                    "quality_score": safe_get(summary, "quality_score"),
                    "errors": errors_val,
                    "warnings": safe_get(summary, "warnings"),
                    "guarantee_met": guarantee_met,
                    "zip_filename": zip_filename,
                })

                st.divider()
                st.subheader("Download package")
                st.download_button(
                    label=f"Download {zip_filename}",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                )
                st.caption(f"A copy was also saved to `deliveries/{zip_filename}` and logged in `orders_log.csv`.")

            except Exception as e:
                st.error("Something went wrong while processing this file.")
                st.exception(e)
                st.stop()

# ==========================================================================
# TAB 2 — Post-import audit (Premium tier deliverable)
# ==========================================================================
with tab_audit:
    st.subheader("Post-import audit")
    st.caption(
        "Run this once the client has imported the clean file into their live CRM and sent you "
        "a fresh export. Compares what's actually in their system against what you delivered."
    )
    expected_zip_hint = st.text_input(
        "Client / project name (for matching the original job)", value="", key="audit_client_name"
    )
    expected_file = st.file_uploader("Original clean_data.csv you delivered", type=["csv"], key="audit_expected")
    exported_file = st.file_uploader("Fresh export from the client's CRM after import", type=["csv"], key="audit_exported")
    audit_key = st.text_input("Unique key column present in both files", value="email")

    if st.button("Run audit", disabled=not (expected_file and exported_file and audit_key)):
        try:
            expected_file.seek(0)
            exported_file.seek(0)
            expected_df = pd.read_csv(expected_file, dtype=str, keep_default_na=False)
            exported_df = pd.read_csv(exported_file, dtype=str, keep_default_na=False)
            audit = audit_import(expected=expected_df, exported=exported_df, key=audit_key)

            st.json(audit.stats())
            st.dataframe(audit.mismatches, use_container_width=True)

            report_html = render_audit_report(audit.stats(), audit.mismatches, expected_zip_hint or "Project")
            st.download_button(
                "Download audit report (HTML)",
                report_html,
                file_name=f"{sanitize_filename(expected_zip_hint or 'audit')}_audit_report.html",
                mime="text/html",
            )
        except Exception as e:
            st.error("Could not complete the audit — check both files share the key column.")
            st.exception(e)

# ==========================================================================
# TAB 3 — Job log
# ==========================================================================
with tab_log:
    st.subheader("Order history")
    if ORDERS_LOG.exists():
        log_df = pd.read_csv(ORDERS_LOG)
        st.dataframe(log_df.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
        st.caption(f"{len(log_df)} job(s) logged · stored locally at `orders_log.csv`")
        st.download_button(
            "Download full log (CSV)",
            log_df.to_csv(index=False),
            file_name="orders_log.csv",
            mime="text/csv",
        )
    else:
        st.caption("No jobs processed yet. This fills in automatically after your first delivery.")