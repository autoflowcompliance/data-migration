# AutoFlow Data Migration Tool

## Architecture: frozen core, additive layers

Layer 1 (`app_files/cleaners`, `mappers`, `validators`, `auditors`, `reporters`)
is **frozen**. Every new capability goes in a new sibling layer that calls into
it. This is what keeps a bug in a new layer from breaking the CRM tool, and it
is the single rule that matters most in this repo.

```
app_files/
├── app.py, admin.py          # Streamlit entrypoints — do not modify
├── pages/                    # Streamlit native multipage (auto-discovered)
├── services/                 # self-contained features (bank reconciliation)
├── cleaners/ mappers/        # LAYER 1 — frozen
├── validators/ auditors/ reporters/  # LAYER 1 — frozen
├── ingestion/                # LAYER 2 — csv/excel/pdf/json adapters
├── rules/                    # LAYER 3 — YAML-driven validation
│   ├── builder.py            # deterministic form -> YAML (no AI, no network)
│   └── execution.py          # run built rules + merge into the QA report
├── profiling/                # LAYER 4 — 5-dimension quality scores
├── lineage/                  # LAYER 5 — row-level transformation log
├── output/                   # LAYER 6 — csv/excel/json/sql writers
├── interface/web/app.py      # LAYER 7 — the web UI
└── configs/                  # one YAML per target system
```

The core reporter's HTML is **not** modified to add the scorecard.
`profiling/report.render_qa_report_with_profile` injects it into the rendered
HTML afterwards. Verify the base report is unpolluted with
`'Quality scorecard' not in run_pipeline(...).qa_report_html`.

## Commands

```bash
python -m pytest -q                 # full suite, 291 tests, ~3s
python -m pytest app_files/tests/   # the original 25 pre-existing tests
python -m streamlit run app_files/app.py                          # CRM tool
python -m streamlit run app_files/interface/web/app.py            # new web UI
python -m streamlit run app_files/interface/web/pages/rules.py    # rule builder
python -m streamlit run app_files/pages/bank_reconciliation_page.py
```

Use `python -m streamlit` rather than the bare `streamlit` script — the console
script is not always on `PATH`.

## Layout of the tests

- `tests/unit/` — one module per layer, plus `test_reconciler.py` and
  `test_error_handling.py`.
- `tests/integration/test_pipeline.py` — full pipeline on the sample files.
- `tests/regression/test_golden_files.py` — known input to known output.

### Golden files are sacred

`tests/regression/golden_files/` holds a known input and the exact output it
must produce. If one breaks, the change is guilty until proven innocent:
revert it or fix the bug. **Never regenerate the expected file to make the test
green** — that silently deletes the only thing protecting the frozen core.

## API notes that are easy to get wrong

- `run_pipeline(source, crm=..., lineage_tracker=LineageTracker())` — lineage
  is opt-in via a tracker instance, not a `track_lineage=` flag.
- `run_reconciliation` takes **raw CSV bytes plus four explicit column names**
  (`bank_date_col`, `bank_amount_col`, `ledger_date_col`, `ledger_amount_col`)
  and an optional `date_tolerance_days`. Calling it with just two byte strings
  raises `TypeError`.
- Paths that hold runtime state must respect `AUTOFLOW_HOME`: audit trail,
  anomaly baselines, workspaces, and hosted-audit orders/reports all resolve
  under it. A new state-writing layer that hardcodes a path under the repo root
  will litter the working tree and fail the portability tests in
  `tests/unit/test_market_layers.py` (`test_orders_storage_honours_autoflow_home`).
- `run_pipeline` does **not** execute the config's `rules:` block. It validates
  the mapped frame only. Rules are run separately by the caller with
  `run_rules_for(frame, crm)`. A config passed as `crm` whose rules never get
  run reports `quality_score: 100` and zero issues — which reads as "your data
  is fine". Never conclude a rule set works without checking `rules_run`.
- Rules are written against **source** column names (`Email Address`) but run
  against the **mapped** frame (`email`). `app_files/rules/execution.py`
  translates between them via `field_map` / `resolve_rules`. Skip that and the
  rule matches no column, runs nothing, and reports zero failures. Rules that
  cannot be resolved are surfaced as `unmatched_rules`, not silently dropped.
- `MappingConfig.fields` is a **list** of `TargetField`; field names are
  `{f.name for f in config.fields}`.
- Lineage `action` values are `clean` (bare, no `clean:` prefix),
  `map:<transform>`, and `removed_duplicate`.
- `run_reconciliation` takes **raw CSV bytes** plus four column-name arguments
  (`bank_bytes, ledger_bytes, bank_date_col, bank_amount_col, ledger_date_col,
  ledger_amount_col`, optional `date_tolerance_days=2`) — not paths and not a
  DataFrame. It returns a dict; the counts are under `result["summary"]`.
  To reconcile a PDF, ingest it with `read_any` and call
  `reconcile_transactions` on the frame.
- `read_any` needs `filename=` when given bytes, since the extension selects
  the adapter.
- Blank values fail only a `required` rule. `range` / `length` /
  `list_of_values` / `regex` skip blanks, because "empty" is the completeness
  check's job — otherwise one problem is counted twice.
- Unparseable amounts/dates in a statement are reported as **unmatched**, not
  dropped and not raised. `UnreadableStatementError` covers empty/headerless
  uploads so the UI can show plain language.
- SQL column typing inspects the actual values. A column is `NUMERIC` only if
  every non-blank value parses as a number. Beware the inverse bug: it is easy
  to write the check as a list of "looks numeric but isn't" exclusions
  (leading `+`, leading zero) and forget to verify it *is* a number, which
  silently types `John` and `john@email.com` as `NUMERIC` and lets SQL numeric
  affinity rewrite them.

## Adding a new target system

Drop a YAML in `app_files/configs/`. `available_crms()` scans the directory, so
it appears in the UI selector with no code change. See `docs/CONFIGURATION.md`
and `docs/RULES.md`.

## Scope discipline

One verified change at a time. Add a single new isolated feature, confirm it
against the full suite and the goldens, then stop. Bundling several unverified
features is how this project previously went sideways.
