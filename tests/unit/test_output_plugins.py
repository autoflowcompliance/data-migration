"""The plugin system for custom output formats."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.output import (
    PluginError,
    available_formats,
    clear_plugins,
    get_plugin,
    plugin_report,
    register_plugin,
    unregister_plugin,
    write_any_extended,
    write_with_plugin,
)

FRAME = pd.DataFrame({"email": ["ann@x.com"], "name": ["Ann"]})


@pytest.fixture(autouse=True)
def isolated_registry():
    clear_plugins()
    yield
    clear_plugins()


def _fixed_width(frame, destination):
    destination.write_text("|".join(map(str, frame.columns)) + "\n")
    return destination


def test_a_plugin_becomes_an_available_format():
    register_plugin("fixed", _fixed_width, extension=".txt")
    assert "fixed" in available_formats()
    assert "csv" in available_formats()


def test_a_plugin_writes_through_its_own_writer(tmp_path):
    register_plugin("fixed", _fixed_width, extension=".txt")
    target = write_with_plugin("fixed", FRAME, tmp_path / "out.txt")
    assert "email|name" in target.read_text()


def test_an_unknown_plugin_is_a_clear_error():
    with pytest.raises(PluginError, match="No plugin named"):
        get_plugin("nope")


def test_a_plugin_name_may_not_shadow_a_builtin_by_default():
    with pytest.raises(PluginError, match="built-in"):
        register_plugin("csv", _fixed_width)


def test_shadowing_a_builtin_is_possible_when_asked():
    register_plugin("csv", _fixed_width, allow_builtin_override=True)
    assert get_plugin("csv") is _fixed_width


def test_duplicate_plugin_names_are_rejected():
    register_plugin("fixed", _fixed_width)
    with pytest.raises(PluginError, match="already registered"):
        register_plugin("fixed", _fixed_width)


def test_a_non_callable_writer_is_rejected():
    with pytest.raises(PluginError, match="not callable"):
        register_plugin("bad", "not a function")


def test_an_empty_name_is_rejected():
    with pytest.raises(PluginError, match="non-empty"):
        register_plugin("  ", _fixed_width)


def test_a_failing_plugin_names_itself_in_the_error(tmp_path):
    def broken(frame, destination):
        raise RuntimeError("disk full")

    register_plugin("broken", broken)
    with pytest.raises(PluginError, match="broken.*disk full"):
        write_with_plugin("broken", FRAME, tmp_path / "out.txt")


def test_the_extension_is_normalised():
    plugin = register_plugin("fixed", _fixed_width, extension="txt")
    assert plugin.extension == ".txt"


def test_unregistering_removes_the_plugin():
    register_plugin("fixed", _fixed_width)
    assert unregister_plugin("fixed") is True
    assert "fixed" not in available_formats()
    assert unregister_plugin("fixed") is False


def test_plugin_report_marks_builtins():
    register_plugin("fixed", _fixed_width)
    report = {item["name"]: item for item in plugin_report()}
    assert report["fixed"]["builtin"] is False


def test_write_any_extended_still_writes_builtins(tmp_path):
    target = write_any_extended(FRAME, tmp_path / "out", "csv")
    assert target.suffix == ".csv"
    assert target.exists()


def test_write_any_extended_uses_a_plugin(tmp_path):
    register_plugin("fixed", _fixed_width, extension=".txt")
    target = write_any_extended(FRAME, tmp_path / "out", "fixed")
    assert target.exists()
    assert "email|name" in target.read_text()


def test_write_any_extended_names_plugins_in_its_unknown_format_error(tmp_path):
    register_plugin("fixed", _fixed_width)
    with pytest.raises(ValueError, match="fixed"):
        write_any_extended(FRAME, tmp_path / "out", "wat")


def test_a_plugin_returning_bytes_is_written(tmp_path):
    def binary(frame, destination):
        return b"\x00\x01"

    register_plugin("binary", binary, extension=".bin")
    target = write_with_plugin("binary", FRAME, tmp_path / "out.bin")
    assert target.read_bytes() == b"\x00\x01"