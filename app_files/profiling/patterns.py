"""Regex pattern inference: what shape is this column?

A profiler that says "this is a string column" is not much use when the string
is an account code. This proposes a regex covering the column's values plus a
label a human recognises (``email``, ``date``, ``uuid``), so a schema can be
described without opening the file.

The distinction that matters is *all* versus *contains*: a column that is
entirely emails is an email column, and one with an email somewhere in a note
is not. Named shapes are therefore tested for full coverage, and the generic
builder falls back to a bounded alternation only when nothing else fits.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from app_files.transforms import is_missing

# How many distinct values feed the generic builder. A 10k-row column of
# unique ids must not become a 10k-branch alternation, so the builder samples
# and the coverage figure tells the truth about the sample it saw.
_SAMPLE_LIMIT = 500

# A cap on the generated regex, so a pathological column cannot produce a
# pattern that is slow to compile or match.
_REGEX_LIMIT = 1200

_NAMED: tuple[tuple[str, str], ...] = (
    ("email", r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    ("uuid", r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"),
    ("url", r"https?://[^\s]+"),
    ("ipv4", r"(?:\d{1,3}\.){3}\d{1,3}"),
    ("date", r"\d{4}-\d{2}-\d{2}"),
    ("datetime", r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?"),
    ("currency", r"[$€£¥]\s?\d[\d,]*\.\d{2}"),
    ("integer", r"[+-]?\d+"),
    ("decimal", r"[+-]?\d+\.\d+"),
)


@dataclass
class InferredPattern:
    """One column's inferred shape."""

    name: str = ""
    label: str = "text"
    regex: str = ""
    coverage: float = 0.0
    sampled: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "regex": self.regex,
            "coverage": self.coverage,
            "sampled": self.sampled,
        }


def _present(series: pd.Series) -> list[str]:
    return [str(value) for value in series if not is_missing(value)]


def match_rate(regex: str, series: pd.Series) -> float:
    """The share of non-blank values ``regex`` matches in full.

    Full match, not search: an unanchored pattern would report 1.0 for any
    column because almost every string contains a substring that matches
    ``.*``. Blank values are excluded, since "empty" is completeness' concern.
    """
    values = _present(series)
    if not values:
        return 0.0
    compiled = re.compile(regex)
    hits = sum(1 for value in values if compiled.fullmatch(value))
    return hits / len(values)


def _named_label(values: list[str]) -> tuple[str, str, float] | None:
    """The first named shape that covers every value, or ``None``."""
    for label, regex in _NAMED:
        compiled = re.compile(regex)
        if all(compiled.fullmatch(value) for value in values):
            return label, regex, 1.0
    return None


def _generic_regex(values: list[str]) -> str:
    """The dominant shape's regex, built from the column's own structure.

    The shape of each value is its run-length encoded character classes, so
    ``AB-1001`` becomes ``[A-Z]{2}-\\d{4}``. The most common shape wins, with
    ties included; shapes that appear once are left out.

    Building an alternation of *every* shape would make ``coverage`` always
    1.0 and therefore meaningless. Keeping the dominant shape makes coverage
    the honest answer to "how much of this column actually conforms", which is
    the question an operator has about a column of mixed content.
    """
    if not values:
        return r".*"
    counts: dict[str, int] = {}
    for value in values:
        shape = _shape_of(value)
        counts[shape] = counts.get(shape, 0) + 1
    best = max(counts.values())
    dominant = [shape for shape, count in counts.items() if count == best]
    # Longest first so a more specific shape is tried before a general one.
    dominant.sort(key=len, reverse=True)
    regex = "|".join(dominant[:20])
    if len(regex) > _REGEX_LIMIT:
        regex = "|".join(dominant[:5])
    return regex


def _shape_of(value: str) -> str:
    """Run-length encode a value into a character-class pattern."""
    parts: list[str] = []
    index = 0
    while index < len(value):
        cls = _class_of(value[index])
        run = 1
        while index + run < len(value) and _class_of(value[index + run]) == cls:
            run += 1
        parts.append(cls if run == 1 else f"{cls}{{{run}}}")
        index += run
    return "".join(parts)


def _class_of(char: str) -> str:
    if char.isdigit():
        return r"\d"
    if char.isupper() and char.isalpha():
        return "[A-Z]"
    if char.islower() and char.isalpha():
        return "[a-z]"
    if char.isalpha():
        return "[A-Za-z]"
    return re.escape(char)


def infer_pattern(series: pd.Series, *, sample_limit: int = _SAMPLE_LIMIT) -> InferredPattern:
    """Infer the shape of ``series``.

    Args:
        sample_limit: how many distinct values to build the generic regex from.
            A large column is sampled; ``coverage`` reports the rate over the
            whole column, so a sample that misses a shape shows up as coverage
            below 1.0 rather than as a silent over-claim.
    """
    values = _present(series)
    if not values:
        return InferredPattern(label="text", regex=r".*", coverage=0.0, sampled=0)

    named = _named_label(values)
    if named is not None:
        label, regex, coverage = named
        return InferredPattern(
            label=label, regex=f"^(?:{regex})$", coverage=coverage, sampled=len(values)
        )

    distinct = list(dict.fromkeys(values))
    sample = distinct[:sample_limit]
    regex = _generic_regex(sample)
    anchored = f"^(?:{regex})$"
    try:
        coverage = match_rate(anchored, series)
    except re.error:
        return InferredPattern(
            label="text", regex=r".*", coverage=0.0, sampled=len(values)
        )
    return InferredPattern(
        label="text", regex=anchored, coverage=coverage, sampled=len(values)
    )


def infer_column_pattern(
    frame: pd.DataFrame,
    *,
    columns: list[str] | None = None,
    sample_limit: int = _SAMPLE_LIMIT,
) -> list[InferredPattern]:
    """Infer a pattern for every column (or the named subset), in order."""
    if frame is None or frame.empty or frame.columns.empty:
        return []
    target = columns if columns is not None else list(frame.columns)
    patterns: list[InferredPattern] = []
    for name in target:
        pattern = infer_pattern(frame[name], sample_limit=sample_limit)
        pattern.name = str(name)
        patterns.append(pattern)
    return patterns
