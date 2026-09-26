# Data & Analytics Platform — 13-Module Specification

Scope: Additive only. Extend `plugins/registry.py`. Never touch the frozen
pipeline. One module per slice, 8-step protocol, full suite + goldens green
before moving on.

## Modules

| # | Module | State | Directory | Scope |
|---|---|---|---|---|
| 1 | Profiling | Complete | `app_files/profiling/` | Column-level statistics, regex pattern inference, outlier detection (IQR, z-score, isolation forest). New sibling modules `column_stats.py`, `patterns.py`, `outliers.py`, `profiling_block.py`, `registry.py`. Existing `profiler.py`, `dimensions.py`, `report.py`, `dimension_anomaly.py`, `binding.py` untouched. Real-file verified on a 12,000-row export. |
| 2 | Cleansing & Standardization | Partially exists — extend | `app_files/cleansing/` | Add NLP address parsing, entity resolution (person/company/product), expanded fuzzy matching (Soundex, Metaphone), phone line-type detection. Extends existing cleaners, does not replace them. |
| 3 | Observability | New | `app_files/observability/` | Continuous monitoring agent, statistical anomaly detection (volume, freshness, distribution), alert rules with routing, observability dashboard. Reuses existing alerting binding and Prometheus metrics. |
| 4 | Master Data Management | New | `app_files/mdm/` | Golden-record assembly, survivorship rules, entity matching (deterministic + probabilistic), hierarchy management, merge policies. Reuses existing dedupe and reconciliation engines. |
| 5 | Pipeline Automation | Extends existing | `app_files/pipeline/` | Visual pipeline builder, typed DSL, error handling with dead-letter queue, retry policies. Extends existing scheduler, dependency chains, job queue, worker pool. |
| 6 | ETL / ELT | Extends existing | `app_files/etl/` | Incremental loads via watermark, change data capture (insert/update/delete), SQL-based transformation engine, bulk load to destinations. Extends existing incremental patterns. |
| 7 | Connector Library | Extends existing | `app_files/connectors/` | Registry + discovery, database connectors (Postgres, MySQL, SQL Server, Snowflake, BigQuery, Redshift, Databricks, ClickHouse, DuckDB), SaaS connectors (Salesforce, HubSpot, Stripe, QuickBooks, Xero, Shopify), file connectors (extend existing S3/GCS/Azure/Sheets/Dropbox/OneDrive/SFTP), REST/GraphQL. |
| 8 | Lineage & Governance | Extends existing | `app_files/lineage/` | Column-level lineage tracking, impact analysis (what breaks if X changes), governance policies (PII tracking, retention), column-level visual graph. Extends existing lineage layer. |
| 9 | Data Catalog | New | `app_files/catalog/` | Automatic metadata harvesting, faceted search, auto-tagging (PII, domain, freshness), business glossary with term linking, catalog web UI. Depends on lineage + profiling. |
| 10 | Quality Scoring | Complete | `app_files/quality/` | Five-dimension scoring, trend tracking, regression detection, SLA enforcement. Done: 2,080 tests passing, all four surfaces wired, real-file verified. |
| 11 | Semantic Layer | New | `app_files/semantic/` | YAML metric/dimension definitions, query compilation (metrics → SQL), versioned registry, semantic validation (no orphan dimensions, no circular refs), semantic query API. |
| 12 | Data Contract Governance | New — must use `contract_governance/` | `app_files/contract_governance/` | Producer/consumer contracts, enforcement at ingestion, versioned registry, breach detection + alerting. Do not touch `app_files/contracts/` — that holds a different schema read by `collaboration/contracts.py`. |
| 13 | Statistical Drift | New — must use `statistical_drift/` | `app_files/statistical_drift/` | KS test, PSI, chi-square; feature-level drift; model prediction drift; drift alerting. Do not touch `app_files/drift/` — that is Layer 19, structural schema drift. Two meanings of "drift" in one package is how silent wrong-answer bugs happen. |

## Build Order

| Order | Module | Why This Order |
|---|---|---|
| 1 | Profiling (extend) | Fills the real gaps in a 70%-done module. Low risk, fast win. |
| 2 | Cleansing (extend) | Extends cleaners that already work. Tests the extension pattern again. |
| 3 | Lineage (extend) | Extends existing lineage. Needed by Catalog later. |
| 4 | Statistical Drift (new dir) | First truly new package. Establishes the new-package template. |
| 5 | Observability (new) | Reuses alerting binding. Moderate scope. |
| 6 | MDM (new) | Larger scope. Reuses dedupe + reconciliation. |
| 7 | Contract Governance (new dir, no collision) | First consumer-side module. |
| 8 | Connector Library (extend) | High integration count. Longest single module. |
| 9 | Catalog (new) | Depends on lineage + profiling. |
| 10 | Semantic Layer (new) | Depends on catalog + contracts. |
| 11 | Pipeline (extend) | Extends scheduler + job queue. |
| 12 | ETL (extend) | Extends incremental patterns. |

Then: full-platform bug scan, packaging, demo, listing.

## Rules

- Additive only. Frozen pipeline not edited. All 1,969 pre-existing tests stay passing.
- Extend `plugins/registry.py`. Do not build a second registry.
- Module 12 goes in `app_files/contract_governance/`. Do not touch `app_files/contracts/`.
- Module 13 goes in `app_files/statistical_drift/`. Do not touch `app_files/drift/`.
- One module at a time. 8-step protocol per module. Full suite + all goldens green before starting the next.
- Report verified numbers (test deltas, insertions/deletions, CI status), not claims.
- If a module already exists in part, extend it — do not rewrite it.

## Per-module protocol (8 steps)

1. Interface first — write the test against the interface before the implementation.
2. Build on existing — depend on existing interfaces, do not modify them.
3. Unit test — happy path, boundary, failure.
4. Integration test — inside the full pipeline; existing behavior unchanged.
5. Golden file — known input, known output, byte-identical.
6. Real file verification — a real file with real data.
7. Regression — full suite green, every prior golden still matching.
8. Document — spec, README, changelog.

Each module ships as a package + an optional config block + thin adapters into
CLI/API/SDK, with no edits to the frozen core.
