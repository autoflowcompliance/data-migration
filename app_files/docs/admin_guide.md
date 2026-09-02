# Admin Dashboard Guide - Private Client Delivery System

This guide explains how to use the private admin dashboard for processing client files locally without command line interface.

## What is the Admin Dashboard?

The admin dashboard (`admin.py`) is your **private backend system** that runs locally on your computer. It's designed for processing paid client work with:

- **No file size limits** - Uses your local machine's RAM/HDD
- **No command line** - Point-and-click GUI interface
- **Automatic ZIP packaging** - All deliverables bundled automatically
- **White-label branding** - Custom branding for each client
- **Complete privacy** - No data leaves your machine

## Setup & Installation

### Prerequisites
- Python 3.10+ installed
- All dependencies installed: `pip install -r data_migration_tool/requirements.txt`

### Running the Admin Dashboard

Open a terminal in your project root directory and run:

```bash
streamlit run admin.py
```

The admin panel will open in your browser at: `http://localhost:8501`

## How to Use the Admin Dashboard

### Step 1: Upload Client File

1. Client sends you their CSV file via secure transfer (Google Drive/Dropbox)
2. Download the file to your computer
3. Open the admin dashboard in your browser
4. Upload the CSV file using the file uploader

**Note:** There are no file size limits since this runs locally.

### Step 2: Configure Processing Settings

In the sidebar, configure:

**Processing Settings:**
- **Remove duplicates**: Automatically remove duplicate records
- **Standardize dates**: Convert dates to ISO format (YYYY-MM-DD)
- **Parse dates day-first**: Enable for European formats (DD/MM/YYYY)
- **Standardize phones**: Convert phone numbers to E.164 format
- **Fix Excel scientific notation**: Expand numbers like 4.05E+14
- **Missing values**: Strategy for handling empty values (flag/auto/drop)
- **Phone region**: Default region for phone numbers (US, UK, etc.)

**Delivery Options:**
- **Client/Project Name**: Used for ZIP file naming
- **Target CRM**: Select from HubSpot, Salesforce, Pipedrive, or custom

**Branding Options:**
- **Brand Name**: Your business name for reports
- **Tool Name**: Custom tool name for white-labeling

### Step 3: Process the File

1. Click the **"🚀 Process Full File for Client"** button
2. Wait for processing (typically 30-60 seconds for most files)
3. View the delivery summary with quality metrics

### Step 4: Download and Deliver

1. Click the **"⬇️ Download Full Package"** button
2. A ZIP file will be downloaded with naming format:
   ```
   ClientName_CRM_YYYYMMDD_HHMM_deliverables.zip
   ```
3. Email the ZIP file to your client
4. Delete the local files for privacy

## ZIP Package Contents

The downloaded ZIP file contains:

- **clean_data.csv** - Import-ready file for the target CRM
- **mapping_log.csv** - Field mapping details and confidence scores
- **cleaning_log.csv** - All cleaning actions performed
- **issues.csv** - Row-level issues requiring manual review
- **qa_report.html** - Comprehensive quality assessment report

## Privacy & Security

### Local Processing Only
- Files are processed on your local machine
- No data is uploaded to external servers
- No AI training with client data
- Complete control over data lifecycle

### Recommended Privacy Workflow

1. **Receive File**: Download from secure transfer (Google Drive/Dropbox)
2. **Process**: Use admin dashboard locally
3. **Deliver**: Email ZIP package to client
4. **Cleanup**: Delete source file from Downloads folder
5. **Clear Browser**: Close admin dashboard (clears memory)

### Additional Security Measures

- Use encrypted file transfer for initial upload
- Sign NDAs with clients before processing
- Delete files immediately after delivery
- Keep your system updated with security patches
- Use strong passwords on your computer

## Advanced Features

### White-Label Delivery

The admin dashboard supports white-labeling for agencies:

1. Set custom brand name in sidebar
2. Set custom tool name for reports
3. QA reports will show your branding instead of generic names
4. Perfect for agencies serving their own clients

### Batch Processing

For multiple client files:

1. Process first client file
2. Download ZIP package
3. Clear the admin dashboard (refresh page)
4. Upload next client file
5. Repeat for each client

### Custom CRM Configurations

If you need to process for a CRM not in the default list:

1. Create custom YAML config in `data_migration_tool/configs/`
2. Follow the guide in `docs/custom_crm_guide.md`
3. The custom CRM will appear in the dropdown automatically

## Troubleshooting

### Admin Dashboard Won't Start

**Issue:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install -r data_migration_tool/requirements.txt
```

### File Upload Fails

**Issue:** "Failed to read file" error

**Solutions:**
- Ensure the file is a valid CSV
- Check that the file isn't corrupted
- Try opening the file in Excel first to verify it's readable

### Processing Takes Too Long

**Issue:** Processing seems stuck or very slow

**Solutions:**
- Large files (>100MB) may take several minutes
- Check your available RAM
- Close other applications to free up resources
- Consider processing in smaller chunks if needed

### ZIP File Won't Open

**Issue:** Downloaded ZIP file is corrupted

**Solutions:**
- Try re-downloading the package
- Check your browser download settings
- Ensure you have enough disk space
- Try a different browser

## Comparison: Admin vs Public App

| Feature | Admin Dashboard | Public Streamlit App |
|---------|----------------|---------------------|
| **File Size Limit** | None (local RAM) | 200MB (cloud limits) |
| **Privacy** | 100% local | Temporary cloud processing |
| **Access** | You only | Anyone with URL |
| **ZIP Packaging** | Automatic | Manual download |
| **White-labeling** | Per-client | Global settings |
| **Use Case** | Paid client work | Free demos/portfolio |

## Integration with Professional Workflow

### Complete Client Workflow

1. **Initial Contact**: Send portfolio + privacy guarantee
2. **File Transfer**: Client uploads to secure Google Drive folder
3. **Local Processing**: Use admin dashboard to process file
4. **Quality Review**: Check QA report for any issues
5. **Delivery**: Email ZIP package to client
6. **Follow-up**: Confirm satisfaction and request feedback

### Pricing Integration

Use the admin dashboard for different service tiers:

- **Standard Processing**: $50-300 (depending on file size)
- **Rush Processing**: 2x standard rate (4-hour turnaround)
- **Agency Partnership**: Custom pricing with white-labeling
- **Complex Migrations**: Custom quotes for multi-CRM projects

## System Requirements

### Minimum Requirements
- **RAM**: 4GB (8GB recommended for large files)
- **Storage**: 2GB free space for temporary processing
- **Python**: 3.10 or higher
- **OS**: Windows, macOS, or Linux

### Recommended Setup
- **RAM**: 16GB for optimal performance
- **Storage**: SSD for faster file processing
- **Python**: Latest stable version
- **Browser**: Chrome, Firefox, or Edge (latest version)

## Next Steps

1. **Test the Dashboard**: Run with sample file first
2. **Create Portfolio**: Generate sample outputs for marketing
3. **Set Pricing**: Determine your service pricing structure
4. **Prepare Templates**: Customize client communication templates
5. **Start Marketing**: Begin outreach to potential clients

## Support

For technical issues:
- Check the main README.md for general troubleshooting
- Review deployment_guide.md for Streamlit-specific issues
- Consult professional_delivery_guide.md for business questions

The admin dashboard is your private, professional backend system for handling paid client data migration work with complete privacy and control.
