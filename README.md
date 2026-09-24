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

## Also included

These ship and are tested, and are reachable from the code rather than from a
dedicated page.

### Connectors — pull from where the file already lives

`app_files/distribution/connectors.py` fetches a file from five providers behind
one interface: `s3`, `google_sheets`, `google_drive`, `dropbox`, `onedrive`.

```python
from app_files.distribution.connectors import pull
file = pull("s3", bucket="my-bucket", key="contacts.csv")   # ConnectorFile(name, data)
```

S3 is exercised end to end against `moto`, a real S3 protocol implementation.
The other four speak their real REST APIs over an injectable HTTP transport, so
request construction is tested; only the provider's own server is untested.
Credentials come from the environment and none are stored in the repository.
`credential_report()` names exactly which variables are missing, so the UI can
tell the user what to set instead of failing with a stack trace.

### Client workspaces

`app_files/collaboration/workspaces.py` gives each client a folder —
`config.yaml`, `samples/`, `output/`, and an append-only `runs.jsonl` audit
trail. Every path is rooted inside the workspace and `resolve_path` refuses to
escape it, so one client's data cannot read another's. `run_in_workspace()`
runs the full pipeline and writes the clean file, QA report, issues and lineage
log into the client's folder. Relocate the tree with `AUTOFLOW_HOME`.

### Quality trends and suggestions

`app_files/intelligence/` records a per-column baseline of each run and flags
when a new run stops looking like the last one, and ranks what to fix next from
the frame's own profile.

### Batch

`python -m app_files.cli batch` processes a whole folder, writing per-file
output, a `summary.csv` and a `dashboard.html`.

## Not included

So a buyer is not surprised: the following are **not** built today, and the code
does not claim them. SFTP or direct database reads; watch folders, a scheduler,
event triggers, dependency chains or incremental/watermark processing; a visual
mapping or rule editor beyond the YAML builder; schema-drift detection;
cross-field rules or rule versioning; an interactive lineage graph, blast-radius
analysis or OpenLineage export; N-way (3+ file) reconciliation or reconciliation
history; signed deliverables; multi-brand profiles, custom domains or a client
portal; RBAC, an immutable audit log, encryption or compliance posture; a job
queue, distributed workers or resource limits; Prometheus metrics; tenant
isolation, cloud orchestration or backup/DR; a plugin system, a public Python
SDK or an admin console; dry-run mode, rollback files or a cutover runbook
generator.

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

`batch` processes a whole folder in one pass and writes a per-file folder, a
`summary.csv` and a `dashboard.html`:

```bash
python -m app_files.cli batch --in app_files/samples --template hubspot \
    --out output/batch --format csv
```

One bad file does not sink the batch: it is reported as `fail` on its line and
the rest continue.

### Exit codes and errors

A bad input is a message on stderr, not a stack trace. The CLI never prints a
traceback for a problem the caller can fix.

| Code | Meaning |
| --- | --- |
| `0` | Ran, no validation errors |
| `1` | Ran, but validation found errors (see `issues.csv`) |
| `2` | Could not run: unreadable/empty input, malformed or incomplete config, unknown target config |

```bash
$ python -m app_files.cli -i missing.csv -c hubspot -o output
error: Could not read missing.csv: [Errno 2] No such file or directory: 'missing.csv'
```

Unparseable dates and amounts are not errors: they are reported as *unmatched*
or as issues so a human can look, and the run completes.

## REST API

For programmatic access, run the API directly. It is a Starlette app, separate
from the web UI:

```bash
python -m app_files.distribution.api --host 127.0.0.1 --port 8600
```

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness plus the available target configs |
| `POST` | `/validate` | Validate an uploaded file against a config |
| `POST` | `/clean` | Clean and map an uploaded file, return the frame |
| `POST` | `/profile` | Return the five-dimension quality profile |
| `POST` | `/reconcile` | Reconcile a bank statement against a ledger |

The POST endpoints take a multipart upload plus form fields.

- `/validate`, `/clean`, `/profile`: a `file` upload and a `config`.
- `/reconcile`: a `statement` upload and a `ledger` upload, plus
  `bank_date_col`, `bank_amount_col`, `ledger_date_col`, `ledger_amount_col`
  (defaulting to `Date`/`Amount`) and an optional `tolerance` in days.

Format errors return a `400` with a short message; unexpected failures return a
`500` rather than leaking a traceback.

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

## Documentation

| Document | Covers |
| --- | --- |
| [docs/INSTALL.md](docs/INSTALL.md) | Install with pip or Docker, verify the install |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Add a new CRM or bank format |
| [docs/RULES.md](docs/RULES.md) | Every rule type with a worked YAML example |

## Tests

```bash
python -m pytest -q
```

Expect the whole suite to pass: over 600 tests in under twenty seconds. It
covers value transforms, each ingestion adapter, each rule type, each profiling
dimension, the lineage tracker, all four output writers, config-schema
validation, golden-file regression fixtures, and malformed-input error handling.
There is no reason not to run it before a commit.

Frozen core: `app_files/cleaners/`, `mappers/`, `validators/`, `auditors/` and
`reporters/` are treated as stable. New capability goes in sibling packages that
call into the core. If a core test fails, the change that broke it is guilty
until proven innocent — revert it rather than editing the expected output.

## Licence

Commercial software. A one-time fee grants a perpetual, non-exclusive,
non-transferable licence for internal business use. Resale, redistribution and
sharing the source are not permitted. Thirty days support, no warranty. See
[LICENSE.md](LICENSE.md).