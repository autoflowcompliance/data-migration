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

Two more cleaners run when a config asks for them, both off by default so a
config that never declared them is unaffected. Fuzzy dedupe merges rows that are
near-duplicates rather than exact ones — `John Smith` and `Jon Smith` collapse at
a similarity of 0.85 and stay apart at 0.95. Address and currency normalization
canonicalise postal addresses and convert amounts to a chosen base currency,
recording the rate and date used for every conversion so the original is still
auditable. Both are configured in the same config file; see
[docs/CONFIGURATION.md](docs/CONFIGURATION.md).

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

The scorecard answers "how good is this file". It cannot answer "is this source
getting better or worse", because nothing remembered yesterday's score — the
trend store and baseline comparison existed in the profiling package but no run
called them. Two flags bind them in:

```bash
# Record this run in the source's history and report the trend
python -m app_files.cli -i inbox/contacts.csv -c hubspot -o out --record-quality

# Pin this run as the source's baseline (records it too)
python -m app_files.cli -i inbox/contacts.csv -c hubspot -o out --baseline

# Exit non-zero when a dimension falls past the pinned baseline
python -m app_files.cli -i inbox/contacts.csv -c hubspot -o out \
    --record-quality --fail-on-regression
```

History is one row per run per source in SQLite under `AUTOFLOW_HOME`, so a
source is remembered by filename (`contacts`) rather than by path and a copy in
another folder continues the same history. `--fail-on-regression` is how a
scheduled run refuses to deliver a file that has rotted since the last accepted
one.

Once a source has five recorded runs, the same history learns a normal range
per dimension and reports a run that falls outside it — an anomaly surfaces
without anyone writing a rule for it. The learning window is the most recent 30
runs, and the range is mean ± three standard deviations (with a floor on the
spread, so a perfectly stable source does not flag a one-point wobble):

```
Quality history: 6 run(s) for contacts, trend declining
  anomaly: 1 ANOMALY(IES) outside the learned range for completeness
```

Read the history back without opening the database:

```bash
# List every source that has recorded runs
python -m app_files.cli quality

# One source, with the trend dashboard written as HTML
python -m app_files.cli quality contacts.csv -o reports
```

`-o` writes `<source>_quality_trend.html` — the same table that shows the
direction (`improving`, `stable`, `declining`) and every recorded score.

### Profiling — column detail

The five scores answer "how good is this file". A second, opt-in report answers
"what is in it": per-column statistics, the shape of each column, and the values
that do not fit it. Declare a `profiling:` block in the config to turn it on.

```yaml
profiling:
  statistics:
    enabled: true
    top_values: 5
  patterns:
    enabled: true
  outliers:
    enabled: true
    method: iqr          # iqr | zscore | isolation_forest
    k: 1.5
```

```bash
python -m app_files.cli profile columns inbox/contacts.csv --config hubspot.yaml
```

Statistics are count, distinct, missing, and — for a numeric column — min, max,
mean, median, quartiles and IQR. Patterns infer a regex plus a label a human
recognises (`email`, `date`, `uuid`, `currency`), and report coverage: the share
of values the pattern actually matches, so a column of mixed content says so
rather than over-claiming.

Outliers come from one of three methods. IQR uses Tukey fences; z-score uses a
standard-deviation cut; the isolation forest needs no threshold at all and is
implemented over numpy rather than scikit-learn, so it adds no dependency to
`requirements.txt`. The isolation forest flags a fixed *share* of the column —
`contamination`, 1% by default — because that is how its threshold is defined.
A caller who wants the tail rather than the rare should use `iqr` or `zscore`.

Everything here is off by default and additive: a config with no `profiling:`
block produces no report and byte-identical output to a run made before the
block existed. The same sections are reachable as `POST /profile/columns` and
`SDK.profile_columns()`, and a custom profiler registers through the existing
plugin registry:

```python
from app_files.plugins.registry import load_plugin

load_plugin(lambda registry: registry.profiler("my_profiler", my_function))
```

### Quality SLA and the action a regression takes

The scorecard says how good a file is; the history says whether it is getting
worse. Neither *acts*. A `quality:` block in the config makes the score a gate:
a floor per dimension that a run must meet, and a decision for what a
regression against the baseline should do.

```yaml
quality:
  sla:
    completeness: 0.98      # a fraction, or a whole percentage (98)
    validity: 0.95
  regression:
    threshold: 5            # percentage points of drop before it counts
    action: alert           # alert | block | quarantine
```

`alert` reports and lets the run through; `block` stops it before output is
written; `quarantine` stops it and marks the output as held for review. `alert`
is the default because it is the only one that cannot lose data. A dimension
the file has nothing to evaluate — timeliness on a file with no dates — is
skipped rather than failed, so a file is never punished for its shape.

Check a file from the shell:

```bash
python -m app_files.cli quality check inbox/contacts.csv --config hubspot.yaml
```

The exit code is the point: `0` met the SLA and did not regress, `1` breached
it or regressed under `block`/`quarantine`, `2` the config could not be read.
A cron job can therefore tell "the data is bad" from "the config is wrong".
`action` softens a *regression*, not the SLA — a declared floor is a hard gate,
so a file under its floor exits `1` even under `alert`. `--baseline` pins this
run as the source's baseline; `--record` adds it to the history. Neither is
implied — the check itself is read-only, so a gate never moves the baseline it
is measuring against. A source with no baseline cannot regress, so a first run
is never blocked for want of history.

Over the API, the same check takes the floors as form fields:

```bash
curl -F file=@contacts.csv -F sla_completeness=0.98 -F regression_action=block \
    http://localhost:8080/quality
```

or from the Python SDK:

```python
client.quality(csv_bytes, sla={"completeness": 0.98}, action="block")
```

A config with no `quality:` block changes nothing: no SLA, no extra file, no
different exit code.

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
7 rows in, 6 out, quality score 66.7%, 1 errors, 2 warnings
Rules: 2 of 2 run, 1 failure(s)
Wrote deliverables to output
```

The `Rules:` line is the config's own `rules:` block being applied — the same
rules the web UI runs. They reach `issues.csv` and the QA report, and are
advisory by default; add `--strict-rules` to fail the run when a declared rule
fails. See [docs/RULES.md](docs/RULES.md#rules-in-an-unattended-run).

### Watch a folder

To process a file the moment it lands, rather than when someone asks:

```bash
python -m app_files.cli watch --in inbox --template hubspot --out out --settle 2
```

`--once` polls once and exits, so a cron job gets the same behaviour as the
long-running loop. A file is only read once its size and mtime have held steady
for `--settle` seconds — an export that arrives in several writes must not be
read at the first write, because a truncated file passes enough checks to
produce a plausible, wrong result. Both the settle observation and the
already-handled record are written to `$AUTOFLOW_HOME/watch_state.json`, which
is what makes `--once` work across processes: the first cron run observes, the
next one processes. In-progress names (`.part`, `.tmp`, `.crdownload`, `~$…`)
are ignored.

Output is byte-identical to a batch run: the watcher is a trigger for the
existing batch engine, not a second pipeline.

### Reconcile a statement from the shell

Reconciliation was reachable from the web page and from Python; a scheduled run
now reaches it too:

```bash
python -m app_files.cli reconcile \
  --statement statement.csv --ledger ledger.csv -c bank_reconciliation -o out
```

`-c` names the config that holds the `matching:` block, so the match logic is
data. Three files come out: `missing_from_books.csv`, `recorded_but_never_cleared.csv`
and `matched.csv`. See
[docs/CONFIGURATION.md](docs/CONFIGURATION.md#matching-bank-reconciliation).

### Rehearse a migration before committing

`migrate` runs the whole safety sequence on one command: profile the source,
take a rollback copy, dry-run the pipeline, and generate a cutover runbook from
the real config. Nothing is migrated unless you pass `--commit`.

```bash
python -m app_files.cli migrate -i app_files/samples/messy_contacts.csv -c hubspot -o output
```

That writes `pre_migration.txt` (and `.json`), `rollback/`, and `runbook.txt`,
then stops — `clean_data.csv` is not written. Add `--commit` to run it. A
blocking issue (an unmapped source column, or quality below the migration
floor) exits non-zero in rehearsal, so a script cannot blithely migrate a
source that was never checked. `--schedule "0 2 * * *"` names a recurring job
in the runbook.

The rehearsal reports every block the config declares — `rules:`, `privacy:`,
`normalization:`, `dedupe:` — under "Config-declared steps the committed run
also applies", because those blocks run on top of the pipeline rather than
inside it. `--commit` applies them and writes their deliverables
(`masked_data.csv`, `deduped_data.csv`, `normalized_data.csv`, `issues.csv`),
so a migration from a config that declares masking never writes raw PII. A
rehearsal applies the rules to report what they would catch but does not
persist the accepted ruleset, so it stays a rehearsal.

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

## Observability

The API exposes Prometheus metrics at `GET /metrics`, a readiness probe at
`GET /ready` and a liveness probe at `GET /live`. Readiness runs the dependency
checks and returns 503 when a required one fails, so a platform stops routing
without killing the process. Liveness is deliberately dependency-free: a
liveness probe that fails when a database is down causes a restart loop that
cannot help.

Runs are recorded through `record_run`, which keeps the metric names in one
place. A dashboard written against them should not have to change when the
pipeline changes underneath.

```python
from app_files.observability import AlertRule, WebhookChannel, notify_alert, record_run

record_run("crm", "ok", duration_seconds=3.2, quality_score=93.0, rows=1200)

notify_alert(
    {"status": "ok", "source": "crm", "quality_score": 61.0, "duration_seconds": 95.0},
    channels=[WebhookChannel("https://hooks.example.com/dataflow")],
    rules=[
        AlertRule("quality_drop", threshold=80.0),
        AlertRule("sla_breach", threshold=60.0),
    ],
)
```

Alert channels are Slack, Microsoft Teams, email and a generic signed webhook.
A channel that fails does not raise: a missed alert is bad, but a failed run
because an alert could not be sent is worse. Alerts fire on failure, a quality
score below its floor, and a run over its duration or SLA budget.

### Alerts and webhooks attached to a run

A config can declare a `notifications:` block, and `--notify` makes a run honour
it. Layer 15's alerts and Layer 8's completion webhook both existed and had no
caller from a run until this binding, so nothing was ever told a run finished or
failed outside a Python caller. The `batch` command takes the same flag and
notifies once per file, which is the unattended case that matters most:

```bash
python -m app_files.cli -i export.csv -c hubspot -o output --notify
python -m app_files.cli batch --in inbox --template hubspot --out output --notify
```

```yaml
notifications:
  alerts:
    - condition: quality_drop
      threshold: 80
      severity: warning
  channels:
    - type: slack
      url_env: SLACK_WEBHOOK
  webhooks:
    - url_env: DATAFLOW_HOOK
      secret_env: DATAFLOW_HOOK_SECRET
```

Endpoints and signing keys come from the environment through `url_env` /
`secret_env`, so a URL is never committed. With no `--notify` flag the run
reaches no network at all. A malformed block stops the run; a dead endpoint is
reported and does not. See
[docs/CONFIGURATION.md](docs/CONFIGURATION.md#notifications).

## Security and governance

Five roles, most to least privileged: `owner`, `admin`, `operator`, `viewer`,
`client`. `require(principal, permission)` raises `AccessDenied` rather than
returning false, because a silent no is how a viewer ends up thinking an admin
action worked. Managing users is owner-only; an admin runs the system but does
not hand out access to it. A client principal carries the workspace it may read,
and a read outside that scope is refused even though the role allows reading —
a role is what you may do, the scope is what you may do it to.

The audit log is append-only in the sense that the code only appends. That is a
promise, not a proof. `AuditChain` makes it tamper-evident: each entry hashes the
entry before it, so editing any record changes every hash after it and
verification fails at the first edit. The chain is written beside the existing
log, so the log format and every reader of it are untouched.

Data at rest is encrypted with AES-256-GCM, which authenticates as well as
encrypts: a tampered ciphertext fails to open rather than returning garbage.
Keys come from a `SecretStore` — a `chmod 600` file or an injected mapping,
never a bare environment variable, which leaks into process listings and crash
dumps. The store refuses a key file other users can read.

```python
from app_files.governance import (
    AuditChain, Permission, Principal, Role, SecretStore,
    encrypt_text, require,
)

principal = Principal("sam", Role.OPERATOR)
require(principal, Permission.RUN_PIPELINE)

chain = AuditChain()
chain.append({"actor": principal.name, "action": "run", "client": "acme"})
assert chain.verify().ok

key = SecretStore().get("default")
sealed = encrypt_text('{"client": "acme"}', key)
```

## Extending DataFlow

A plugin is a module with a `register(registry)` function. It declares a
transform, a rule type, an output format or a destination, and the pipeline
picks it up without a fork.

```python
from app_files.plugins import PluginSpec, load_plugin

def register(registry):
    registry.transform("shout", lambda value: str(value).upper())
    registry.rule_type(
        "starts_with",
        lambda value, rule: str(value).startswith(rule.options["prefix"]),
        options=("prefix",),
    )

load_plugin(register, PluginSpec(name="acme", version="1.0"))
```

Every registration is additive. A plugin cannot shadow a built-in name unless
it passes `override=True`, because a plugin that silently replaces the CSV
writer is how an install stops producing CSV for everyone and nobody notices
until someone opens the file. A refused claim is recorded on the registry, not
raised, so one bad claim does not abandon the rest of the plugin.

`app_files.plugins.events` carries the same idea to lifecycle points: subscribe
a handler to `run.completed`, `job.finished`, `plugin.loaded` and others. A
handler that raises does not fail the run — the failure comes back in the
receipt, because a correct run must not break because an observer did.

```python
from app_files.plugins import LifecycleEvent, subscribe

subscribe(LifecycleEvent.RUN_COMPLETED, lambda event, payload: audit(payload))
```

## Orchestration

A durable queue sits beside the batch engine: jobs are submitted, persisted,
claimed by a worker, and completed, and none of that needs the submitter to
stay alive. State is a JSONL log under `AUTOFLOW_HOME` — append per submission
and per state change, never rewritten in place, so a crash leaves the old state
or the new state and never a torn one.

Operators drive it with one command. `jobs submit` queues a batch folder,
`jobs list` shows the queue, and `jobs run` drains it:

```bash
python -m app_files.cli jobs submit --input-dir inbox --template hubspot --out out
python -m app_files.cli jobs submit --input-dir inbox --template hubspot --out out2 \
    --priority high --depends-on <job-id>
python -m app_files.cli jobs run --workers 3 --threads
```

A job that fails exits non-zero, so a scheduled drain surfaces the failure. The
built-in `batch` handler is registered by `jobs run`, not on import, so
importing the queue never mutates the global handler registry.

```python
from app_files.orchestration import JobQueue, JobSpec, Priority, run_workers, register_handler

register_handler("batch", lambda payload: run_batch(**payload).as_dict())
queue = JobQueue()
queue.submit(JobSpec("batch", {"input_dir": "in", "output_dir": "out"}, priority=Priority.HIGH))
reports = run_workers(queue, count=3, threads=True)
```

Three properties the tests pin:

- **No job is lost.** Two workers can never claim the same job — the select and
  the mark run under one lock. A worker that dies mid-job is recovered by
  `requeue_stale`, which is what stops a durable queue from quietly losing work.
- **Priority means something.** Lanes drain high-first, oldest-first within a
  lane, so a burst of low-priority work cannot leapfrog a high-priority job that
  has been waiting.
- **One job cannot starve the system.** A job declares a memory, CPU and runtime
  budget, and a worker refuses to start a job whose declared memory exceeds what
  is available. Memory is measured as what the job *adds*, not the interpreter's
  total footprint, so an in-process worker does not fail every small job.

## Cloud licensing and brand profiles

Two additions for a hosted, multi-client install. Both are inert until asked
for, so an existing single-brand, offline install behaves exactly as before.

```bash
python tools/cloud_license.py issue-trial buyer@acme.com --days 14
python tools/cloud_license.py activate acme@example.com --issued 2026-01-01T00:00:00 --seats 5
python tools/cloud_license.py add-seat alice
python tools/cloud_license.py usage
```

- **Seats are refused, not warned about.** Activating past the seat count raises;
  a limit that only logs is a limit that gets ignored. Releasing a seat frees it,
  and the count that matters is *active* seats, not total history.
- **Metering is per account**, so an invoice is reconstructed from what ran.
- **A trial expires on its own date**, not "issued plus N days", so a shortened
  trial is possible and a client clock change cannot extend it. `days_remaining`
  rounds up, because a 14-day trial issued a microsecond ago must say 14, not 13.

Brand profiles (`app_files.branding.profiles`) hold one brand per client:

```python
from app_files.branding import resolve_profile, save_profile

save_profile("acme", Branding(company_name="Acme Corp"))
outcome = run_migration(frame, source_name="c.csv", template="hubspot",
                        limits=limits, brand_profile="acme")
```

`resolve_profile(None)` is the install's existing single-brand settings, so the
default path is unchanged. An unknown profile name **raises** rather than falling
back — falling back would put one client's brand on another client's report.

## Compliance posture

`app_files.governance.compliance` answers the questions a buyer's legal team
actually asks, from the running code rather than from a marketing page.

```python
from app_files.governance import build_packet, write_packet

packet = build_packet(retention_days=365, tenants=registry.list())
write_packet(packet, "docs/compliance.md")   # also writes compliance.json
print(packet.ready, packet.counts)           # ready only when there are no gaps
```

- **Controls are checked against the real code.** Is the audit chain actually
  append-only? Is encryption keyed from a secret store? A check that cannot run
  is a **gap**, never an assumed pass — a compliance document that quietly
  rounds up is worse than none.
- **Retention is days and enforced by age**, so the rule is testable. An
  unreadable timestamp is kept, not deleted: the safe direction is to retain.
- **Residency is per tenant**, read from the tenant's metadata, because one
  global region would misstate where a specific tenant's data sits.
- **Exception messages never reach the packet.** Only the exception *type* is
  recorded; the message can carry a path or a value, and this document goes to
  a third party.

## Tenants, backup and deployment

A tenant is the unit of isolation for a hosted install: its own data, config,
outputs, queue and license under one root. The existing client workspaces still
apply inside a tenant; a tenant is the layer around them.

```python
from app_files.tenancy import TenantRegistry, create_backup, restore_backup

tenant = TenantRegistry().create("Acme Corp", tenant_id="acme")
backup = create_backup(tenant)              # archive + per-file digest manifest
restore_backup(backup, TenantRegistry().get("acme"))
```

- **The id is not the name.** Folder is keyed on an immutable id, so renaming a
  client does not move their history, and two clients called "Acme" do not
  collide. `resolve_path` refuses `..`, which is what the isolation test asserts.
- **A restore is verifiable.** The digest manifest travels inside the archive, so
  a backup copied to another machine is self-describing. `verify_backup` checks
  every file; `restore_backup` verifies *before* writing, because restoring a
  corrupt file over a healthy one is worse than refusing to restore.
- **One-command deploy.** `app_files.tenancy.deployment_plan` generates a compose
  file, a Render blueprint or a Kubernetes manifest. It mirrors the port
  precedence in `settings.resolve_port` and sets both state homes, because
  getting either wrong is a deploy that fails with a message pointing at
  networking instead of the config.
- **Billing reads `tenant.usage()`** — bytes and files per subtree.

## Documentation

| Document | Covers |
| --- | --- |
| [docs/INSTALL.md](docs/INSTALL.md) | Install with pip or Docker, verify the install |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Add a new CRM or bank format |
| [docs/RULES.md](docs/RULES.md) | Every rule type with a worked YAML example |
| [docs/PRIVACY.md](docs/PRIVACY.md) | Detect and mask personal data |
| [docs/WATCH.md](docs/WATCH.md) | Process files the moment they land |
| [docs/LARGE_FILES.md](docs/LARGE_FILES.md) | Stream a file too big for memory |
| [docs/CONNECTORS.md](docs/CONNECTORS.md) | Read from a database, SFTP or cloud storage |
| [docs/DRIFT.md](docs/DRIFT.md) | Stop a run when a source's schema changes |
| [docs/SWEEP.md](docs/SWEEP.md) | The acceptance run: clean install, full suite, one real file, measured scale |
| [CHANGELOG.md](CHANGELOG.md) | What each extended layer adds, and every fix |

## Tests

```bash
python -m pytest -q
```

Expect the whole suite to pass — around 1,970 tests in about seventy seconds.
Five database tests run only when a PostgreSQL server is reachable (see
`docs/CONNECTORS.md`); without one they report as skipped, not failed. The
suite covers value transforms, each ingestion adapter,
each rule type, each profiling dimension, the lineage tracker, all four output
writers, PII detection and masking, cross-field rules and rule versioning,
multi-way reconciliation, migration safety, metrics, alerting and health checks,
role-based access control, the tamper-evident audit chain, encryption at rest,
plugin registration for transforms, rule types, output formats and
destinations, the durable job queue and its resource limits, tenant isolation,
backup and verified restore, deployment manifests, cloud/SaaS licensing with
seats and metering, trials, brand profiles, a compliance packet, the
folder watcher and its settle window, chunked ingestion for large files,
direct database and SFTP connectors, allocation-based memory enforcement,
the schema drift gate,
config-schema validation, golden-file regression fixtures, and malformed-input
error handling. It runs in about seventy seconds, so there is no reason not to
run it before a commit.

Frozen core: `app_files/cleaners/`, `mappers/`, `validators/`, `auditors/` and
`reporters/` are treated as stable. New capability goes in sibling packages that
call into the core. If a core test fails, the change that broke it is guilty
until proven innocent — revert it rather than editing the expected output.

## Licence

Commercial software. A one-time fee grants a perpetual, non-exclusive,
non-transferable licence for internal business use. Resale, redistribution and
sharing the source are not permitted. Thirty days support, no warranty. See
[LICENSE.md](LICENSE.md).