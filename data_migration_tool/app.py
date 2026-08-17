"""Streamlit front end for the AutoFlow data migration tool.

Run with: ``streamlit run data_migration_tool/app.py``
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import chardet
import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

if __package__ in (None, ""):  # allow `streamlit run data_migration_tool/app.py` 
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_migration_tool.auditors import audit_import
from data_migration_tool.cleaners import CleaningConfig
from data_migration_tool.mappers import available_crms, load_mapping_config
from data_migration_tool.pipeline import run_pipeline
from data_migration_tool.reporters import render_audit_report

# Configure Streamlit
st.set_page_config(page_title="Data Migration Tool", page_icon="🚀", layout="wide")

# --- PRIVACY & DISCLAIMER ---
st.warning("""
🔒 **Privacy Guarantee**: Your file is processed temporarily in memory. 
It is **not** stored on our servers and is automatically deleted after your session ends. 
""")
# --- END PRIVACY ---

# Configure file upload size limit (200MB)
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB in bytes


def read_upload(upload: UploadedFile) -> pd.DataFrame:
    """Read uploaded CSV with automatic encoding detection."""
    raw = upload.read()
    result = chardet.detect(raw)
    encoding = result['encoding'] or 'utf-8'
    return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)


def get_brand_config() -> dict[str, str]:
    """Load white-label branding configuration from environment or defaults."""
    import os
    
    return {
        "brand_name": os.getenv("BRAND_NAME", "AutoFlow"),
        "tool_name": os.getenv("TOOL_NAME", "Data Migration Tool"),
        "logo_url": os.getenv("LOGO_URL", ""),
    }


brand = get_brand_config()
st.title(f"🚀 {brand['tool_name']}")
st.caption(f"Clean, map and validate a CRM export, then download import-ready deliverables.")

with st.sidebar:
    st.header("Cleaning options")
    remove_duplicates = st.checkbox("Remove duplicate records", value=True)
    standardize_dates = st.checkbox("Standardise dates to YYYY-MM-DD", value=True)
    standardize_phones = st.checkbox("Standardise phones to E.164", value=True)
    fix_scientific = st.checkbox("Repair Excel scientific notation", value=True)
    normalize_unicode = st.checkbox("Fold accents to ASCII", value=False)
    missing_strategy = st.selectbox(
        "Missing values", ["flag", "auto", "drop"], help="auto fills median/mode"
    )
    region = st.text_input("Default phone region", value="US", max_chars=2)
    
    # Critical fix: Day-first date ambiguity toggle
    date_first = st.checkbox(
        "Parse dates day-first (DD/MM/YYYY)", 
        value=False,
        help="Enable for European date formats. Disable for US (MM/DD/YYYY)."
    )

st.subheader("Step 1 — Upload your messy CSV")
uploaded = st.file_uploader(
    "CSV export from the source CRM", 
    type=["csv"],
    help=f"Maximum file size: {MAX_UPLOAD_SIZE // (1024*1024)}MB"
)

st.subheader("Step 2 — Select your target CRM")
crm = st.selectbox("Target CRM", available_crms(), format_func=str.title)

st.subheader("Step 3 — Configure output")
project_name = st.text_input("Project name", value="Client migration")
include_qa = st.checkbox("Include QA report", value=True)
include_mapping_log = st.checkbox("Include mapping log", value=True)
include_audit = st.checkbox("Include post-import audit (requires a CRM export)", value=False)
audit_upload = None
audit_key = None
if include_audit:
    audit_upload = st.file_uploader("CRM export to audit against", type=["csv"], key="audit")
    audit_key = st.text_input("Unique key column (must exist in both files)", value="email")

with st.expander("Preview the target template"):
    config = load_mapping_config(crm)
    st.write(
        pd.DataFrame(
            [
                {"field": f.name, "required": f.required, "unique": f.unique,
                 "transform": f.transform or ""}
                for f in config.fields
            ]
        )
    )

if st.button("🔄 Process File", type="primary", disabled=uploaded is None) and uploaded:
    # Critical fix: File size validation
    if uploaded.size > MAX_UPLOAD_SIZE:
        st.error(
            f"File too large ({uploaded.size // (1024*1024)}MB). "
            f"Maximum allowed size is {MAX_UPLOAD_SIZE // (1024*1024)}MB."
        )
        st.stop()
    
    # Critical fix: Error handling with try/except
    try:
        with st.spinner("Cleaning, mapping and validating…"):
            source = read_upload(uploaded)
            result = run_pipeline(
                source=source,
                crm=crm,
                cleaning_config=CleaningConfig(
                    remove_duplicates=remove_duplicates,
                    standardize_dates=standardize_dates,
                    standardize_phones=standardize_phones,
                    fix_scientific_notation=fix_scientific,
                    normalize_unicode=normalize_unicode,
                    missing_value_strategy=missing_strategy,
                    default_region=region.upper() or "US",
                    date_first=date_first,  # Critical fix: Pass date_first parameter
                ),
                project_name=project_name,
                source_filename=getattr(uploaded, "name", "upload.csv"),
            )

        summary = result.summary()
        st.success(
            f"Done — {summary['rows_in']} rows in, {summary['rows_out']} out, "
            f"quality score {summary['quality_score']}%."
        )
        columns = st.columns(5)
        columns[0].metric("Quality score", f"{summary['quality_score']}%")
        columns[1].metric("Records", summary["rows_out"])
        columns[2].metric("Duplicates removed", summary["duplicates_removed"])
        columns[3].metric("Errors", summary["errors"])
        columns[4].metric("Warnings", summary["warnings"])

        st.subheader("Step 4 — Download results")
        downloads = st.columns(3)
        downloads[0].download_button(
            "📊 Clean CSV",
            result.clean_frame.to_csv(index=False),
            file_name="clean_data.csv",
            mime="text/csv",
        )
        if include_qa:
            downloads[1].download_button(
                "📋 QA report (HTML)",
                result.qa_report_html,
                file_name="qa_report.html",
                mime="text/html",
            )
        if include_mapping_log:
            downloads[2].download_button(
                "📝 Mapping log",
                result.mapping_log().to_csv(index=False),
                file_name="mapping_log.csv",
                mime="text/csv",
            )

        tabs = st.tabs(["Mapped data", "Field mapping", "Cleaning actions", "Issues", "QA report"])
        tabs[0].dataframe(result.clean_frame.head(200), use_container_width=True)
        tabs[1].dataframe(result.mapping_log(), use_container_width=True)
        tabs[2].dataframe(result.cleaning_log(), use_container_width=True)
        tabs[3].dataframe(result.validation.issues_frame(), use_container_width=True)
        with tabs[4]:
            st.components.v1.html(result.qa_report_html, height=700, scrolling=True)

        if include_audit and audit_upload is not None and audit_key:
            audit = audit_import(
                expected=result.clean_frame, exported=read_upload(audit_upload), key=audit_key
            )
            st.subheader("Post-import audit")
            st.json(audit.stats())
            st.dataframe(audit.mismatches, use_container_width=True)
            st.download_button(
                "🧾 Audit report (HTML)",
                render_audit_report(audit.stats(), audit.mismatches, project_name),
                file_name="audit_report.html",
                mime="text/html",
            )
            
    except UnicodeDecodeError as e:
        st.error(
            "Oops, the file encoding looks unusual. "
            "Please check that it's a valid CSV export and try again."
        )
        st.error(f"Technical details: {str(e)}")
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears to be empty. Please check the file and try again.")
    except pd.errors.ParserError as e:
        st.error(
            "Oops, the file format looks unusual. "
            "Please check that it's a valid CSV export and try again."
        )
        st.error(f"Technical details: {str(e)}")
    except Exception as e:
        st.error(
            "Oops, something went wrong while processing the file. "
            "Please check that it's a valid CSV export and try again."
        )
        st.error(f"Technical details: {str(e)}")
elif uploaded is None:
    st.info("Upload a CSV to enable processing.")
