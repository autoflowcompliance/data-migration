"""Reconciliation dashboard (Utility 5).

One screen for a complete reconciliation: matched, missing from the books,
never cleared, date drift, and total variance. The matching itself is done by
the existing ``reconcile_transactions`` service; this module turns its result
into the numbers a bookkeeper reads first and a standalone HTML dashboard.

Variance is computed here because the service deliberately does not do it: it
matches and reports, and leaves the money arithmetic to the presentation layer.
``variance`` is the sum of the unmatched bank amounts minus the sum of the
unmatched ledger amounts — the figure that explains a difference between the
bank balance and the books.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ReconciliationSummary:
    """The headline numbers."""

    bank_transactions: int = 0
    ledger_transactions: int = 0
    matched: int = 0
    missing_from_books: int = 0
    never_cleared: int = 0
    date_drift: int = 0
    """Matched pairs whose dates differ but within tolerance."""
    total_variance: float = 0.0
    bank_duplicates_removed: int = 0
    ledger_duplicates_removed: int = 0
    match_rate: float = 0.0
    tolerance_days: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "bank_transactions": self.bank_transactions,
            "ledger_transactions": self.ledger_transactions,
            "matched": self.matched,
            "missing_from_books": self.missing_from_books,
            "never_cleared": self.never_cleared,
            "date_drift": self.date_drift,
            "total_variance": round(self.total_variance, 2),
            "match_rate": round(self.match_rate, 1),
            "tolerance_days": self.tolerance_days,
            "bank_duplicates_removed": self.bank_duplicates_removed,
            "ledger_duplicates_removed": self.ledger_duplicates_removed,
        }


@dataclass
class Dashboard:
    summary: ReconciliationSummary
    missing_from_books: pd.DataFrame = field(default_factory=pd.DataFrame)
    never_cleared: pd.DataFrame = field(default_factory=pd.DataFrame)
    matched_pairs: pd.DataFrame = field(default_factory=pd.DataFrame)

    def status(self) -> str:
        if self.summary.missing_from_books or self.summary.never_cleared:
            return "differences found"
        return "fully reconciled"


def _amount_sum(frame: pd.DataFrame, column: str | None) -> float:
    if frame is None or frame.empty or not column or column not in frame.columns:
        return 0.0
    total = 0.0
    for value in frame[column]:
        try:
            total += float(value)
        except (TypeError, ValueError):
            continue
    return total


def build_dashboard(
    result: dict[str, Any],
    amount_column: str,
    tolerance_days: int = 2,
) -> Dashboard:
    """Turn a ``run_reconciliation`` result into the dashboard view."""
    raw_summary = result.get("summary", {})
    missing = result.get("bank_only", pd.DataFrame())
    never = result.get("ledger_only", pd.DataFrame())
    matches = result.get("matches", []) or []

    drift = sum(1 for match in matches if int(match.get("date_diff_days", 0)) != 0)

    summary = ReconciliationSummary(
        bank_transactions=int(raw_summary.get("bank_transactions", 0)),
        ledger_transactions=int(raw_summary.get("ledger_transactions", 0)),
        matched=int(raw_summary.get("matched", len(matches))),
        missing_from_books=int(raw_summary.get("missing_from_books", len(missing))),
        never_cleared=int(raw_summary.get("recorded_but_never_cleared", len(never))),
        date_drift=drift,
        bank_duplicates_removed=int(raw_summary.get("bank_duplicates_removed", 0)),
        ledger_duplicates_removed=int(raw_summary.get("ledger_duplicates_removed", 0)),
        tolerance_days=tolerance_days,
        total_variance=_amount_sum(missing, amount_column) - _amount_sum(never, amount_column),
    )
    if summary.bank_transactions:
        summary.match_rate = summary.matched / summary.bank_transactions * 100

    pairs = pd.DataFrame(matches) if matches else pd.DataFrame(
        columns=["bank_row", "ledger_row", "amount", "date_diff_days"]
    )
    return Dashboard(
        summary=summary,
        missing_from_books=missing if missing is not None else pd.DataFrame(),
        never_cleared=never if never is not None else pd.DataFrame(),
        matched_pairs=pairs,
    )


_DASH_STYLE = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;
     background:#F5F0E6;color:#2B2420;}
.wrap{max-width:1100px;margin:0 auto;padding:28px;}
h1{font-size:22px;margin:0 0 4px;font-family:Georgia,'Times New Roman',serif;}
h2{font-size:15px;margin:26px 0 10px;text-transform:uppercase;letter-spacing:.05em;color:#6B6255;}
.cards{display:flex;gap:12px;flex-wrap:wrap;}
.card{border-radius:8px;padding:14px 18px;min-width:130px;color:#FDFBF7;
      border:1px solid rgba(43,36,32,.12);}
.card .n{font-size:26px;font-weight:800;}
.card .l{font-size:11px;text-transform:uppercase;letter-spacing:.05em;opacity:.9;}
/* Warm Editorial: amber/teal/slate from the app palette, not the old
   green/red/orange, so an embedded dashboard matches the page around it. */
.green{background:#2C7A6B;}.red{background:#B3392F;}.orange{background:#C97A2E;}
.yellow{background:#C97A2E;}.slate{background:#6B6255;}
table{border-collapse:collapse;width:100%;background:#FDFBF7;font-size:13px;
      border:1px solid #E4DCC8;border-radius:8px;overflow:hidden;margin-bottom:8px;}
th,td{border-bottom:1px solid #E4DCC8;padding:6px 8px;text-align:left;}
th{background:#F5F0E6;font-weight:600;color:#2B2420;}
td{color:#3A322B;}
.empty{color:#6B6255;font-size:13px;background:#FDFBF7;border:1px solid #E4DCC8;
       border-radius:8px;padding:12px 16px;}
.foot{margin-top:22px;font-size:12px;color:#6B6255;}
"""


