"""JSON writer.

Two shapes are offered:

* ``records`` (default) — a flat list of row objects. Easy to consume, and the
  round-trip is lossless, which is what the "all four formats contain identical
  data" test checks.
* ``nested`` — re-nests columns whose names contain ``.`` (e.g. ``address.city``)
  into real nested objects, which is what flat JSON exports are usually
  expected to look like.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def _nest(record: dict[str, Any]) -> dict[str, Any]:
    """Turn ``{"address.city": "Boston"}`` into ``{"address": {"city": "Boston"}}``."""
    nested: dict[str, Any] = {}
    for key, value in record.items():
        if "." not in str(key):
            nested[key] = value
            continue
        parts = str(key).split(".")
        cursor = nested
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
    return nested


def write(
    df: pd.DataFrame, path: str | Path, shape: str = "records", indent: int = 2
) -> Path:
    """Write ``df`` as JSON to ``path`` and return the path written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {str(key): _clean(value) for key, value in record.items()}
        for record in df.to_dict(orient="records")
    ]
    if shape == "nested":
        records = [_nest(record) for record in records]
    elif shape != "records":
        raise ValueError(f"Unknown JSON shape {shape!r}. Use 'records' or 'nested'.")

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=indent, ensure_ascii=False, default=str)
    return path


def _clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)