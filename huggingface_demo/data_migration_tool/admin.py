"""Admin Dashboard - Private Client Delivery System

This is your personal backend system for processing client files locally.
Run this on your own computer to handle paid client work without command line.

Usage: streamlit run admin.py
"""
import streamlit as st
import pandas as pd
import zipfile
import io
import tempfile
from pathlib import Path
import datetime
import sys

# Import your existing pipeline
if __package__ in (None, ""):  # allow `streamlit run admin.py` 
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_migration_tool.pipeline import run_pipeline
from data_migration_tool.cleaners import CleaningConfig
from data_migration_tool.mappers import available_crms

st.set_page_config(page_title="🧑‍💻 Admin - Client Delivery System", layout="wide")

st.title("🧑‍💻 Client Job Processor (Backend)")
st.caption("Upload a client's full file here. No row limits. Generates the full zip package for delivery.")

# --- Privacy Notice ---
st.warning("""
🔒 **Private Admin Panel**: This runs locally on your machine only. 
Client data is never uploaded to external servers. Files are processed in memory 
and can be deleted after delivery for maximum privacy.
""")

# --- Sidebar Settings ---
with st.sidebar:
    st.header("⚙️ Processing Settings")
    remove_duplicates = st.checkbox("Remove duplicates", value=True)
    standardize_dates = st.checkbox("Standardize dates", value=True)
    date_first = st.checkbox(
        "Parse dates day-first (DD/MM/YYYY)", 
        value=False,
        help="Enable for European date formats. Disable for US (MM/DD/YYYY)."
    )
    standardize_phones = st.checkbox("Standardize phones (E.164)", value=True)
    fix_scientific = st.checkbox("Fix Excel scientific notation", value=True)
    missing_strategy = st.selectbox("Missing values", ["flag", "auto", "drop"])
    region = st.text_input("Phone region", value="US")
    
    st.divider()
    st.header("📦 Delivery Options")
    client_name = st.text_input("Client / Project Name", value="Client_Migration")
    target_crm = st.selectbox("Target CRM", available_crms())
    
    # White-labeling options
    st.divider()
    st.header("🏷️ Branding Options")
    brand_name = st.text_input("Brand Name (for reports)", value="Your Business Name")
    tool_name = st.text_input("Tool Name (for reports)", value="Data Migration Tool")

# --- Main Upload Area ---
uploaded_file = st.file_uploader("Upload the FULL Client CSV (No row limits)", type=["csv"])

if uploaded_file is not None:
    # 1. Read the file (No row limit here!)
    with st.spinner("Reading file..."):
        try:
            # Auto-detect encoding
            raw_data = uploaded_file.read()
            import chardet
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
            import io
            source = pd.read_csv(io.BytesIO(raw_data), dtype=str, encoding=encoding, keep_default_na=False)
            st.success(f"✅ File loaded: {len(source)} rows, {len(source.columns)} columns.")
        except Exception as e:
            st.error(f"Failed to read file: {e}")
            st.stop()

    # 2. Processing Button
    if st.button("🚀 Process Full File for Client", type="primary"):
        
        # Show progress
        progress_bar = st.progress(0, text="Starting pipeline...")

        try:
            # Run the exact same pipeline, but without the 500-row limit
            config = CleaningConfig(
                remove_duplicates=remove_duplicates,
                standardize_dates=standardize_dates,
                date_first=date_first,
                standardize_phones=standardize_phones,
                fix_scientific_notation=fix_scientific,
                missing_value_strategy=missing_strategy,
                default_region=region.upper() or "US",
            )
            
            progress_bar.progress(30, text="Cleaning, mapping, and validating...")
            
            # Set environment variables for branding
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
            
            progress_bar.progress(90, text="Generating deliverables...")
            
            # 3. Prepare the ZIP file for the client
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Add Clean CSV
                zip_file.writestr("clean_data.csv", result.clean_frame.to_csv(index=False))
                # Add Mapping Log
                zip_file.writestr("mapping_log.csv", result.mapping_log().to_csv(index=False))
                # Add Cleaning Log
                zip_file.writestr("cleaning_log.csv", result.cleaning_log().to_csv(index=False))
                # Add Issues CSV
                zip_file.writestr("issues.csv", result.validation.issues_frame().to_csv(index=False))
                # Add QA Report (HTML)
                zip_file.writestr("qa_report.html", result.qa_report_html)
            
            zip_buffer.seek(0)
            
            progress_bar.progress(100, text="Done!")
            st.balloons()
            
            # 4. Show Summary Statistics
            summary = result.summary()
            st.subheader("📊 Delivery Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Quality Score", f"{summary['quality_score']}%")
            col2.metric("Records Out", summary['rows_out'])
            col3.metric("Duplicates Removed", summary['duplicates_removed'])
            col4.metric("Errors to Review", summary['errors'])
            
            # Show a preview of the issues
            issues = result.validation.issues_frame()
            if not issues.empty:
                st.warning(f"⚠️ {len(issues)} issues found. Check the 'issues.csv' in the zip.")
                st.dataframe(issues.head(10))
            
            # 5. THE DOWNLOAD BUTTON
            st.divider()
            st.subheader("📥 Download Client Package")
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            zip_filename = f"{client_name}_{target_crm}_{timestamp}_deliverables.zip"
            
            st.download_button(
                label=f"⬇️ Download Full Package ({zip_filename})",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip",
                use_container_width=True,
            )
            
            st.success("✅ Processing complete! Send this zip file to your client.")
            
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.stop()

st.info("""
👆 **Admin Panel Usage**:
1. Upload client CSV file (no size limits)
2. Configure processing settings in sidebar
3. Click "Process Full File for Client"
4. Download the complete ZIP package
5. Email ZIP to client and delete local files for privacy

🔒 **Privacy**: All processing happens locally. No data leaves your machine.
""")
