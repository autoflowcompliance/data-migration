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