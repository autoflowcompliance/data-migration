# Admin CLI — Usage Guide

**Status**: ✅ Ready to use (no external dependencies, no Hugging Face)

## Quick Start

```bash
python admin.py
```

This opens an interactive menu system for processing client files.

---

## Menu Options

### 1️⃣ Process a New Job

Process a complete CSV file for a client with full output package.

**What it does:**
- Uploads and validates a CSV file
- Selects target CRM (HubSpot, Salesforce, Pipedrive)
- Applies data cleaning (configurable)
- Validates data quality
- Generates ZIP package with all deliverables

**Deliverables by tier:**
- **Starter** ($600): `clean_data.csv` only
- **Standard** ($1,500): CSV + Mapping Log + Cleaning Log + Issues + QA Report
- **Premium** ($2,000): All of Standard

**Prompts:**
```
Path to client's CSV file: [full/path/to/file.csv]
Client / project name: [Client Name]
Client email: [client@example.com]
Package tier: Select 1, 2, or 3
Price: [$ amount]
Target CRM: Select 1, 2, or 3 (HubSpot/Salesforce/Pipedrive)
Use default cleaning settings: [y/n]
```

**Output:**
- ZIP file in `deliveries/` folder
- Entry added to `orders_log.csv`
- Quality score and guarantee check

---

### 2️⃣ Run Post-Import Audit

Verify that data imported correctly into the client's CRM.

**What it does:**
- Compares expected data (what you sent) vs. actual data (what imported)
- Identifies mismatches, missing records, data corruption
- Generates HTML audit report

**Prompts:**
```
Client / project name: [for report]
Path to the clean_data.csv you delivered: [path]
Path to the client's fresh CRM export: [path]
Unique key column: [email, id, etc]
```

**Output:**
- HTML audit report in `deliveries/` folder
- Summary of:
  - Total records
  - Match count
  - Mismatch details
  - Missing records

---

### 3️⃣ View Job Log

Display all processed jobs in reverse chronological order.

**Shows:**
- Timestamp
- Client name & email
- Tier & price
- Rows in/out
- Quality score
- Errors & warnings
- Guarantee met status
- ZIP filename

---

### 4️⃣ Exit

Close the application.

---

## Configuration

### Cleaning Options (Customizable per job)

```
✓ Remove duplicate records (default: yes)
✓ Standardise dates to YYYY-MM-DD (default: yes)
✓ Standardise phones to E.164 (default: yes)
✓ Repair Excel scientific notation (default: yes)
✗ Fold accents to ASCII (default: no)
? Missing values strategy: flag | auto | drop (default: flag)
? Default phone region: US | UK | etc (default: US)
✗ Parse dates day-first DD/MM/YYYY (default: no for US)
```

### Branding (Custom per job)

```
Brand name: [AutoFlow]
Tool name: [Data Migration Tool]
```

---

## Files & Directories

### Output Locations

```
deliveries/              # ZIP packages and audit reports
  ├─ Client_A_hubspot_20260901_120000.zip
  ├─ Client_B_salesforce_20260901_130000.zip
  └─ audit_Client_A_20260901_120000.html

orders_log.csv           # Job history (CSV format)
```

### Order Log Columns

```
timestamp              2026-09-01T12:00:00
client_name            ACME Corp
client_email           ops@acme.com
tier                   Standard
price                  1500
target_crm             hubspot
rows_in                5000
rows_out               4999
quality_score          95
errors                 0
warnings               5
guarantee_met          TRUE
zip_filename           ACME_Corp_hubspot_20260901_120000.zip
```

---

## ZIP Package Contents

### Starter Package
```
client_name_crm_timestamp.zip
└─ clean_data.csv          (Import-ready CSV file)
```

### Standard/Premium Packages
```
client_name_crm_timestamp.zip
├─ clean_data.csv          (Import-ready data)
├─ mapping_log.csv         (Source column → Target field)
├─ cleaning_log.csv        (All cleaning actions taken)
├─ issues.csv              (Rows needing review)
└─ qa_report.html          (Professional QA report)
```

---

## Quality Gates

### Guarantee Threshold

```
Guarantee Met (PASS):
  ✅ 0 errors (default setting)
  → Safe to deliver to client

Guarantee NOT Met (WARN):
  ⚠️  > 0 errors detected
  → Prompt user to review before delivery
  → Option to proceed anyway with warning
```

### Quality Score Calculation

Based on:
- Completeness (required fields filled)
- Uniqueness (unique keys valid)
- Validity (email, phone, date formats correct)
- Consistency (data type matches expected)

Range: 0-100%

---

## Example Workflows

### Workflow 1: Basic Job Processing

```
$ python admin.py
1) Process a new job ← Select 1

Path to CSV: /Users/data/client_export.csv
Client name: Acme Inc
Email: ops@acme.com
Tier: 2 (Standard)
Price: 1500
CRM: 1 (HubSpot)
Use defaults: y (yes)

[Processing...]
✅ Done: 5,000 rows → 4,999 rows
✅ Guarantee met: YES
Saved to: deliveries/Acme_Inc_hubspot_20260901_120000.zip
```

### Workflow 2: Audit Import

```
$ python admin.py
2) Run post-import audit ← Select 2

Project name: Acme Inc
Expected CSV: deliveries/clean_data.csv
Actual export: /Users/acme_crm_export.csv
Key column: email

[Comparing...]
✅ Audit complete
📊 Report saved: deliveries/audit_Acme_Inc_20260901_120000.html
```

---

## Troubleshooting

### Error: File not found
**Solution**: Provide full path, e.g., `/Users/Downloads/file.csv` not `~/Downloads/file.csv`

### Error: Could not read file
**Solution**: 
- Verify CSV encoding (UTF-8 preferred)
- Ensure first row has column headers
- Test with `app_files/samples/messy_contacts.csv`

### Error: Audit failed
**Solution**:
- Check both files have the key column
- Key column name must match exactly
- Both files must be valid CSVs

### Quality score too low
**Review:**
- Missing required fields (check `issues.csv`)
- Invalid phone/email formats
- Inconsistent data types
- Apply different cleaning options

---

## Advanced Usage

### Running from Python

```python
from admin import process_new_job, run_audit_flow, view_job_log

# Process a job
process_new_job()

# Run an audit
run_audit_flow()

# View all jobs
view_job_log()
```

### Batch Processing (Coming Soon)

For automating multiple files, see `admin.py` for CLI version or contact support.

---

## Support

For issues:
1. Check error message carefully
2. Review file format with sample: `app_files/samples/messy_contacts.csv`
3. Verify all required columns are present
4. Check phone/email/date formats

---

## Features

✅ No row limit (processes full files)  
✅ No file size limit (uses your RAM)  
✅ Configurable data cleaning  
✅ Quality scoring  
✅ Tier-based deliverables  
✅ Post-import audit  
✅ Job history tracking  
✅ Custom branding  
✅ ZIP packaging  
✅ No external dependencies (except core Python libs)  
✅ No Hugging Face or cloud dependencies  

---

*Last updated: 2026-09-01*
