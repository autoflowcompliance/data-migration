"""Layer 17 — extensibility: registering transforms, rule types, output
formats and destinations without forking, plus lifecycle events.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.output import (
    FORMATS,
    build_destination,
    register_destination,
    register_format,
    registered_destinations,
    write_any,
)
from app_files.output.destinations import DeliveryReceipt
from app_files.plugins import (
    EventBus,
    LifecycleEvent,
    PluginError,
    PluginRegistry,
    PluginSpec,
    active_plugins,
    emit,
    load_plugin,
    subscribe,
)
from app_files.rules import register_validator, registered_rule_types, run_rules
from app_files.rules.schema import Rule, RuleConfigError
from app_files.transforms import TRANSFORMS, get_transform, register_transform


@pytest.fixture(autouse=True)
def _clean_registries():
    """Every test restores the built-in registries, so an addition cannot leak."""
    from app_files.output.destinations import DESTINATION_TYPES
    from app_files.plugins.registry import _LOADED
    from app_files.rules.validators import VALIDATORS

    transforms = dict(TRANSFORMS)
    formats = dict(FORMATS)
    validators = dict(VALIDATORS)
    destinations = dict(DESTINATION_TYPES)
    loaded = dict(_LOADED)
    yield
    for registry, snapshot in (
        (TRANSFORMS, transforms),
        (FORMATS, formats),
        (VALIDATORS, validators),
        (DESTINATION_TYPES, destinations),
        (_LOADED, loaded),
    ):
        registry.clear()
        registry.update(snapshot)


def _unregister_rule_type(name: str) -> None:
    from app_files.rules.validators import VALIDATORS

    VALIDATORS.pop(name, None)


class TestRegisterTransform:
    def test_a_registered_transform_becomes_available(self):
        register_transform("shout", lambda v: str(v).upper())
        assert get_transform("shout")("hi") == "HI"

    def test_a_duplicate_name_is_refused(self):
        with pytest.raises(ValueError, match="already exists"):
            register_transform("trim", lambda v: v)

    def test_the_refusal_protects_the_built_in(self):
        with pytest.raises(ValueError):
            register_transform("trim", lambda v: "clobbered")
        assert get_transform("trim")("  padded  ") == "padded"

    def test_an_explicit_override_replaces_it(self):
        register_transform("trim", lambda v: "replaced", override=True)
        assert get_transform("trim")("x") == "replaced"

    def test_a_non_callable_is_refused(self):
        with pytest.raises(ValueError, match="callable"):
            register_transform("bad", "not callable")  # type: ignore[arg-type]

    def test_an_empty_name_is_refused(self):
        with pytest.raises(ValueError, match="needs a name"):
            register_transform("  ", lambda v: v)


class TestRegisterRuleType:
    def test_a_registered_rule_type_can_be_used(self):
        def validator(value, rule):
            return str(value).endswith(rule.options.get("suffix", ""))

        register_validator("ends_with", validator, options=("suffix",))
        rule = Rule.from_dict(
            {"name": "ends", "field": "code", "type": "ends_with", "suffix": "-X"}
        )
        assert rule.options["suffix"] == "-X"
        frame = pd.DataFrame({"code": ["A-X", "B-Y"]})
        result = run_rules(frame, [rule])
        assert result.total_failures == 1
        assert result.issues[0].row == 1

    def test_the_options_survive_on_the_rule(self):
        register_validator("noop", lambda v, r: True, options=("threshold",))
        rule = Rule.from_dict(
            {"field": "x", "type": "noop", "threshold": 0.9}
        )
        assert rule.options == {"threshold": 0.9}

    def test_a_key_no_one_declared_is_still_a_typo(self):
        register_validator("noop", lambda v, r: True, options=("threshold",))
        with pytest.raises(RuleConfigError, match="unknown keys"):
            Rule.from_dict({"field": "x", "type": "noop", "threshhold": 0.9})

    def test_an_unknown_rule_type_is_listed_among_the_known(self):
        register_validator("noop", lambda v, r: True)
        with pytest.raises(RuleConfigError, match="noop"):
            Rule.from_dict({"field": "x", "type": "nope"})

    def test_a_duplicate_rule_type_is_refused(self):
        with pytest.raises(ValueError, match="already exists"):
            register_validator("range", lambda v, r: True)

    def test_the_built_in_rule_types_are_still_known(self):
        assert {"required", "range", "length", "list_of_values", "regex"} <= set(
            registered_rule_types()
        )
        _unregister_rule_type("nothing")


class TestRegisterOutputFormat:
    def test_a_registered_format_is_usable(self, tmp_path):
        def writer(df, path, **kwargs):
            target = _with_suffix(path, ".tsv")
            df.to_csv(target, sep="\t", index=False)
            return target

        register_format("tsv_custom", ".tsv", writer)
        frame = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        out = write_any(frame, tmp_path / "data", "tsv_custom")
        assert out.read_text().splitlines()[0] == "a\tb"

    def test_a_missing_dot_in_the_extension_is_refused(self):
        with pytest.raises(ValueError, match="must start with a dot"):
            register_format("weird", "txt", lambda df, path, **k: path)

    def test_a_duplicate_format_is_refused(self):
        with pytest.raises(ValueError, match="already exists"):
            register_format("csv", ".csv", lambda df, path, **k: path)

    def test_overriding_a_built_in_is_explicit(self, tmp_path):
        calls = {"n": 0}

        def writer(df, path, **kwargs):
            calls["n"] += 1
            return _with_suffix(path, ".csv")

        register_format("csv", ".csv", writer, override=True)
        write_any(pd.DataFrame({"a": [1]}), tmp_path / "x", "csv")
        assert calls["n"] == 1


def _with_suffix(path, suffix):
    from pathlib import Path

    target = Path(path)
    return target if target.suffix == suffix else target.with_suffix(suffix)


class TestRegisterDestination:
    def test_a_registered_destination_can_be_built(self):
        register_destination("memory", lambda config: _MemoryDestination(config["label"]))
        destination = build_destination("memory", {"label": "one"})
        assert destination.deliver(b"x", "f.csv").delivered

    def test_an_unknown_destination_names_the_known_ones(self):
        register_destination("memory", lambda config: _MemoryDestination("x"))
        with pytest.raises(ValueError, match="memory"):
            build_destination("carrier_pigeon")

    def test_a_duplicate_destination_is_refused(self):
        register_destination("memory", lambda config: _MemoryDestination("x"))
        with pytest.raises(ValueError, match="already exists"):
            register_destination("memory", lambda config: _MemoryDestination("y"))

    def test_the_registry_lists_what_is_available(self):
        register_destination("memory", lambda config: _MemoryDestination("x"))
        assert "memory" in registered_destinations()


class _MemoryDestination:
    name = "memory"

    def __init__(self, label: str):
        self.label = label

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt:
        return DeliveryReceipt(self.name, True, f"{self.label}:{filename}:{len(data)}")


class TestPluginRegistry:
    def test_an_inline_plugin_registers_several_capabilities(self):
        def register(registry: PluginRegistry):
            registry.transform("shout", lambda v: str(v).upper())
            registry.rule_type("always", lambda v, r: True)
            registry.output_format("tsv_custom", ".tsv", lambda df, p, **k: _with_suffix(p, ".tsv"))
            registry.destination("memory", lambda config: _MemoryDestination("m"))

        registry = load_plugin(register, PluginSpec(name="demo", version="1.2"))
        assert registry.summary()["accepted"] == 4
        assert registry.summary()["refused"] == 0

    def test_a_refused_claim_does_not_abandon_the_rest(self):
        def register(registry: PluginRegistry):
            registry.transform("trim", lambda v: "clobber")
            registry.transform("shout", lambda v: str(v).upper())

        registry = load_plugin(register, PluginSpec(name="partial"))
        summary = registry.summary()
        assert summary["accepted"] == 1
        assert summary["refused"] == 1
        assert get_transform("shout")("x") == "X"

    def test_the_refusal_detail_explains_why(self):
        def register(registry: PluginRegistry):
            registry.transform("trim", lambda v: v)

        registry = load_plugin(register, PluginSpec(name="explain"))
        detail = registry.registered[0].detail
        assert detail and "already exists" in detail

    def test_a_module_without_register_is_rejected(self):
        with pytest.raises(PluginError, match="register"):
            load_plugin("json")

    def test_an_unimportable_plugin_is_reported(self):
        with pytest.raises(PluginError, match="Could not import"):
            load_plugin("no_such_module_anywhere")

    def test_loaded_plugins_are_listed(self):
        load_plugin(lambda registry: None, PluginSpec(name="listed"))
        assert any(entry["plugin"] == "listed" for entry in active_plugins())

    def test_plugins_are_recorded_by_kind(self):
        def register(registry: PluginRegistry):
            registry.transform("shout", lambda v: v)
            registry.destination("memory", lambda config: _MemoryDestination("m"))

        registry = load_plugin(register, PluginSpec(name="kinds"))
        assert registry.claimed("transform") == ["shout"]
        assert registry.claimed("destination") == ["memory"]


class TestLifecycleEvents:
    def test_a_subscriber_receives_an_event(self):
        seen = []
        bus = EventBus()
        bus.subscribe(LifecycleEvent.RUN_COMPLETED, lambda e, p: seen.append((e, p)))
        bus.emit(LifecycleEvent.RUN_COMPLETED, {"rows": 3})
        assert seen == [("run.completed", {"rows": 3})]

    def test_a_subscriber_does_not_receive_other_events(self):
        seen = []
        bus = EventBus()
        bus.subscribe(LifecycleEvent.RUN_COMPLETED, lambda e, p: seen.append(e))
        bus.emit(LifecycleEvent.RUN_FAILED)
        assert seen == []

    def test_a_wildcard_subscriber_receives_everything(self):
        seen = []
        bus = EventBus()
        bus.subscribe("*", lambda e, p: seen.append(e))
        bus.emit(LifecycleEvent.RUN_STARTED)
        bus.emit(LifecycleEvent.RUN_FAILED)
        assert seen == ["run.started", "run.failed"]

    def test_a_raising_handler_does_not_raise_into_the_emitter(self):
        def boom(event, payload):
            raise RuntimeError("observer is broken")

        bus = EventBus()
        bus.subscribe(LifecycleEvent.RUN_COMPLETED, boom, name="boom")
        receipts = bus.emit(LifecycleEvent.RUN_COMPLETED)
        assert receipts[0].ok is False
        assert "observer is broken" in receipts[0].detail

    def test_the_failed_receipt_names_the_handler(self):
        bus = EventBus()
        bus.subscribe("*", lambda e, p: (_ for _ in ()).throw(ValueError("x")), name="bad")
        assert bus.emit("anything")[0].handler == "bad"

    def test_a_non_callable_handler_is_refused(self):
        with pytest.raises(ValueError, match="callable"):
            EventBus().subscribe("run.completed", "nope")  # type: ignore[arg-type]

    def test_a_subscriber_can_be_removed(self):
        bus = EventBus()
        bus.subscribe("run.completed", lambda e, p: None, name="temp")
        assert bus.unsubscribe("run.completed", "temp") is True
        assert bus.subscribers("run.completed") == []

    def test_removing_an_absent_subscriber_reports_false(self):
        assert EventBus().unsubscribe("run.completed", "ghost") is False

    def test_subscribers_list_both_exact_and_wildcard(self):
        bus = EventBus()
        bus.subscribe("run.completed", lambda e, p: None, name="exact")
        bus.subscribe("*", lambda e, p: None, name="all")
        assert set(bus.subscribers("run.completed")) == {"exact", "all"}

    def test_the_module_level_bus_is_shared(self):
        seen = []
        subscribe(LifecycleEvent.OUTPUT_WRITTEN, lambda e, p: seen.append(p), name="modtest")
        emit(LifecycleEvent.OUTPUT_WRITTEN, {"file": "out.csv"})
        assert seen == [{"file": "out.csv"}]

    def test_loading_a_plugin_emits_an_event(self):
        seen = []
        subscribe(LifecycleEvent.PLUGIN_LOADED, lambda e, p: seen.append(p), name="plugwatch")
        load_plugin(lambda registry: None, PluginSpec(name="emitter"))
        assert any(item["plugin"]["name"] == "emitter" for item in seen)
