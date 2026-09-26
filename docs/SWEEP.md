# Final Sweep

The buyer's acceptance run: a clean copy, the README's own commands, one real
file, and the failure paths. Everything below was run against a copy of the
tree with no `.venv`, no `__pycache__`, and no `.git`, so nothing depended on
state left behind by development.

## Result: pass

| Step | Command | Result | Time |
| --- | --- | --- | --- |
| Install | `python -m venv .venv && pip install -r requirements.txt` | ok | 27s |
| Full suite | `python -m pytest -q` | 1958 passed | 69s |
| Process one file | `python -m app_files.cli migrate -i app_files/samples/everything_on_contacts.csv -c everything_on -o out --commit` | exit 0, 14 deliverables | 2s |
| Web interface | `python main.py` | `root=200` on port 8080 | ~15s to ready |

Total from a cold copy: about 100 seconds, against a ten-minute budget.

## One config, everything on

`app_files/configs/everything_on.yaml` declares every extension block, so one
run exercises all of them. Its committed deliverables:

```
clean_data.csv            masked_data.csv          normalized_data.csv
deduped_data.csv          duplicates_removed.csv   currency_conversions.csv
issues.csv                qa_report.html           privacy_report.html
mapping_log.csv           cleaning_log.csv         lineage_report.csv
pre_migration.txt/.json   runbook.txt              <source>.rollback.csv/.nulls.json
```

The declared-block artifacts are byte-identical whether the run comes from the
flat CLI, `batch`, or `migrate --commit` — pinned by
`tests/unit/test_config_bindings.py` and `tests/integration/test_migrate_command.py`.

## Failure paths

Each exits non-zero with a plain-language message and writes no output. Pinned
by `tests/integration/test_failure_paths.py`.

| Input | Exit | Message |
| --- | --- | --- |
| Config that does not exist | 2 | `No mapping config for '…'. Known CRMs: …` |
| Malformed YAML | 2 | `Invalid mapping config …: while parsing a flow node …` |
| Config with no `fields` | 2 | `it declares no 'fields', so every source column would be dropped` |
| Empty file | 2 | `… is empty — it has no header row, so there is nothing to map.` |
| Bad `normalization:` block | 2 | `Invalid normalization configuration: currency needs 'column' or 'columns'` |

A rehearsal of a source with a blocking issue exits 1 before writing anything,
and reports the block in `pre_migration.txt` (`Ready to migrate: no`).

## A rehearsal is still a rehearsal

`migrate` applies the config's declared blocks to report what a committed run
would do, but it does not persist the accepted rule YAML to the state home.
`persist_rules=False` is the flag that keeps it honest; a test asserts the
state home stays empty after a rehearsal.

## Scale

The acceptance run above uses a 6-row sample, which proves the pipeline is
wired but says nothing about a real export. Measured on a generated
500,000-row, 64 MB contacts file with every declared block on
(`everything_on.yaml`):

| Stage | Time | Notes |
| --- | --- | --- |
| Read | 0.9s | |
| `run_pipeline` (clean, map, profile) | 75.6s | |
| Declared blocks | 453.9s | the bulk of the run |
| **Total** | **530.4s** | 943 rows/s, peak RSS 1,421 MB |

The declared blocks break down as:

| Block | Time | Peak RSS |
| --- | --- | --- |
| Rules (4 rules) | 246.8s | 720 MB |
| Privacy (detect + mask) | 172.7s | 981 MB |
| Normalization | 14.2s | 981 MB |
| Dedupe | 19.9s | 981 MB |

Rule validation dominates. `run_rules` walks every value in Python and calls a
validator per value, so its cost is rows x rules — four rules over half a
million rows is two million Python calls. Privacy is next, because detection
runs seven patterns over every cell. Normalization and dedupe are cheap by
comparison.

This is a characteristic of the frozen validator interface, not a defect: the
core pipeline is untouched and a config that declares no blocks pays none of
it. A file large enough for the rules pass to matter should either run the
blocks on a filtered frame or accept the linear cost. `docs/LARGE_FILES.md`
covers the streaming path for files that do not fit in memory; the declared
blocks operate on a materialised frame, so chunked ingestion and the blocks are
separate paths, not a combined one.

