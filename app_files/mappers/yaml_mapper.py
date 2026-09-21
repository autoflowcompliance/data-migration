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


def _score_source(target: TargetField, columns: list[str]) -> tuple[str | None, float]:
    """Best source column for ``target`` and its score, ignoring who else wants it."""
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
    return best


def _best_source(target: TargetField, columns: list[str]) -> tuple[str | None, float]:
    column, score = _score_source(target, columns)
    return (column, score) if score >= MATCH_THRESHOLD else (None, score)


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
    """Produce the target-shaped frame plus a log of how each field was filled.

    Auto-mapping is decided globally rather than field-by-field. A near-miss on
    one field must not cost a later field its exact name: in HubSpot's config
    the ``state`` alias ``County`` scores 0.923 against a ``Country`` column,
    so a first-come mapping hands ``state`` the country values and leaves
    ``country`` nothing to match. Claims are therefore put in descending
    confidence order and each column is consumed once, letting ``country``
    claim ``Country`` at 1.0 before ``state`` can reach it.
    """
    columns = list(source.columns)
    output = pd.DataFrame(index=source.index)
    result = MappingResult(frame=output, config=config)
    used: set[str] = set()

    # Explicit sources win outright and reserve their columns. Each entry is
    # (origin, confidence, match, sources) so the two explicit shapes — a joined
    # multi-column value and a direct single column — stay distinguishable.
    reserved: dict[str, tuple[str, float, str, list[str]]] = {}
    for target in config.fields:
        if target.sources:
            present = [s for s in target.sources if s in columns]
            used.update(present)
            if present:
                reserved[target.name] = (
                    " + ".join(present), 1.0, "explicit", present,
                )
            else:
                reserved[target.name] = ("", 0.0, "missing", [])
        elif target.source and target.source in columns:
            used.add(target.source)
            reserved[target.name] = (target.source, 1.0, "explicit", [target.source])

    # Then auto-mapped fields, strongest claim first, each column taken once.
    auto = [t for t in config.fields if t.name not in reserved]
    ranked = sorted(auto, key=lambda t: _score_source(t, columns)[1], reverse=True)
    claimed: dict[str, str | None] = {}
    for target in ranked:
        guess, _score = _best_source(target, columns)
        if guess is None or guess in used:
            claimed[target.name] = None
        else:
            claimed[target.name] = guess
            used.add(guess)

    for target in config.fields:
        transform = get_transform(target.transform) if target.transform else None

        if target.name in reserved:
            origin, confidence, match, sources = reserved[target.name]
            if match == "explicit" and sources:
                if len(sources) > 1:
                    values = source.apply(
                        lambda row, cols=sources, sep=target.separator: _combine(row, cols, sep),
                        axis=1,
                    )
                else:
                    values = source[sources[0]]
            else:
                values = pd.Series([target.default] * len(source), index=source.index)
        else:
            origin = claimed[target.name]
            if origin is None:
                confidence, match = round(_score_source(target, columns)[1], 2), "missing"
                origin = ""
                values = pd.Series([target.default] * len(source), index=source.index)
            else:
                confidence, match = round(_score_source(target, columns)[1], 2), "auto"
                values = source[origin]

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