def _cards(summary: ReconciliationSummary) -> str:
    cards = [
        ("green", summary.matched, "matched"),
        ("red", summary.missing_from_books, "missing from books"),
        ("orange", summary.never_cleared, "never cleared"),
        ("yellow", summary.date_drift, "date drift"),
        ("slate", f"{summary.total_variance:,.2f}", "total variance"),
    ]
    return "".join(
        f"<div class='card {colour}'><div class='n'>{value}</div><div class='l'>{label}</div></div>"
        for colour, value, label in cards
    )


def _table(frame: pd.DataFrame, limit: int = 100) -> str:
    if frame is None or frame.empty:
        return "<p class='empty'>None.</p>"
    shown = frame.head(limit)
    header = "".join(f"<th>{html.escape(str(c))}</th>" for c in shown.columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>"
        for row in shown.itertuples(index=False)
    )
    extra = (
        f"<p class='foot'>Showing {len(shown)} of {len(frame)} rows.</p>"
        if len(frame) > limit else ""
    )
    return f"<table><tr>{header}</tr>{body}</table>{extra}"


def render_dashboard_html(dashboard: Dashboard, title: str = "Reconciliation") -> str:
    """A standalone reconciliation dashboard. No external resources."""
    summary = dashboard.summary
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>{_DASH_STYLE}</style></head><body><div class='wrap'>"
        f"<h1>{html.escape(title)}</h1>"
        f"<p class='foot'>{dashboard.status()} · match rate {summary.match_rate:.1f}% · "
        f"{summary.bank_transactions} bank lines vs {summary.ledger_transactions} ledger lines · "
        f"±{summary.tolerance_days} day tolerance</p>"
        f"<div class='cards'>{_cards(summary)}</div>"
        "<h2>Missing from the books</h2>"
        f"{_table(dashboard.missing_from_books)}"
        "<h2>Recorded but never cleared</h2>"
        f"{_table(dashboard.never_cleared)}"
        "<h2>Matched pairs</h2>"
        f"{_table(dashboard.matched_pairs, limit=50)}"
        "<p class='foot'>This report finds discrepancies. Resolving them is the "
        "bookkeeper's judgement, not the tool's.</p>"
        "</div></body></html>"
    )


def write_dashboard_html(dashboard: Dashboard, path: str, title: str = "Reconciliation") -> str:
    from pathlib import Path

    target = Path(path)
    if target.suffix.lower() not in {".html", ".htm"}:
        target = target.with_suffix(".html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_dashboard_html(dashboard, title=title), encoding="utf-8")
    return str(target)


def dashboard_frame(dashboard: Dashboard) -> pd.DataFrame:
    """The summary as a one-row frame, for CSV output."""
    return pd.DataFrame([dashboard.summary.as_dict()])