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
python -m pytest -q                 # full suite, 204 tests, ~2s
python -m pytest app_files/tests/   # the original 25 pre-existing tests
python -m streamlit run app_files/app.py                          # CRM tool
python -m streamlit run app_files/interface/web/app.py            # new web UI
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
- `MappingConfig.fields` is a **list** of `TargetField`; field names are
  `{f.name for f in config.fields}`.
- Lineage `action` values are `clean` (bare, no `clean:` prefix),
  `map:<transform>`, and `removed_duplicate`.
- `run_reconciliation` takes **raw CSV bytes**, not paths and not a DataFrame.
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
