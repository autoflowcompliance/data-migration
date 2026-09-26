"""Fuzzy duplicate detection.

Exact deduplication compares whole rows for equality. This finds rows that
*describe the same thing* — "John Smith" and "Jon Smith", "Acme Inc" and "Acme,
Inc", "john.smith@example.com" and "j.smith@example.com" — and merges them,
recording every merge so it can be undone or audited.

Two things keep it honest:

* **Blocking.** Comparing every row to every other is O(n²) and unusable at
  12,000 rows (72 million comparisons). Rows are first grouped by a cheap key —
  the first characters of the compared columns — and only members of the same
  block are compared. The key is generated in several ways so a typo in the
  first character does not hide a duplicate, and the union of the blocks is
  considered with no pair compared twice.
* **Exact-first.** Any rows that are byte-identical are merged by the exact
  rule regardless of the threshold, because they are duplicates by definition.

No row is ever silently dropped: ``FuzzyDedupeResult.merges`` lists each merged
row, the survivor it merged into, and the score that caused it.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.dedupe.similarity import MIN_FUZZY_LENGTH, similarity
from app_files.transforms import is_missing

DEFAULT_THRESHOLD = 0.9
#: Jaro-Winkler by default: it tolerates the transpositions and dropped
#: letters that names actually contain ("Jon"/"John" scores 0.93) far better
#: than edit distance, which rates the same pair 0.75.
DEFAULT_METRIC = "jaro_winkler"
#: Prefix/suffix lengths used to form block keys. Several short lengths, not one
#: long one: "John"/"Jon" agree at length 2 but not at 3, so a single long
#: prefix would miss the pair the metric is built to catch.
BLOCK_KEY_LENGTHS = (2, 3)
#: A block at or below this many rows is compared exhaustively.
EXHAUSTIVE_BLOCK_LIMIT = 200
#: A larger block is sorted and each row compared to its next few neighbours,
#: which bounds the work on a column of values that all share a prefix.
NEIGHBOUR_WINDOW = 25


class DedupeConfigError(ValueError):
    """Raised when a fuzzy dedupe configuration is malformed."""


class ClusterTooLargeError(ValueError):
    """Raised when one merge would fold more rows together than allowed.

    Raised instead of writing a frame that silently lost most of its rows, so a
    serial-number-shaped column cannot collapse a file without the caller
    noticing.
    """


@dataclass
class Merge:
    """One row folded into another, with the evidence."""

    kept_index: Any
    dropped_index: Any
    score: float
    metric: str
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "kept_row": self.kept_index,
            "dropped_row": self.dropped_index,
            "score": round(self.score, 4),
            "metric": self.metric,
            "reason": self.reason,
        }


@dataclass
class FuzzyDedupeResult:
    frame: pd.DataFrame
    merges: list[Merge] = field(default_factory=list)
    rows_in: int = 0
    compared_pairs: int = 0

    @property
    def duplicates_removed(self) -> int:
        return len(self.merges)

    @property
    def rows_out(self) -> int:
        return len(self.frame)

    def summary(self) -> dict[str, Any]:
        return {
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "duplicates_removed": self.duplicates_removed,
            "compared_pairs": self.compared_pairs,
        }

    def merges_frame(self) -> pd.DataFrame:
        columns = ["kept_row", "dropped_row", "score", "metric", "reason"]
        if not self.merges:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([merge.as_dict() for merge in self.merges], columns=columns)


@dataclass
class FuzzyRule:
    """Which columns to compare, how, and how close counts as a duplicate."""

    columns: list[str]
    threshold: float = DEFAULT_THRESHOLD
    metric: str = DEFAULT_METRIC
    require_all: bool = True
    """``True``: every compared column must be at least ``threshold`` similar.
    ``False``: a single column meeting the threshold is enough."""

    max_cluster_size: int | None = None
    """Refuse to fold more than this many rows into one survivor.

    Jaro-Winkler rates any two strings that share a long prefix as very
    similar, so a column of serial-number-shaped values ("Customer00Record",
    "Customer01Record") will legitimately score above 0.9 and collapse. That is
    a property of the metric, not a bug — the merges are recorded so they can
    be reviewed. This cap is the backstop: set it and a run that would fold a
    whole file into one row stops with an error instead of doing so quietly.
    ``None`` means no cap."""

    _KNOWN = frozenset(
        {"columns", "threshold", "metric", "require_all", "max_cluster_size"}
    )

    @classmethod
    def from_dict(cls, data: Any) -> FuzzyRule:
        if not isinstance(data, dict):
            raise DedupeConfigError(f"Each fuzzy rule must be a mapping, got {type(data).__name__}")
        unknown = set(data) - cls._KNOWN
        if unknown:
            raise DedupeConfigError(
                f"Fuzzy rule has unknown keys: {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(cls._KNOWN))}"
            )
        columns = data.get("columns")
        if not columns:
            raise DedupeConfigError("Each fuzzy rule needs 'columns'")
        if isinstance(columns, str):
            columns = [columns]
        threshold = float(data.get("threshold", DEFAULT_THRESHOLD))
        if not 0.0 < threshold <= 1.0:
            raise DedupeConfigError(f"threshold must be in (0, 1], got {threshold}")
        metric = str(data.get("metric", DEFAULT_METRIC)).strip().lower()
        if metric not in {"levenshtein", "jaro_winkler"}:
            raise DedupeConfigError(
                f"Unknown metric {metric!r}. Available: levenshtein, jaro_winkler"
            )
        max_cluster_size = data.get("max_cluster_size")
        if max_cluster_size is not None:
            max_cluster_size = int(max_cluster_size)
            if max_cluster_size < 1:
                raise DedupeConfigError(
                    f"max_cluster_size must be >= 1, got {max_cluster_size}"
                )
        return cls(
            columns=list(columns),
            threshold=threshold,
            metric=metric,
            require_all=bool(data.get("require_all", True)),
            max_cluster_size=max_cluster_size,
        )


def _block_keys(row: pd.Series, columns: list[str]) -> set[str]:
    """Several short keys per row, so a typo does not hide a match.

    For "john" this yields prefixes and suffixes at two and three characters,
    plus a sorted-character key that survives an anagram-like transposition.
    Two rows sharing *any* key are compared.
    """
    keys: set[str] = set()
    for column in columns:
        value = row.get(column)
        if is_missing(value):
            continue
        text = "".join(str(value).lower().split())
        if not text:
            continue
        for length in BLOCK_KEY_LENGTHS:
            keys.add(text[:length])
            keys.add(text[-length:])
        keys.add("".join(sorted(text))[:4])
    return keys


def _compare_pairs(members: list[Any]) -> Iterable[tuple[Any, Any]]:
    """Pairs within a block, exhaustive when small and windowed when large."""
    if len(members) <= EXHAUSTIVE_BLOCK_LIMIT:
        for i, left in enumerate(members):
            for right in members[i + 1 :]:
                yield left, right
        return
    for i, left in enumerate(members):
        for right in members[i + 1 : i + 1 + NEIGHBOUR_WINDOW]:
            yield left, right


def _row_similarity(
    left: pd.Series, right: pd.Series, rule: FuzzyRule
) -> tuple[float, str]:
    scores: list[float] = []
    for column in rule.columns:
        a, b = left.get(column), right.get(column)
        if is_missing(a) and is_missing(b):
            scores.append(1.0)
            continue
        if is_missing(a) or is_missing(b):
            # One side blank is not evidence of a duplicate; never let it vote
            # for a merge when every column must agree.
            scores.append(0.0)
            continue
        text_a, text_b = str(a), str(b)
        if max(len(text_a.strip()), len(text_b.strip())) < MIN_FUZZY_LENGTH:
            scores.append(1.0 if text_a.strip().lower() == text_b.strip().lower() else 0.0)
            continue
        scores.append(similarity(text_a, text_b, rule.metric))

    if rule.require_all:
        return (min(scores) if scores else 0.0), rule.metric
    best = max(scores) if scores else 0.0
    return best, rule.metric


def find_fuzzy_duplicates(
    frame: pd.DataFrame,
    rule: FuzzyRule,
) -> tuple[list[Merge], int]:
    """Pairs of rows that describe the same thing, plus the number of pairs compared."""
    if frame.empty:
        return [], 0
    missing = [column for column in rule.columns if column not in frame.columns]
    if missing:
        raise DedupeConfigError(
            f"Fuzzy rule columns not in frame: {', '.join(missing)}"
        )

    # Exact duplicates first: cheap, and unambiguous.
    merges: list[Merge] = []
    merged_away: set[Any] = set()
    exact_seen: dict[tuple, Any] = {}
    for index, row in frame.iterrows():
        exact_key = tuple(
            "" if is_missing(row.get(column)) else str(row.get(column)).strip().lower()
            for column in rule.columns
        )
        if exact_key in exact_seen:
            merges.append(Merge(exact_seen[exact_key], index, 1.0, "exact", "identical values"))
            merged_away.add(index)
        else:
            exact_seen[exact_key] = index

    # Then fuzzy, within blocks, skipping anything already merged.
    blocks: dict[str, list[Any]] = {}
    for index, row in frame.iterrows():
        if index in merged_away:
            continue
        for key in _block_keys(row, rule.columns):
            blocks.setdefault(key, []).append(index)

    positions = {index: position for position, index in enumerate(frame.index)}
    compared: set[tuple] = set()
    for members in blocks.values():
        if len(members) < 2:
            continue
        # Sort by the joined compared values so a windowed large block compares
        # neighbours that actually resemble each other, not arbitrary order.
        if len(members) > EXHAUSTIVE_BLOCK_LIMIT:
            members = sorted(
                members,
                key=lambda index: "|".join(
                    ""
                    if is_missing(frame.at[index, column])
                    else str(frame.at[index, column]).lower()
                    for column in rule.columns
                ),
            )
        for left_index, right_index in _compare_pairs(members):
            if left_index in merged_away or right_index in merged_away:
                continue
            pair = (left_index, right_index)
            if pair in compared:
                continue
            compared.add(pair)
            score, metric = _row_similarity(
                frame.loc[left_index], frame.loc[right_index], rule
            )
            if score >= rule.threshold:
                merges.append(
                    Merge(left_index, right_index, score, metric, "fuzzy match")
                )
                merged_away.add(right_index)

    merges.sort(key=lambda merge: positions[merge.dropped_index])
    return merges, len(compared)


def fuzzy_dedupe(
    frame: pd.DataFrame,
    rule: FuzzyRule,
    keep: str = "first",
) -> FuzzyDedupeResult:
    """Drop fuzzy duplicates, keeping the first occurrence by default.

    ``keep='last'`` is not supported for fuzzy matching: which row survives
    changes which other rows match it, so "keep last" is not well defined
    without a second pass. Passing it raises rather than producing a result
    that silently depends on iteration order.
    """
    if keep != "first":
        raise DedupeConfigError(
            "fuzzy_dedupe only supports keep='first'; 'last' is undefined for "
            "approximate matching"
        )
    merges, compared_pairs = find_fuzzy_duplicates(frame, rule)
    if rule.max_cluster_size is not None and merges:
        kept_counts: dict[Any, int] = {}
        for merge in merges:
            kept_counts[merge.kept_index] = kept_counts.get(merge.kept_index, 0) + 1
        worst, count = max(kept_counts.items(), key=lambda item: item[1])
        if count >= rule.max_cluster_size:
            raise ClusterTooLargeError(
                f"Fuzzy match would fold {count + 1} rows into the row at index "
                f"{worst!r}, above max_cluster_size={rule.max_cluster_size}. "
                "Lower the threshold, narrow the columns, or raise "
                "max_cluster_size if the merge is intended."
            )
    dropped = {merge.dropped_index for merge in merges}
    result_frame = frame.drop(index=list(dropped)).reset_index(drop=True)
    return FuzzyDedupeResult(
        frame=result_frame,
        merges=merges,
        rows_in=len(frame),
        compared_pairs=compared_pairs,
    )
