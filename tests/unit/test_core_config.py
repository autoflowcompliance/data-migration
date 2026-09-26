"""The config precedence chain: defaults < YAML < env < CLI.

The specification asked for "one config pattern" and a precedence chain, but
before this the chain was a description of nothing — YAML blocks were read with
no env layer and env vars were read ad hoc. These tests pin the order so every
new module resolves config the same way, and pin the two safety rules that make
the chain safe to rely on: fail closed, and absence is not an empty value.

Written before the implementation, against the interface the resolver exposes.
"""

from __future__ import annotations

import pytest

from app_files.core.config import ConfigError, Layer, resolve


class TestOrder:
    """Later layers win, in the documented order."""

    def test_default_applies_when_nothing_else_is_set(self):
        assert resolve("quality", {"sla": {"completeness": 0.98}}) == {
            "sla": {"completeness": 0.98}
        }

    def test_yaml_overrides_the_default(self):
        assert resolve(
            "quality",
            {"sla": {"completeness": 0.98}},
            yaml_values={"sla": {"completeness": 0.90}},
        ) == {"sla": {"completeness": 0.90}}

    def test_env_overrides_yaml(self):
        assert resolve(
            "quality",
            {"sla": {"completeness": 0.98}},
            yaml_values={"sla": {"completeness": 0.90}},
            env={"AUTOFLOW_QUALITY_SLA_COMPLETENESS": "0.95"},
        ) == {"sla": {"completeness": 0.95}}

    def test_cli_overrides_env(self):
        assert resolve(
            "quality",
            {"sla": {"completeness": 0.98}},
            yaml_values={"sla": {"completeness": 0.90}},
            env={"AUTOFLOW_QUALITY_SLA_COMPLETENESS": "0.95"},
            cli={"sla": {"completeness": 0.80}},
        ) == {"sla": {"completeness": 0.80}}

    def test_the_full_chain_resolves_to_the_last_layer_that_spoke(self):
        # Every layer supplies a value; only the narrowest survives.
        resolved = resolve(
            "quality",
            {"threshold": 0.02, "action": "alert"},
            yaml_values={"threshold": 0.03},
            env={"AUTOFLOW_QUALITY_THRESHOLD": "0.04"},
            cli={"threshold": 0.05},
        )
        assert resolved["threshold"] == 0.05
        # A key no later layer mentioned keeps the value from the layer below.
        assert resolved["action"] == "alert"

    def test_merging_is_per_key_not_per_layer(self):
        # YAML sets one key, env sets a different one; both survive.
        resolved = resolve(
            "quality",
            {"a": 1, "b": 2},
            yaml_values={"a": 10},
            env={"AUTOFLOW_QUALITY_B": "20"},
        )
        assert resolved == {"a": 10, "b": 20}


class TestEnvParsing:
    """Env values arrive as strings and must land as the right type."""

    def test_a_number_is_parsed_as_a_number(self):
        resolved = resolve(
            "quality", {"threshold": 0.02}, env={"AUTOFLOW_QUALITY_THRESHOLD": "0.5"}
        )
        assert resolved["threshold"] == 0.5
        assert isinstance(resolved["threshold"], float)

    def test_an_integer_keeps_its_type(self):
        resolved = resolve(
            "quality", {"retries": 1}, env={"AUTOFLOW_QUALITY_RETRIES": "5"}
        )
        assert resolved["retries"] == 5
        assert isinstance(resolved["retries"], int)

    def test_booleans_are_parsed_from_the_usual_spellings(self):
        for spelling in ("true", "True", "1", "yes", "on"):
            resolved = resolve(
                "quality", {"enabled": False}, env={"AUTOFLOW_QUALITY_ENABLED": spelling}
            )
            assert resolved["enabled"] is True, spelling
        for spelling in ("false", "False", "0", "no", "off"):
            resolved = resolve(
                "quality", {"enabled": True}, env={"AUTOFLOW_QUALITY_ENABLED": spelling}
            )
            assert resolved["enabled"] is False, spelling

    def test_a_json_list_is_parsed(self):
        resolved = resolve(
            "observability",
            {"channels": []},
            env={"AUTOFLOW_OBSERVABILITY_CHANNELS": '["slack", "email"]'},
        )
        assert resolved["channels"] == ["slack", "email"]

    def test_a_plain_string_stays_a_string(self):
        resolved = resolve(
            "quality", {"action": "alert"}, env={"AUTOFLOW_QUALITY_ACTION": "block"}
        )
        assert resolved["action"] == "block"

    def test_a_type_mismatch_against_the_default_is_reported_not_ignored(self):
        # Fail closed: a malformed override raises rather than silently
        # reverting to the default, which would hide a typo'd deployment.
        with pytest.raises(ConfigError, match="AUTOFLOW_QUALITY_THRESHOLD"):
            resolve(
                "quality",
                {"threshold": 0.02},
                env={"AUTOFLOW_QUALITY_THRESHOLD": "not-a-number"},
            )

    def test_an_unrelated_env_variable_is_ignored(self):
        resolved = resolve(
            "quality", {"threshold": 0.02}, env={"PATH": "/usr/bin", "HOME": "/root"}
        )
        assert resolved == {"threshold": 0.02}


