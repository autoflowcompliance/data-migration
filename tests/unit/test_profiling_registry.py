"""Interface tests for the plugin-registry extension.

The specification is explicit: extend ``plugins/registry.py``, do not build a
second registry. A profiling extension registers through the same
``PluginRegistry`` and its claims are recorded the same way, including the
refusal of a duplicate claim.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.plugins.registry import PluginRegistry, load_plugin
from app_files.profiling.registry import (
    PROFILER_KIND,
    get_profiler,
    profiler_names,
    register_profiler,
)


@pytest.fixture(autouse=True)
def _restore_registry():
    """Snapshot and restore the profiler registry around every test."""
    from app_files.profiling import registry as mod

    snapshot = dict(mod.PROFILERS)
    yield
    mod.PROFILERS.clear()
    mod.PROFILERS.update(snapshot)


def test_the_built_in_profilers_are_registered():
    assert "statistics" in profiler_names()
    assert "patterns" in profiler_names()


def test_registering_a_new_profiler_extends_the_registry():
    register_profiler("always_five", lambda frame: 5)
    assert "always_five" in profiler_names()
    assert get_profiler("always_five")(pd.DataFrame()) == 5


def test_a_duplicate_name_is_refused_without_override():
    with pytest.raises(ValueError, match="already exists"):
        register_profiler("statistics", lambda frame: 0)


def test_override_replaces_a_registration():
    register_profiler("statistics", lambda frame: 0, override=True)
    assert get_profiler("statistics")(pd.DataFrame()) == 0


def test_a_non_callable_registration_is_refused():
    with pytest.raises(ValueError, match="callable"):
        register_profiler("bad", "not callable")


def test_an_empty_name_is_refused():
    with pytest.raises(ValueError, match="name"):
        register_profiler("", lambda frame: 1)


def test_an_unknown_profiler_raises_a_named_error():
    with pytest.raises(KeyError, match="nope"):
        get_profiler("nope")


def test_the_plugin_registry_can_register_a_profiler():
    """The extension point is the existing registry, not a parallel one."""
    registry = PluginRegistry()
    registry.profiler("from_plugin", lambda frame: len(frame))
    assert registry.claimed(PROFILER_KIND) == ["from_plugin"]
    assert get_profiler("from_plugin")(pd.DataFrame({"a": [1, 2, 3]})) == 3


def test_a_refused_claim_is_recorded_not_raised():
    register_profiler("taken", lambda frame: 1)
    registry = PluginRegistry()
    registry.profiler("taken", lambda frame: 2)
    assert registry.claimed(PROFILER_KIND) == []
    summary = registry.summary()
    assert summary["refused"] == 1
    assert summary["registered"][0]["ok"] is False


def test_load_plugin_registers_through_the_same_registry():
    def register(registry):
        registry.profiler("via_module", lambda frame: 42)

    result = load_plugin(register)
    assert result.claimed(PROFILER_KIND) == ["via_module"]
