# AutoFlow Data Migration Tool

Takes a messy CRM export and returns an import-ready CSV, a mapping log and a QA report.
Optionally audits what the client actually ended up with after the import.

```
raw CSV -> CLEANER -> MAPPER -> VALIDATOR -> deliverables -> POST-IMPORT AUDITOR
```

## Quick start

```bash
cd app_files
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Web interface
streamlit run app.py

# Command line
python -m app_files.cli \
  -i app_files/samples/messy_contacts.csv \
  -c hubspot \
  -o output              # run from the repository root
```

The CLI exits with status `1` when the validator found errors, so it can gate a delivery script.

## Deliverables

| File | Contents |
| --- | --- |
| `clean_data.csv` | Import-ready file in the target CRM's column layout |
| `mapping_log.csv` | Target field, source column, match type, confidence, transform |
| `cleaning_log.csv` | Every cleaning action and how many records it touched |
| `issues.csv` | Row-level issues with a recommended fix |
| `qa_report.html` | Quality score, check summary, issues, mapping, sample records |
| `audit_report.html` + `audit_mismatches.csv` | Optional post-import comparison |

## Components

### Cleaner (`cleaners/`)

Configuration driven, with no hardcoded column names: each column's role
(email / phone / date / numeric / identifier) is inferred from its header and its
values, and can be overridden in a YAML config.

| Issue | Before | After |
| --- | --- | --- |
| Date formats | `12/31/24`, `31-Dec-24` | `2024-12-31` |
| Phone numbers | `(555) 123-4567`, `555.123.4567` | `+15551234567` |
| Excel scientific notation | `4.05E+14` | `405000000000000` |
| Whitespace | `"  John   Smith "` | `"John Smith"` |
| Email case | `JOHN@Email.com` | `john@email.com` |
| Duplicates / missing values | duplicated rows, blanks | deduplicated; blanks flagged, filled or dropped |

```yaml
# cleaning.yaml
pipeline:
  cleaning:
    remove_duplicates: true
    missing_value_strategy: auto   # flag | auto | drop
    date_format: "%Y-%m-%d"
    date_first: false              # true for DD/MM/YYYY, false for MM/DD/YYYY
    default_region: US             # phone region for national-format numbers
    normalize_unicode: false
    phone_columns: ["Phone 1"]     # optional explicit roles
```

```bash
python -m app_files.cli -i raw.csv -c hubspot --cleaning-config cleaning.yaml
```

### Mapper (`mappers/`, `configs/`)

Each target CRM is a YAML template listing its fields, aliases and per-field transforms.
A source column is matched to a target field by alias, then by fuzzy name match; anything
unmatched is reported in the mapping log rather than silently dropped.

```yaml
crm: HubSpot
fields:
  - name: email
    required: true
    unique: true
    transform: email_lowercase
    aliases: ["Email Address", "E-mail", "Primary Email"]
  - name: Name            # several source columns can feed one field
    sources: ["First Name", "Last Name"]
    separator: " "
```

Ships with `hubspot`, `salesforce` and `pipedrive`; add a CRM by dropping a YAML file into
`configs/`, or pass a path to any config with `-c path/to/config.yaml`.
Available transforms: `phone_e164`, `email_lowercase`, `date_iso`, `trim`, `title_case`,
`upper_case`, `lower_case`, `digits_only`, `ascii`, `expand_scientific_notation`.

### Validator (`validators/`)

Checks completeness (required fields), uniqueness, validity (emails via pattern, phones via
`phonenumbers`, dates against the target format) and consistency, and runs a structural check
over the output file with Frictionless. The quality score is the share of records with no
error and no warning.

### Post-import auditor (`auditors/`)

```bash
python -m app_files.cli -i raw.csv -c hubspot \
  --audit-export exported_from_crm.csv --audit-key email
```

Diffs the delivered file against the client's post-import export on a key column and reports
missing records, unexpected records and per-field value mismatches.

## Critical Fixes Implemented

This version includes several critical fixes for production use:

1. **File Encoding Detection**: Automatically detects file encoding using `chardet` to handle non-UTF-8 files (common with legacy CRMs)
2. **Day-First Date Parsing**: Added `--date-dayfirst` CLI option and UI toggle to handle European vs American date formats
3. **Scientific Notation Fix**: Restored `expand_scientific_notation` transform to prevent Excel corruption of numeric IDs
4. **Frictionless Framework**: Fully integrated Frictionless for structural validation and schema checking
5. **Report Generation**: Fixed Jinja2 template rendering for standalone QA reports
6. **White-Label Branding**: Added customizable branding via environment variables/Streamlit secrets

## White-Label Branding

The tool supports custom branding for agencies:

1. Go to your app dashboard on share.streamlit.io
2. Click the "Settings" gear icon
3. Scroll to "Secrets" 
4. Add the following environment variables:
   ```
   BRAND_NAME = "Your Agency Name"
   TOOL_NAME = "Migration Engine"
   LOGO_URL = "https://your-logo-url.png"  # Optional
   ```

This allows agencies to white-label the tool for their clients with their own branding.

## Development

```bash
pip install -r requirements-dev.txt
pytest                     # from app_files/
ruff check .
mypy .                     # run as `mypy app_files` from the repository root
```

## Custom CRM Configurations

See `docs/custom_crm_guide.md` for detailed instructions on creating custom CRM mapping configurations. A template is provided in `configs/mapping_template.yaml`.

## License

This tool is provided as-is for data migration projects.