class TestAbsenceVersusEmpty:
    """A layer that said nothing is not a layer that said 'empty'."""

    def test_an_absent_key_falls_through_to_the_layer_below(self):
        resolved = resolve(
            "quality", {"threshold": 0.02}, yaml_values={"other": 1}
        )
        assert resolved["threshold"] == 0.02

    def test_an_explicit_empty_value_is_a_value(self):
        resolved = resolve(
            "quality", {"action": "alert"}, yaml_values={"action": ""}
        )
        assert resolved["action"] == ""

    def test_an_explicit_none_is_a_value(self):
        resolved = resolve(
            "quality", {"action": "alert"}, yaml_values={"action": None}
        )
        assert resolved["action"] is None

    def test_an_empty_yaml_block_does_not_erase_the_default(self):
        resolved = resolve("quality", {"threshold": 0.02}, yaml_values={})
        assert resolved["threshold"] == 0.02


class TestNamespacing:
    """Env keys are namespaced per module so two modules cannot collide."""

    def test_one_module_does_not_read_another_modules_env(self):
        resolved = resolve(
            "quality",
            {"threshold": 0.02},
            env={"AUTOFLOW_DRIFT_THRESHOLD": "0.9"},
        )
        assert resolved["threshold"] == 0.02

    def test_the_namespace_is_uppercased_and_joined_with_underscores(self):
        resolved = resolve(
            "statistical_drift",
            {"tests": [{"threshold": 0.05}]},
            env={"AUTOFLOW_STATISTICAL_DRIFT_TESTS": '[{"threshold": 0.01}]'},
        )
        assert resolved["tests"] == [{"threshold": 0.01}]


class TestFailClosed:
    """Invalid config produces a safe value, never a silent wrong answer."""

    def test_yaml_that_is_not_a_mapping_is_refused(self):
        with pytest.raises(ConfigError, match="quality"):
            resolve("quality", {"threshold": 0.02}, yaml_values=["not", "a", "mapping"])

    def test_cli_that_is_not_a_mapping_is_refused(self):
        with pytest.raises(ConfigError, match="quality"):
            resolve("quality", {"threshold": 0.02}, cli="nope")

    def test_the_error_names_the_module_and_the_layer(self):
        with pytest.raises(ConfigError) as excinfo:
            resolve("quality", {"a": 1}, yaml_values=42)
        message = str(excinfo.value)
        assert "quality" in message
        assert "yaml" in message.lower()

    def test_a_non_mapping_nested_value_is_refused(self):
        with pytest.raises(ConfigError, match="sla"):
            resolve("quality", {"sla": {"completeness": 0.98}}, yaml_values={"sla": 5})


class TestProvenance:
    """Every resolved key can say which layer supplied it."""

    def test_provenance_names_the_winning_layer(self):
        resolved = resolve(
            "quality",
            {"threshold": 0.02},
            env={"AUTOFLOW_QUALITY_THRESHOLD": "0.04"},
            cli={"threshold": 0.05},
            with_provenance=True,
        )
        assert resolved.provenance["threshold"] is Layer.CLI

    def test_provenance_falls_back_to_default(self):
        resolved = resolve("quality", {"threshold": 0.02}, with_provenance=True)
        assert resolved.provenance["threshold"] is Layer.DEFAULTS

    def test_provenance_is_available_for_a_nested_key(self):
        resolved = resolve(
            "quality",
            {"sla": {"completeness": 0.98}},
            yaml_values={"sla": {"completeness": 0.90}},
            with_provenance=True,
        )
        assert resolved.provenance["sla.completeness"] is Layer.YAML

    def test_the_resolved_mapping_behaves_like_a_dict(self):
        resolved = resolve(
            "quality", {"sla": {"completeness": 0.98}}, with_provenance=True
        )
        assert resolved["sla"]["completeness"] == 0.98
        assert resolved == {"sla": {"completeness": 0.98}}
