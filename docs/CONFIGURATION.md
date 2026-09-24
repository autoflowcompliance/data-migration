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

### `dedupe`

An optional block that folds near-duplicate rows out of a copy of the pipeline
output using fuzzy matching, for the cases where the cleaner's exact-match
dedupe is too strict (`"John Smith"` and `"Jon Smith"` are the same person).
Bound in unattended runs: the filtered data is written as `deduped_data.csv`
and every merge to `duplicates_removed.csv` with the score that drove it.
`clean_data.csv` is never rewritten.

```yaml
dedupe:
  rules:
    - columns: [first_name, last_name]   # every compared column
      threshold: 0.85                    # 0 < threshold <= 1, default 0.9
      metric: jaro_winkler               # or levenshtein
      require_all: true                  # false: one matching column is enough
      max_cluster_size: 50               # optional safety cap
```

| Key | Meaning |
| --- | --- |
| `rule` / `rules` | One rule, or a list of rules applied in order. |
| `columns` | The columns to compare. |
| `threshold` | How close two rows must be to count as one. |
| `metric` | `jaro_winkler` (default) or `levenshtein`. |
| `require_all` | `true`: every column must match. `false`: one is enough. |
| `max_cluster_size` | Stop with an error rather than fold more than this many rows into one survivor. |
| `enabled` | Set `false` to keep the block but turn it off. |

Jaro-Winkler rates any two values sharing a long prefix as similar, so a column
of serial-number-shaped values can legitimately collapse; the merges are
recorded, and `max_cluster_size` is the backstop.

### `notifications`

An optional block that turns a run into something the outside world hears about.
It binds Layer 8's completion webhook and Layer 15's alerting, both of which
were complete and unreachable from a run until this block existed. Nothing fires
unless the run is asked to notify (`--notify` on the CLI single-file and `batch`
commands), so a run that never passes the flag reaches no network and its output
is byte-identical to before.

```yaml
notifications:
  alerts:                       # omit entirely for a critical alert on failure
    - condition: quality_drop   # failure | quality_drop | sla_breach | duration_breach
      threshold: 80             # the floor (drop) or ceiling (breach)
      severity: warning         # info | warning | critical
  channels:                     # where alerts go
    - type: slack               # webhook | slack | teams
      url_env: SLACK_WEBHOOK    # read from the environment, not the YAML
  webhooks:                     # run.completed / run.failed payloads
    - url_env: DATAFLOW_HOOK
      events: [run.completed, run.failed]
      secret_env: DATAFLOW_HOOK_SECRET   # HMAC-signs the body when set
```

| Key | Meaning |
| --- | --- |
| `alerts` | Alert rules. Omitting the key gives a critical alert on any failure; `alerts: []` turns alerts off. |
| `alerts[].condition` | `failure`, `quality_drop`, `sla_breach`, or `duration_breach`. |
| `alerts[].threshold` | The floor for `quality_drop`, the ceiling for a breach. |
| `alerts[].severity` | `info`, `warning`, or `critical`. |
| `channels` | Alert channels: `webhook`, `slack`, or `teams`. |
| `webhooks` | Completion webhooks. `events` filters which of `run.completed` / `run.failed` fire. |
| `url` / `url_env` | A channel or webhook URL, inline or from an environment variable. |
| `secret_env` | Environment variable holding an HMAC key; the payload is signed when set. |

Endpoints and their signing keys are named through `url_env` / `secret_env`
rather than committed to the YAML. A URL with no `url` and no `url_env`, or a
named environment variable that is not set, fails the run loudly rather than
silently notifying nobody. Delivery itself is best-effort: a dead endpoint is
reported in the run's output but never fails a run that produced correct data.
The alerting evaluation is also reachable directly from Python —
`notify_run(config, summary, run_id=…)` returns `None` when the config declares
no block, so a caller can tell "unconfigured" from "configured and clean".

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

## Matching (bank reconciliation)

A config can declare how a statement line is matched to a ledger line. This is
the same match logic the reconciler has always used, written as data so it can
be tuned without editing Python. Omit the block and the frozen amount-and-date
default runs unchanged.

```yaml
matching:
  name: amount_and_date
  components:
    - type: amount
      column: Amount
      weight: 1.0
    - type: date
      column: Date
      weight: 1.0
      date_window_days: 2
  threshold: 2.0
```

Each component is weighted and scored; a pair matches when the passing weight
reaches `threshold`. Component types are `amount`, `date`, `reference`, and
`text`. A reference-only strategy can match on the reference alone, and a
weighted strategy can let a strong amount agreement excuse a differing
reference:

```yaml
matching:
  name: reference_only
  components:
    - type: reference
      column: Reference
      weight: 1.0
  threshold: 1.0
```

Run it from the command line, pointing `-c` at the config that holds the block:

```bash
python -m app_files.cli reconcile \
  --statement statement.csv --ledger ledger.csv -c bank_reconciliation -o out
```

With no `matching:` block the config resolves to the frozen default, so a
config that never asked for a strategy behaves exactly as before.