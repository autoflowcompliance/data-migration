"""Layer 7 — reconciliation beyond two files.

The frozen matcher compares a bank statement to a ledger on amount plus a date
window. That covers the common case and nothing else. Buyers arrive with a third
feed (a payment processor, a card acquirer), and with match logic that is not
"amount and date" — a reference and an amount, or a weighted blend where a
reference hit can excuse a date that is a few days out.

This module adds both, without touching the two-file matcher:

- ``MatchStrategy`` describes how rows are compared, as data. Components carry a
  weight, and a pair matches when the passing weight reaches a threshold. The
  default — amount and date, both required — reproduces the two-file behaviour.
- ``reconcile_multiway`` matches three or more sources at once. Its two-source
  case is the existing engine's job, and the tests assert the two agree.
- ``ReconciliationHistory`` records every run so a month can be compared to the
  one before it.

Sources are named. The first source given is the anchor: every group is built
around one of its rows, and a group counts as matched only when *every* source
contributes a row. A row that matches in some sources but not all is reported
per source as unmatched, with the partial group recorded, because "it matched
two of three feeds" is exactly the fact a reconciliation is looking for.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

AMOUNT = "amount"
DATE = "date"
REFERENCE = "reference"
TEXT = "text"
COMPONENT_TYPES = (AMOUNT, DATE, REFERENCE, TEXT)


class MatchStrategyError(ValueError):
    """Raised when a match strategy is malformed."""


def _as_amount(value: Any) -> float | None:
    from app_files.services.bank_reconciliation.reconciler import clean_currency_amount

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    return clean_currency_amount(text)


def _as_date(value: Any) -> pd.Timestamp | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if parsed is None or pd.isna(parsed):
        return None
    return parsed


def _normalise_text(value: Any) -> str:
    return str(value or "").strip().casefold()


@dataclass
class MatchComponent:
    """One way two rows can agree."""

    type: str
    column: str
    weight: float = 1.0
    tolerance: float = 0.01
    date_window_days: int = 2

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MatchComponent:
        if not isinstance(data, dict):
            raise MatchStrategyError(
                f"Each match component must be a mapping, got {type(data).__name__}"
            )
        component_type = str(data.get("type", "")).strip().lower()
        if component_type not in COMPONENT_TYPES:
            raise MatchStrategyError(
                f"Unknown match component type {component_type!r}. "
                f"Allowed: {', '.join(COMPONENT_TYPES)}"
            )
        column = str(data.get("column", "")).strip()
        if not column:
            raise MatchStrategyError(f"Match component {component_type!r} needs a 'column'")
        weight = float(data.get("weight", 1.0))
        if weight <= 0:
            raise MatchStrategyError(
                f"Match component on {column!r} has non-positive weight {weight}"
            )
        window = data.get("date_window_days", data.get("window_days", 2))
        return cls(
            type=component_type,
            column=column,
            weight=weight,
            tolerance=float(data.get("tolerance", 0.01)),
            date_window_days=int(window) if window is not None else 2,
        )

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": self.type,
            "column": self.column,
            "weight": self.weight,
        }
        if self.type == AMOUNT:
            payload["tolerance"] = self.tolerance
        if self.type == DATE:
            payload["date_window_days"] = self.date_window_days
        return payload


@dataclass
class MatchStrategy:
    """How two rows are compared, and when the comparison counts as a match."""

    name: str = "amount_and_date"
    components: list[MatchComponent] = field(default_factory=list)
    threshold: float = 1.0

    @classmethod
    def amount_and_date(
        cls, amount_column: str = "amount", date_column: str = "date",
        date_window_days: int = 2,
    ) -> MatchStrategy:
        """The frozen matcher's logic, expressed as a strategy."""
        return cls(
            name="amount_and_date",
            components=[
                MatchComponent(AMOUNT, amount_column, 1.0),
                MatchComponent(DATE, date_column, 1.0, date_window_days=date_window_days),
            ],
            threshold=2.0,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MatchStrategy:
        if not isinstance(data, dict):
            raise MatchStrategyError("A match strategy must be a mapping")
        raw = data.get("components")
        if not isinstance(raw, list) or not raw:
            raise MatchStrategyError("A match strategy needs a non-empty 'components' list")
        components = [MatchComponent.from_dict(item) for item in raw]
        columns = [component.column for component in components]
        if len(set(columns)) != len(columns):
            # Two components on one column would double its weight silently.
            raise MatchStrategyError(
                f"A match strategy cannot use a column twice: {', '.join(columns)}"
            )
        total = sum(component.weight for component in components)
        threshold = float(data.get("threshold", total))
        if not 0 < threshold <= total + 1e-9:
            raise MatchStrategyError(
                f"threshold {threshold} must be above zero and at most the total "
                f"component weight {total}"
            )
        return cls(
            name=str(data.get("name", "strategy")),
            components=components,
            threshold=threshold,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "threshold": self.threshold,
            "components": [component.as_dict() for component in self.components],
        }

    def score(self, left: pd.Series, right: pd.Series) -> tuple[float, list[str]]:
        """Weighted score for a candidate pair, plus which components agreed."""
        total = 0.0
        agreed: list[str] = []
        for component in self.components:
            if _component_agrees(component, left, right):
                total += component.weight
                agreed.append(f"{component.type}:{component.column}")
        return total, agreed

    def matches(self, left: pd.Series, right: pd.Series) -> bool:
        score, _ = self.score(left, right)
        return score + 1e-9 >= self.threshold


@dataclass(frozen=True)
class MatchGroup:
    """One reconciled group: one row per source, all describing the same event."""

    rows: dict[str, int]
    score: float
    agreed: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "rows": dict(self.rows),
            "score": self.score,
            "agreed": list(self.agreed),
        }


