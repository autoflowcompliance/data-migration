# Rules

Rules let a config declare what a *valid* value looks like, without touching
code. They live under a top-level `rules:` list in any config YAML and run
against the mapped frame, so they see the canonical column names
(`email`, not `Email Address`).

Failures land in the same issues list the built-in quality validator writes to,
which means they appear in the issues CSV and the QA report like any other
issue. There is nothing extra to wire up.

```yaml
rules:
  - name: amount_positive
    field: amount
    type: range
    min: 0
    severity: error
```

## Common keys

| Key | Required | Meaning |
| --- | --- | --- |
| `field` | yes | Mapped column the rule applies to. |
| `type` | yes | One of `required`, `range`, `length`, `list_of_values`, `regex`. |
| `name` | no | Identifier used in the issues CSV. Defaults to `<type>_<field>`. |
| `severity` | no | `error`, `warning`, or `info`. Defaults to `error`. |
| `message` | no | Custom failure text, replacing the generated message. |

Every rule type also accepts only its own parameters. An unknown key is a config
error rather than a silent no-op, so a typo is caught on load:

```
Rule has unknown keys: minimum. Allowed: case_sensitive, exactly, field, ...
```

## Blank values

A blank value fails **only** a `required` rule. `range`, `length`,
`list_of_values`, and `regex` all skip blanks, because "the value is empty" is
already the completeness check's job. Reporting it again here would
double-count one problem as two.

## `required`

Fails when the cell is empty or null. Accepts no other parameters.

```yaml
- name: lastname_required
  field: lastname
  type: required
  severity: error
```

## `range`

Numeric bounds, inclusive on both ends. Needs at least one of `min` or `max`.
Values that aren't numbers fail the rule.

```yaml
- name: amount_within_expected_range
  field: amount
  type: range
  min: -1000000
  max: 1000000
  severity: warning
  message: "Amount is unusually large for this account — check for a typo"
```

## `length`

Character count. `exactly` is mutually exclusive with `min_length` /
`max_length`; use `exactly` alone for a fixed width, or the bounds for a range.
Needs at least one of the three.

```yaml
- name: phone_length
  field: phone
  type: length
  exactly: 10
  severity: warning
```

```yaml
- name: state_code_length
  field: state
  type: length
  min_length: 2
  max_length: 2
  severity: error
```

## `list_of_values`

The value must be one of `values`. Matching is case-insensitive by default,
which suits CRM status fields where `Lead`, `lead`, and `LEAD` are the same
thing. Set `case_sensitive: true` when case is meaningful. Needs a non-empty
`values` list.

```yaml
- name: status_valid
  field: lifecyclestage
  type: list_of_values
  values: [lead, customer, other]
  severity: error
```

```yaml
- name: country_code_upper
  field: country_code
  type: list_of_values
  values: [US, GB, ZA]
  case_sensitive: true
  severity: warning
```

## `regex`

The value must match the pattern. Needs a `pattern`. Note that YAML double
quotes process backslashes, so escape them (`"^\\+[1-9]\\d{6,14}$"`); single
quotes avoid the doubling.

```yaml
- name: phone_e164_format
  field: phone
  type: regex
  pattern: "^\\+[1-9]\\d{6,14}$"
  severity: warning
  message: "Phone is not in E.164 form (e.g. +15551234567)"
```

## Rules on columns that aren't present

A rule whose `field` is not in the frame is skipped, not an error. That lets one
config's rules be reused where the mapped output differs slightly, and lets a
config declare rules for optional fields.

## Validating your YAML with an editor

`app_files/configs/schema/rules_schema.json` is a JSON Schema for the `rules:`
list. Editors that understand it will autocomplete rule types and flag a missing
`pattern` or an unknown key before you run anything. The loader enforces the same
constraints at runtime, so the schema is a convenience rather than the only
safety net.

## Running rules from Python

```python
from app_files.mappers import load_mapping_config, map_data
from app_files.rules import run_rules_for

mapped = map_data(source_frame, load_mapping_config("hubspot")).frame
result = run_rules_for(mapped, "hubspot")

print(result.rules_run, result.total_failures)
print(result.failures_by_rule)   # {'phone_e164_format': 1}
for issue in result.issues:
    print(issue.row, issue.field, issue.check, issue.message)
```

