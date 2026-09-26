"""Shared core for the additive modules: config resolution and config errors.

Deliberately small. The specification asked for a ``core`` package holding a
registry, a schema validator and an error type. Two of those already exist and
are not duplicated here:

* the **registry** is ``app_files/plugins/registry.py`` — one binding pattern,
  extended rather than forked;
* the **rule schema** is ``app_files/rules/schema.py``, with the JSON schema in
  ``app_files/configs/schema/``.

What had no home is the config precedence chain (see
``docs/CONFIG_PRECEDENCE.md``), which this package implements once so no module
invents its own order.
"""

from __future__ import annotations

from app_files.core.config import ConfigError, Layer, Resolved, resolve

__all__ = ["ConfigError", "Layer", "Resolved", "resolve"]
