"""Layer 17 end to end: a plugin-registered transform runs inside the real
pipeline, and a lifecycle event fires on load.

The point of the layer is that a buyer extends the tool without touching core.
So the test drives the core: a registered transform is used through the
mapping config path, and a custom rule type flows into the rules engine.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.ingestion import read_any
from app_files.output import register_format, write_any
from app_files.pipeline import run_pipeline
from app_files.plugins import (
    LifecycleEvent,
    PluginSpec,
    active_plugins,
    load_plugin,
    subscribe,
)
from app_files.rules import register_validator, run_rules
from app_files.rules.schema import Rule
from app_files.transforms import register_transform


@pytest.fixture(autouse=True)
def _restore_registries():
    from app_files.output.destinations import DESTINATION_TYPES
    from app_files.output.formats import FORMATS
    from app_files.rules.validators import VALIDATORS
    from app_files.transforms import TRANSFORMS

    snapshots = [
        (TRANSFORMS, dict(TRANSFORMS)),
        (FORMATS, dict(FORMATS)),
        (VALIDATORS, dict(VALIDATORS)),
        (DESTINATION_TYPES, dict(DESTINATION_TYPES)),
    ]
    yield
    for registry, snapshot in snapshots:
        registry.clear()
        registry.update(snapshot)


class TestPluginTransformInThePipeline:
    def test_a_registered_transform_is_reachable_by_name(self):
        register_transform("shout", lambda value: str(value).upper())
        from app_files.transforms import get_transform

        assert get_transform("shout")("hello") == "HELLO"

    def test_a_plugin_transform_runs_through_the_pipeline(self, contacts_csv, tmp_path):
        """Register a transform, reference it from a mapping config, run the pipeline.

        The config is a real config file, read by the real loader. The only new
        thing is the transform name, which the core resolves at map time.
        """
        from app_files.mappers import load_mapping_config
        from app_files.mappers.yaml_mapper import map_data

        register_transform("shout", lambda value: str(value).upper())

        config_path = tmp_path / "shout.yaml"
        config_path.write_text(
            "crm: shout_demo\n"
            "fields:\n"
            "  - name: email\n"
            "    source: Email Address\n"
            "    transform: shout\n"
        )
        config = load_mapping_config(config_path)
        frame = pd.DataFrame({"Email Address": ["ada@example.com", "alan@example.com"]})
        mapped = map_data(frame, config)
        assert mapped.frame["email"].tolist() == ["ADA@EXAMPLE.COM", "ALAN@EXAMPLE.COM"]

    def test_the_pipeline_still_produces_its_usual_output(self, contacts_csv):
        """A registered transform must not disturb a run that does not use it."""
        register_transform("shout", lambda value: str(value).upper())
        source = read_any(contacts_csv)
        result = run_pipeline(source, crm="hubspot")
        assert len(result.clean_frame) == 6


class TestPluginRuleTypeInTheEngine:
    def test_a_registered_rule_type_fires_on_the_real_engine(self):
        register_validator(
            "starts_with",
            lambda value, rule: str(value).lower().startswith(
                str(rule.options.get("prefix", "")).lower()
            ),
            options=("prefix",),
        )
        rule = Rule.from_dict(
            {"name": "acct_prefix", "field": "account", "type": "starts_with", "prefix": "AC"}
        )
        frame = pd.DataFrame({"account": ["AC-1", "AC-2", "ZZ-9"]})
        result = run_rules(frame, [rule])
        assert result.rules_run == 1
        assert result.total_failures == 1
        assert result.issues[0].row == 2

    def test_an_unresolvable_plugin_rule_is_not_silently_dropped(self):
        register_validator("always_pass", lambda value, rule: True)
        rule = Rule.from_dict({"field": "account", "type": "always_pass"})
        frame = pd.DataFrame({"other": [1]})
        # The column is absent, so the rule is skipped -- and the engine says so
        # by running zero rules rather than claiming a clean result.
        assert run_rules(frame, [rule]).rules_run == 0


class TestPluginOutputFormatInTheWriter:
    def test_a_registered_format_writes_through_write_any(self, tmp_path):
        def writer(df, path, **kwargs):
            target = path.with_suffix(".tsv")
            df.to_csv(target, sep="\t", index=False)
            return target

        register_format("tsv_custom", ".tsv", writer)
        out = write_any(pd.DataFrame({"a": [1], "b": [2]}), tmp_path / "clean", "tsv_custom")
        assert out.read_text().splitlines()[0] == "a\tb"


class TestPluginLoadEndToEnd:
    def test_one_plugin_registers_several_capabilities_at_once(self):
        def register(registry):
            registry.transform("plus_one", lambda value: int(value) + 1)
            registry.rule_type("even", lambda value, rule: int(value) % 2 == 0)
            registry.output_format("plus", ".plus", lambda df, path, **k: path)

        spec = PluginSpec(name="arith", version="1.0", description="small arithmetic plugin")
        registry = load_plugin(register, spec)
        summary = registry.summary()
        assert summary["accepted"] == 3
        assert summary["plugin"]["version"] == "1.0"
        assert any(entry["plugin"] == "arith" for entry in active_plugins())

    def test_loading_emits_a_lifecycle_event_a_subscriber_sees(self):
        seen = []
        subscribe(LifecycleEvent.PLUGIN_LOADED, lambda e, p: seen.append(p), name="e2e")
        load_plugin(lambda registry: None, PluginSpec(name="watched"))
        assert any(item["plugin"]["name"] == "watched" for item in seen)
