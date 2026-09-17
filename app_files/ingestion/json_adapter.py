"""JSON adapter: flatten arbitrarily nested JSON into tabular rows.

Accepts a top-level list of objects, a single object, or an object wrapping
one list of records (a very common API export shape, e.g. ``{"data": [...]}``).
Nested objects become ``parent.child`` columns and nested arrays are joined
with ``"; "``, which keeps one output row per input record.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd

from app_files.ingestion.base import Adapter, UnsupportedFormatError

# Keys commonly used to wrap the real record list in an API export.
_WRAPPER_KEYS = ("data", "records", "rows", "results", "items", "values")


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten one JSON value into a single-level dict."""
    flat: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            flat.update(_flatten(item, f"{prefix}{key}."))
    elif isinstance(value, list):
        if all(not isinstance(item, (dict, list)) for item in value):
            flat[prefix.rstrip(".")] = "; ".join(str(item) for item in value)
        else:
            for index, item in enumerate(value):
                flat.update(_flatten(item, f"{prefix}{index}."))
    else:
        flat[prefix.rstrip(".")] = value
    return flat


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item if isinstance(item, dict) else {"value": item} for item in payload]
    if isinstance(payload, dict):
        for key in _WRAPPER_KEYS:
            if isinstance(payload.get(key), list):
                return _records(payload[key])
        # A dict of dicts keyed by id is also common.
        if payload and all(isinstance(v, dict) for v in payload.values()):
            return [{"_key": key, **value} for key, value in payload.items()]
        return [payload]
    return [{"value": payload}]


class JSONAdapter(Adapter):
    name = "json"
    extensions = (".json",)

    def read(self, source: str | Path | BinaryIO | bytes) -> pd.DataFrame:
        raw = self._as_bytes(source)
        if not raw.strip():
            return pd.DataFrame()
        try:
            payload = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise UnsupportedFormatError(f"Could not parse JSON file: {exc}") from exc
        rows = [_flatten(record) for record in _records(payload)]
        if not rows:
            return pd.DataFrame()
        return self._stringify(pd.DataFrame(rows))