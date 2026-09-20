# Bank Reconciliation

**Who it is for:** bookkeepers and small businesses reconciling a bank statement
against their ledger.

**What it does**

- Normalises statement dates to ISO 8601 and keeps accounting-style amounts
  (`(250.00)` and `1,200.00 CR`) readable.
- Flags any statement line with no amount (error).
- Flags unusually large amounts as probable typos (warning).

Pair this template with the **Bank Reconciliation** page, which matches the
cleaned statement against your ledger and reports what is missing from your
books and what never cleared the bank.
