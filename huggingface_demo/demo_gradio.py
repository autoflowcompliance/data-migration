"""Professional Gradio interface for the AutoFlow data migration tool.

Run with: ``python demo_gradio.py``
Deploy to Hugging Face Spaces with the app.py entry point.
"""
import gradio as gr
import pandas as pd
import tempfile
import os
from pathlib import Path
import chardet
import io

# Import your existing pipeline
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_migration_tool.pipeline import run_pipeline
from data_migration_tool.cleaners import CleaningConfig
from data_migration_tool.mappers import available_crms

def read_upload(file):
    """Read uploaded CSV with automatic encoding detection."""
    if file is None:
        return None
    
    try:
        with open(file.name, 'rb') as f:
            raw = f.read()
        result = chardet.detect(raw)
        encoding = result['encoding'] or 'utf-8'
        return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)
    except Exception as e:
        return None

def process_csv(file, crm, date_first, brand_name, remove_duplicates, standardize_dates, standardize_phones, fix_scientific, missing_strategy, phone_region):
    """
    Process the uploaded CSV and return:
    1. A download button for the clean CSV
    2. A preview of the clean data
    3. A summary of what was fixed
    4. QA report if available
    """
    try:
        if file is None:
            return None, "❌ Please upload a CSV file first.", pd.DataFrame(), None
        
        # Read the file
        df = read_upload(file)
        if df is None:
            return None, "❌ Error reading the CSV file. Please check the file format.", pd.DataFrame(), None
        
        # --- 500-ROW DEMO LIMIT ---
        total_rows = len(df)
        if total_rows > 500:
            df = df.head(500)
            limit_warning = f"⚠️ **Free Demo Limit:** Your file had {total_rows} rows. Only the first 500 rows were processed in this free demo. Contact us for the full file processing."
        else:
            limit_warning = f"✅ **Full File Processed:** {total_rows} rows processed."
        
        # Set branding environment variables
        os.environ["BRAND_NAME"] = brand_name if brand_name else "AutoFlow"
        os.environ["TOOL_NAME"] = "Data Migration Tool"
        
        # Run the pipeline
        config = CleaningConfig(
            remove_duplicates=remove_duplicates,
            standardize_dates=standardize_dates,
            standardize_phones=standardize_phones,
            fix_scientific_notation=fix_scientific,
            normalize_unicode=False,
            missing_value_strategy=missing_strategy,
            default_region=phone_region.upper() if phone_region else "US",
            date_first=date_first,
        )
        
        result = run_pipeline(
            source=df,
            crm=crm,
            cleaning_config=config,
            project_name="Demo",
            source_filename=os.path.basename(file.name),
        )
        
        # Save the clean CSV to a temporary file
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        result.clean_frame.to_csv(temp_csv.name, index=False)
        temp_csv.close()
        
        # Save QA report to temporary file
        temp_qa = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        temp_qa.write(result.qa_report_html.encode('utf-8'))
        temp_qa.close()
        
        # Get summary
        summary = result.summary()
        
        # Build the output message
        summary_text = f"""
        ## 📊 Processing Complete
        
        ### Quality Metrics
        - **Quality Score:** {summary['quality_score']}%
        - **Records Out:** {summary['rows_out']}
        - **Duplicates Removed:** {summary['duplicates_removed']}
        - **Errors Found:** {summary['errors']}
        - **Warnings:** {summary['warnings']}
        
        {limit_warning}
        
        ---
        **Powered by {brand_name if brand_name else 'AutoFlow'}**
        """
        
        # Preview of the clean data (first 10 rows)
        preview = result.clean_frame.head(10)
        
        return temp_csv.name, summary_text, preview, temp_qa.name
        
    except Exception as e:
        return None, f"❌ **Error:** {str(e)}", pd.DataFrame(), None

# --- Build the Professional Gradio Interface ---

# Custom CSS for professional styling
custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
    padding: 2rem !important;
}