@dataclass
class MultiwayResult:
    """Outcome of matching three or more sources at once."""

    sources: list[str]
    groups: list[MatchGroup] = field(default_factory=list)
    unmatched: dict[str, pd.DataFrame] = field(default_factory=dict)
    partial: list[dict[str, Any]] = field(default_factory=list)
    strategy: str = ""

    @property
    def matched_groups(self) -> int:
        return len(self.groups)

    def unmatched_counts(self) -> dict[str, int]:
        return {name: int(len(frame)) for name, frame in self.unmatched.items()}

    def summary(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "sources": list(self.sources),
            "matched_groups": self.matched_groups,
            "unmatched": self.unmatched_counts(),
            "partial_groups": len(self.partial),
        }

    def render(self) -> str:
        lines = [
            "Reconciliation",
            "=" * 60,
            f"Strategy: {self.strategy}",
            f"Sources: {', '.join(self.sources)}",
            f"Matched groups: {self.matched_groups}",
            "",
            "Unmatched per source:",
        ]
        for name in self.sources:
            lines.append(f"  {name}: {self.unmatched_counts().get(name, 0)}")
        if self.partial:
            lines.append("")
            lines.append(f"Partial groups (matched in some sources, not all): {len(self.partial)}")
        return "\n".join(lines)


def _component_agrees(component: MatchComponent, left: pd.Series, right: pd.Series) -> bool:
    left_value = left.get(component.column)
    right_value = right.get(component.column)
    if component.type == AMOUNT:
        left_amount = _as_amount(left_value)
        right_amount = _as_amount(right_value)
        if left_amount is None or right_amount is None:
            return False
        return abs(left_amount - right_amount) <= component.tolerance
    if component.type == DATE:
        left_date = _as_date(left_value)
        right_date = _as_date(right_value)
        if left_date is None or right_date is None:
            return False
        return abs((left_date - right_date).days) <= component.date_window_days
    if component.type == REFERENCE:
        left_text = _normalise_text(left_value)
        return bool(left_text) and left_text == _normalise_text(right_value)
    left_text = _normalise_text(left_value)
    return bool(left_text) and left_text == _normalise_text(right_value)


