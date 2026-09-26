# Changelog

The frozen core is the original twelve layers, which the CRM tool ships and
depends on. Everything below is additive: new sibling layers that call into the
core, plus the wiring that lets a config declare them. A run that worked before
this work produces byte-identical output.

## Unreleased — extended architecture

### Added — extension layers

- **Ingestion.** Chunked ingestion for files too large for memory, with an
  allocation-based memory ceiling. Database connectors (PostgreSQL, MySQL, SQL
  Server, SQLite) and SFTP behind the existing `read_any` contract. A folder
  watcher that triggers a run when a file lands. Schema drift detection that
  stops a changed source before it runs.
- **Cleaning.** PII detection and masking (redact, hash, tokenize, partial)
  across email, phone, national ID, card, IBAN, passport and custom patterns.
  Fuzzy dedupe (Levenshtein, Jaro-Winkler) alongside exact dedupe. Address and
  currency normalization with a recorded rate and date.
- **Mapping.** Learned mapping keyed by source fingerprint, with confidence.
- **Rules.** Cross-field rules, rule versioning, and a sandbox gate before
  promotion.
- **Profiling.** Quality trend history, baseline comparison, and dimension
  anomaly detection. A `quality:` config block turns the score into a gate: a
  floor per dimension, plus the action a regression against the pinned baseline
  should take (`alert`, `block`, `quarantine`). Reachable as
  `quality check`, `POST /quality` and `SDK.quality()`.
- **Lineage.** Interactive lineage graph, blast-radius analysis, OpenLineage
  export.
- **Reconciliation.** N-way reconciliation with configurable match logic and
  stored history.
- **Output.** Signed deliverables (HMAC), completion webhooks, and direct push
  to S3, SFTP, Sheets and email.
- **Batch.** Scheduler, event triggers, dependency chains, retry with backoff,
  incremental processing.
- **Branding.** Multiple brand profiles, one per client or run.
- **Licensing.** Cloud/SaaS licensing with seats and metering, plus trials.

### Added — new layers

- **Layer 13 Security and governance.** Role-based access control, an
  append-only audit log, encryption at rest and in transit, and a compliance
  posture packet (GDPR, CCPA, SOC 2, residency, retention).
- **Layer 14 Orchestration.** A durable job queue, distributed workers, and
  per-job resource limits.
- **Layer 15 Observability.** Prometheus metrics, multi-channel alerting, and
  liveness/readiness probes.
- **Layer 16 Multi-tenancy and cloud.** Tenant isolation, verified
  backup/restore, and deploy manifests.
- **Layer 17 Extensibility.** Plugin registration for transforms, rules, output
  formats and destinations.
- **Layer 18 Migration safety.** Pre-migration analysis, rollback files, dry
  run, and a cutover runbook generator.

### Added — interfaces

- The extended layers are reachable through the API and a Python SDK.
- `migrate`, `batch` and `jobs` CLI commands.
- `app_files/configs/everything_on.yaml`, a single config that declares every
  block at once.

### Fixed

- **`migrate` ignored every block a config declared.** A rehearsal reported no
  duplicates for a config whose dedupe removes rows, and `--commit` wrote raw
  email and phone values for a config that declared them masked. The binding
  sequence is now one shared helper called by every entry path, so `migrate`,
  `batch` and the flat CLI produce byte-identical declared-block artifacts.
- **A rehearsal persisted an accepted ruleset.** Applying the config's rules to
  report them also wrote rule YAML to the state home, breaking the documented
  "writes nothing" contract. A rehearsal now passes `persist_rules=False`.
- **A refused database connection raised the driver's own exception.** A wrong
  password produced a raw `psycopg2.OperationalError` instead of the documented
  `DatabaseError`, so the catch every caller writes missed it. The password is
  now scrubbed from the message.
- **Running the API module as `__main__` imported the extras twice**, making a
  client error a 500 because the registered handler keyed off a different
  `BadRequest` class.

### Changed

- The API server serves the extra routes by default. Tests pinning the original
  five pass `include_extras=False`.
- `run_pipeline` still does not apply a config's declared blocks; that remains
  the caller's job. A config that declares none is unaffected.

### Infrastructure

- CI runs the documented suite (`python -m pytest -q`) from
  `requirements.txt` on Python 3.10 (the interpreter `python:3.10-slim` ships)
  and 3.12, with `AUTOFLOW_HOME` pointed at the runner temp so runtime state
  stays out of the checkout.
- Removed stray `out/report.*` committed from a development run, and anchored
  `/out/` in `.gitignore` so a short `-o out` cannot litter the tree.