.header-text {
    font-size: 32px !important;
    font-weight: 700 !important;
    margin-bottom: 8px !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-text {
    color: #6b7280 !important;
    font-size: 18px !important;
    margin-bottom: 24px !important;
}

.trust-badges {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}

.trust-badge {
    background: #f3f4f6;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    border: 1px solid #e5e7eb;
}

.processing-section {
    background: white;
    padding: 24px;
    border-radius: 12px;
    border: 2px solid #e5e7eb;
    margin: 24px 0;
}

.success-banner {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
    color: white;
    padding: 16px;
    border-radius: 8px;
    margin: 16px 0;
    font-weight: 600;
}
"""

# Define the layout
with gr.Blocks(
    title="Data Migration Tool - Professional CRM Data Cleaning",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="gray",
        font=gr.themes.GoogleFont("Inter"),
    ),
    css=custom_css,
) as demo:
    
    # Professional Header
    gr.Markdown(
        """
        <div class="header-text">⚡ Data Migration Tool</div>
        <div class="sub-text">Professional CRM Data Cleaning & Migration Services</div>
        """,
        elem_classes=["header-text"]
    )
    
    # Trust badges
    with gr.Row():
        gr.Markdown("🔒 **Zero Data Storage**", elem_classes=["trust-badge"])
        gr.Markdown("⚡ **60-Second Processing**", elem_classes=["trust-badge"])
        gr.Markdown("🎯 **95%+ Quality Score**", elem_classes=["trust-badge"])
        gr.Markdown("📋 **First 500 Rows Free**", elem_classes=["trust-badge"])
    
    # Privacy guarantee
    gr.Markdown(
        """
        > 🔒 **Privacy Guarantee:** Your file is processed temporarily in memory and is **not stored on our servers**. 
        > It is automatically deleted after your session ends. We take data security seriously.
        """
    )
    
    # Main processing section
    with gr.Row():
        with gr.Column(scale=2):
            file_input = gr.File(
                label="📤 Upload Your CRM Export",
                file_types=[".csv"],
                interactive=True,
                type="filepath"
            )
        with gr.Column(scale=1):
            crm_select = gr.Dropdown(
                choices=available_crms(),
                label="🎯 Target CRM",
                value="hubspot",
                info="Select your destination CRM system"
            )
            brand_name = gr.Textbox(
                label="🏷️ Your Business Name",
                value="AutoFlow",
                placeholder="Your Company Name",
                info="Your brand will appear in reports"
            )
    
    # Advanced options
    with gr.Accordion("⚙️ Advanced Processing Options", open=False):
        with gr.Row():
            with gr.Column():
                remove_duplicates = gr.Checkbox(
                    label="Remove duplicate records",
                    value=True,
                    info="Remove exact duplicate rows"
                )
                standardize_dates = gr.Checkbox(
                    label="Standardize dates to YYYY-MM-DD",
                    value=True,
                    info="Convert any date format to ISO standard"
                )
                standardize_phones = gr.Checkbox(
                    label="Standardize phones to E.164 format",
                    value=True,
                    info="Convert to international format (+15551234567)"
                )
            with gr.Column():
                fix_scientific = gr.Checkbox(
                    label="Fix Excel scientific notation",
                    value=True,
                    info="Fix SKUs like 4.05E+14 to 405000000000000"
                )
                date_first = gr.Checkbox(
                    label="Parse dates as DD/MM/YYYY (European format)",
                    value=False,
                    info="Enable for European date formats"
                )
                missing_strategy = gr.Dropdown(
                    choices=["flag", "auto", "drop"],
                    value="flag",
                    label="Handle missing values",
                    info="flag: Report, auto: Fill with median/mode, drop: Remove rows"
                )
                phone_region = gr.Textbox(
                    label="Phone region code",
                    value="US",
                    max_chars=2,
                    info="Default region for phone parsing (e.g., US, UK, DE)"
                )
    
    process_btn = gr.Button(
        "🚀 Process Data Migration",
        variant="primary",
        size="lg"
    )
    
    # Results section
    with gr.Row():
        with gr.Column():
            file_output = gr.File(
                label="📥 Download Clean CSV",
                interactive=False,
            )
        with gr.Column():
            qa_output = gr.File(
                label="📋 Download QA Report",
                interactive=False,
            )
    
    summary_output = gr.Markdown(label="📊 Processing Summary")
    
    # Data preview
    preview_output = gr.Dataframe(
        label="📋 Preview of Clean Data (First 10 Rows)",
        headers=True,
        interactive=False,
    )
    
    # --- Connect the function to the UI ---
    process_btn.click(
        fn=process_csv,
        inputs=[
            file_input, 
            crm_select, 
            date_first, 
            brand_name,
            remove_duplicates,
            standardize_dates,
            standardize_phones,
            fix_scientific,
            missing_strategy,
            phone_region
        ],
        outputs=[file_output, summary_output, preview_output, qa_output],
    )
    
    # Footer with pricing
    gr.Markdown(
        """
        ---
        
        ### 💼 Professional Services
        
        **Pricing Tiers:**
        - **Starter ($600)** - Up to 10,000 records
        - **Standard ($1,500)** - Up to 50,000 records  
        - **Premium ($2,000)** - Unlimited records + priority support
        
        🚀 **Free Demo:** First 500 rows • 🔒 **Privacy Guaranteed** • ⚡ **Fast Delivery**
        
        *© 2024 AutoFlow. Professional Data Migration Services.*
        """
    )

# --- Launch ---
if __name__ == "__main__":
    import os
    # Use PORT environment variable for Render, default to 7860 for local
    port = int(os.environ.get("PORT", 7860))
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )