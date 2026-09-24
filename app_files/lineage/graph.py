"""Interactive lineage graph, blast radius, and OpenLineage export.

Three views over the same lineage events the tracker already records:

* **A graph** — source columns and target fields as nodes, transformations as
  edges. Rendered as standalone HTML with the nodes laid out in columns
  (source left, output right) and edges drawn as SVG paths, so it opens in a
  browser with no JavaScript dependencies and no CDN.

* **Blast radius** — "if this source column is wrong, which target fields and
  rows are affected?". Walks the same edges forward from a node and returns the
  reachable set. This is the question asked when a source file turns out to be
  bad after import.

* **OpenLineage export** — the run, its inputs and its outputs in the
  OpenLineage event shape, so the lineage can be pushed to a data catalogue
  instead of living only inside this tool. The facet names follow the spec; the
  payload carries the counts this tool actually knows.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.lineage.tracker import LineageTracker


# ------------------------------------------------------------------- the graph
@dataclass
class GraphNode:
    id: str
    kind: str  # "source" | "target"
    label: str
    rows: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "kind": self.kind, "label": self.label, "rows": self.rows}


@dataclass
class GraphEdge:
    source: str
    target: str
    transform: str
    count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "transform": self.transform,
            "count": self.count,
        }


@dataclass
class LineageGraph:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)

    def node_ids(self) -> set[str]:
        return {n.id for n in self.nodes}

    def as_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.as_dict() for n in self.nodes],
            "edges": [e.as_dict() for e in self.edges],
        }

    def blast_radius(self, node_id: str) -> dict[str, Any]:
        """Everything downstream of ``node_id``.

        Returns the reachable target fields, the edges walked, and the number of
        source rows that touched the starting node — the size of the problem if
        that column was wrong.
        """
        if node_id not in self.node_ids():
            raise KeyError(f"No lineage node {node_id!r}.")

        adjacency: dict[str, list[str]] = {}
        for edge in self.edges:
            adjacency.setdefault(edge.source, []).append(edge.target)

        reached: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for neighbour in adjacency.get(current, []):
                if neighbour not in reached:
                    reached.add(neighbour)
                    frontier.append(neighbour)

        affected = [n.as_dict() for n in self.nodes if n.id in reached]
        start = next(n for n in self.nodes if n.id == node_id)
        return {
            "start": node_id,
            "affected_nodes": affected,
            "affected_count": len(affected),
            "rows_at_risk": start.rows,
            "edges": [
                e.as_dict() for e in self.edges if e.source == node_id or e.target in reached
            ],
        }


def _transform_for(action: str) -> str:
    if action == "clean":
        return "clean"
    if action.startswith("map:"):
        return action.split(":", 1)[1]
    return action


def build_lineage_graph(tracker: LineageTracker) -> LineageGraph:
    """Fold the event log into nodes and edges.

    Source-column nodes are named ``src:<field>`` and target-field nodes
    ``tgt:<field>``, because the same name on both sides is two different
    things and collapsing them would invent a false link.
    """
    frame = tracker.to_frame()
    nodes: dict[str, GraphNode] = {}
    edge_counts: dict[tuple[str, str, str], int] = {}

    for record in frame.to_dict("records"):
        action = str(record.get("action", ""))
        field_name = str(record.get("field", ""))
        if not field_name or pd.isna(record.get("field")):
            continue
        transform = _transform_for(action)

        if action == "clean":
            source_id, target_id = f"src:{field_name}", f"tgt:{field_name}"
        elif action.startswith("map:"):
            source_id, target_id = f"src:{field_name}", f"tgt:{field_name}"
        else:
            continue

        rows = int(record.get("source_row")) if pd.notna(record.get("source_row")) else 0
        for node_id, kind in ((source_id, "source"), (target_id, "target")):
            if node_id not in nodes:
                nodes[node_id] = GraphNode(id=node_id, kind=kind, label=field_name)
        key = (source_id, target_id, transform)
        edge_counts[key] = edge_counts.get(key, 0) + 1

    # Row counts per node, from the rows that actually appeared.
    for record in frame.to_dict("records"):
        if pd.isna(record.get("source_row")):
            continue
        row = int(record["source_row"])
        field_name = str(record.get("field", ""))
        for node_id in (f"src:{field_name}", f"tgt:{field_name}"):
            if node_id in nodes:
                nodes[node_id].rows = max(nodes[node_id].rows, row + 1)

    edges = [
        GraphEdge(source=source, target=target, transform=transform, count=count)
        for (source, target, transform), count in sorted(edge_counts.items())
    ]
    return LineageGraph(nodes=sorted(nodes.values(), key=lambda n: n.id), edges=edges)


def render_lineage_graph_html(
    graph: LineageGraph,
    *,
    title: str = "Transformation lineage",
    palette: dict[str, str] | None = None,
) -> str:
    """Standalone HTML with a two-column layout and SVG edges."""
    colours = {
        "background": "#F5F0E6",
        "panel": "#FDFBF7",
        "ink": "#2B2420",
        "border": "#E4DCC8",
        "source": "#3F6C51",
        "target": "#B26A2E",
        "edge": "#9A8F7A",
    }
    if palette:
        colours.update(palette)

    sources = [n for n in graph.nodes if n.kind == "source"]
    targets = [n for n in graph.nodes if n.kind == "target"]
    row_height = 30
    width, height = 900, max(len(sources), len(targets), 1) * row_height + 80

    positions: dict[str, tuple[int, int]] = {}
    for index, node in enumerate(sources):
        positions[node.id] = (40, 60 + index * row_height)
    for index, node in enumerate(targets):
        positions[node.id] = (width - 240, 60 + index * row_height)

    edges_svg = ""
    for edge in graph.edges:
        start = positions.get(edge.source)
        end = positions.get(edge.target)
        if not start or not end:
            continue
        x1, y1 = start[0] + 160, start[1] + 10
        x2, y2 = end[0], end[1] + 10
        edges_svg += (
            f"<path d='M{x1},{y1} C{(x1+x2)//2},{y1} {(x1+x2)//2},{y2} {x2},{y2}' "
            f"fill='none' stroke='{colours['edge']}' stroke-width='1.5'/>"
            f"<title>{edge.transform}</title>"
        )

    def node_box(node: GraphNode) -> str:
        x, y = positions[node.id]
        colour = colours["source"] if node.kind == "source" else colours["target"]
        return (
            f"<rect x='{x}' y='{y}' width='160' height='24' rx='6' "
            f"fill='{colours['panel']}' stroke='{colour}'/>"
            f"<text x='{x+8}' y='{y+16}' font-size='12' fill='{colours['ink']}'>"
            f"{node.label}</text>"
        )

    boxes = "".join(node_box(n) for n in graph.nodes if n.id in positions)
    return (
        "<html><head><meta charset='utf-8'>"
        f"<title>{title}</title>"
        "<style>body{margin:0;background:" + colours["background"] + ";}"
        "h1{font-family:Georgia,'Times New Roman',serif;color:" + colours["ink"] + ";"
        "padding:16px 24px 0;font-size:20px;}"
        "p{font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:" + colours["ink"] + ";"
        "padding:0 24px;font-size:13px;}</style></head><body>"
        f"<h1>{title}</h1>"
        f"<p>{len(sources)} source column(s), {len(targets)} target field(s), "
        f"{len(graph.edges)} transformation(s).</p>"
        f"<svg width='{width}' height='{height}' role='img' aria-label='lineage graph'>"
        f"{edges_svg}{boxes}</svg>"
        "</body></html>"
    )


# --------------------------------------------------------- OpenLineage export
OPENLINEAGE_SCHEMA = "https://openlineage.io/spec/2-0-2/OpenLineage.json#/definitions/RunEvent"


def openlineage_export(
    tracker: LineageTracker,
    *,
    job_name: str = "dataflow.migration",
    namespace: str = "dataflow",
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    run_id: str = "",
    event_time: str = "",
) -> dict[str, Any]:
    """Render the run as an OpenLineage event.

    The spec's required shape is ``eventTime``, ``eventType``, ``run`` and
    ``job``, plus ``inputs``/``outputs``. The run facet carries the row counts,
    so a catalogue shows "6 of 7 rows out" rather than just "a run happened".
    """
    frame = tracker.to_frame()
    stats = {
        "rows_touched": int(frame["source_row"].nunique()) if not frame.empty else 0,
        "events": tracker.total_events,
        "actions": tracker.actions(),
    }
    return {
        "eventTime": event_time or datetime.now(timezone.utc).isoformat(),
        "eventType": "COMPLETE",
        "producer": "https://github.com/autoflowcompliance/data-migration",
        "schemaURL": OPENLINEAGE_SCHEMA,
        "run": {
            "runId": run_id or _stable_run_id(job_name, stats),
            "facets": {
                "dataflow_lineage": {
                    "_producer": "https://github.com/autoflowcompliance/data-migration",
                    "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/RunFacet.json",
                    **stats,
                }
            },
        },
        "job": {"namespace": namespace, "name": job_name},
        "inputs": [{"namespace": namespace, "name": name} for name in (inputs or [])],
        "outputs": [{"namespace": namespace, "name": name} for name in (outputs or [])],
    }


def _stable_run_id(job_name: str, stats: dict[str, Any]) -> str:
    import hashlib

    payload = json.dumps({"job": job_name, **stats}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def write_openlineage_event(event: dict[str, Any], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(event, indent=2), encoding="utf-8")
    return destination