"""Interface tests for the profiling extension's config block and adapters.

Written before the implementation. The block follows the one config pattern the
rest of the platform uses: resolved through ``app_files/core/config.py``
(``defaults < YAML < env < CLI``), refused on an unknown key, and inert when a
config declares no ``profiling:`` block.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.profiling.profiling_block import (
    ProfilingBinding,
    ProfilingBlockError,
    bind_profiling,
    profiling_from_config,
)

BLOCK = {
    "profiling": {
        "statistics": {"enabled": True, "top_values": 3},
        "patterns": {"enabled": True},
        "outliers": {"enabled": True, "method": "iqr", "k": 1.5},
    }
}


def test_a_config_without_the_block_binds_nothing():
    assert profiling_from_config({}) is None
    assert profiling_from_config({"fields": []}) is None


def test_an_empty_block_binds_nothing():
    assert profiling_from_config({"profiling": {}}) is None


def test_the_block_resolves_into_a_binding():
    binding = profiling_from_config(BLOCK)
    assert isinstance(binding, ProfilingBinding)
    assert binding.method == "iqr"
    assert binding.k == 1.5


def test_the_three_sections_default_to_off():
    binding = profiling_from_config({"profiling": {"statistics": {"enabled": True}}})
    assert binding.statistics_enabled is True
    assert binding.patterns_enabled is False
    assert binding.outliers_enabled is False


def test_an_unknown_key_is_refused():
    with pytest.raises(ProfilingBlockError, match="unknown key"):
        profiling_from_config({"profiling": {"statistic": {"enabled": True}}})


def test_an_unknown_nested_key_is_refused():
    with pytest.raises(ProfilingBlockError, match="unknown key"):
        profiling_from_config(
            {"profiling": {"outliers": {"enabled": True, "kk": 1}}}
        )


def test_an_unknown_outlier_method_is_refused():
    with pytest.raises(ProfilingBlockError, match="method"):
        profiling_from_config(
            {"profiling": {"outliers": {"enabled": True, "method": "vibes"}}}
        )


def test_a_non_mapping_block_is_refused():
    with pytest.raises(ProfilingBlockError, match="mapping"):
        profiling_from_config({"profiling": ["not", "a", "mapping"]})


def test_env_overrides_the_yaml_layer(monkeypatch):
    monkeypatch.setenv("AUTOFLOW_PROFILING_OUTLIERS_K", "3.0")
    binding = profiling_from_config(BLOCK)
    assert binding.k == 3.0


def test_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("AUTOFLOW_PROFILING_OUTLIERS_K", "3.0")
    binding = profiling_from_config(BLOCK, cli={"outliers": {"k": 2.0}})
    assert binding.k == 2.0


def test_provenance_records_where_a_value_came_from(monkeypatch):
    from app_files.core import Layer

    monkeypatch.setenv("AUTOFLOW_PROFILING_OUTLIERS_K", "3.0")
    binding = profiling_from_config(BLOCK, with_provenance=True)
    assert binding.source_of("outliers.k") == Layer.ENV


# ------------------------------------------------------------------- binding
def test_bind_profiling_runs_the_declared_sections():
    frame = pd.DataFrame({"amount": [1.0, 2, 3, 4, 5, 1000.0], "who": ["a@x.com"] * 6})
    binding = bind_profiling(frame, BLOCK)
    assert binding.statistics  # one ColumnStats per column
    assert binding.patterns
    assert binding.outliers["amount"].count == 1


def test_bind_profiling_writes_nothing_for_an_undeclared_config():
    frame = pd.DataFrame({"a": [1, 2]})
    assert bind_profiling(frame, {}) is None


def test_a_disabled_section_produces_no_work():
    frame = pd.DataFrame({"amount": [1.0, 2, 3, 4, 5, 1000.0]})
    binding = bind_profiling(
        frame,
        {"profiling": {"statistics": {"enabled": True}, "outliers": {"enabled": False}}},
    )
    assert binding.statistics
    assert binding.outliers == {}


def test_the_binding_summarises_into_json_safe_types():
    frame = pd.DataFrame({"amount": [1.0, 2, 3, 4, 5, 1000.0], "who": ["a@x.com"] * 6})
    summary = bind_profiling(frame, BLOCK).summary()
    import json

    json.dumps(summary)  # must not raise
    assert "outliers" in summary
    assert "patterns" in summary


def test_outliers_are_only_computed_for_numeric_columns():
    frame = pd.DataFrame({"who": ["a@x.com", "b@y.org"], "n": [1.0, 2.0]})
    binding = bind_profiling(frame, BLOCK)
    assert "n" in binding.outliers
    assert "who" not in binding.outliers
