# Configuration

A config file tells the mapper how to turn one source file's columns into a
target system's canonical columns. Configs live in `app_files/configs/` and are
loaded by name: `app_files/configs/hubspot.yaml` is the `hubspot` config.

Anything in that folder shows up in the web UI's **Target config** selector
automatically — `available_crms()` scans the directory, so adding a file is the
whole step. No code change, no registry to update.

```
app_files/configs/
├── bank_reconciliation.yaml
├── hubspot.yaml
├── pipedrive.yaml
├── quickbooks.yaml
├── salesforce.yaml
└── schema/
    └── rules_schema.json   # validates the rules: block
```

## Config anatomy

```yaml
crm: HubSpot          # display name, shown in the UI
version: "1.0"        # free-form; bump when you change the mapping

fields:               # the target columns, in output order
  - name: email
    required: true
    unique: true
    transform: email_lowercase
    aliases: ["Email Address", "E-mail", "Primary Email"]

rules:                # optional validation rules, see RULES.md
  - name: email_required
    field: email
    type: required
    severity: error
```

### `fields`

| Key | Meaning |
| --- | --- |
| `name` | The output column name. This is what appears in the clean file. |
| `aliases` | Source header names to accept for this field. Matching is case- and punctuation-insensitive, so `"Email Address"`, `"email address"`, and `"EMAIL_ADDRESS"` all resolve. |
| `source` | Pin the field to one exact source column, bypassing alias matching. |
| `sources` | Combine several source columns, e.g. `["First Name", "Last Name"]`. Use with `separator`. |
| `transform` | One of the transforms below, applied after the value is selected. |
| `separator` | Joiner used with `sources`. Defaults to a single space. |
| `required` | Marks the field required. Reportable via a `required` rule. |
| `unique` | Marks the field as needing distinct values, for reporting. |
| `default` | Value to use when the source cell is empty. |
| `type` | `string` or `number`. Numbers are parsed and normalised. |

### Available transforms

`ascii`, `date_iso`, `digits_only`, `email_lowercase`, `expand_scientific_notation`,
`lower_case`, `phone_e164`, `split_full_name_first`, `split_full_name_last`,
`title_case`, `trim`, `upper_case`

`phone_e164` needs a country context to interpret national-format numbers;
numbers that already start with `+` are parsed as-is.

### `normalization`

An optional block that canonicalises addresses and converts currencies after
the pipeline has run. It is bound in unattended runs (CLI and batch): the
normalised data is written as `normalized_data.csv` beside `clean_data.csv`,
and every conversion is written to `currency_conversions.csv` with the rate and
the date it applied. The pipeline's own `clean_data.csv` is never rewritten, so
a config without this block is byte-identical to before.

```yaml
normalization:
  addresses:
    - column: address          # one entry per address column
  currency:
    target: USD
    columns: [amount, fee]     # or a single `column:`
    source_currency: EUR       # optional: for bare numbers with no symbol
    rates:
      - {base: EUR, quote: USD, rate: 1.08, as_of: 2026-01-15}
      - {base: GBP, quote: USD, rate: 1.27, as_of: 2026-01-15}
    rate_file: rates.yaml      # optional; resolved relative to the config
```

| Key | Meaning |
| --- | --- |
| `addresses` | A list of `column` entries (or plain names) to canonicalise. |
| `currency.target` | The currency to convert amounts into. |
| `currency.column` / `columns` | The amount column(s) to convert. |
| `currency.source_currency` | Currency to assume for values with no symbol or code. Without it, such a value is reported as unconverted rather than guessed. |
| `currency.rates` / `rate_file` | Rates, inline or in a YAML file beside the config. A file's top-level `rates:` key (or a bare list) is accepted. |
| `enabled` | Set `false` to keep the block but turn it off. |

An unrecognised address is left alone, not rewritten. A rate with no matching
entry leaves its amount unconverted and counted, so a missing rate is visible
rather than silently zeroing the value. A rate must be positive.

## Adding a new CRM

1. Look at your source file's header row and decide the target column names.
2. Copy an existing config as a starting point:

   ```bash
   cp app_files/configs/hubspot.yaml app_files/configs/my_crm.yaml
   ```

3. Edit `crm:`, then one `fields:` entry per target column, listing every
   header spelling you have seen in `aliases`.
4. Confirm it loads:

   ```bash
   python -c "from app_files.mappers import available_crms; print(available_crms())"
   ```

5. Run it against a real export through the web UI, or from Python:

   ```python
   import pandas as pd
   from app_files.pipeline import run_pipeline

   source = pd.read_csv("my_export.csv", dtype=str, keep_default_na=False)
   result = run_pipeline(source, crm="my_crm")
   print(result.summary())
   ```

## Adding a new bank format

Bank configs are ordinary configs. `bank_reconciliation.yaml` maps whatever the
statement calls its columns onto `date` / `description` / `amount`:

```yaml
fields:
  - name: date
    required: true
    transform: date_iso
    aliases: ["Date", "Transaction Date", "Posting Date", "Value Date"]
  - name: description
    aliases: ["Description", "Details", "Narrative", "Memo", "Particulars"]
  - name: amount
    type: number
    required: true
    aliases: ["Amount", "Value", "Transaction Amount"]
```

To support another bank, add its header spellings to the `aliases` lists. If the
statement uses an unusual date layout, `date_iso` handles the common
ISO / `DD-MMM-YY` / `MM/DD/YYYY` forms; a format it cannot infer is reported as
an issue rather than guessed at, so check the issues CSV after the first run.

## Input file formats

The ingestion layer picks an adapter from the file extension:

| Extension | Adapter | Notes |
| --- | --- | --- |
| `.csv`, `.txt`, `.tsv` | `csv_adapter` | Encoding auto-detected; delimiter follows the extension (`.tsv` is tab-separated). |
| `.xlsx`, `.xlsm`, `.xls` | `excel_adapter` | Reads the first sheet. `.xlsx`/`.xlsm` use `openpyxl`; legacy `.xls` uses `xlrd`. |
| `.json` | `json_adapter` | Nested objects are flattened to dotted columns (`address.city`). |
| `.pdf` | `pdf_adapter` | Extracts the transaction table; multi-page aware. Needs `pdfplumber`. |

From Python, `read_any` handles a path or raw bytes:

```python
from app_files.ingestion import read_any

frame = read_any("statement.pdf")
frame = read_any(uploaded_bytes, filename="statement.pdf")
```

Bytes need a `filename=` because the extension is what selects the adapter.

## Output formats

Set `output_format` to `csv`, `excel`, `json`, or `sql`. The SQL writer emits
portable `CREATE TABLE` + `INSERT` statements that load into SQLite, MySQL,
PostgreSQL, or SQL Server unchanged.

The SQL writer deliberately keeps a column as `TEXT` when its values only look
numeric but carry meaning in their formatting — `+14155552671` (a phone number)
and `01234` (an account or zip code). Without that, SQL numeric affinity would
silently store `14155552671` and `1234`.