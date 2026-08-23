"""Streamlit front end for the AutoFlow data migration tool.

Run with: ``streamlit run app.py``
Deploy to Streamlit Cloud: Configure main file path as app.py
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

import chardet
import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Add the data_migration_tool directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_migration_tool.auditors import audit_import
from data_migration_tool.cleaners import CleaningConfig
from data_migration_tool.mappers import available_crms, load_mapping_config
from data_migration_tool.pipeline import run_pipeline
from data_migration_tool.reporters import render_audit_report

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(page_title="Data Migration Tool", page_icon="◆", layout="wide")

MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB in bytes
MAX_DEMO_ROWS = 500


def get_brand_config() -> dict[str, str]:
    """Load white-label branding configuration from environment or defaults."""
    return {
        "brand_name": os.getenv("BRAND_NAME", "AutoFlow"),
        "tool_name": os.getenv("TOOL_NAME", "Data Migration Tool"),
        "operator_name": os.getenv("OPERATOR_NAME", "Your Name"),
        "contact_email": os.getenv("CONTACT_EMAIL", "you@example.com"),
    }


brand = get_brand_config()


def read_upload(upload: UploadedFile) -> pd.DataFrame:
    """Read uploaded CSV with automatic encoding detection."""
    raw = upload.read()
    result = chardet.detect(raw)
    encoding = result["encoding"] or "utf-8"
    return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)


# --------------------------------------------------------------------------
# Design system
# Palette: ink #14181F, paper #F7F6F3, slate #5B6472, teal #1F9E8B,
#          amber #C9822B, line #DDD9D0. Type: IBM Plex Mono (labels/numbers,
#          used sparingly) + Inter (everything else). Signature element:
#          a literal pipeline rail for the four processing steps, since the
#          workflow genuinely is a sequence.
# --------------------------------------------------------------------------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    :root{
        --ink:#14181F; --ink-soft:#232A35; --paper:#F7F6F3; --paper-card:#FFFFFF;
        --slate:#5B6472; --slate-light:#8A93A3; --teal:#1F9E8B; --teal-soft:#E4F3F0;
        --amber:#C9822B; --amber-soft:#FBF0E1; --line:#DDD9D0; --danger:#C1443C;
    }

    html, body, [class*="css"] { font-family:'Inter', -apple-system, sans-serif; }
    .stApp { background:var(--paper); }
    #MainMenu, footer, header[data-testid="stHeader"] { background:transparent; }

    .block-container { padding-top:1.5rem; max-width:1120px; }

    h1, h2, h3, h4 { color:var(--ink) !important; font-weight:600 !important; }

    /* ---------- Header ---------- */
    .af-header{
        background:var(--ink); border-radius:10px; padding:28px 32px;
        margin-bottom:20px; display:flex; align-items:center; justify-content:space-between;
        flex-wrap:wrap; gap:12px;
    }
    .af-wordmark{
        font-family:'IBM Plex Mono', monospace; font-size:1.05rem; letter-spacing:.12em;
        color:#F7F6F3; font-weight:600;
    }
    .af-wordmark span{ color:var(--teal); }
    .af-tagline{ color:#AEB6C2; font-size:.92rem; margin-top:4px; }
    .af-header-badge{
        font-family:'IBM Plex Mono', monospace; font-size:.72rem; letter-spacing:.06em;
        color:var(--teal); border:1px solid rgba(31,158,139,.45); border-radius:20px;
        padding:5px 12px; white-space:nowrap;
    }

    /* ---------- Privacy note ---------- */
    .af-note{
        display:flex; gap:10px; align-items:flex-start; background:var(--paper-card);
        border:1px solid var(--line); border-left:3px solid var(--teal); border-radius:6px;
        padding:12px 16px; margin-bottom:22px; font-size:.88rem; color:var(--slate);
    }
    .af-note b{ color:var(--ink); }

    /* ---------- Pipeline rail ---------- */
    .af-rail{ display:flex; align-items:flex-start; margin:6px 0 30px 0; }
    .af-rail-step{ flex:1; text-align:left; position:relative; padding-right:14px; }
    .af-rail-step:not(:last-child)::after{
        content:""; position:absolute; top:13px; left:32px; right:0; height:1px;
        background:var(--line);
    }
    .af-rail-num{
        display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px;
        border-radius:50%; background:var(--ink); color:var(--paper); font-family:'IBM Plex Mono', monospace;
        font-size:.78rem; font-weight:600; position:relative; z-index:1;
    }
    .af-rail-label{ font-size:.82rem; color:var(--slate); margin-top:8px; line-height:1.3; max-width:150px; }

    /* ---------- Step headings ---------- */
    .af-step-heading{ display:flex; align-items:baseline; gap:10px; margin:30px 0 10px 0; }
    .af-step-kicker{
        font-family:'IBM Plex Mono', monospace; font-size:.78rem; color:var(--teal);
        border:1px solid var(--teal-soft); background:var(--teal-soft); border-radius:4px;
        padding:2px 8px; font-weight:600;
    }
    .af-step-title{ font-size:1.15rem; font-weight:600; color:var(--ink); }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"]{ background:var(--ink) !important; }
    section[data-testid="stSidebar"] *{ color:#DDE2E8 !important; }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3{
        font-family:'IBM Plex Mono', monospace !important; font-size:.82rem !important;
        letter-spacing:.08em; text-transform:uppercase; color:#8FE0D2 !important;
        border-bottom:1px solid rgba(255,255,255,.12); padding-bottom:8px; margin-top:6px !important;
    }
    section[data-testid="stSidebar"] .stCheckbox label p{ font-size:.88rem !important; }
    section[data-testid="stSidebar"] hr{ border-color:rgba(255,255,255,.12) !important; }

    /* ---------- File uploader ---------- */
    [data-testid="stFileUploaderDropzone"]{
        background:var(--paper-card) !important; border:1.5px dashed var(--slate-light) !important;
        border-radius:8px !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--teal) !important; }

    /* ---------- Buttons ---------- */
    .stButton > button{
        background:var(--ink) !important; color:var(--paper) !important; border:none !important;
        border-radius:6px !important; font-weight:600 !important; padding:.55rem 1.4rem !important;
        transition:background .15s ease;
    }
    .stButton > button:hover{ background:var(--teal) !important; color:var(--ink) !important; }
    .stButton > button:disabled{ background:var(--line) !important; color:var(--slate-light) !important; }

    .stDownloadButton > button{
        background:var(--paper-card) !important; color:var(--ink) !important;
        border:1px solid var(--line) !important; border-radius:6px !important; font-weight:600 !important;
    }
    .stDownloadButton > button:hover{ border-color:var(--teal) !important; color:var(--teal) !important; }

    /* ---------- Metrics ---------- */
    [data-testid="stMetric"]{
        background:var(--paper-card); border:1px solid var(--line); border-radius:8px;
        padding:14px 16px 10px 16px;
    }
    [data-testid="stMetricLabel"]{
        font-family:'IBM Plex Mono', monospace !important; font-size:.72rem !important;
        letter-spacing:.05em; text-transform:uppercase; color:var(--slate) !important;
    }
    [data-testid="stMetricValue"]{ color:var(--ink) !important; font-weight:600 !important; }

    /* ---------- Alerts ---------- */
    div[data-testid="stAlertContentSuccess"]{ color:var(--ink) !important; }
    .stAlert{ border-radius:8px !important; }

    /* ---------- Expander / Tabs ---------- */
    [data-testid="stExpander"]{ border:1px solid var(--line) !important; border-radius:8px !important; background:var(--paper-card); }
    button[data-baseweb="tab"]{ font-weight:600 !important; }

    /* ---------- Footer ---------- */
    .af-footer{
        margin-top:52px; padding:22px 0 10px 0; border-top:1px solid var(--line);
        display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;
        font-size:.82rem; color:var(--slate);
    }
    .af-footer b{ color:var(--ink); }

    @media (max-width: 640px){
        .af-rail{ flex-direction:column; gap:16px; }
        .af-rail-step:not(:last-child)::after{ display:none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def step_heading(number: str, title: str) -> None:
    st.markdown(
        f'<div class="af-step-heading"><span class="af-step-kicker">STEP {number}</span>'
        f'<span class="af-step-title">{title}</span></div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="af-header">
        <div>
            <div class="af-wordmark">{brand['tool_name'].upper()}<span>_</span></div>
            <div class="af-tagline">Clean, map, and validate a CRM export into an import-ready file.</div>
        </div>
        <div class="af-header-badge">FREE DEMO · 500 ROW LIMIT</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="af-note">
        <span>🔒</span>
        <div><b>Your file stays in memory.</b> Nothing is written to disk or stored after your
        session ends — the upload is discarded once you close this tab.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Pipeline rail (a real sequence, not decoration)
# --------------------------------------------------------------------------
rail_steps = [
    ("1", "Upload", "Source CSV export"),
    ("2", "Map", "Match to target CRM fields"),
    ("3", "Clean", "Dedupe, format, validate"),
    ("4", "Export", "Download clean files"),
]
rail_html = '<div class="af-rail">'
for num, label, desc in rail_steps:
    rail_html += (
        f'<div class="af-rail-step"><span class="af-rail-num">{num}</span>'
        f'<div class="af-rail-label"><b>{label}</b><br>{desc}</div></div>'
    )
rail_html += "</div>"
st.markdown(rail_html, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Sidebar — cleaning options & branding
# --------------------------------------------------------------------------
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
    date_first = st.checkbox(
        "Parse dates day-first (DD/MM/YYYY)",
        value=False,
        help="Enable for European date formats. Disable for US (MM/DD/YYYY).",
    )

    st.divider()
    st.header("Branding")
    brand_name = st.text_input("Brand name", value=brand["brand_name"], help="Shown on generated reports")
    tool_name = st.text_input("Tool name", value=brand["tool_name"], help="Custom tool name for white-labeling")

# --------------------------------------------------------------------------
# Step 1 — Upload
# --------------------------------------------------------------------------
step_heading("1", "Upload your source CSV")
uploaded = st.file_uploader(
    "CSV export from the source CRM",
    type=["csv"],
    help=f"Maximum file size: {MAX_UPLOAD_SIZE // (1024*1024)}MB",
    label_visibility="collapsed",
)
if uploaded is not None:
    st.caption(f"**{uploaded.name}** · {uploaded.size / 1024:,.0f} KB")

# --------------------------------------------------------------------------
# Step 2 — Target CRM
# --------------------------------------------------------------------------
step_heading("2", "Select the target CRM")
crm = st.selectbox("Target CRM", available_crms(), format_func=str.title, label_visibility="collapsed")

with st.expander("Preview the target field template"):
    config = load_mapping_config(crm)
    st.dataframe(
        pd.DataFrame(
            [
                {"field": f.name, "required": f.required, "unique": f.unique, "transform": f.transform or ""}
                for f in config.fields
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------------------------------
# Step 3 — Output configuration
# --------------------------------------------------------------------------
step_heading("3", "Configure the output")
project_name = st.text_input("Project name", value="Client migration")
col_a, col_b, col_c = st.columns(3)
include_qa = col_a.checkbox("Include QA report", value=True)
include_mapping_log = col_b.checkbox("Include mapping log", value=True)
include_audit = col_c.checkbox("Include post-import audit", value=False, help="Requires a CRM export to check against")

audit_upload = None
audit_key = None
if include_audit:
    audit_upload = st.file_uploader("CRM export to audit against", type=["csv"], key="audit")
    audit_key = st.text_input("Unique key column (must exist in both files)", value="email")

st.write("")
run_clicked = st.button("Process file", type="primary", disabled=uploaded is None)

# --------------------------------------------------------------------------
# Processing
# --------------------------------------------------------------------------
if run_clicked and uploaded:
    if uploaded.size > MAX_UPLOAD_SIZE:
        st.error(
            f"File too large ({uploaded.size // (1024*1024)}MB). "
            f"Maximum allowed size is {MAX_UPLOAD_SIZE // (1024*1024)}MB."
        )
        st.stop()

    try:
        with st.spinner("Cleaning, mapping and validating…"):
            source = read_upload(uploaded)

            if len(source) > MAX_DEMO_ROWS:
                st.info(
                    f"This demo processes the first {MAX_DEMO_ROWS} of {len(source)} rows. "
                    f"Contact {brand['operator_name']} ({brand['contact_email']}) to run the full file."
                )
                source = source.head(MAX_DEMO_ROWS)

            os.environ["BRAND_NAME"] = brand_name
            os.environ["TOOL_NAME"] = tool_name

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
                    date_first=date_first,
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

        step_heading("4", "Download the results")
        downloads = st.columns(3)
        downloads[0].download_button(
            "Clean CSV",
            result.clean_frame.to_csv(index=False),
            file_name="clean_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if include_qa:
            downloads[1].download_button(
                "QA report (HTML)",
                result.qa_report_html,
                file_name="qa_report.html",
                mime="text/html",
                use_container_width=True,
            )
        if include_mapping_log:
            downloads[2].download_button(
                "Mapping log",
                result.mapping_log().to_csv(index=False),
                file_name="mapping_log.csv",
                mime="text/csv",
                use_container_width=True,
            )

        tabs = st.tabs(["Mapped data", "Field mapping", "Cleaning actions", "Issues", "QA report"])
        tabs[0].dataframe(result.clean_frame.head(200), use_container_width=True)
        tabs[1].dataframe(result.mapping_log(), use_container_width=True)
        tabs[2].dataframe(result.cleaning_log(), use_container_width=True)
        tabs[3].dataframe(result.validation.issues_frame(), use_container_width=True)
        with tabs[4]:
            st.components.v1.html(result.qa_report_html, height=700, scrolling=True)

        if include_audit and audit_upload is not None and audit_key:
            audit = audit_import(expected=result.clean_frame, exported=read_upload(audit_upload), key=audit_key)
            st.subheader("Post-import audit")
            st.json(audit.stats())
            st.dataframe(audit.mismatches, use_container_width=True)
            st.download_button(
                "Audit report (HTML)",
                render_audit_report(audit.stats(), audit.mismatches, project_name),
                file_name="audit_report.html",
                mime="text/html",
            )

    except UnicodeDecodeError as e:
        st.error("The file encoding looks unusual. Check that it's a valid CSV export and try again.")
        st.caption(f"Technical details: {str(e)}")
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears to be empty. Check the file and try again.")
    except pd.errors.ParserError as e:
        st.error("The file format looks unusual. Check that it's valid CSV export and try again.")
        st.caption(f"Technical details: {str(e)}")
    except Exception as e:
        st.error("Something went wrong while processing the file. Check that it's a valid CSV export and try again.")
        st.caption(f"Technical details: {str(e)}")
elif uploaded is None:
    st.caption("Upload a CSV above to enable processing.")

# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="af-footer">
        <div>Built and maintained by <b>{brand['operator_name']}</b> — data migration & CRM cleanup.
        Questions? <b>{brand['contact_email']}</b></div>
        <div>This is a working demo. Full-file processing available on request.</div>
    </div>
    """,
    unsafe_allow_html=True,
)