# Schema drift gate

A source that has changed shape should not reach the pipeline unattended. The
registry in `app_files/mappers/learning.py` already knows how to *detect* a
changed schema; the drift gate in `app_files/drift/` decides whether the run may
proceed.

## What it compares

The gate remembers the schema of a source — its column names and the coarse type
inferred from the values actually present (blank cells ignored). On the next run
it compares the incoming file against that memory and classifies every change:

| Change | Meaning |
|---|---|
| added | a column that was not there last time |
| removed | a column that is gone |
| retyped | a column whose inferred type changed |

Names are matched on their normalised form, so `Email Address` and
`email_address` are the same column and a pure rename is not reported as a
removal plus an addition.

## Verdicts

| Verdict | When | What happens |
|---|---|---|
| `ok` | no change, or first run for the source | run proceeds |
| `warn` | drift the mapping absorbs | run proceeds, the caller prints the change |
| `block` | drift that loses a required target mapping | run stops, exit code 1 |

Two things are deliberately *not* blocking:

- **An unknown source.** With nothing remembered there is nothing to have
  drifted from, so a first run can never be blocked by a gate meant to catch
  changes.
- **A required field that was already unmapped.** Blocking is drift-relative: a
  required target only blocks when it mapped from the old schema and no longer
  maps from the new one. A target that never resolved before did not work
  before either, and the gate does not pretend the drift caused it.

## Command line

```bash
python -m app_files.cli drift -i contacts.csv -c hubspot --source crm_export -o output
```

- `--source` names the remembered source. Defaults to the input filename; set it
  when the same logical feed arrives under different filenames.
- A blocked run writes nothing and exits 1, so a scheduled job stops instead of
  quietly migrating a changed source.
- `--accept` records the current schema after a human has reviewed the change,
  so the next run is judged against what was actually migrated.

The run that succeeds records the schema automatically. Only a blocked run
leaves the remembered schema untouched.

## Library

```python
from app_files.drift import DriftBlocked, DriftGate

gate = DriftGate()
result, decision = gate.guarded_run("crm_export", frame, "hubspot")
if decision.verdict == "warn":
    print(decision.summary())
```

`guarded_run` raises `DriftBlocked` (with `.decision` attached) when the verdict
is `block`, so no caller can accidentally run a blocked source.

## State

The remembered schemas live in `$AUTOFLOW_HOME/mapping/schemas.json`. With
`AUTOFLOW_HOME` set, nothing is written into the repository working tree.
