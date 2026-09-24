"""Blast radius: what a proposed change would affect, before it is applied.

Change a mapping, a rule or a cleaning flag and something downstream moves. This
answers "what exactly" by diffing the mapping log against a proposed one, or by
reading the lineage graph for the fields a source column feeds.

It is deliberately read-only: it reports impact, it does not apply anything.

    before = map_data(source, current_config)
    after = map_data(source, proposed_config)
    radius = blast_radius(before, after)
    radius.affected_targets      # ['email', 'phone']
    radius.changed_source_columns # ['Email Address']
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.lineage.graph import LineageGraph


@dataclass
class Impact:
    """One target field whose behaviour changes."""

    target_field: str
    before_source: str
    after_source: str
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_field": self.target_field,
            "before_source": self.before_source,
            "after_source": self.after_source,
            "reason": self.reason,
        }


@dataclass
class BlastRadius:
    impacts: list[Impact] = field(default_factory=list)
    added_targets: list[str] = field(default_factory=list)
    removed_targets: list[str] = field(default_factory=list)

    @property
    def affected_targets(self) -> list[str]:
        ordered = [impact.target_field for impact in self.impacts]
        return ordered + [target for target in self.added_targets if target not in ordered]

    @property
    def changed_source_columns(self) -> list[str]:
        columns: set[str] = set()
        for impact in self.impacts:
            for source in (impact.before_source, impact.after_source):
                if source:
                    columns.add(source)
        return sorted(columns)

    @property
    def is_empty(self) -> bool:
        return not self.impacts and not self.added_targets and not self.removed_targets

    def summary(self) -> dict[str, Any]:
        return {
            "affected_targets": self.affected_targets,
            "changed_source_columns": self.changed_source_columns,
            "added_targets": self.added_targets,
            "removed_targets": self.removed_targets,
            "impact_count": len(self.impacts),
        }

    def render_html(self) -> str:
        if self.is_empty:
            return "<div class='blast-radius'><p>No impact: this change affects nothing.</p></div>"
        rows = "".join(
            "<tr>"
            f"<td>{impact.target_field}</td>"
            f"<td>{impact.before_source or '—'}</td>"
            f"<td>{impact.after_source or '—'}</td>"
            f"<td>{impact.reason}</td>"
            "</tr>"
            for impact in self.impacts
        )
        return (
            "<div class='blast-radius'>"
            f"<p>{len(self.impacts)} target field(s) affected.</p>"
            "<table><thead><tr><th>Target</th><th>Before</th><th>After</th>"
            f"<th>Reason</th></tr></thead><tbody>{rows}</tbody></table>"
            "</div>"
        )


def _mapping_index(result) -> dict[str, tuple[str, str]]:
    """``{target_field: (source_column, transform)}`` from a MappingResult."""
    index: dict[str, tuple[str, str]] = {}
    for row in result.mapping_log().to_dict("records"):
        target = str(row.get("target_field") or "")
        if not target:
            continue
        index[target] = (
            str(row.get("source_column") or ""),
            str(row.get("transform") or ""),
        )
    return index


def blast_radius(before, after) -> BlastRadius:
    """Diff two ``MappingResult``\\s and report every target that changed."""
    before_index = _mapping_index(before)
    after_index = _mapping_index(after)
    impacts: list[Impact] = []
    for target in sorted(set(before_index) | set(after_index)):
        before_source, before_transform = before_index.get(target, ("", ""))
        after_source, after_transform = after_index.get(target, ("", ""))
        if (before_source, before_transform) == (after_source, after_transform):
            continue
        reasons = []
        if before_source != after_source:
            reasons.append("source column changed")
        if before_transform != after_transform:
            reasons.append("transform changed")
        impacts.append(
            Impact(
                target_field=target,
                before_source=before_source,
                after_source=after_source,
                reason=" and ".join(reasons) or "changed",
            )
        )
    added = sorted(set(after_index) - set(before_index))
    removed = sorted(set(before_index) - set(after_index))
    return BlastRadius(impacts=impacts, added_targets=added, removed_targets=removed)


def downstream_from_source(graph: LineageGraph, source_column: str) -> list[str]:
    """Every field the lineage log shows ``source_column`` feeding into."""
    downstream: set[str] = set()
    for edge in graph.edges:
        if edge.field == source_column and edge.before and edge.after:
            downstream.add(edge.field)
    return sorted(downstream)


def affected_outputs(before: pd.DataFrame, after: pd.DataFrame) -> list[str]:
    """Columns whose values differ between two frames.

    The second half of a blast radius: which output columns actually change
    content, not just mapping metadata.
    """
    changed: list[str] = []
    for column in before.columns:
        if column not in after.columns:
            changed.append(column)
            continue
        if not before[column].equals(after[column]):
            changed.append(column)
    for column in after.columns:
        if column not in before.columns:
            changed.append(column)
    return sorted(set(changed))
