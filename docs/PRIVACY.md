# Privacy — detecting and masking personal data

The privacy layer finds personally identifiable information in your data and
replaces it before the data reaches a destination. It is a separate package,
`app_files/privacy/`, that reads the frame the pipeline produced. It does not
modify the cleaning, mapping, validation, audit or reporting code, and it never
runs unless a config turns it on.

```python
from app_files.privacy import PrivacyConfig, detect_frame, mask_frame

config = PrivacyConfig(enabled=True)
report = detect_frame(frame, config)   # report only; never mutates the frame
masked = mask_frame(frame, config)     # a new frame; the input is untouched
```

`mask_frame` returns a `MaskResult`:

| Attribute | Holds |
| --- | --- |
| `.frame` | The masked frame |
| `.report` | What was found, per column and kind |
| `.masked_counts` | `{kind: count}` actually masked |
| `.vault` | Reversible token vault, when `tokenize` was used |
| `.summary()` | The whole result as a plain dict |

## What it detects

Structured identifiers are validated, not merely pattern-matched. A 16-digit
order number that fails the Luhn checksum is not reported as a card, and an
IBAN whose mod-97 check fails is not reported as an account number. This is
what keeps the layer from masking values that only look sensitive.

| Kind | Validation |
| --- | --- |
| `email` | RFC-shaped local part and a real-looking domain |
| `phone` | Parsed and validated with `phonenumbers` against the configured region |
| `credit_card` | Luhn checksum, 12–19 digits, at least two distinct digits |
| `iban` | ISO 13616 mod-97 check |
| `national_id` | US SSN shape with legal area/group/serial ranges |
| `passport` | Letter-plus-digits shape. Off by default, no checksum |
| `custom:<name>` | Your own regular expression |

Detection is offline and deterministic: no network call, no model. The same
input always produces the same detections.

## What it masks

Four strategies, chosen per column and optionally scoped to particular kinds:

| Strategy | Result | Joinable | Reversible |
| --- | --- | --- | --- |
| `redact` | `[REDACTED]` | No | No |
| `hash` | SHA-256 digest, salted | Yes | No |
| `tokenize` | `PII_<digest>` backed by an encrypted vault | Yes | Yes, with the key |
| `partial` | `****1234`, last four kept | No | No |

`hash` is deterministic, so two tables masked with the same salt still join on
that column. `tokenize` is also deterministic and additionally lets you resolve
a token back to its original from the vault.

Only the matched span is rewritten. A phone number inside a free-text note is
masked while the sentence around it survives.

## Configuration

The layer reads a `privacy:` block. It can sit in a CRM config alongside
`fields:` and `rules:`, or in a config file of its own:

```yaml
privacy:
  default_strategy: redact
  region: US
  detect:
    passport: true          # opt in; it has no checksum
  fields:
    - column: email
      strategy: hash        # joins still work on this column
    - column: Notes
      strategy: redact
      kinds: [email]        # only email inside Notes; a phone there is left alone
  custom_patterns:
    employee_id:
      pattern: 'EMP-\d{6}'
      label: Employee ID
```

| Key | Meaning |
| --- | --- |
| `default_strategy` | Strategy for any column without its own rule. Default `redact` |
| `detect` | Turn individual detectors on or off |
| `fields` | Per-column rules: `column`, `strategy`, optional `kinds`, optional `salt` |
| `custom_patterns` | Named regular expressions, detected as `custom:<name>` |
| `hash_salt` | Salt for `hash`. A per-field `salt` overrides it |
| `token_key` | Key for `tokenize`. Prefer `token_key_env` over committing a key |
| `token_key_env` | Environment variable to read the token key from. Default `DATAREADY_PII_KEY` |
| `region` | Region for phone parsing. Default `US` |
| `vault_path` | Where the token vault is written. Nothing is written unless this is set |

A column with no rule uses `default_strategy`. A rule with `kinds` applies only
to those kinds in that column, so a mixed free-text column can be redacted for
emails while its phone numbers are left intact.

## Reversible tokenization

`tokenize` is the only strategy that needs a key. Without one, `mask_frame`
raises `PrivacyKeyError` rather than quietly degrading to an irreversible form:

```python
import os
os.environ["DATAREADY_PII_KEY"] = "..."     # or set privacy.token_key

config = PrivacyConfig(
    enabled=True,
    fields=[FieldRule(column="email", strategy="tokenize")],
    vault_path="vault.json",                 # omit to keep the vault in memory
)
```

The token is `HMAC(key, value)`, so it is stable across runs. The original is
sealed with the same key and written to the vault. The vault file is created
`0600`, and reading an entry with the wrong key fails an integrity check
instead of returning garbage.

## Reading the report

```python
report = detect_frame(frame, config)

report.total                       # how many matches
report.kind_counts()               # {'email': 12, 'phone': 9}
report.columns_with_pii            # ['email', 'phone']
report.affected_columns()          # {'email': {'email': 12}, ...}
report.detections_frame()          # one row per match: column, kind, value, start, end
```

The rendered card appends to the QA report without touching it:

```python
from app_files.privacy import inject_pii_report

augmented = inject_pii_report(pipeline_result.qa_report_html, report, masked.summary())
```

The base report is a prefix of the augmented one, byte for byte — the frozen
reporter is never rewritten.

## Verifying a mask worked

The property that matters is that nothing sensitive survives. Re-scan the
output and expect a total of zero:

```python
masked = mask_frame(frame, config).frame
assert detect_frame(masked, config).total == 0
```

`tests/regression/golden_files/pii/` holds a fixture with planted PII and the
exact masked output it must produce. `tests/unit/test_privacy.py` checks a
generated corpus of 600 known values for false negatives, and an end-to-end run
over a 12,000-row file with planted PII.

## Scope

Detection is pattern- and checksum-based. It will not find a name or an address
that has no structured shape, and a value that passes a checksum is treated as
real. Add a `custom_patterns` entry for identifiers specific to your data. The
layer's promise is that every value matching a configured pattern is masked —
not that it recognises personal data the way a person would.

Tokenized originals live in the vault wherever `vault_path` points. Put it on
encrypted storage; the vault plus the key is the data.
