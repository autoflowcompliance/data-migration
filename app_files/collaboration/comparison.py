"""Before/after comparison: show the buyer exactly what was fixed.

The single most persuasive output for a non-technical buyer is a side-by-side
view where changed cells are highlighted, removed rows are struck through, and
added rows are called out. This module builds that report from the lineage
events the pipeline already records, so it describes changes that actually
happened rather than re-deriving them by diffing and hoping.

``build_comparison(frame, tracker)`` returns a :class:`Comparison` holding the
counts, the per-row detail, and an HTML renderer. The HTML is standalone: no
CDN, no fonts, no scripts.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

CHANGED = "changed"
REMOVED = "removed"
UNCHANGED = "unchanged"


@dataclass
class CellChange:
    """One field that changed on one row."""

    field: str
    before: Any
    after: Any
    action: str

    def as_row(self) -> dict[str, Any]:
        return {"field": self.field, "before": self.before, "after": self.after, "action": self.action}


@dataclass
class RowComparison:
    """How one input row ended up."""

    source_row: int
    target_row: int | None
    status: str
    changes: list[CellChange] = field(default_factory=list)


@dataclass
class Comparison:
    """The full before/after picture."""

    original: pd.DataFrame
    cleaned: pd.DataFrame
    rows: list[RowComparison] = field(default_factory=list)

    @property
    def rows_in(self) -> int:
        return len(self.original)

    @property
    def rows_out(self) -> int:
        return len(self.cleaned)

    @property
    def rows_removed(self) -> int:
        return sum(1 for row in self.rows if row.status == REMOVED)

    @property
    def rows_changed(self) -> int:
        return sum(1 for row in self.rows if row.status == CHANGED)

    @property
    def rows_unchanged(self) -> int:
        return sum(1 for row in self.rows if row.status == UNCHANGED)

    @property
    def cells_changed(self) -> int:
        return sum(len(row.changes) for row in self.rows)

    def summary(self) -> dict[str, Any]:
        return {
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "rows_removed": self.rows_removed,
            "rows_changed": self.rows_changed,
            "rows_unchanged": self.rows_unchanged,
            "cells_changed": self.cells_changed,
        }

    def changes_frame(self) -> pd.DataFrame:
        records = []
        for row in self.rows:
            for change in row.changes:
                records.append(
                    {
                        "source_row": row.source_row,
                        "target_row": row.target_row if row.target_row is not None else "",
                        "status": row.status,
                        **change.as_row(),
                    }
                )
        columns = ["source_row", "target_row", "status", "field", "before", "after", "action"]
        return pd.DataFrame(records, columns=columns)


def build_comparison(original: pd.DataFrame, tracker, cleaned: pd.DataFrame | None = None) -> Comparison:
    """Build a comparison from a lineage tracker's events.

    Row identity is the subtle part. ``source_row`` in an event is an index into
    the *input* frame; ``output_row`` is a label into the *cleaned* frame, and
    dropping a duplicate shifts every later output label by one. Reusing one for
    the other silently mis-attributes changes and can index past the end of the
    cleaned frame.

    So: recover which input rows were dropped from the ``removed_duplicate``
    events, then treat the surviving input rows in order as the output rows.
    That matches what dedup actually does (``drop_duplicates`` preserves order)
    and stays correct without the stripped ``_lineage_id`` column.

    Args:
        original: the frame that went in.
        tracker: a ``LineageTracker`` that was passed to ``run_pipeline``.
        cleaned: the frame that came out.
    """
    if cleaned is None:
        cleaned = getattr(tracker, "output_frame", None) or getattr(tracker, "frame", None)
    if cleaned is None:
        raise ValueError(
            "build_comparison needs the cleaned frame; pass it explicitly when the "
            "tracker does not hold one."
        )

    events = list(getattr(tracker, "events", []))
    original = original.reset_index(drop=True)
    cleaned = cleaned.reset_index(drop=True)

    changes_by_source: dict[int, list[CellChange]] = {}
    removed_sources: set[int] = set()

    for event in events:
        action = str(_get(event, "action", ""))
        source_row = _as_int(_get(event, "source_row", None))
        output_row = _as_int(_get(event, "output_row", None))
        before = _get(event, "before", None)
        after = _get(event, "after", None)
        field_name = str(_get(event, "field", ""))

        if action == "removed_duplicate" or output_row is None:
            removed_sources.add(_id_from_event(source_row, before))
            continue

        key = source_row if source_row is not None else output_row
        changes_by_source.setdefault(key, []).append(
            CellChange(field=field_name, before=before, after=after, action=action)
        )

    removed_sources.discard(-1)
    survivors = [index for index in range(len(original)) if index not in removed_sources]

    rows: list[RowComparison] = []
    for index in range(len(original)):
        if index in removed_sources:
            rows.append(RowComparison(source_row=index, target_row=None, status=REMOVED))
            continue
        position = survivors.index(index) if index in survivors else None
        if position is None or position >= len(cleaned):
            # The output does not have a home for this row. Say so rather than
            # pretending it survived.
            rows.append(RowComparison(source_row=index, target_row=None, status=REMOVED))
            continue
        changes = [c for c in changes_by_source.get(index, []) if not _same(c.before, c.after)]
        status = CHANGED if changes else UNCHANGED
        rows.append(RowComparison(source_row=index, target_row=position, status=status, changes=changes))

    return Comparison(original=original, cleaned=cleaned, rows=rows)


def _id_from_event(source_row: int | None, before: Any) -> int:
    """Recover a dropped row's original index.

    Dropped-row events carry ``source_row=None`` when the tracker was given an
    id column, but the original index is preserved in the event's ``before``
    text ("row 3"). Parse it rather than losing the row from the report.
    """
    if source_row is not None:
        return source_row
    text = str(before)
    if text.startswith("row "):
        parsed = _as_int(text[4:])
        if parsed is not None:
            return parsed
    return -1


def _get(event: Any, key: str, default: Any) -> Any:
    if isinstance(event, dict):
        return event.get(key, default)
    return getattr(event, key, default)


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _same(left: Any, right: Any) -> bool:
    left_blank = left is None or str(left).strip() in {"", "nan", "None"}
    right_blank = right is None or str(right).strip() in {"", "nan", "None"}
    if left_blank and right_blank:
        return True
    return str(left).strip() == str(right).strip()


# ------------------------------------------------------------------- HTML
_STYLE = """
/* Warm Editorial, matching the app: paper page, surface cards, ink text. */
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
     margin:0;padding:24px;color:#2B2420;background:#F5F0E6;}
