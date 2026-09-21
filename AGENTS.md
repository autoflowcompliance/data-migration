# AutoFlow Data Migration Tool

## Architecture: frozen core, additive layers

Layer 1 (`app_files/cleaners`, `mappers`, `validators`, `auditors`, `reporters`)
is **frozen**. Every new capability goes in a new sibling layer that calls into
it. This is what keeps a bug in a new layer from breaking the CRM tool, and it
is the single rule that matters most in this repo.

```
app_files/
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
├── interface/web/main.py     # LAYER 7 — the web UI entry (NiceGUI)
│   ├── routes/               # one module per page; import registers the route
│   ├── theme.py              # LAYER 7 — design tokens + stylesheet
│   ├── components.py         # LAYER 7 — shared widgets
│   └── state.py              # LAYER 7 — page logic (where the tests point)
└── configs/                  # one YAML per target system
```

The core reporter's HTML is **not** modified to add the scorecard.
`profiling/report.render_qa_report_with_profile` injects it into the rendered
HTML afterwards. Verify the base report is unpolluted with
`'Quality scorecard' not in run_pipeline(...).qa_report_html`.

## Commands

```bash
python -m pytest -q                 # full suite, 536 tests, ~12s
python -m pytest app_files/tests/   # the original 25 pre-existing tests
python main.py                      # DataFlow (NiceGUI) — port 8080
python build_desktop.py --check     # packaged desktop target
```

One UI ships. There is no second entry point and no `DATAREADY_UI` setting —
`main.py`, the container and the desktop launcher all reach
`app_files/interface/web/main.py:run_server`, so there is one server to reason
about. **Rule builder UI is a follow-up feature — not yet in NiceGUI.**

## Deployment (Render)

`render.yaml` deploys the NiceGUI app as a Docker web service off `Dockerfile` /
`main.py`.

- **Port precedence is `PORT` > `DATAREADY_PORT` > 8080.** Render injects `PORT`
  (default 10000) and routes traffic only there. The Dockerfile bakes
  `DATAREADY_PORT=8080`, so the old `getenv("DATAREADY_PORT", getenv("PORT"))`
  order made the container bind 8080 while Render scanned 10000 → the deploy
  fails with *no open ports detected*. `resolve_port()` in
  `app_files/settings.py` encodes the correct order; the Dockerfile
  HEALTHCHECK resolves the port the same way so it does not probe a dead 8080.
  Pinned by `tests/unit/test_deployment.py`. Do not set `PORT` in `render.yaml`.
- **Two state-home env vars, not one.** The licensing/branding layers read
  `DATAREADY_HOME`; the collaboration/audit/anomaly layers read
  `AUTOFLOW_HOME`. Set both (the blueprint points them at `/app/run_config`).
  Setting only one leaves the other writing into the repo.

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

### The UI end-to-end test has one trick worth knowing

`tests/integration/test_ui_end_to_end.py` renders the real pages through
NiceGUI's simulation. Its `app_user` fixture is not the library's `user`
fixture, and it cannot be: NiceGUI runs `main.py` once per process and then
drops every route it registered, so the second test in a process 404s on
everything. The fixture purges `app_files.interface.web.routes` from
`sys.modules` and re-imports it after the reset — the import is what re-runs the
`@ui.page` decorators. It also sets `NICEGUI_USER_SIMULATION=true` so `ui.run`
wires up the in-process ASGI app instead of a socket. A new route test should
take `app_user`, not `user`.

`tests/unit/test_design_port.py` is the design guard: it pins every palette
token and asserts each Quasar control the app uses has an override. The design
source of truth is `theme.py` (palette, `STYLESHEET`) and `components.py` (the
skinned widgets). Routes must reach for the `components` helpers rather than raw
`ui.input`/`ui.select`, and render markup through `ui.html`.

### Never give a button a Quasar `color`

NiceGUI defaults a button to Quasar's `primary` colour, which makes Quasar
attach the `bg-primary` and `text-white` utilities. Those ship inside Quasar's
`quasar_importants` cascade layer, and **CSS reverses layer precedence for
`!important` declarations** — so a layered `!important` utility beats our
unlayered `!important` rule even when ours is more specific. The symptom is a
hidden `.active` state: a nav button whose amber background never painted, and
no blue pixels anywhere to explain why.

`theme.button`/`theme.download_button` therefore force `color=None`. Any new
widget helper that wraps a Quasar control with a colour prop needs the same
treatment. The `inject_theme` call also repoints Quasar's JS-level brand config
(`app.colors`) at the palette, because Quasar serialises a second copy that CSS
variables do not reach. `tests/integration/test_ui_end_to_end.py` pins both the
stock-blue absence and the button-props invariant on the served HTML.

The demo is a run allowance (`DEMO_RUNS_PER_SESSION`), not a feature cut:
lineage, batch and branding are all on, and the only real difference is the
report watermark. Do not reintroduce per-feature `if demo` checks — read the
resolved `Limits`. The counts in the banner and the exhausted-runs notice are
passed in from the limits rather than written into the copy, so lowering the
constant changes the text too.

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
