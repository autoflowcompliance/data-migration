"""Export lineage events in OpenLineage format.

OpenLineage is a JSON event schema used by data catalogs (Marquez, DataHub,
OpenMetadata). A ``RunEvent`` names a job, the inputs it read, the outputs it
wrote, and the column-level lineage between them.

This reads the frozen lineage tracker and emits conforming events. It does not
change how lineage is recorded.

    events = to_openlineage(tracker, job_name="dataflow.clean", ...)
    write_openlineage(events, "lineage_openlineage.json")
    validate_openlineage(events)      # raises on a malformed event
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_files.lineage.graph import LineageGraph
from app_files.lineage.tracker import LineageTracker

#: The schema version this emits against.
OPENLINEAGE_SCHEMA = "https://openlineage.io/spec/2-0-2/OpenLineage.json#/definitions/RunEvent"

PRODUCER = "https://github.com/dataflow/data-migration"
SCHEMA_URL = "https://openlineage.io/spec/facets/1-0-0/SchemaDatasetFacet.json"


def _iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class OpenLineageConfig:
    job_name: str = "dataflow.pipeline"
    namespace: str = "dataflow"
    source_name: str = "source"
    output_name: str = "output"
    source_columns: list[str] = field(default_factory=list)
    output_columns: list[str] = field(default_factory=list)


def _dataset(
    namespace: str, name: str, columns: list[str], facets_kind: str
) -> dict[str, Any]:
    facet: dict[str, Any] = {
        "_producer": PRODUCER,
        "_schemaURL": SCHEMA_URL,
        "fields": [{"name": column, "type": "string"} for column in columns],
    }
    return {
        "namespace": namespace,
        "name": name,
        "facets": {facets_kind: facet},
    }


def _column_lineage_facet(graph: LineageGraph) -> dict[str, Any]:
    """Column-level lineage: which input field produced which output field.

    Every field in the log that changed is a dependency of itself, because a
    transform rewrites the column in place. Where a field's ``before`` value
    came from a differently named column (a mapping), that is recorded too, so
    the facet reflects the mapping as well as the transforms.
    """
    fields: dict[str, dict[str, Any]] = {}
    for edge in graph.edges:
        entry = fields.setdefault(
            edge.field,
            {
                "inputFields": [],
                "outputFields": [],
                "transformationType": "DIRECT",
                "transformationDescription": "",
            },
        )
        if edge.before and {"namespace": "source", "name": edge.before} not in entry["inputFields"]:
            entry["inputFields"].append({"namespace": "source", "name": edge.before})
        entry["outputFields"].append({"namespace": "output", "name": edge.after or edge.field})
        if edge.action.startswith("map:"):
            entry["transformationType"] = "DIRECT"
            entry["transformationDescription"] = edge.action.removeprefix("map:")
        elif edge.action == "clean":
            entry["transformationDescription"] = "cleaned"
        else:
            entry["transformationDescription"] = edge.action
    return {
        "_producer": PRODUCER,
        "_schemaURL": (
            "https://openlineage.io/spec/facets/1-0-0/"
            "ColumnLineageDatasetFacet.json"
        ),
        "fields": fields,
    }


def to_openlineage(
    tracker: LineageTracker | LineageGraph,
    config: OpenLineageConfig | None = None,
    *,
    run_id: str | None = None,
    event_time: datetime | None = None,
    success: bool = True,
) -> dict[str, Any]:
    """A single COMPLETE ``RunEvent`` describing the run."""
    config = config or OpenLineageConfig()
    graph = tracker if isinstance(tracker, LineageGraph) else LineageGraph.from_tracker(tracker)
    now = event_time or datetime.now(timezone.utc)
    run_id = run_id or str(uuid.uuid4())

    return {
        "eventType": "COMPLETE" if success else "FAIL",
        "eventTime": _iso(now),
        "producer": PRODUCER,
        "schemaURL": OPENLINEAGE_SCHEMA,
        "run": {"runId": run_id},
        "job": {"namespace": config.namespace, "name": config.job_name},
        "inputs": [
            _dataset(
                config.namespace,
                config.source_name,
                config.source_columns,
                "schema",
            )
        ],
        "outputs": [
            {
                **_dataset(
                    config.namespace,
                    config.output_name,
                    config.output_columns,
                    "schema",
                ),
                "facets": {
                    "schema": {
                        "_producer": PRODUCER,
                        "_schemaURL": SCHEMA_URL,
                        "fields": [
                            {"name": column, "type": "string"}
                            for column in config.output_columns
                        ],
                    },
                    "columnLineage": _column_lineage_facet(graph),
                },
            }
        ],
    }


def validate_openlineage(event: dict[str, Any]) -> None:
    """Check the required shape of a ``RunEvent``.

    A structural check against the spec's required keys rather than a full JSON
    Schema evaluation, so it has no dependency and fails with a message that
    names the missing key.
    """
    required = ("eventType", "eventTime", "producer", "schemaURL", "run", "job", "inputs", "outputs")
    missing = [key for key in required if key not in event]
    if missing:
        raise ValueError(f"OpenLineage event is missing: {', '.join(missing)}")
    if event["eventType"] not in {"START", "RUNNING", "COMPLETE", "ABORT", "FAIL", "OTHER"}:
        raise ValueError(f"Unknown eventType {event['eventType']!r}")
    if "runId" not in event["run"]:
        raise ValueError("OpenLineage run is missing runId")
    if not event["job"].get("namespace") or not event["job"].get("name"):
        raise ValueError("OpenLineage job needs a namespace and a name")
    for dataset in [*event["inputs"], *event["outputs"]]:
        if not dataset.get("namespace") or not dataset.get("name"):
            raise ValueError("Every OpenLineage dataset needs a namespace and a name")


def write_openlineage(events: dict[str, Any] | list[dict[str, Any]], path: str | Path) -> Path:
    """Write one event or a list of them to a JSON file."""
    location = Path(path)
    location.parent.mkdir(parents=True, exist_ok=True)
    payload = events if isinstance(events, list) else [events]
    for event in payload:
        validate_openlineage(event)
    location.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return location