h1{font-size:20px;margin:0 0 4px;font-family:Georgia,'Times New Roman',serif;}
h2{font-size:15px;margin:24px 0 8px;}
.wrap{max-width:1100px;margin:0 auto;}
.note{color:#6B6255;font-size:13px;margin:0 0 16px;}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0;}
.card{background:#FDFBF7;border:1px solid #E4DCC8;border-radius:8px;padding:12px 16px;min-width:110px;}
.card .n{font-size:22px;font-weight:700;}
.card .l{font-size:12px;color:#6B6255;text-transform:uppercase;letter-spacing:.04em;}
table{border-collapse:collapse;width:100%;background:#FDFBF7;font-size:13px;
      border:1px solid #E4DCC8;border-radius:8px;overflow:hidden;}
th,td{border-bottom:1px solid #E4DCC8;padding:6px 8px;text-align:left;vertical-align:top;}
th{background:#F5F0E6;font-weight:600;position:sticky;top:0;color:#2B2420;}
tr.removed td{background:#F3DEDA;color:#7F2A22;text-decoration:line-through;}
tr.changed td{background:#FDFBF7;}
td.changed{background:#F3E3D0;font-weight:600;}
.badge{display:inline-block;font-size:11px;padding:1px 6px;border-radius:10px;font-weight:600;}
.b-removed{background:#F3DEDA;color:#8F362C;}
.b-changed{background:#F3E3D0;color:#8A5420;}
.b-unchanged{background:#E4DCC8;color:#3A322B;}
.reason{font-size:11px;color:#6B6255;}
"""


def render_comparison_html(comparison: Comparison, title: str = "What changed") -> str:
    """Render a standalone side-by-side report. No external resources."""
    summary = comparison.summary()
    columns = list(comparison.original.columns)
    fields = list(comparison.cleaned.columns)
    show = list(dict.fromkeys([*columns, *fields]))

    by_source = {row.source_row: row for row in comparison.rows}

    header = (
        "<tr><th>Row</th><th>Status</th>"
        + "".join(f"<th>{html.escape(str(c))}<div class='reason'>before → after</div></th>" for c in show)
        + "</tr>"
    )

    body_rows = []
    for index in range(len(comparison.original)):
        comparison_row = by_source.get(index)
        status = comparison_row.status if comparison_row else UNCHANGED
        changed_fields = {c.field: c for c in (comparison_row.changes if comparison_row else [])}
        cells = []
        for column in show:
            before = comparison.original.iloc[index][column] if column in comparison.original.columns else ""
            change = changed_fields.get(column)
            if comparison_row and status == REMOVED:
                after = "—"
            else:
                after = (
                    comparison.cleaned.iloc[comparison_row.target_row][column]
                    if comparison_row and comparison_row.target_row is not None
                    and column in comparison.cleaned.columns
                    else before
                )
            changed_class = " class='changed'" if change else ""
            cells.append(
                f"<td{changed_class}>{html.escape(str(before))}"
                f"<div class='reason'>{html.escape(str(after))}</div></td>"
            )
        badge = {
            REMOVED: "<span class='badge b-removed'>removed</span>",
            CHANGED: "<span class='badge b-changed'>changed</span>",
            UNCHANGED: "<span class='badge b-unchanged'>unchanged</span>",
        }.get(status, "")
        body_rows.append(
            f"<tr class='{status}'><td>{index}</td><td>{badge}</td>{''.join(cells)}</tr>"
        )

    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>{_STYLE}</style></head><body><div class='wrap'>"
        f"<h1>{html.escape(title)}</h1>"
        "<p class='note'>Left value is the original; the grey line beneath is the cleaned value. "
        "Amber cells changed. Removed rows are struck through.</p>"
        "<div class='cards'>"
        f"<div class='card'><div class='n'>{summary['rows_in']}</div><div class='l'>rows in</div></div>"
        f"<div class='card'><div class='n'>{summary['rows_out']}</div><div class='l'>rows out</div></div>"
        f"<div class='card'><div class='n'>{summary['rows_removed']}</div><div class='l'>removed</div></div>"
        f"<div class='card'><div class='n'>{summary['rows_changed']}</div><div class='l'>changed</div></div>"
        f"<div class='card'><div class='n'>{summary['cells_changed']}</div><div class='l'>cells changed</div></div>"
        "</div>"
        "<h2>Before and after, row by row</h2>"
        f"<table>{header}{''.join(body_rows)}</table>"
        "</div></body></html>"
    )


def changed_cell_count(comparison: Comparison) -> int:
    return comparison.cells_changed