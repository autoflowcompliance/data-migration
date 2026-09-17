"""Row-level lineage tracking.

Records every transformation as a flat event row:

    source_row, output_row, field, before, after, action

The tracker is deliberately a passive observer. It does not perform the
transformation — it is told what changed — which keeps it usable from the
cleaner, the mapper and the pipeline without any of them depending on it.

Row identity is tracked with a synthetic ``_lineage_id`` column rather than
DataFrame position, because cleaning drops and reorders rows. Each event can
therefore be traced back to the original source row even after dedup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

LINEAGE_ID = "_lineage_id"
EVENT_COLUMNS = ["source_row", "output_row", "field", "before", "after", "action"]


@dataclass
class LineageEvent:
    source_row: int | None
    output_row: int | None
    field: str
    before: Any
    after: Any
    action: str

    def as_row(self) -> dict[str, Any]:
        return {
            "source_row": self.source_row,
            "output_row": self.output_row,
            "field": self.field,
            "before": _stringify(self.before),
            "after": _stringify(self.after),
            "action": self.action,
        }


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    return str(value)


@dataclass
class LineageTracker:
    """Accumulates transformation events for one pipeline run."""

    events: list[LineageEvent] = field(default_factory=list)
    enabled: bool = True

    def record(
        self,
        *,
        field_name: str,
        before: Any,
        after: Any,
        action: str,
        source_row: int | None = None,
        output_row: int | None = None,
    ) -> None:
        """Record one transformation of one value."""
        if not self.enabled:
            return
        if _stringify(before) == _stringify(after):
            return
        self.events.append(
            LineageEvent(
                source_row=source_row,
                output_row=output_row,
                field=field_name,
                before=before,
                after=after,
                action=action,
            )
        )

    def record_frame_diff(
        self,
        before: pd.DataFrame,
        after: pd.DataFrame,
        field_name: str,
        action: str,
        id_column: str | None = None,
    ) -> int:
        """Record every changed cell in ``field_name`` between two frames.

        Matching is by ``_lineage_id`` when present (survives dedup/reorder),
        otherwise by position. Returns the number of events recorded.
        """
        if not self.enabled or field_name not in before.columns or field_name not in after.columns:
            return 0

        if id_column and id_column in before.columns and id_column in after.columns:
            lookup = {
                row[id_column]: (index, row[field_name])
                for index, row in before.iterrows()
            }
            pairs = []
            for output_index, row in after.iterrows():
                source = lookup.get(row[id_column])
                if source is None:
                    continue
                pairs.append((source[0], source[1], output_index, row[field_name]))
        else:
            limit = min(len(before), len(after))
            pairs = [
                (i, before[field_name].iloc[i], i, after[field_name].iloc[i])
                for i in range(limit)
            ]

        count = 0
        for source_index, before_value, output_index, after_value in pairs:
            if _stringify(before_value) == _stringify(after_value):
                continue
            self.record(
                field_name=field_name,
                before=before_value,
                after=after_value,
                action=action,
                source_row=int(source_index),
                output_row=int(output_index),
            )
            count += 1
        return count

    def record_removed_rows(
        self, frame: pd.DataFrame, removed_ids: list[Any], action: str = "removed_duplicate"
    ) -> None:
        """Record rows that were dropped, so nothing vanishes untraceably."""
        if not self.enabled or not removed_ids:
            return
        id_column = LINEAGE_ID if LINEAGE_ID in frame.columns else None
        for removed_id in removed_ids:
            source_row = int(removed_id) if not id_column else None
            self.record(
                field_name="*",
                before=f"row {removed_id}",
                after="",
                action=action,
                source_row=source_row,
            )

    @property
    def total_events(self) -> int:
        return len(self.events)

    def to_frame(self) -> pd.DataFrame:
        """The whole log as a DataFrame, ready for CSV output."""
        if not self.events:
            return pd.DataFrame(columns=EVENT_COLUMNS)
        frame = pd.DataFrame([event.as_row() for event in self.events], columns=EVENT_COLUMNS)
        # Nullable integer keeps dropped-row events readable as blank rather
        # than "NaN"/"1.0" in the CSV.
        for column in ("source_row", "output_row"):
            frame[column] = frame[column].astype("Int64")
        return frame

    def events_for_output_row(self, output_row: int) -> pd.DataFrame:
        """Every event that produced a given output row — the trace-back query."""
        frame = self.to_frame()
        if frame.empty:
            return frame
        return frame[frame["output_row"] == output_row]

    def actions(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self.events:
            counts[event.action] = counts.get(event.action, 0) + 1
        return counts


def attach_lineage_ids(frame: pd.DataFrame) -> pd.DataFrame:
    """Add a stable ``_lineage_id`` column recording the original row position."""
    frame = frame.copy()
    frame[LINEAGE_ID] = range(len(frame))
    return frame


def strip_lineage_ids(frame: pd.DataFrame) -> pd.DataFrame:
    """Remove the helper column before output."""
    if LINEAGE_ID in frame.columns:
        return frame.drop(columns=[LINEAGE_ID])
    return frame