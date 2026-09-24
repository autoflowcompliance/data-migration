# AutoFlow Data Migration Tool

AutoFlow takes a messy export from almost any system and turns it into clean,
import-ready data. It cleans values, maps columns onto a target system's schema,
checks every record against built-in and buyer-defined rules, scores data quality
across five dimensions, and records what changed in every cell so the result can
be audited.

Input can be CSV, Excel, PDF or JSON. Output can be CSV, Excel, JSON or SQL. It
runs from a web UI or the command line, and installs with Docker or pip.

## Quickstart

Three commands, from the repository root:

```bash
pip install -r requirements.txt
python -m pytest -q
python main.py
```

Then open <http://localhost:8080>, upload a file, pick a target config and an
output format, and download the results. See [docs/INSTALL.md](docs/INSTALL.md)
for Docker and Render, and [docs/CONFIGURATION.md](docs/CONFIGURATION.md) to add
your own target format.

One interface ships: **DataFlow**, the NiceGUI web app, served by
`python main.py`. It reads the frozen core, the target configs and the licence
file, and the same command serves the hosted demo and the packaged desktop
build.

## What it does

### Ingestion — read the file you already have

The ingestion layer detects the file type from its extension and picks the right
reader, so no format logic leaks into the rest of the pipeline.

| Format | Extensions | Notes |
| --- | --- | --- |
| CSV | `.csv`, `.tsv`, `.txt` | Encoding detected automatically; separator follows the extension |
| Excel | `.xlsx`, `.xlsm`, `.xls` | Openpyxl for `.xlsx`/`.xlsm`, xlrd for legacy `.xls` |
| PDF | `.pdf` | Bank statement tables, multi-page, standard US and UK layouts |
| JSON | `.json` | Nested objects flattened to dotted column names |

Every reader returns a plain DataFrame, so the same cleaning and mapping code
works regardless of where the data came from.

### Cleaning and mapping — normalise values, match columns

Cleaning standardises values that mean the same thing but are written
differently: phone numbers to E.164, emails to lower case, dates to ISO 8601,
names split into first and last, and so on.

Mapping then lines the source columns up with a target system's schema. Columns
are matched by alias, with fuzzy matching for headers that do not match exactly.

Five target configs ship today, and each one is a YAML file rather than code:

`bank_reconciliation`, `hubspot`, `pipedrive`, `quickbooks`, `salesforce`

### Rule engine — buyer-defined validation, in YAML

Rules declare what a valid value looks like, without touching code. They live in
a `rules:` list in any config file and run against the mapped frame, so they see
canonical column names.

```yaml
rules:
  - name: amount_positive
    field: amount
    type: range
    min: 0
    severity: error

  - name: status_valid
    field: lifecyclestage
    type: list_of_values
    values: [lead, customer, other]
    severity: warning
```

Five rule types: `range`, `length`, `list_of_values`, `regex`, `required`. Each
carries a severity of `error`, `warning` or `info`. Failures join the same issues
list the built-in validators write to, so they appear in the issues CSV and the
QA report with nothing extra to wire up. Full reference in
[docs/RULES.md](docs/RULES.md).

A second block, `cross_field:`, holds rules that read more than one column:
`close_date` must not precede `open_date`, `total` must equal
`subtotal + tax`. They produce the same `Issue` objects as the single-field
rules, so they flow into the same report.

```yaml
cross_field:
  - name: close_after_open
    type: date_order
    fields: [open_date, close_date]

  - name: total_matches_parts
    type: sum_equals
    fields: [total, subtotal, tax]
    tolerance: 0.01
```

Three cross-field types: `date_order`, `sum_equals`, `compare` (with an
operator of `<`, `<=`, `==`, `!=`, `>` or `>=`). A rule whose columns are
missing from the frame is reported as skipped rather than dropped; a row with a
blank in any referenced column is skipped, because empty is the completeness
check's job.

Rule sets are versioned under `AUTOFLOW_HOME/rules`. A new version starts as a
draft, runs in a sandbox against sample frames, and only then can be promoted to
production. Rolling back restores an earlier version as a *new* version, so the
history survives the reversal.

