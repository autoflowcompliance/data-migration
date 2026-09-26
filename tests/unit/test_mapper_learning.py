"""Learned mapping suggestions and schema drift detection."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.mappers import (
    MappingMemory,
    SchemaRegistry,
    detect_drift,
    infer_column_type,
    load_mapping_config,
    map_data,
    normalise_column,
    schema_of,
    source_fingerprint,
    suggest_mapping,
)


@pytest.fixture
def memory(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return MappingMemory(path=tmp_path / "mapping" / "learned.json")


@pytest.fixture
def registry(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return SchemaRegistry(path=tmp_path / "mapping" / "schemas.json")


def source_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Email Address": ["a@x.com", "b@x.com"],
            "Phone": ["+14155552671", "+14155559999"],
            "First Name": ["Jane", "John"],
            "Last Name": ["Doe", "Smith"],
        }
    )


class TestFingerprint:
    def test_order_independent(self):
        assert source_fingerprint(["a", "b"]) == source_fingerprint(["b", "a"])

    def test_name_variants_collapse(self):
        assert source_fingerprint(["Email Address"]) == source_fingerprint(["email_address"])
        assert source_fingerprint(["EmailAddress"]) == source_fingerprint(["EMAIL ADDRESS"])

    def test_different_columns_differ(self):
        assert source_fingerprint(["a"]) != source_fingerprint(["b"])

    def test_normalise_column_strips_punctuation(self):
        assert normalise_column("Email Address!") == "emailaddress"


class TestLearnedMapping:
    def test_save_then_suggest_is_learned(self, memory):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)

        retyped = frame.copy()
        retyped["Email Address"] = ["z@x.com", "y@x.com"]
        suggestion = suggest_mapping(retyped, config, memory)

        learned = {field.target_field: field for field in suggestion.fields if field.learned}
        assert learned["email"].source_column == "Email Address"
        assert learned["email"].confidence == 1.0
        assert suggestion.is_learned

    def test_repeat_file_maps_without_intervention(self, memory):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)
        suggestion = suggest_mapping(frame, config, memory)
        mapped = {
            field.target_field: field.source_column
            for field in suggestion.fields
            if field.confidence == 1.0
        }
        assert mapped["email"] == "Email Address"
        assert mapped["phone"] == "Phone"

    def test_unseen_schema_falls_back_to_the_alias_matcher(self, memory):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)

        different = pd.DataFrame(
            {"contact_email": ["a@x.com"], "mobile": ["+1"], "given_name": ["A"], "family_name": ["B"]}
        )
        suggestion = suggest_mapping(different, config, memory)
        assert not suggestion.is_learned
        assert all(not field.learned for field in suggestion.fields)

    def test_dropped_learned_column_falls_back(self, memory):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)

        renamed = frame.rename(columns={"Email Address": "E-Mail"}).copy()
        suggestion = suggest_mapping(renamed, config, memory)
        email = next(f for f in suggestion.fields if f.target_field == "email")
        assert not email.learned

    def test_times_seen_increments(self, memory):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)
        learned = memory.save(frame, map_data(frame, config), crm=config.crm)
        assert learned.times_seen == 2

    def test_memory_persists(self, memory, tmp_path):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)
        reopened = MappingMemory(path=tmp_path / "mapping" / "learned.json")
        assert len(reopened.all()) == 1

    def test_clear_removes_everything(self, memory):
        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)
        assert memory.clear() == 1
        assert memory.all() == []

    def test_corrupt_store_does_not_raise(self, memory):
        memory.path.parent.mkdir(parents=True, exist_ok=True)
        memory.path.write_text("{not json")
        assert memory.all() == []

    def test_summary_is_json_safe(self, memory):
        import json

        config = load_mapping_config("hubspot")
        frame = source_frame()
        memory.save(frame, map_data(frame, config), crm=config.crm)
        json.dumps(suggest_mapping(frame, config, memory).summary())


class TestColumnType:
    @pytest.mark.parametrize(
        ("values", "expected"),
        [
            ([1, 2], "integer"),
            ([1.5, 2.5], "number"),
            ([1, 2.5], "number"),
            ([True, False], "boolean"),
            (["+14155552671", "+14155559999"], "string"),
            (["1", "2"], "integer"),
            (["1,234", "2,345"], "integer"),
            (["1.5", "2"], "number"),
            (["-5", "+3"], "integer"),
            (["n/a", "x"], "string"),
            ([None, None], "empty"),
            (["2024-01-01", "2024-06-01"], "date"),
            (["a@x.com"], "string"),
        ],
    )
    def test_inference(self, values, expected):
        assert infer_column_type(pd.Series(values, dtype=object)) == expected

    def test_one_stray_value_makes_it_a_string(self):
        assert infer_column_type(pd.Series([1, 2, "oops"], dtype=object)) == "string"


class TestSchemaDrift:
    def test_added_column(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        grown = frame.copy()
        grown["New Column"] = ["x", "y"]
        drift = registry.check("crm", grown)
        assert drift.added == ["New Column"]
        assert drift.has_drift

    def test_removed_column(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        shrunk = frame.drop(columns=["Phone"])
        drift = registry.check("crm", shrunk)
        assert drift.removed == ["Phone"]

    def test_retyped_column(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        changed = frame.copy()
        changed["Email Address"] = [1, 2]
        drift = registry.check("crm", changed)
        assert drift.retyped == ["Email Address"]

    def test_rename_is_not_add_plus_remove(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        renamed = frame.rename(columns={"Email Address": "email_address"})
        drift = registry.check("crm", renamed)
        assert not drift.has_drift

    def test_no_change_reports_none(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        assert not registry.check("crm", frame).has_drift

    def test_unknown_source_has_no_drift(self, registry):
        assert not registry.check("never-seen", source_frame()).has_drift

    def test_integer_widening_is_not_drift(self):
        drift = detect_drift({"count": "integer"}, {"count": "number"})
        assert not drift.has_drift

    def test_empty_to_typed_is_not_drift(self):
        drift = detect_drift({"maybe": "empty"}, {"maybe": "string"})
        assert not drift.has_drift

    def test_summary_counts_each_kind(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        modified = frame.drop(columns=["Phone"]).copy()
        modified["New Column"] = [1, 2]
        summary = registry.check("crm", modified).summary()
        assert summary["added"] == ["New Column"]
        assert summary["removed"] == ["Phone"]

    def test_render_html_lists_the_change(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        grown = frame.copy()
        grown["New Column"] = ["x", "y"]
        html = registry.check("crm", grown).render_html()
        assert "alert" in html
        assert "New Column" in html

    def test_render_html_quiet_when_unchanged(self, registry):
        frame = source_frame()
        registry.remember("crm", frame)
        assert "No schema change" in registry.check("crm", frame).render_html()

    def test_schema_of_returns_types(self):
        assert schema_of(source_frame())["Phone"] == "string"

    def test_registry_persists(self, registry, tmp_path):
        registry.remember("crm", source_frame())
        reopened = SchemaRegistry(path=tmp_path / "mapping" / "schemas.json")
        assert reopened.known("crm") is not None

    def test_registry_clear_one(self, registry):
        registry.remember("a", source_frame())
        registry.remember("b", source_frame())
        assert registry.clear("a") == 1
        assert registry.known("a") is None
        assert registry.known("b") is not None
