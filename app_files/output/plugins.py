"""A plugin system for custom output formats.

The four built-in writers cover csv, excel, json and sql. A buyer who needs a
fifth — Parquet, a fixed-width mainframe layout, an in-house format — can add
one without touching this repository: a plugin is any callable
``(frame, destination) -> Path`` registered against a name.

Registration is explicit and namespaced. A plugin can be registered from the
entry-point group ``dataflow.output_formats`` (so an installed package announces
itself) or registered directly in code, and either way it appears in
:func:`available_formats` and becomes usable through ``write_any``. A plugin
that raises is reported with its own name, not a mystery traceback.

Built-in names cannot be replaced by default: a plugin that quietly shadows
``csv`` would change every existing run, so shadowing is an opt-in.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

ENTRY_POINT_GROUP = "dataflow.output_formats"


class PluginError(RuntimeError):
    """Raised for a plugin that cannot be registered or that fails to run."""


Writer = Callable[[pd.DataFrame, Path], Path]

_BUILTIN_NAMES = frozenset({"csv", "excel", "json", "sql"})
_PLUGINS: dict[str, Writer] = {}


@dataclass(frozen=True)
class Plugin:
    name: str
    writer: Writer
    extension: str = ".dat"
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "extension": self.extension,
            "description": self.description,
            "builtin": self.name in _BUILTIN_NAMES,
        }


def register_plugin(
    name: str,
    writer: Writer,
    *,
    extension: str = ".dat",
    description: str = "",
    allow_builtin_override: bool = False,
) -> Plugin:
    """Register an output format under ``name``."""
    key = str(name).strip().lower()
    if not key:
        raise PluginError("A plugin needs a non-empty name.")
    if not callable(writer):
        raise PluginError(f"Plugin {key!r} writer is not callable.")
    if key in _BUILTIN_NAMES and not allow_builtin_override:
        raise PluginError(
            f"{key!r} is a built-in format. Pass allow_builtin_override=True to replace it."
        )
    if key in _PLUGINS and not allow_builtin_override:
        raise PluginError(f"A plugin named {key!r} is already registered.")
    if not extension.startswith("."):
        extension = f".{extension}"

    _PLUGINS[key] = writer
    return Plugin(name=key, writer=writer, extension=extension, description=description)


def unregister_plugin(name: str) -> bool:
    return _PLUGINS.pop(str(name).strip().lower(), None) is not None


def clear_plugins() -> None:
    _PLUGINS.clear()


def get_plugin(name: str) -> Writer:
    key = str(name).strip().lower()
    if key not in _PLUGINS:
        known = ", ".join(sorted(_PLUGINS)) or "none"
        raise PluginError(f"No plugin named {key!r}. Registered plugins: {known}.")
    return _PLUGINS[key]


def available_formats() -> list[str]:
    return sorted(_BUILTIN_NAMES | set(_PLUGINS))


def plugin_report() -> list[dict[str, Any]]:
    return [
        Plugin(name=name, writer=_PLUGINS[name], extension=".dat").as_dict()
        for name in sorted(_PLUGINS)
    ]


def write_with_plugin(name: str, frame: pd.DataFrame, destination: str | Path) -> Path:
    """Run a registered plugin, wrapping its failure with its own name."""
    plugin = get_plugin(name)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = plugin(frame, target)
    except Exception as error:  # noqa: BLE001 - name the plugin, do not leak the trace
        raise PluginError(
            f"Output plugin {name!r} failed: {type(error).__name__}: {error}"
        ) from error
    if isinstance(result, Path):
        return result
    if isinstance(result, (str, bytes)):
        target = target if target.suffix else target.with_suffix(".dat")
        target.write_bytes(result if isinstance(result, bytes) else result.encode("utf-8"))
        return target
    return target


def load_entry_point_plugins(group: str = ENTRY_POINT_GROUP) -> list[str]:
    """Discover plugins announced by installed packages.

    Missing metadata is not an error: a source checkout with no plugins
    installed is the normal case, and it returns an empty list.
    """
    loaded: list[str] = []
    try:
        from importlib.metadata import entry_points
    except ImportError:  # pragma: no cover - Python < 3.10
        return loaded

    try:
        discovered = entry_points(group=group)
    except TypeError:  # pragma: no cover - older API shape
        discovered = entry_points().get(group, [])
    except Exception:  # noqa: BLE001
        return loaded

    for entry in discovered:
        try:
            factory = entry.load()
            plugin = factory() if callable(factory) else factory
            if isinstance(plugin, Plugin):
                register_plugin(
                    plugin.name, plugin.writer, extension=plugin.extension,
                    description=plugin.description,
                )
                loaded.append(plugin.name)
        except Exception:  # noqa: BLE001 - one bad plugin must not stop the rest
            continue
    return loaded