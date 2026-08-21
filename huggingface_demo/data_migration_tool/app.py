"""Professional Streamlit front end for the AutoFlow data migration tool.

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

# Professional page configuration
st.set_page_config(
    page_title="Data Migration Tool | Professional CRM Data Cleaning",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 1rem;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .trust-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .trust-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .upload-section {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px dashed #e2e8f0;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
    }
    
    .privacy-banner {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .step-number {
        background: #667eea;
        color: white;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 0.75rem;
    }
    
    .crm-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #e0e7ff;
        color: #3730a3;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

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

# === PROFESSIONAL HEADER ===
st.markdown(f"""
<div class="main-header">
    <div class="header-title">⚡ {brand['tool_name']}</div>
    <div class="header-subtitle">Professional CRM Data Cleaning & Migration Services</div>
    <div class="trust-badges">
        <div class="trust-badge">🔒 Zero Data Storage</div>
        <div class="trust-badge">⚡ 60-Second Processing</div>
        <div class="trust-badge">🎯 95%+ Quality Score</div>
        <div class="trust-badge">📋 First 500 Rows Free</div>
    </div>
</div>
""", unsafe_allow_html=True)

# === PRIVACY GUARANTEE ===
st.markdown(f"""
<div class="privacy-banner">
    <strong>🔒 Privacy Guarantee:</strong> Your file is processed temporarily in memory and is <strong>not stored on our servers</strong>. It is automatically deleted after your session ends. We take data security seriously.
</div>
""", unsafe_allow_html=True)

# === MAIN WORKFLOW ===
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Step 1: Upload Your CSV")
    st.markdown("Upload your CRM export file (CSV format, max 200MB)")
    
    uploaded = st.file_uploader(
        "",
        type=["csv"],
        help=f"Drag and drop or click to browse. Maximum file size: {MAX_UPLOAD_SIZE // (1024*1024)}MB",
        label_visibility="collapsed"
    )
    
    if uploaded:
        st.success(f"✅ File uploaded: {uploaded.name} ({uploaded.size / (1024*1024):.1f} MB)")

with col2:
    st.markdown("### 🎯 Step 2: Select Target CRM")
    crm = st.selectbox(
        "Choose your destination CRM",
        available_crms(),
        format_func=lambda x: f"{x.title()} CRM",
        help="Select the CRM system you're migrating to"
    )
    
    st.markdown("### ⚙️ Processing Options")
    
    with st.expander("Advanced Cleaning Options", expanded=False):
        remove_duplicates = st.checkbox("Remove duplicate records", value=True)
        standardize_dates = st.checkbox("Standardize dates to YYYY-MM-DD", value=True)
        standardize_phones = st.checkbox("Standardize phones to E.164 format", value=True)
        fix_scientific = st.checkbox("Fix Excel scientific notation", value=True)
        normalize_unicode = st.checkbox("Normalize special characters", value=False)
        missing_strategy = st.selectbox(
            "Handle missing values",
            ["flag", "auto", "drop"],
            help="flag: Report missing values, auto: Fill with median/mode, drop: Remove rows with missing values"
        )
        region = st.text_input("Phone region code", value="US", max_chars=2, help="Default region for phone number parsing (e.g., US, UK, DE)")
        
        date_first = st.checkbox(
            "Parse dates as DD/MM/YYYY (European format)",
            value=False,
            help="Enable for European date formats. Disable for US formats (MM/DD/YYYY)"
        )

# === BRANDING & PROJECT ===
st.markdown("### 🏷️ Project & Branding")
col_a, col_b = st.columns([2, 1])
project_name = col_a.text_input("Project name", value="Client Migration", help="Name for this migration project")
brand_name_input = col_b.text_input("Your business name", value=brand["brand_name"], help="Your company name for reports")

# === OUTPUT OPTIONS ===
st.markdown("### 📦 Deliverables")
include_qa = st.checkbox("Include QA Report", value=True, help="Generate comprehensive quality assessment report")
include_mapping_log = st.checkbox("Include Mapping Log", value=True, help="Show how source columns map to target fields")
include_audit = st.checkbox("Post-Import Audit", value=False, help="Compare delivered file against exported CRM data")

audit_upload = None
audit_key = None
if include_audit:
    st.markdown("#### 🔍 Audit Configuration")
    col_c, col_d = st.columns([1, 1])
    audit_upload = col_c.file_uploader("Exported CRM file for audit", type=["csv"], key="audit")
    audit_key = col_d.text_input("Unique identifier column", value="email", help="Column that uniquely identifies records in both files")

# === CRM TEMPLATE PREVIEW ===
with st.expander(f"📋 Preview {crm.title()} CRM Template"):
    config = load_mapping_config(crm)
    template_df = pd.DataFrame([
        {
            "Field": f.name,
            "Required": "✅ Yes" if f.required else "No",
            "Unique": "🔑 Yes" if f.unique else "No",
            "Transform": f.transform or "None",
            "Aliases": ", ".join(f.aliases[:3]) if f.aliases else "None"
        }
        for f in config.fields
    ])
    st.dataframe(template_df, use_container_width=True, hide_index=True)

# === PROCESS BUTTON ===
st.markdown("---")
process_btn = st.button(
    "🚀 Process Data Migration",
    type="primary",
    use_container_width=True,
    disabled=uploaded is None
)

if process_btn and uploaded:
    # File size validation
    if uploaded.size > MAX_UPLOAD_SIZE:
        st.error(f"❌ File too large ({uploaded.size // (1024*1024)}MB). Maximum allowed size is {MAX_UPLOAD_SIZE // (1024*1024)}MB.")
        st.stop()
    
    try:
        with st.spinner("🔄 Processing your data... This may take 30-60 seconds."):
            source = read_upload(uploaded)
            
            # 500-row demo limit
            MAX_DEMO_ROWS = 500
            if len(source) > MAX_DEMO_ROWS:
                st.warning(f"⚠️ **Free Demo Limit:** Your file has {len(source)} rows. Only the first {MAX_DEMO_ROWS} rows will be processed in this free demo. For full file processing, contact us for professional services.")
                source = source.head(MAX_DEMO_ROWS)
            
            # Set branding
            import os
            os.environ["BRAND_NAME"] = brand_name_input
            os.environ["TOOL_NAME"] = brand["tool_name"]
            
            # Run pipeline
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

        # Success message
        summary = result.summary()
        st.markdown(f"""