def reconcile_multiway(
    datasets: dict[str, pd.DataFrame],
    strategy: MatchStrategy,
) -> MultiwayResult:
    """Match three or more sources at once, anchored on the first.

    A group is matched only when every source contributes a row. A partial
    group — matched in some sources, not all — is recorded in ``partial`` and
    its rows stay in the per-source ``unmatched`` frames, because a row that
    matched two of three feeds still needs a human to look at it.
    """
    if len(datasets) < 2:
        raise ValueError("reconcile_multiway needs at least two sources")
    sources = list(datasets)
    frames = {name: frame.reset_index(drop=True) for name, frame in datasets.items()}
    used: dict[str, set[int]] = {name: set() for name in sources}
    anchor = sources[0]
    others = sources[1:]

    result = MultiwayResult(sources=sources, strategy=strategy.name)

    for anchor_index in range(len(frames[anchor])):
        if anchor_index in used[anchor]:
            continue
        anchor_row = frames[anchor].iloc[anchor_index]
        chosen: dict[str, tuple[int, float, list[str]]] = {}
        for name in others:
            best: tuple[int, float, list[str]] | None = None
            for candidate_index in range(len(frames[name])):
                if candidate_index in used[name]:
                    continue
                score, agreed = strategy.score(anchor_row, frames[name].iloc[candidate_index])
                if score + 1e-9 < strategy.threshold:
                    continue
                if best is None or score > best[1] or (
                    score == best[1] and candidate_index < best[0]
                ):
                    best = (candidate_index, score, agreed)
            if best is not None:
                chosen[name] = best

        if not chosen:
            continue
        if set(chosen) != set(others):
            # The row matched in some sources and not others. That is the fact
            # a reconciliation is looking for, so record it; the row stays in
            # the per-source unmatched frames for a human to resolve.
            result.partial.append(
                {
                    "anchor_row": anchor_index,
                    "matched_rows": {anchor: anchor_index,
                                     **{name: index for name, (index, _, _) in chosen.items()}},
                    "missing_sources": sorted(set(others) - set(chosen)),
                }
            )
            continue

        rows = {anchor: anchor_index}
        agreed_names: list[str] = []
        lowest = float("inf")
        for name, (index, score, agreed) in chosen.items():
            rows[name] = index
            agreed_names.extend(agreed)
            lowest = min(lowest, score)

        used[anchor].add(anchor_index)
        for name, (index, _, _) in chosen.items():
            used[name].add(index)
        result.groups.append(
            MatchGroup(rows=rows, score=lowest, agreed=tuple(sorted(set(agreed_names))))
        )

    result.unmatched = {
        name: frames[name].loc[[i for i in range(len(frames[name])) if i not in used[name]]]
        .reset_index(drop=True)
        for name in sources
    }
    return result


def compare_two_way(
    bank_bytes: bytes | None = None,
    ledger_bytes: bytes | None = None,
    *,
    bank: pd.DataFrame | None = None,
    ledger: pd.DataFrame | None = None,
    bank_date_col: str = "date",
    bank_amount_col: str = "amount",
    ledger_date_col: str = "date",
    ledger_amount_col: str = "amount",
    date_tolerance_days: int = 2,
) -> MultiwayResult:
    """Run the two-source case through :func:`reconcile_multiway`.

    Lets the tests assert the multiway engine agrees with the frozen matcher on
    the same input, rather than asserting against a second implementation.
    """
    if bank is None or ledger is None:
        if bank_bytes is None or ledger_bytes is None:
            raise ValueError("Provide either raw bytes or both frames")
        from app_files.services.bank_reconciliation.reconciler import run_reconciliation

        if bank_bytes is not None and ledger_bytes is not None:
            raw = run_reconciliation(
                bank_bytes, ledger_bytes, bank_date_col, bank_amount_col,
                ledger_date_col, ledger_amount_col, date_tolerance_days,
            )
            bank = raw["bank_only"].copy()
            ledger = raw["ledger_only"].copy()

    assert bank is not None and ledger is not None
    strategy = MatchStrategy.amount_and_date(
        bank_amount_col, bank_date_col, date_tolerance_days
    )
    # Column names must line up across both frames for a shared strategy, so
    # rename each side's columns to a common role name.
    left = bank.rename(columns={bank_amount_col: "amount", bank_date_col: "date"})
    right = ledger.rename(columns={ledger_amount_col: "amount", ledger_date_col: "date"})
    return reconcile_multiway({"bank": left, "ledger": right}, strategy)


