"""An explorable view over the lineage event log.

The frozen lineage layer writes one row per changed value: source row, output
row, field, before, after, action. That is a flat log. This turns the same
events into a graph you can traverse in either direction:

* click a *value* and see every transformation that touched it
* click a *transformation* and see every value it changed

Nothing here writes lineage; it only reads ``LineageTracker`` events, so the
frozen layer is untouched.

    graph = LineageGraph.from_tracker(tracker)
    graph.transformations_of("email", "jane@example.com")
    graph.values_changed_by("map:email_lowercase")
    graph.ancestry("email", "jane@example.com")   # every step that produced it
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable

from app_files.lineage.tracker import LineageTracker


def _key(value: Any) -> str:
    return "" if value is None else str(value)


@dataclass(frozen=True)
class ValueNode:
    """One field's value at one point, identified by field and value."""

    field: str
    value: str


@dataclass
class TransformationEdge:
    """One recorded change from ``before`` to ``after`` in a field."""

    field: str
    before: str
    after: str
    action: str
    source_row: int | None
    output_row: int | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "before": self.before,
            "after": self.after,
            "action": self.action,
            "source_row": self.source_row,
            "output_row": self.output_row,
        }


@dataclass
class LineageGraph:
    """A traversable view of a lineage log."""

    edges: list[TransformationEdge] = field(default_factory=list)

    @classmethod
    def from_tracker(cls, tracker: LineageTracker) -> LineageGraph:
        return cls.from_events(tracker.events)

    @classmethod
    def from_events(cls, events: Iterable[Any]) -> LineageGraph:
        edges = [
            TransformationEdge(
                field=event.field,
                before=_key(event.before),
                after=_key(event.after),
                action=event.action,
                source_row=event.source_row,
                output_row=event.output_row,
            )
            for event in events
        ]
        return cls(edges=edges)

    @classmethod
    def from_frame(cls, events_frame) -> LineageGraph:
        """Build from ``tracker.to_frame()`` output rather than live events."""
        edges = [
            TransformationEdge(
                field=str(row["field"]),
                before=_key(row["before"]),
                after=_key(row["after"]),
                action=str(row["action"]),
                source_row=None if row["source_row"] == "" else int(row["source_row"]),
                output_row=None if row["output_row"] == "" else int(row["output_row"]),
            )
            for row in events_frame.to_dict("records")
        ]
        return cls(edges=edges)

    # ------------------------------------------------------------ traversal

    @property
    def actions(self) -> list[str]:
        return sorted({edge.action for edge in self.edges})

    @property
    def fields(self) -> list[str]:
        return sorted({edge.field for edge in self.edges})

    def transformations_of(self, field_name: str, value: str) -> list[TransformationEdge]:
        """Every edge where ``value`` was the before *or* the after.

        Searching both sides is what makes a value traceable in either
        direction: the value you are holding may be the input or the output.
        """
        wanted = _key(value)
        return [
            edge
            for edge in self.edges
            if edge.field == field_name and (edge.before == wanted or edge.after == wanted)
        ]

    def values_changed_by(self, action: str) -> list[ValueNode]:
        """Every resulting value for an action, deduplicated."""
        seen: dict[tuple[str, str], ValueNode] = {}
        for edge in self.edges:
            if edge.action == action:
                seen[(edge.field, edge.after)] = ValueNode(edge.field, edge.after)
        return sorted(seen.values(), key=lambda node: (node.field, node.value))

    def ancestry(self, field_name: str, value: str, max_depth: int = 50) -> list[TransformationEdge]:
        """Walk backwards: the chain of edges that produced ``value``.

        Follows ``before -> after`` links within the field until it reaches a
        value that was never itself produced. Returned oldest-first.
        """
        chain: list[TransformationEdge] = []
        seen: set[tuple[str, str]] = set()
        current = _key(value)
        for _ in range(max_depth):
            produced_by = [
                edge
                for edge in self.edges
                if edge.field == field_name and edge.after == current
            ]
            if not produced_by:
                break
            edge = produced_by[0]
            marker = (edge.before, edge.after)
            if marker in seen:
                break
            seen.add(marker)
            chain.append(edge)
            current = edge.before
        return list(reversed(chain))

    def descendants(self, field_name: str, value: str, max_depth: int = 50) -> list[TransformationEdge]:
        """Walk forwards: every edge reachable from ``value`` as its input."""
        chain: list[TransformationEdge] = []
        seen: set[tuple[str, str]] = set()
        frontier = [_key(value)]
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: list[str] = []
            for current in frontier:
                for edge in self.edges:
                    if edge.field != field_name or edge.before != current:
                        continue
                    marker = (edge.before, edge.after)
                    if marker in seen:
                        continue
                    seen.add(marker)
                    chain.append(edge)
                    next_frontier.append(edge.after)
            frontier = next_frontier
            depth += 1
        return chain

    def summary(self) -> dict[str, Any]:
        actions: dict[str, int] = defaultdict(int)
        for edge in self.edges:
            actions[edge.action] += 1
        return {
            "edges": len(self.edges),
            "fields": self.fields,
            "actions": dict(sorted(actions.items())),
        }

    # ------------------------------------------------------------- rendering

    def render_html(self, limit: int = 500) -> str:
        """A small self-contained page listing the edges, for the web UI."""
        rows = "".join(
            "<tr>"
            f"<td>{edge.field}</td>"
            f"<td>{edge.before}</td>"
            f"<td>{edge.after}</td>"
            f"<td>{edge.action}</td>"
            f"<td>{'' if edge.source_row is None else edge.source_row}</td>"
            "</tr>"
            for edge in self.edges[:limit]
        )
        summary = self.summary()
        return (
            "<div class='lineage-graph'>"
            f"<p>{summary['edges']} transformations across "
            f"{len(summary['fields'])} fields.</p>"
            "<table><thead><tr><th>Field</th><th>Before</th><th>After</th>"
            f"<th>Action</th><th>Source row</th></tr></thead><tbody>{rows}</tbody></table>"
            "</div>"
        )
