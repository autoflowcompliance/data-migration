"""Lineage graph, blast radius, and OpenLineage export."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from app_files.lineage import LineageTracker, build_lineage_graph, openlineage_export
from app_files.lineage.graph import render_lineage_graph_html, write_openlineage_event
from app_files.pipeline import run_pipeline

SOURCE = pd.DataFrame(
    {
        "First Name": ["Ann", "Bob", "Ann"],
        "Last Name": ["Lee", "Ray", "Lee"],
        "Email Address": ["ANN@X.com", "bob@x.com", "ANN@X.com"],
        "Phone": ["(555) 123-4567", "555.987.6543", "(555) 123-4567"],
    }
)


@pytest.fixture
def tracker():
    tracker = LineageTracker()
    run_pipeline(SOURCE, "hubspot", lineage_tracker=tracker, run_structural_check=False)
    return tracker


def test_graph_has_source_and_target_nodes(tracker):
    graph = build_lineage_graph(tracker)
    kinds = {node.kind for node in graph.nodes}
    assert kinds == {"source", "target"}
    labels = {node.label for node in graph.nodes}
    assert "Email Address" in labels
    # Source and target sides are distinct nodes even for the same column name,
    # so a column-to-column edge is a real link and not a self-loop.
    assert "src:Email Address" in graph.node_ids()
    assert "tgt:Email Address" in graph.node_ids()


def test_graph_edges_carry_the_transform(tracker):
    graph = build_lineage_graph(tracker)
    assert graph.edges
    transforms = {edge.transform for edge in graph.edges}
    assert any(t for t in transforms)


def test_blast_radius_walks_downstream(tracker):
    graph = build_lineage_graph(tracker)
    radius = graph.blast_radius("src:Email Address")
    assert radius["affected_count"] >= 1
    affected_ids = {n["id"] for n in radius["affected_nodes"]}
    assert "tgt:Email Address" in affected_ids
    assert radius["rows_at_risk"] >= 1


def test_blast_radius_of_an_unknown_node_is_an_error(tracker):
    graph = build_lineage_graph(tracker)
    with pytest.raises(KeyError):
        graph.blast_radius("src:Does Not Exist")


def test_graph_renders_self_contained_html(tracker):
    graph = build_lineage_graph(tracker)
    html = render_lineage_graph_html(graph)
    assert "<svg" in html
    assert "Email Address" in html
    # No external assets: a deliverable must open offline.
    assert "http://" not in html and "https://" not in html


def test_openlineage_export_has_the_spec_shape(tracker):
    event = openlineage_export(
        tracker,
        job_name="dataflow.migration.hubspot",
        inputs=["s3://in/messy.csv"],
        outputs=["s3://out/clean.csv"],
    )
    assert event["eventType"] == "COMPLETE"
    assert event["job"]["name"] == "dataflow.migration.hubspot"
    assert event["run"]["runId"]
    assert event["inputs"][0]["name"] == "s3://in/messy.csv"
    assert event["outputs"][0]["name"] == "s3://out/clean.csv"
    assert event["run"]["facets"]["dataflow_lineage"]["events"] > 0
    json.dumps(event)  # must serialise for a catalogue HTTP push


def test_openlineage_event_is_written_to_disk(tracker, tmp_path):
    event = openlineage_export(tracker)
    path = write_openlineage_event(event, tmp_path / "ol.json")
    assert json.loads(path.read_text())["eventType"] == "COMPLETE"


def test_openlineage_run_id_is_stable_for_the_same_run(tracker):
    first = openlineage_export(tracker)["run"]["runId"]
    second = openlineage_export(tracker)["run"]["runId"]
    assert first == second