def history_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "reconciliation_history"


@dataclass
class ReconciliationRun:
    """One recorded reconciliation, for month-over-month comparison."""

    name: str
    run_at: str
    summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "run_at": self.run_at, "summary": dict(self.summary)}

    @property
    def matched(self) -> int:
        return int(self.summary.get("matched_groups", 0))

    @property
    def unmatched_total(self) -> int:
        return int(sum(self.summary.get("unmatched", {}).values()))

    def month(self) -> str:
        return self.run_at[:7]


class ReconciliationHistory:
    """Persisted record of every reconciliation run, under ``AUTOFLOW_HOME``."""

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else history_dir()

    def _path(self, name: str) -> Path:
        keep = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
        return self.root / f"{keep or 'recon'}.json"

    def record(
        self, name: str, result: MultiwayResult, run_at: str | None = None
    ) -> ReconciliationRun:
        entry = ReconciliationRun(
            name=name,
            run_at=run_at or datetime.now(timezone.utc).isoformat(),
            summary=result.summary(),
        )
        runs = self.runs(name)
        runs.append(entry)
        self._path(name).parent.mkdir(parents=True, exist_ok=True)
        self._path(name).write_text(
            json.dumps({"runs": [run.as_dict() for run in runs]}, indent=2),
            encoding="utf-8",
        )
        return entry

    def runs(self, name: str) -> list[ReconciliationRun]:
        path = self._path(name)
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [
            ReconciliationRun(
                name=str(item.get("name", name)),
                run_at=str(item.get("run_at", "")),
                summary=dict(item.get("summary", {})),
            )
            for item in payload.get("runs", [])
        ]

    def compare_months(self, name: str) -> dict[str, Any]:
        """Month-over-month matched and unmatched movement, by calendar month."""
        by_month: dict[str, list[ReconciliationRun]] = {}
        for run in self.runs(name):
            by_month.setdefault(run.month(), []).append(run)
        months = sorted(by_month)
        series: list[dict[str, Any]] = [
            {
                "month": month,
                "runs": len(by_month[month]),
                "matched": sum(run.matched for run in by_month[month]),
                "unmatched": sum(run.unmatched_total for run in by_month[month]),
            }
            for month in months
        ]
        deltas: list[dict[str, Any]] = []
        for previous, current in zip(series, series[1:], strict=False):
            deltas.append(
                {
                    "from_month": previous["month"],
                    "to_month": current["month"],
                    "matched_delta": int(current["matched"]) - int(previous["matched"]),
                    "unmatched_delta": int(current["unmatched"]) - int(previous["unmatched"]),
                }
            )
        return {"name": name, "months": series, "deltas": deltas}

    def render_trend(self, name: str) -> str:
        report = self.compare_months(name)
        lines = [f"Reconciliation history: {name}", "=" * 60]
        for month in report["months"]:
            lines.append(
                f"{month['month']}: {month['runs']} run(s), "
                f"{month['matched']} matched, {month['unmatched']} unmatched"
            )
        for delta in report["deltas"]:
            lines.append(
                f"{delta['from_month']} -> {delta['to_month']}: "
                f"matched {delta['matched_delta']:+d}, "
                f"unmatched {delta['unmatched_delta']:+d}"
            )
        return "\n".join(lines)


__all__ = [
    "AMOUNT",
    "COMPONENT_TYPES",
    "DATE",
    "REFERENCE",
    "TEXT",
    "MatchComponent",
    "MatchGroup",
    "MatchStrategy",
    "MatchStrategyError",
    "MultiwayResult",
    "ReconciliationHistory",
    "ReconciliationRun",
    "compare_two_way",
    "history_dir",
    "reconcile_multiway",
]