`run_rules_for` accepts a config name (`"hubspot"`) or a path to a YAML file.

## Rules in an unattended run

A config's `rules:` block runs automatically in every entry point — the CLI,
the batch engine and the web UI — not only when you call `run_rules_for`
yourself. The failures land in the same issue list the core validator fills, so
they appear in `issues.csv`, in the QA report and in the quality score:

```bash
python -m app_files.cli -i contacts.csv -c hubspot -o out/
# 7 rows in, 6 out, quality score 66.7%, 1 errors, 2 warnings
# Rules: 2 of 2 run, 1 failure(s)
```

A rule failure is **advisory by default** — it is reported, not enforced, so a
run whose core validation passes still exits 0. Add `--strict-rules` to make a
declared failure fail the run (exit 1); it works for both the single-file and
`batch` commands:

```bash
python -m app_files.cli batch --in inbox/ --template hubspot --out out/ --strict-rules
```

The batch `summary.csv` gains two columns, `rules_run` and `rule_failures`, one
row per file.

In Python, `run_configured` returns the pipeline result with the config's rules
already applied, and `apply_configured_rules` does the same on top of a result
you ran yourself (pass the same `project_name` and `source_filename` so the
re-rendered report keeps its header):

```python
from app_files.rules.binding import run_configured, failures_exceed

built = run_configured(source_frame, "hubspot", project_name="Acme")
print(built.rule_result.rules_run, built.rule_result.total_failures)
print(failures_exceed(built))   # True when anything declared failed
```

A config with no `rules:` block behaves exactly as the plain pipeline did — same
clean data, same report, byte for byte.

## Cross-field rules

Single-field rules judge one value. Some rules span columns: `close_date` must
not precede `open_date`; `total` must equal `subtotal + tax`. Declare those under
a top-level `cross_field:` list:

```yaml
cross_field:
  - name: close_after_open
    type: date_order
    fields: [open_date, close_date]
    severity: error

  - name: total_matches_parts
    type: sum_equals
    fields: [total, subtotal, tax]
    tolerance: 0.01

  - name: discount_below_total
    type: compare
    fields: [discount, total]
    operator: "<"
```

| Type | Fields | Meaning |
| --- | --- | --- |
| `date_order` | `[earlier, later]` | `earlier` must be on or before `later`. |
| `sum_equals` | `[total, part, ...]` | `total` must equal the sum of the parts, within `tolerance`. |
| `compare` | `[left, right]` | The declared `operator` must hold. |

`compare` requires an `operator` of `<`, `<=`, `==`, `!=`, `>` or `>=`.
`sum_equals` needs a total plus at least two parts. A `message` overrides the
generated failure text, and `date_format` pins date parsing when a column is
ambiguous.

A cross-field rule is evaluated row by row and reports one `Issue` per failing
row, under the check name `cross_field:<rule name>`. Those issues are the same
type the single-field rules produce, so they appear in the issues CSV and the QA
report with nothing extra to wire up.

Two things a rule will not do:

- A rule whose columns are not in the frame is reported in `skipped_rules`
  rather than raising or silently passing.
- A row with a blank in any referenced column is skipped. Empty values belong to
  the completeness check; failing them here would count one problem twice.

## Rule versioning and sandbox

Rule sets are versioned under `AUTOFLOW_HOME/rules`, one JSON file per set. No
rule set reaches production without a sandbox run first:

```python
from app_files.rules import SandboxStore

store = SandboxStore()
version = store.save_version("crm_rules", cross_field=rules, note="stricter close date")

# Run the candidate against recent files. This never promotes.
outcome = store.sandbox_run("crm_rules", version.version, [recent_frame])
print(outcome.failures, outcome.failures_by_rule)

store.promote("crm_rules", version.version)      # needs the sandbox run above
store.rollback_to("crm_rules", 1)                # restores v1 as a new version
```

Versions are append-only. Promoting a new version marks the previous one
`superseded`; rolling back writes the earlier rules as a new version rather than
deleting the version it replaced. `store.history("crm_rules")` lists every
version with its status, timestamp and sandbox runs.