```python
from app_files.rules import SandboxStore

store = SandboxStore()
version = store.save_version("crm_rules", cross_field=rules, note="stricter close date")
store.sandbox_run("crm_rules", version.version, [recent_frame])
store.promote("crm_rules", version.version)   # refuses without a sandbox run
```

### Privacy — find and mask personal data

A separate layer finds personally identifiable information and replaces it
before the data reaches a destination. It reads the frame the pipeline
produced and never modifies the cleaning, mapping or reporting code.

Detected kinds: emails, phone numbers, credit cards, IBANs, national ID
numbers, passports and your own named patterns. Structured identifiers are
validated rather than pattern-matched alone — a card must pass Luhn, an IBAN
must pass mod-97 — so an order number is not mistaken for a card.

Four masking strategies, chosen per column: `redact`, `hash` (deterministic, so
masked tables still join), `tokenize` (reversible from an encrypted vault), and
`partial` (last four kept). Only the matched span is rewritten, so a phone
number inside a note is masked while the note survives.

The layer is off unless a config turns it on. See
[docs/PRIVACY.md](docs/PRIVACY.md).

### Profiling — five quality scores

Every run scores the data 0 to 100 on five dimensions:

| Dimension | Measures |
| --- | --- |
| Completeness | Share of cells that are not empty |
| Uniqueness | Share of rows that are not duplicates |
| Validity | Share of emails and phones that match their format |
| Consistency | Share of values already in the expected casing and date format |
| Timeliness | How recent the dates are against a rolling 24-month window |

Timeliness scores each date by freshness, so old dates lose points in proportion
to their age and future dates are penalised as likely typos. Pass an explicit
`timeliness_window` to score against a fixed date range instead.

The five scores render as a scorecard in the HTML QA report and in the web UI.

### Lineage — prove what changed

Every transformation is recorded as one row: source row index, output row index,
field, before value, after value, and the action taken. Duplicate merges and
drops are recorded too, so any output row can be traced back to the source rows
it came from.

Lineage is off by default and costs nothing when it is off. Turn it on to get
`lineage_report.csv` alongside the clean data. This is the feature that answers
"we think the data is clean" with "here is the proof".

### Output — four formats

| Format | Use |
| --- | --- |
| CSV | Universal import |
| Excel | Business-user friendly, `.xlsx` |
| JSON | API-ready |
| SQL | `CREATE TABLE` and `INSERT` statements for direct load |

All four carry identical data. SQL column types are inferred from content, so a
column of phone numbers or postcodes becomes `TEXT` rather than being handed to
SQL's numeric affinity and silently rewritten.

## Web UI

DataFlow is the shipped interface: **Upload → Verify → Results**, plus
Templates, Batch, Branding and Settings. Upload a file, pick a target config,
run the migration, then download the clean data, the QA report and the mapping
log — and, when lineage tracking is on, the row-level lineage log. Unlicensed
installs run under the demo limits (a few runs per session, with a watermarked
QA report), and the page says so rather than failing silently.

Routes live in `app_files/interface/web/routes/`, one module per page, and each
is registered by importing the package. Widgets come from
`app_files/interface/web/components.py` and the palette from `theme.py`, so a
visual change happens in one place. The decision logic sits in
`app_files/interface/web/state.py`, which is where the tests point.

## Command line

For scripting and batch runs:

```bash
python -m app_files.cli -i app_files/samples/messy_contacts.csv -c hubspot -o output
```

```
7 rows in, 6 out, quality score 66.7%, 1 errors, 1 warnings
Wrote deliverables to output
```

## Docker

```bash
docker compose up --build
```

The app is at <http://localhost:8080>. `configs/`, `samples/` and `output/` are
mounted from the host, so dropping a new YAML into `app_files/configs/` appears
in the config selector without a rebuild. The image includes a healthcheck.

### Render

