"""Map a cleaned frame onto a target CRM import template."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from difflib import SequenceMatcher

import pandas as pd

from app_files.transforms import get_transform, is_missing
from app_files.mappers.schema import MappingConfig, TargetField

MATCH_THRESHOLD = 0.82


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _best_source(target: TargetField, columns: list[str]) -> tuple[str | None, float]:
    candidates = [target.name, *target.aliases]
    normalized_columns = {column: _normalize(column) for column in columns}
    best: tuple[str | None, float] = (None, 0.0)
    for candidate in candidates:
        wanted = _normalize(candidate)
        for column, normalized in normalized_columns.items():
            if normalized == wanted:
                return column, 1.0
            score = SequenceMatcher(None, wanted, normalized).ratio()
            if score > best[1]:
                best = (column, score)
    return best if best[1] >= MATCH_THRESHOLD else (None, best[1])


@dataclass
class MappingResult:
    frame: pd.DataFrame
    mappings: list[dict[str, object]] = field(default_factory=list)
    unmapped_sources: list[str] = field(default_factory=list)
    config: MappingConfig | None = None

    def mapping_log(self) -> pd.DataFrame:
        columns = ["target_field", "source_column", "match", "confidence", "transform"]
        log = pd.DataFrame(self.mappings, columns=columns)
        extra = pd.DataFrame(
            [
                {
                    "target_field": "",
                    "source_column": column,
                    "match": "dropped",
                    "confidence": "",
                    "transform": "",
                }
                for column in self.unmapped_sources
            ],
            columns=columns,
        )
        return pd.concat([log, extra], ignore_index=True) if len(extra) else log


def _defaulter(default: object) -> Callable[[object], object]:
    def apply(value: object) -> object:
        return default if is_missing(value) else value

    return apply


def _combine(row: pd.Series, sources: list[str], separator: str) -> str:
    parts = [str(row[s]).strip() for s in sources if s in row and not is_missing(row[s])]
    return separator.join(part for part in parts if part)


def map_data(source: pd.DataFrame, config: MappingConfig) -> MappingResult:
    """Produce the target-shaped frame plus a log of how each field was filled."""
    columns = list(source.columns)
    output = pd.DataFrame(index=source.index)
    result = MappingResult(frame=output, config=config)
    used: set[str] = set()

    for target in config.fields:
        transform = get_transform(target.transform) if target.transform else None

        if target.sources:
            present = [s for s in target.sources if s in columns]
            values = source.apply(
                lambda row, cols=present, sep=target.separator: _combine(row, cols, sep),
                axis=1,
            )
            used.update(present)
            match, confidence, origin = (
                ("explicit", 1.0, " + ".join(present)) if present else ("missing", 0.0, "")
            )
        else:
            if target.source and target.source in columns:
                origin, confidence, match = target.source, 1.0, "explicit"
            else:
                guessed, score = _best_source(target, columns)
                origin, confidence = guessed or "", round(score, 2)
                match = "auto" if guessed else "missing"
            if origin:
                values = source[origin]
                used.add(origin)
            else:
                values = pd.Series([target.default] * len(source), index=source.index)

        if transform is not None:
            values = values.map(transform)
        output[target.name] = values
        if target.default is not None:
            output[target.name] = output[target.name].map(_defaulter(target.default))

        result.mappings.append(
            {
                "target_field": target.name,
                "source_column": origin,
                "match": match,
                "confidence": confidence,
                "transform": target.transform or "",
            }
        )

    result.unmapped_sources = [column for column in columns if column not in used]
    result.frame = output
    return result