<div class="success-message">
    ✅ <strong>Processing Complete!</strong>
    <br>
    <strong>{summary['rows_in']}</strong> rows processed → <strong>{summary['rows_out']}</strong> clean rows
    <br>
    Quality Score: <strong>{summary['quality_score']}%</strong>
</div>
""", unsafe_allow_html=True)

        # Quality metrics
        st.markdown("### 📊 Quality Metrics")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric("Quality Score", f"{summary['quality_score']}%", delta="high")
        metric_col2.metric("Records Out", summary["rows_out"])
        metric_col3.metric("Duplicates Removed", summary["duplicates_removed"])
        metric_col4.metric("Issues Found", summary["errors"])

        # Download section
        st.markdown("### 📥 Download Deliverables")
        download_col1, download_col2, download_col3 = st.columns(3)
        
        download_col1.download_button(
            "📊 Clean CSV",
            result.clean_frame.to_csv(index=False),
            file_name="clean_data.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        if include_qa:
            download_col2.download_button(
                "📋 QA Report",
                result.qa_report_html,
                file_name="qa_report.html",
                mime="text/html",
                use_container_width=True
            )
        
        if include_mapping_log:
            download_col3.download_button(
                "📝 Mapping Log",
                result.mapping_log().to_csv(index=False),
                file_name="mapping_log.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Tabbed results
        st.markdown("### 🔍 Detailed Results")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Clean Data Preview",
            "📋 Field Mapping Log", 
            "🧹 Cleaning Actions",
            "⚠️ Issues Found",
            "📄 Full QA Report"
        ])
        
        with tab1:
            st.dataframe(result.clean_frame.head(50), use_container_width=True)
            st.caption(f"Showing first 50 of {len(result.clean_frame)} clean rows")
        
        with tab2:
            st.dataframe(result.mapping_log(), use_container_width=True)
            st.caption("How source columns were mapped to target CRM fields")
        
        with tab3:
            st.dataframe(result.cleaning_log(), use_container_width=True)
            st.caption("All cleaning transformations applied to your data")
        
        with tab4:
            issues = result.validation.issues_frame()
            if not issues.empty:
                st.dataframe(issues, use_container_width=True)
                st.caption(f"Found {len(issues)} issues requiring manual review")
            else:
                st.success("✅ No issues found! Data is perfectly clean.")
        
        with tab5:
            st.components.v1.html(result.qa_report_html, height=800, scrolling=True)

        # Audit section
        if include_audit and audit_upload is not None and audit_key:
            st.markdown("### 🔍 Post-Import Audit Results")
            audit = audit_import(
                expected=result.clean_frame, 
                exported=read_upload(audit_upload), 
                key=audit_key
            )
            
            audit_col1, audit_col2 = st.columns(2)
            audit_col1.json(audit.stats())
            audit_col2.dataframe(audit.mismatches, use_container_width=True)
            
            st.download_button(
                "🧾 Download Audit Report",
                render_audit_report(audit.stats(), audit.mismatches, project_name),
                file_name="audit_report.html",
                mime="text/html",
                use_container_width=True
            )

    except UnicodeDecodeError as e:
        st.error("❌ **File Encoding Error**: The file appears to use an unusual encoding. Please check that it's a valid CSV export and try again.")
        st.error(f"Technical details: {str(e)}")
    except pd.errors.EmptyDataError:
        st.error("❌ **Empty File Error**: The uploaded file appears to be empty. Please check the file and try again.")
    except pd.errors.ParserError as e:
        st.error("❌ **File Format Error**: The file format looks unusual. Please check that it's a valid CSV export and try again.")
        st.error(f"Technical details: {str(e)}")
    except Exception as e:
        st.error("❌ **Processing Error**: Something went wrong while processing the file. Please check that it's a valid CSV export and try again.")
        st.error(f"Technical details: {str(e)}")

elif uploaded is None:
    st.info("👆 Upload a CSV file above to begin the data migration process.")

# === FOOTER ===
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6b7280; font-size: 0.9rem; margin-top: 2rem;">
    <p><strong>Professional Data Migration Services</strong></p>
    <p>Pricing: <strong>Starter $600</strong> | <strong>Standard $1,500</strong> | <strong>Premium $2,000</strong></p>
    <p>🚀 <strong>Free Demo:</strong> First 500 rows • 🔒 <strong>Privacy Guaranteed</strong> • ⚡ <strong>Fast Delivery</strong></p>
    <p>© 2024 {brand['brand_name']}. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
