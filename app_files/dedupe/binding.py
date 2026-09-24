"""Bind a config's ``dedupe:`` block into an attended run.

The fuzzy-dedupe engine (Jaro-Winkler and Levenshtein matching, blocking, the
cluster-size safety cap, the merge log) was complete and tested, and its
``FuzzyRule.from_dict`` was written to be read from a config. No run ever read
a ``dedupe:`` block, so the layer had zero callers outside its own package: a
buyer could declare a fuzzy rule, run the tool, and get every near-duplicate
back with no warning.

This binding follows the same shape as :mod:`app_files.privacy.binding` and
:mod:`app_files.normalization.binding`. The filtered frame is written as
``deduped_data.csv`` beside ``clean_data.csv``, the merge log as
``duplicates_removed.csv``. The pipeline's own output is never rewritten, so a
config with no ``dedupe:`` block is byte-identical to before.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from app_files.dedupe.engine import (
    DedupeConfigError,
    FuzzyDedupeResult,
    FuzzyRule,
    fuzzy_dedupe,
)
from app_files.mappers.schema import CONFIG_DIR


def _config_path(crm: str | Path) -> Path | None:
    path = Path(crm)
    if not path.exists():
        path = CONFIG_DIR / f"{str(crm).strip().lower()}.yaml"
    return path if path.exists() else None


def dedupe_block(crm: str | Path) -> dict[str, Any] | None:
    """The raw ``dedupe:`` mapping a config declares, or None."""
    path = _config_path(crm)
    if path is None:
        return None
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    block = data.get("dedupe") if isinstance(data, dict) else None
    return block if isinstance(block, dict) else None


def declared_dedupe_rules(crm: str | Path) -> list[FuzzyRule]:
    """The fuzzy rules a config declares. Raises on a malformed one."""
    block = dedupe_block(crm)
    if block is None or block.get("enabled") is False:
        return []
    unknown = set(block) - {"enabled", "rules", "rule"}
    if unknown:
        raise DedupeConfigError(
            f"dedupe block has unknown keys: {', '.join(sorted(unknown))}. "
            f"Allowed: enabled, rule, rules"
        )
    raw = block.get("rules")
    if raw is None and "rule" in block:
        raw = [block["rule"]]
    if raw is None:
        return []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise DedupeConfigError("'rules' must be a list of fuzzy rules")
    return [FuzzyRule.from_dict(item) for item in raw]


@dataclass
class DedupeOutcome:
    """A deduplicated frame plus the merge log, in the shape a caller writes."""

    result: FuzzyDedupeResult
    rules: list[FuzzyRule] = field(default_factory=list)

    @property
    def frame(self) -> pd.DataFrame:
        return self.result.frame

    @property
    def duplicates_removed(self) -> int:
        return self.result.duplicates_removed

    def merges_frame(self) -> pd.DataFrame:
        return self.result.merges_frame()

    def summary(self) -> dict[str, Any]:
        return {**self.result.summary(), "rules": len(self.rules)}


def apply_dedupe(frame: pd.DataFrame, rules: list[FuzzyRule]) -> DedupeOutcome:
    """Apply ``rules`` in order; each drops duplicates from the previous frame."""
    current = frame
    all_merges: list[Any] = []
    compared = 0
    rows_in = len(frame)
    for rule in rules:
        run = fuzzy_dedupe(current, rule)
        all_merges.extend(run.merges)
        compared += run.compared_pairs
        current = run.frame
    combined = FuzzyDedupeResult(
        frame=current,
        merges=all_merges,
        rows_in=rows_in,
        compared_pairs=compared,
    )
    return DedupeOutcome(result=combined, rules=rules)


def apply_configured_dedupe(
    frame: pd.DataFrame, crm: str | Path
) -> DedupeOutcome | None:
    """Deduplicate ``frame`` with ``crm``'s declared rules, or None.

    None means the config declares no dedupe, the signal to a caller that it
    must write no dedupe artifacts and change no existing output.
    """
    rules = declared_dedupe_rules(crm)
    if not rules:
        return None
    return apply_dedupe(frame, rules)


__all__ = [
    "DedupeOutcome",
    "apply_configured_dedupe",
    "apply_dedupe",
    "declared_dedupe_rules",
    "dedupe_block",
]
