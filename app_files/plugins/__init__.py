"""Layer 17 — extensibility.

Plugins register a transform, a rule type, an output format or a destination,
and the pipeline picks it up without a fork or a core edit.

The registration points already exist, each on the layer that owns the concept:
``app_files.transforms.register_transform``, ``app_files.rules.register_validator``
and ``app_files.output.register_format``. This package adds the glue that lets a
plugin author declare several of them in one place.

The design rule is that registration is explicit and additive. A plugin cannot
silently replace a built-in: every registration refuses to shadow an existing
name unless the caller passes ``override=True``. A plugin that swaps the CSV
writer for its own is how an install stops producing CSV for everyone, and the
failure stays invisible until someone opens the file.
"""

from __future__ import annotations

from app_files.plugins.events import (
    EventBus,
    EventReceipt,
    LifecycleEvent,
    emit,
    subscribe,
)
from app_files.plugins.registry import (
    PluginError,
    PluginRegistry,
    PluginSpec,
    active_plugins,
    load_plugin,
)

__all__ = [
    "EventBus",
    "EventReceipt",
    "LifecycleEvent",
    "PluginError",
    "PluginRegistry",
    "PluginSpec",
    "active_plugins",
    "emit",
    "load_plugin",
    "subscribe",
]
