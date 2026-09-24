"""A plugin registers capabilities and reports what it registered.

A plugin is a module with a ``register(registry)`` function. Loading it runs
that function against a registry that proxies the per-layer registration
points and records every name a plugin claims. The record is what makes a
plugin auditable: after a load, the operator can see exactly which transform,
rule type, format or destination came from where.

The registry also enforces the additive rule in one place. A plugin that tries
to take a name that already exists is refused, and the refusal is recorded
rather than raised, so one bad claim does not abandon the rest of the plugin.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class PluginError(RuntimeError):
    """Raised when a plugin cannot be loaded at all."""


@dataclass
class PluginSpec:
    """What a plugin declared about itself."""

    name: str
    version: str = "0"
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "version": self.version, "description": self.description}


@dataclass
class RegisteredItem:
    kind: str
    name: str
    ok: bool
    detail: str | None = None


@dataclass
class PluginRegistry:
    """The collection of registration points a plugin may call into.

    Each ``register_*`` delegates to the owning layer's registry, so there is
    one source of truth per capability. This class adds the bookkeeping, not a
    second registry.
    """

    spec: PluginSpec | None = None
    registered: list[RegisteredItem] = field(default_factory=list)

    # Each of these returns the layer's own registration call.
    def transform(self, name: str, function: Callable[[Any], Any], override: bool = False) -> None:
        from app_files.transforms import register_transform

        self._claim("transform", name, lambda: register_transform(name, function, override))

    def rule_type(
        self,
        rule_type: str,
        validator: Callable[..., bool],
        options: tuple[str, ...] | list[str] | None = None,
        override: bool = False,
    ) -> None:
        from app_files.rules.validators import register_validator

        self._claim(
            "rule_type",
            rule_type,
            lambda: register_validator(rule_type, validator, options, override),
        )

    def output_format(
        self,
        name: str,
        extension: str,
        writer: Callable[..., Any],
        override: bool = False,
    ) -> None:
        from app_files.output.formats import register_format

        self._claim(
            "output_format",
            name,
            lambda: register_format(name, extension, writer, override),
        )

    def destination(
        self,
        name: str,
        factory: Callable[[dict[str, Any]], Any],
        override: bool = False,
    ) -> None:
        from app_files.output.destinations import register_destination

        self._claim("destination", name, lambda: register_destination(name, factory, override))

    def _claim(self, kind: str, name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except Exception as exc:  # noqa: BLE001 - a refused claim is data, not a crash
            self.registered.append(RegisteredItem(kind, str(name), False, str(exc)))
        else:
            self.registered.append(RegisteredItem(kind, str(name), True, None))

    def summary(self) -> dict[str, Any]:
        accepted = [item for item in self.registered if item.ok]
        return {
            "plugin": self.spec.as_dict() if self.spec else None,
            "registered": [item.__dict__ for item in self.registered],
            "accepted": len(accepted),
            "refused": len(self.registered) - len(accepted),
        }

    def claimed(self, kind: str) -> list[str]:
        return [item.name for item in self.registered if item.ok and item.kind == kind]


_LOADED: dict[str, PluginRegistry] = {}


def load_plugin(target: Any, spec: PluginSpec | None = None) -> PluginRegistry:
    """Load a plugin from a module, a module path, or a callable.

    A module exposes ``register(registry)``. Passing a callable is the same
    thing for an inline plugin, which is what a test or an embedder uses.
    """
    registry = PluginRegistry(spec=spec)

    if callable(target) and not isinstance(target, str):
        target(registry)
        _LOADED[registry.spec.name if registry.spec else f"inline-{id(target)}"] = registry
        _emit_loaded(registry)
        return registry

    module = _import(target)
    register = getattr(module, "register", None)
    if not callable(register):
        raise PluginError(f"Plugin {target!r} has no callable register(registry)")
    declared = getattr(module, "PLUGIN", None)
    resolved = spec or declared
    if resolved is None:
        resolved = PluginSpec(name=getattr(module, "__name__", str(target)))
    registry.spec = resolved
    register(registry)
    _LOADED[resolved.name] = registry
    _emit_loaded(registry)
    return registry


def _emit_loaded(registry: PluginRegistry) -> None:
    try:
        from app_files.plugins.events import LifecycleEvent, emit

        emit(
            LifecycleEvent.PLUGIN_LOADED,
            {"plugin": registry.spec.as_dict() if registry.spec else None,
             "accepted": registry.summary()["accepted"]},
        )
    except Exception:  # noqa: BLE001 - emitting is best-effort
        pass


def _import(target: Any) -> Any:
    if not isinstance(target, str):
        raise PluginError(f"Cannot load a plugin from {type(target).__name__}")
    try:
        return importlib.import_module(target)
    except Exception as exc:  # noqa: BLE001 - surface the import error as a plugin error
        raise PluginError(f"Could not import plugin {target!r}: {exc}") from exc


def active_plugins() -> list[dict[str, Any]]:
    return [
        {"plugin": name, "spec": registry.summary()["plugin"],
         "registered": registry.summary()["registered"],
         "accepted": registry.summary()["accepted"],
         "refused": registry.summary()["refused"]}
        for name, registry in sorted(_LOADED.items())
    ]


def loaded_names() -> list[str]:
    return sorted(_LOADED)


__all__ = [
    "PluginError",
    "PluginRegistry",
    "PluginSpec",
    "RegisteredItem",
    "active_plugins",
    "load_plugin",
    "loaded_names",
]
