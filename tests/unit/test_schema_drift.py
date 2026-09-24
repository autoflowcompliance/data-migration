"""Schema drift and learned mapping."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.intelligence import (
    detect_drift,
    learn_mapping,
    load_snapshot,
    proposals_to_yaml,
    record_snapshot,
    snapshot_schema,
)

CONTACTS = pd.DataFrame(
    {
        "First Name": ["Ann", "Bob"],
        "Last Name": ["Lee", "Ray"],
        "Email Address": ["ann@x.com", "bob@x.com"],
        "Phone": ["5551234567", "5559876543"],
    }
)


# ------------------------------------------------------------------- drift
def test_an_unchanged_schema_has_no_drift():
    previous = snapshot_schema(CONTACTS)
    assert detect_drift(previous, CONTACTS).has_drift is False


def test_a_dropped_column_is_reported_as_removed():
    previous = snapshot_schema(CONTACTS)
    current = CONTACTS.drop(columns=["Phone"])
    drift = detect_drift(previous, current, rename_threshold=0.95)
    assert [c.column for c in drift.of_kind("removed")] == ["Phone"]


def test_a_new_column_is_reported_as_added():
    previous = snapshot_schema(CONTACTS)
    current = CONTACTS.assign(Company=["Acme", "Globex"])
    drift = detect_drift(previous, current, rename_threshold=0.95)
    assert [c.column for c in drift.of_kind("added")] == ["Company"]


def test_a_renamed_column_is_reported_as_a_rename_not_a_remove_and_add():
    previous = snapshot_schema(CONTACTS)
    current = CONTACTS.rename(columns={"Email Address": "Email"})
    drift = detect_drift(previous, current)
    renames = drift.of_kind("renamed")
    assert len(renames) == 1
    assert renames[0].previous == "Email Address"
    assert renames[0].column == "Email"
    assert drift.of_kind("added") == []


def test_a_type_change_is_reported():
    previous = snapshot_schema(pd.DataFrame({"amount": ["10", "20"]}))
    current = pd.DataFrame({"amount": [10.5, 20.5]})
    drift = detect_drift(previous, current, rename_threshold=0.95)
    changes = drift.of_kind("type_changed")
    assert len(changes) == 1
    assert "float" in changes[0].detail


def test_drift_report_summarises_its_changes():
    previous = snapshot_schema(CONTACTS)
    current = CONTACTS.drop(columns=["Phone"]).assign(Company=["A", "B"])
    report = detect_drift(previous, current, rename_threshold=0.95).as_dict()
    assert report["has_drift"] is True
    assert report["summary"]["removed"] == 1
    assert report["summary"]["added"] == 1


def test_snapshots_round_trip_on_disk(tmp_path):
    path = tmp_path / "schema.json"
    record_snapshot(snapshot_schema(CONTACTS, source="contacts.csv"), "contacts", path=path)
    loaded = load_snapshot("contacts", path=path)
    assert loaded.columns == list(CONTACTS.columns)
    assert loaded.source == "contacts.csv"


def test_a_missing_snapshot_loads_as_none(tmp_path):
    assert load_snapshot("nope", path=tmp_path / "nothing.json") is None


def test_a_corrupt_snapshot_loads_as_none(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json")
    assert load_snapshot("bad", path=path) is None


# ---------------------------------------------------------- learned mapping
TARGETS = [
    {"name": "email", "type": "email"},
    {"name": "firstname", "type": "string"},
    {"name": "lastname", "type": "string"},
    {"name": "phone", "type": "phone"},
]


def test_learned_mapping_links_the_obvious_columns():
    mapping = learn_mapping(CONTACTS, TARGETS)
    field_map = mapping.to_field_map()
    assert field_map["Email Address"] == "email"
    assert field_map["Phone"] == "phone"


def test_name_matches_beat_unrelated_columns():
    mapping = learn_mapping(CONTACTS, TARGETS)
    by_target = {p.target: p for p in mapping.proposals}
    assert by_target["email"].column == "Email Address"
    assert by_target["email"].confidence > 0.5


def test_a_column_is_used_at_most_once():
    mapping = learn_mapping(CONTACTS, TARGETS)
    columns = [p.column for p in mapping.proposals]
    assert len(columns) == len(set(columns))


def test_unmatched_targets_are_reported():
    mapping = learn_mapping(CONTACTS, [{"name": "billing_reference", "type": "string"}])
    assert mapping.unmatched_targets == ["billing_reference"]
    assert mapping.proposals == []


def test_low_confidence_proposals_are_not_applied():
    mapping = learn_mapping(CONTACTS, TARGETS)
    strict = mapping.to_field_map(min_confidence=0.99)
    assert strict == {}


def test_value_fit_lifts_a_wrongly_named_email_column():
    frame = pd.DataFrame({"contact": ["a@x.com", "b@x.com", "c@x.com"]})
    mapping = learn_mapping(frame, [{"name": "email", "type": "email"}])
    assert mapping.proposals
    assert mapping.proposals[0].column == "contact"
    assert "values" in mapping.proposals[0].reason


def test_a_phone_typed_target_rejects_an_email_column():
    frame = pd.DataFrame({"email": ["a@x.com", "b@x.com"]})
    mapping = learn_mapping(frame, [{"name": "phone", "type": "phone"}])
    # The value check should keep this below the bar.
    assert mapping.proposals == []


def test_learned_mapping_renders_as_yaml():
    mapping = learn_mapping(CONTACTS, TARGETS)
    text = proposals_to_yaml(mapping, crm="hubspot")
    assert "crm: hubspot" in text
    assert "fields:" in text
    assert "source: Email Address" in text


def test_learning_is_deterministic():
    first = learn_mapping(CONTACTS, TARGETS).as_dict()
    second = learn_mapping(CONTACTS, TARGETS).as_dict()
    assert first == second