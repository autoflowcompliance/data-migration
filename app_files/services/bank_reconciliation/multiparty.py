"""N-way reconciliation (3+ statements) and reconciliation history.

The two-way reconciler answers "does the bank agree with the books". Real
finance work needs more: a bank statement, the ledger, and a payment processor's
export should all agree, and the useful question is which one is the odd one out.

* **N-way reconciliation** matches a transaction across any number of sources.
  Each transaction is identified by (amount, date within tolerance), and is then
  classified by which sources contain it: present everywhere, present in a
  known subset, or present in only one. A transaction in two of three sources is
  named — "bank and ledger agree, the processor is missing it" — rather than
  reported as a pair of unrelated two-way mismatches.

* **Reconciliation history** records each run under ``AUTOFLOW_HOME`` and can
  compare two runs, so "did last month's reconciliation get better or worse" has
  an answer. Every run is a dated entry, never an overwrite.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.services.bank_reconciliation.reconciler import (
    _date_or_none,
    _numeric_or_none,
)


class MultiReconciliationError(ValueError):
    """Raised for an N-way reconciliation that cannot be run."""


# ------------------------------------------------------- N-way reconciliation
@dataclass
class Transaction:
    amount: float
    date: Any
    row: int

    def key(self) -> tuple[float, Any]:
        return (round(self.amount, 2), self.date)

    def as_dict(self, label: str = "") -> dict[str, Any]:
        return {
            "source": label,
            "row": self.row,
            "amount": self.amount,
            "date": "" if self.date is None else str(self.date.date()),
        }


@dataclass
class NwayResult:
    sources: list[str]
    matched_everywhere: list[dict[str, Any]] = field(default_factory=list)
    partial: list[dict[str, Any]] = field(default_factory=list)
    unique_to: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    unreadable: dict[str, int] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "sources": self.sources,
            "matched_everywhere": len(self.matched_everywhere),
            "partial": len(self.partial),
            "unique": {name: len(rows) for name, rows in self.unique_to.items()},
            "unreadable": dict(self.unreadable),
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "matched_everywhere": self.matched_everywhere,
            "partial": self.partial,
            "unique_to": self.unique_to,
        }


def reconcile_many(
    sources: dict[str, pd.DataFrame],
    *,
    date_col: str,
    amount_col: str,
    date_tolerance_days: int = 2,
) -> NwayResult:
    """Reconcile any number of statements against each other.

    Each source is consumed at most once per match, and a match is the closest
    available candidate by date, so two same-amount transactions on different
    days do not pair up arbitrarily.
    """
    if len(sources) < 2:
        raise MultiReconciliationError(
            f"N-way reconciliation needs at least 2 sources; got {len(sources)}."
        )

    # Parse each source once, keeping the readable transactions and a count of
    # the ones that could not be parsed (reported, never dropped silently).
    parsed: dict[str, list[Transaction]] = {}
    unreadable: dict[str, int] = {}
    for label, frame in sources.items():
        if date_col not in frame.columns or amount_col not in frame.columns:
            raise MultiReconciliationError(
                f"Source {label!r} has no {date_col!r} or {amount_col!r} column."
            )
        transactions: list[Transaction] = []
        bad = 0
        for index, row in frame.iterrows():
            amount = _numeric_or_none(row[amount_col])
            date = _date_or_none(row[date_col])
            if amount is None or date is None:
                bad += 1
                continue
            transactions.append(Transaction(amount=amount, date=date, row=int(index)))
        parsed[label] = transactions
        unreadable[label] = bad

    labels = list(sources)
    used: dict[str, set[int]] = {label: set() for label in labels}
    groups: list[dict[str, Transaction]] = []

    # The first source drives the search; every other source offers its closest
    # unused candidate within tolerance.
    anchor = labels[0]
    for candidate in parsed[anchor]:
        if candidate.row in used[anchor]:
            continue
        group = {anchor: candidate}
        for label in labels[1:]:
            best: Transaction | None = None
            best_diff: int | None = None
            for other in parsed[label]:
                if other.row in used[label]:
                    continue
                if abs(other.amount - candidate.amount) >= 0.01:
                    continue
                diff = abs((other.date - candidate.date).days)
                if diff <= date_tolerance_days and (best_diff is None or diff < best_diff):
                    best, best_diff = other, diff
            if best is not None:
                group[label] = best
        if len(group) > 1:
            for label, transaction in group.items():
                used[label].add(transaction.row)
            groups.append(group)

    matched_everywhere: list[dict[str, Any]] = []
    partial: list[dict[str, Any]] = []
    unique_to: dict[str, list[dict[str, Any]]] = {label: [] for label in labels}

    for group in groups:
        entry = {
            "amount": round(next(iter(group.values())).amount, 2),
            "date": str(next(iter(group.values())).date.date()),
            "present_in": sorted(group),
            "missing_from": sorted(set(labels) - set(group)),
        }
        if len(group) == len(labels):
            matched_everywhere.append(entry)
        else:
            partial.append(entry)

    for label in labels:
        for transaction in parsed[label]:
            if transaction.row not in used[label]:
                unique_to[label].append(transaction.as_dict(label))

    return NwayResult(
        sources=labels,
        matched_everywhere=matched_everywhere,
        partial=partial,
        unique_to=unique_to,
        unreadable=unreadable,
    )


# ------------------------------------------------------- reconciliation history
def history_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path(__file__).resolve().parents[3]
    return base / "reconciliation_history"


@dataclass
class HistoryEntry:
    recorded_at: str
    label: str
    summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"recorded_at": self.recorded_at, "label": self.label, "summary": self.summary}


def record_reconciliation(
    summary: dict[str, Any], *, label: str = "", path: str | Path | None = None
) -> HistoryEntry:
    """Append a reconciliation summary to the history log."""
    entry = HistoryEntry(
        recorded_at=datetime.now(timezone.utc).isoformat(),
        label=label,
        summary=dict(summary),
    )
    destination = Path(path) if path else history_dir() / "history.jsonl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.as_dict()) + "\n")
    return entry


def read_history(path: str | Path | None = None) -> list[dict[str, Any]]:
    destination = Path(path) if path else history_dir() / "history.jsonl"
    if not destination.exists():
        return []
    entries = []
    with open(destination, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def compare_reconciliations(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """The change in the matched/missing counts between two runs.

    Positive deltas are stated in the direction that helps: more matched is
    good, more missing is bad.
    """
    keys = ["matched", "missing_from_books", "recorded_but_never_cleared"]
    changes = {}
    for key in keys:
        old = float(before.get(key, 0) or 0)
        new = float(after.get(key, 0) or 0)
        changes[key] = {"before": old, "after": new, "delta": new - old}
    matched_delta = changes["matched"]["delta"]
    return {
        "changes": changes,
        "direction": "improving" if matched_delta > 0 else ("declining" if matched_delta < 0 else "flat"),
    }