The repo ships a `render.yaml` Blueprint. Push to GitHub/GitLab, then in the
Render Dashboard choose **New + → Blueprint** and pick the repo. Render builds
the `Dockerfile` and starts the app on the port it injects via `PORT`. See
[docs/INSTALL.md](docs/INSTALL.md#render) for the details that matter.

## Demo data

`app_files/samples/` holds deliberately messy files with known problems:

| File | Contains |
| --- | --- |
| `messy_contacts.csv` | Mixed date formats, inconsistent casing, a duplicate row, a blank email, one malformed phone |
| `messy_contacts.json` | The same records as nested JSON |
| `employee_records.csv` | Ten records for profiling |
| `bank_statement.csv` | A statement with one deposit missing from the ledger |
| `bank_statement.pdf` | The same statement as a PDF, for testing the PDF reader |
| `ledger.csv` | The matching ledger, with one uncleared cheque |

Running `messy_contacts.csv` through the `hubspot` config produces this
scorecard, which shows the tool finding real problems rather than reporting
success:

```
rows in 7, rows out 6 (1 duplicate removed)
quality score 66.7%   errors 1   warnings 1

completeness 71.1   uniqueness 100.0   validity 90.9
consistency  91.4   timeliness  88.8   overall 86.2
```

## Bank reconciliation

A separate page reconciles a bank statement against a ledger and reports three
groups: transactions missing from your books, transactions recorded but never
cleared, and matched pairs. It reads CSV or PDF statements. Matching is on exact
amount and date within a configurable tolerance, because bank clearing dates
usually differ slightly from ledger entry dates.

This is prep work for a bookkeeper, not finished bookkeeping. The tool finds and
cleans discrepancies. It does not categorise transactions or make accounting
judgments.

For three or more feeds — statement, ledger, and a payment processor, say —
`reconcile_multiway` matches them all at once. The first source is the anchor,
and a group counts as matched only when every source contributes a row; a row
that matched two feeds out of three is reported as a partial group and stays in
the unmatched list. The two-file case runs through the same engine and produces
the same counts as the original matcher.

Match logic is data, not code. A strategy lists weighted components —
`amount`, `date`, `reference` or `text` — and a pair matches when the passing
weight reaches a threshold. The default requires both an amount and a date, which
is the original behaviour; a reference strategy can match on the reference alone,
and a weighted strategy can let a strong amount agreement excuse a differing
reference.

```python
from app_files.services.bank_reconciliation import (
    MatchStrategy, ReconciliationHistory, reconcile_multiway,
)

strategy = MatchStrategy.from_dict({
    "name": "amount_date_reference",
    "components": [
        {"type": "amount", "column": "Amount", "weight": 2.0},
        {"type": "date", "column": "Date", "weight": 1.0, "date_window_days": 2},
        {"type": "reference", "column": "Reference", "weight": 1.0},
    ],
    "threshold": 2.5,
})
result = reconcile_multiway(
    {"bank": bank, "ledger": ledger, "processor": processor}, strategy
)
print(result.summary())
print(result.render())

store = ReconciliationHistory()          # under AUTOFLOW_HOME
store.record("acme", result)
print(store.render_trend("acme"))        # month over month
```

## Documentation

| Document | Covers |
| --- | --- |
| [docs/INSTALL.md](docs/INSTALL.md) | Install with pip or Docker, verify the install |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Add a new CRM or bank format |
| [docs/RULES.md](docs/RULES.md) | Every rule type with a worked YAML example |
| [docs/PRIVACY.md](docs/PRIVACY.md) | Detect and mask personal data |

## Tests

```bash
python -m pytest -q
```

Expect `1097 passed`. The suite covers value transforms, each ingestion adapter,
each rule type, each profiling dimension, the lineage tracker, all four output
writers, PII detection and masking, cross-field rules and rule versioning,
multi-way reconciliation, migration safety, config-schema validation, golden-file
regression fixtures, and malformed-input error handling. It runs in about
twenty-eight seconds, so there is no reason not to run it before a commit.

Frozen core: `app_files/cleaners/`, `mappers/`, `validators/`, `auditors/` and
`reporters/` are treated as stable. New capability goes in sibling packages that
call into the core. If a core test fails, the change that broke it is guilty
until proven innocent — revert it rather than editing the expected output.

## Licence

Commercial software. A one-time fee grants a perpetual, non-exclusive,
non-transferable licence for internal business use. Resale, redistribution and
sharing the source are not permitted. Thirty days support, no warranty. See
[LICENSE.md](LICENSE.md).