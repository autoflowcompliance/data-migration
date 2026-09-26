"""Resolve a module's config through one chain: defaults < YAML < env < CLI.

See ``docs/CONFIG_PRECEDENCE.md`` for why the chain exists and what it does not
cover. Two properties matter more than the order itself:

* **Fail closed.** An unparseable value raises rather than quietly reverting to
  the layer below, because a typo'd deployment override that silently becomes
  the default is a wrong answer with no signal.
* **Absence is not emptiness.** A layer that does not mention a key falls
  through; a layer that sets it to ``""`` or ``None`` has spoken.

The env layer is namespaced ``AUTOFLOW_<MODULE>_<SETTING>`` so two modules
cannot read each other's overrides, and nested keys join with ``_``.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from enum import Enum
from typing import Any

_MISSING = object()


class ConfigError(ValueError):
    """Raised when config cannot be resolved into a safe, unambiguous value."""


class Layer(str, Enum):
    """The four layers, ordered from widest scope to narrowest."""

    DEFAULTS = "defaults"
    YAML = "yaml"
    ENV = "env"
    CLI = "cli"


class Resolved(dict):
    """A resolved config that also says which layer supplied each leaf.

    Subclasses ``dict`` so a caller can ignore provenance entirely and treat it
    as the plain mapping it is.
    """

    def __init__(self, mapping: Mapping[str, Any], provenance: Mapping[str, Layer]):
        super().__init__(mapping)
        self.provenance: dict[str, Layer] = dict(provenance)

    def source_of(self, dotted_key: str) -> Layer | None:
        """Which layer supplied ``dotted_key``, or ``None`` if it was never set."""
        return self.provenance.get(dotted_key)


def resolve(
    module: str,
    defaults: Mapping[str, Any],
    yaml_values: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
    cli: Mapping[str, Any] | None = None,
    *,
    with_provenance: bool = False,
) -> Any:
    """Resolve ``module``'s config by walking the four layers in order.

    Args:
        module: the module name, which is also its env namespace.
        defaults: the safe values, always present.
        yaml_values: the module's block from a config file, if declared.
        env: the environment to read; defaults to the process environment, so
            the env layer is active wherever this is used rather than only
            where a caller remembered to pass it. Pass ``{}`` to disable it.
        cli: flags for this invocation, if any.
        with_provenance: return a :class:`Resolved` carrying per-key origins.

    Returns:
        The merged mapping, or a :class:`Resolved` when ``with_provenance``.
    """
    if env is None:
        env = os.environ

    merged: dict[str, Any] = {}
    provenance: dict[str, Layer] = {}
    _merge(merged, defaults, Layer.DEFAULTS, provenance)

    if yaml_values is not None:
        _require_mapping(yaml_values, module, Layer.YAML)
        _merge(merged, yaml_values, Layer.YAML, provenance)

    env_values = _parse_env(module, env, merged)
    if env_values:
        _merge(merged, env_values, Layer.ENV, provenance)

    if cli is not None:
        _require_mapping(cli, module, Layer.CLI)
        _merge(merged, cli, Layer.CLI, provenance)

    return Resolved(merged, provenance) if with_provenance else merged


def _require_mapping(value: Any, module: str, layer: Layer) -> None:
    if not isinstance(value, Mapping):
        raise ConfigError(
            f"{module}: the {layer.value} layer must be a mapping, "
            f"got {type(value).__name__}"
        )


def _merge(
    target: dict[str, Any],
    source: Mapping[str, Any],
    layer: Layer,
    provenance: dict[str, Layer],
    prefix: str = "",
) -> None:
    """Merge ``source`` onto ``target`` per key, recursing into mappings.

    A mapping in one layer and a scalar in another is a shape conflict, not a
    value: silently replacing a whole block with a scalar (or the reverse) is
    how a config typo becomes a wrong answer. Both directions raise.
    """
    for key, value in source.items():
        path = f"{prefix}{key}"
        existing = target.get(key, _MISSING)
        if isinstance(value, Mapping):
            if existing is not _MISSING and not isinstance(existing, Mapping):
                raise ConfigError(
                    f"{path!r} is a {type(existing).__name__} in a lower layer "
                    f"but a mapping in the {layer.value} layer"
                )
            if existing is _MISSING:
                target[key] = {}
                existing = target[key]
            _merge(existing, value, layer, provenance, prefix=f"{path}.")
        else:
            if isinstance(existing, Mapping):
                raise ConfigError(
                    f"{path!r} is a mapping in a lower layer "
                    f"but a {type(value).__name__} in the {layer.value} layer"
                )
            target[key] = value
            provenance[path] = layer


def _leaf_paths(mapping: Mapping[str, Any], prefix: str = "") -> list[str]:
    paths: list[str] = []
    for key, value in mapping.items():
        path = f"{prefix}{key}"
        if isinstance(value, Mapping):
            paths.extend(_leaf_paths(value, prefix=f"{path}."))
        else:
            paths.append(path)
    return paths


def _parse_env(
    module: str, env: Mapping[str, str] | None, base: Mapping[str, Any]
) -> dict[str, Any]:
    """Turn the module's ``AUTOFLOW_*`` variables into a nested mapping.

    Nested keys are matched against the leaf paths already known from the
    layers below, so ``AUTOFLOW_QUALITY_SLA_COMPLETENESS`` lands on
    ``sla.completeness``. A remainder containing an underscore that matches no
    known path is refused rather than invented as a new key, because that is
    the shape of a typo.
    """
    if not env:
        return {}

    prefix = f"AUTOFLOW_{module.upper()}_"
    known = {path.replace(".", "_").upper(): path for path in _leaf_paths(base)}
    hints = {path: _at_path(base, path) for path in known.values()}

    parsed: dict[str, Any] = {}
    for key, raw in env.items():
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix) :].upper()
        path = known.get(remainder)
        if path is None:
            if "_" in remainder:
                raise ConfigError(
                    f"{module}: {key} names no known setting "
                    f"(known: {', '.join(sorted(known)) or 'none'})"
                )
            path = remainder.lower()
        _set_path(parsed, path, _coerce(module, key, raw, hints.get(path)))
    return parsed


def _at_path(mapping: Mapping[str, Any], dotted: str) -> Any:
    value: Any = mapping
    for part in dotted.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return _MISSING
        value = value[part]
    return value


def _set_path(target: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = target
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def _coerce(module: str, key: str, raw: str, hint: Any) -> Any:
    """Parse an env string into the type the layer below already uses.

    The hint is the value at that path from defaults/YAML. Without one the
    string is kept as-is, since guessing a type from an env var alone is how
    ``"false"`` becomes truthy.
    """
    if hint is _MISSING or hint is None or isinstance(hint, str):
        return raw
    if isinstance(hint, bool):
        parsed = _BOOLEANS.get(raw.strip().lower())
        if parsed is None:
            raise ConfigError(
                f"{module}: {key}={raw!r} is not a boolean "
                f"(use true/false, yes/no, on/off, 1/0)"
            )
        return parsed
    if isinstance(hint, int):
        try:
            return int(raw)
        except ValueError:
            try:
                as_float = float(raw)
            except ValueError:
                pass
            else:
                if as_float.is_integer():
                    return int(as_float)
            raise ConfigError(f"{module}: {key}={raw!r} is not an integer") from None
    if isinstance(hint, float):
        try:
            return float(raw)
        except ValueError:
            raise ConfigError(f"{module}: {key}={raw!r} is not a number") from None
    if isinstance(hint, Mapping):
        try:
            parsed_mapping = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{module}: {key} is not valid JSON ({exc.msg})") from None
        if not isinstance(parsed_mapping, Mapping):
            raise ConfigError(f"{module}: {key} must be a JSON object")
        return parsed_mapping
    if isinstance(hint, list):
        stripped = raw.strip()
        if stripped.startswith("["):
            try:
                parsed_list = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ConfigError(f"{module}: {key} is not valid JSON ({exc.msg})") from None
            if not isinstance(parsed_list, list):
                raise ConfigError(f"{module}: {key} must be a JSON array")
            return parsed_list
        if "," in raw:
            return [part.strip() for part in raw.split(",") if part.strip()]
        return [stripped] if stripped else []
    return raw


_BOOLEANS: dict[str, bool] = {
    "true": True,
    "yes": True,
    "on": True,
    "1": True,
    "false": False,
    "no": False,
    "off": False,
    "0": False,
}


__all__ = ["ConfigError", "Layer", "Resolved", "resolve"]
