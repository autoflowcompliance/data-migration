"""Lineage extensions: the interactive graph, blast radius and OpenLineage."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import pytest

from app_files.lineage import (
    LineageGraph,
    LineageTracker,
    OpenLineageConfig,
    affected_outputs,
    blast_radius,
    downstream_from_source,
    to_openlineage,
    validate_openlineage,
    write_openlineage,
)
from app_files.mappers import MappingConfig, TargetField, load_mapping_config, map_data


def build_tracker() -> LineageTracker:
    """Two rows, an email cleaned then mapped, a phone cleaned."""
    tracker = LineageTracker()
    tracker.record(
        field_name="email", before="Jane@Example.COM", after="jane@example.com",
        action="clean", source_row=0, output_row=0,
    )
    tracker.record(
        field_name="email", before="jane@example.com", after="jane@example.com",
        action="map:email_lowercase", source_row=0, output_row=0,
    )
    tracker.record(
        field_name="phone", before="(415) 555-2671", after="+14155552671",
        action="clean", source_row=0, output_row=0,
    )
    tracker.record(
        field_name="phone", before="(415) 555-9999", after="+14155559999",
        action="clean", source_row=1, output_row=1,
    )
    return tracker


class TestLineageGraph:
    def test_edges_match_recorded_events(self):
        graph = LineageGraph.from_tracker(build_tracker())
        # Three clean events; the no-op map step (before == after) is not recorded.
        assert graph.fields == ["email", "phone"]
        assert graph.actions == ["clean"]

    def test_transformations_of_a_value(self):
        graph = LineageGraph.from_tracker(build_tracker())
        edges = graph.transformations_of("email", "jane@example.com")
        assert len(edges) == 1
        assert edges[0].before == "Jane@Example.COM"

    def test_transformations_search_both_sides(self):
        """A value is traceable whether it is the input or the output."""
        graph = LineageGraph.from_tracker(build_tracker())
        assert graph.transformations_of("phone", "(415) 555-2671")
        assert graph.transformations_of("phone", "+14155552671")

    def test_values_changed_by_an_action(self):
        graph = LineageGraph.from_tracker(build_tracker())
        values = graph.values_changed_by("clean")
        assert ("email", "jane@example.com") in {(node.field, node.value) for node in values}
        assert len(values) == 3

    def test_ancestry_walks_backwards(self):
        graph = LineageGraph.from_tracker(build_tracker())
        chain = graph.ancestry("email", "jane@example.com")
        assert [edge.before for edge in chain] == ["Jane@Example.COM"]

    def test_descendants_walk_forwards(self):
        graph = LineageGraph.from_tracker(build_tracker())
        chain = graph.descendants("email", "Jane@Example.COM")
        assert [edge.after for edge in chain] == ["jane@example.com"]

    def test_ancestry_of_an_original_value_is_empty(self):
        graph = LineageGraph.from_tracker(build_tracker())
        assert graph.ancestry("email", "Jane@Example.COM") == []

    def test_cycle_does_not_loop_forever(self):
        tracker = LineageTracker()
        tracker.record(field_name="x", before="a", after="b", action="clean")
        tracker.record(field_name="x", before="b", after="a", action="clean")
        graph = LineageGraph.from_tracker(tracker)
        assert len(graph.ancestry("x", "a", max_depth=10)) <= 2

    def test_from_frame_matches_from_tracker(self):
        tracker = build_tracker()
        a = LineageGraph.from_tracker(tracker)
        b = LineageGraph.from_frame(tracker.to_frame())
        assert len(a.edges) == len(b.edges)
        assert [e.before for e in a.edges] == [e.before for e in b.edges]

    def test_summary_counts_actions(self):
        graph = LineageGraph.from_tracker(build_tracker())
        assert graph.summary()["actions"] == {"clean": 3}

    def test_render_html_is_self_contained(self):
        html = LineageGraph.from_tracker(build_tracker()).render_html()
        assert "lineage-graph" in html
        assert "jane@example.com" in html


class TestBlastRadius:
    def _source(self):
        return pd.DataFrame(
            {
                "Email Address": ["a@x.com"],
                "Phone": ["+14155552671"],
                "First Name": ["Jane"],
                "Last Name": ["Doe"],
            }
        )

    def _remap_email_to_phone(self):
        current = load_mapping_config("hubspot")
        proposed = MappingConfig(
            crm=current.crm,
            fields=[
                TargetField(
                    name=f.name, aliases=f.aliases, transform=f.transform,
                    source=f.source, sources=f.sources,
                )
                for f in current.fields
            ],
        )
        for field in proposed.fields:
            if field.name == "email":
                field.source = "Phone"
        return current, proposed

    def test_remap_lists_every_affected_target(self):
        current, proposed = self._remap_email_to_phone()
        source = self._source()
        radius = blast_radius(map_data(source, current), map_data(source, proposed))
        assert "email" in radius.affected_targets
        # The second-order effect: Phone is consumed by email, so phone loses it.
        assert "phone" in radius.affected_targets

    def test_remap_lists_changed_source_columns(self):
        current, proposed = self._remap_email_to_phone()
        source = self._source()
        radius = blast_radius(map_data(source, current), map_data(source, proposed))
        assert set(radius.changed_source_columns) == {"Email Address", "Phone"}

    def test_identical_mapping_has_no_impact(self):
        current = load_mapping_config("hubspot")
        source = self._source()
        radius = blast_radius(map_data(source, current), map_data(source, current))
        assert radius.is_empty

    def test_adding_a_target_is_reported(self):
        current = load_mapping_config("hubspot")
        proposed = MappingConfig(
            crm=current.crm,
            fields=[
                *[
                    TargetField(
                        name=f.name, aliases=f.aliases, transform=f.transform,
                        source=f.source, sources=f.sources,
                    )
                    for f in current.fields
                ],
                TargetField(name="brand_new", aliases=["Nothing"]),
            ],
        )
        source = self._source()
        radius = blast_radius(map_data(source, current), map_data(source, proposed))
        assert "brand_new" in radius.added_targets

    def test_render_html_names_the_impact(self):
        current, proposed = self._remap_email_to_phone()
        source = self._source()
        html = blast_radius(map_data(source, current), map_data(source, proposed)).render_html()
        assert "blast-radius" in html
        assert "email" in html

    def test_affected_outputs_finds_changed_values(self):
        before = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        after = pd.DataFrame({"a": [1, 3], "b": ["x", "y"]})
        assert affected_outputs(before, after) == ["a"]

    def test_affected_outputs_finds_added_and_removed_columns(self):
        before = pd.DataFrame({"a": [1]})
        after = pd.DataFrame({"b": [1]})
        assert affected_outputs(before, after) == ["a", "b"]


class TestOpenLineage:
    def test_event_has_every_required_key(self):
        event = to_openlineage(build_tracker())
        validate_openlineage(event)
        assert event["eventType"] == "COMPLETE"

    def test_failure_event_type(self):
        event = to_openlineage(build_tracker(), success=False)
        assert event["eventType"] == "FAIL"

    def test_column_lineage_lists_changed_fields(self):
        event = to_openlineage(
            build_tracker(),
            OpenLineageConfig(source_columns=["Email"], output_columns=["email", "phone"]),
        )
        fields = event["outputs"][0]["facets"]["columnLineage"]["fields"]
        assert set(fields) == {"email", "phone"}
        assert fields["email"]["inputFields"][0]["name"] == "Jane@Example.COM"

    def test_schema_facet_lists_output_columns(self):
        event = to_openlineage(
            build_tracker(), OpenLineageConfig(output_columns=["email", "phone"])
        )
        names = [f["name"] for f in event["outputs"][0]["facets"]["schema"]["fields"]]
        assert names == ["email", "phone"]

    def test_run_id_is_stable_when_supplied(self):
        event = to_openlineage(build_tracker(), run_id="fixed-run")
        assert event["run"]["runId"] == "fixed-run"

    def test_event_time_is_utc_iso(self):
        moment = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
        event = to_openlineage(build_tracker(), event_time=moment)
        assert event["eventTime"] == "2024-06-01T12:00:00Z"

    def test_validator_names_a_missing_key(self):
        event = to_openlineage(build_tracker())
        del event["job"]
        with pytest.raises(ValueError, match="job"):
            validate_openlineage(event)

    def test_validator_rejects_unknown_event_type(self):
        event = to_openlineage(build_tracker())
        event["eventType"] = "DONE"
        with pytest.raises(ValueError, match="eventType"):
            validate_openlineage(event)

    def test_validator_requires_dataset_names(self):
        event = to_openlineage(build_tracker())
        event["inputs"][0]["name"] = ""
        with pytest.raises(ValueError, match="namespace and a name"):
            validate_openlineage(event)

    def test_write_produces_valid_json(self, tmp_path):
        path = write_openlineage(to_openlineage(build_tracker()), tmp_path / "ol.json")
        payload = json.loads(path.read_text())
        assert isinstance(payload, list)
        validate_openlineage(payload[0])

    def test_write_accepts_a_list(self, tmp_path):
        events = [to_openlineage(build_tracker()), to_openlineage(build_tracker())]
        path = write_openlineage(events, tmp_path / "many.json")
        assert len(json.loads(path.read_text())) == 2


class TestDownstream:
    def test_downstream_from_source_column(self):
        graph = LineageGraph.from_tracker(build_tracker())
        assert downstream_from_source(graph, "email") == ["email"]
