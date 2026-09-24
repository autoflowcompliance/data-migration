"""Approximate string similarity, implemented here rather than pulled in.

Two metrics, both operating on whole strings:

``levenshtein_ratio``  1 - (edit distance / longest length), so 1.0 is
                       identical. A banded dynamic program is used; it is O(n*m)
                       time but O(min(n,m)) space, which matters when a file has
                       tens of thousands of rows.
``jaro_winkler``      The Jaro similarity boosted for a shared prefix, the
                       metric that handles transposed names ("Jon" / "John")
                       better than edit distance alone.

Both are case- and whitespace-insensitive by default: "John Smith" and
"john  smith" are the same person, and a matcher that says otherwise is wrong
for deduplication.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Values shorter than this are compared exactly. Fuzzy-matching two three-letter
#: strings produces a stream of false merges ("Ann"/"Ana"/"Amy") that no
#: threshold can separate, so short values are left to exact comparison.
MIN_FUZZY_LENGTH = 4


def normalise(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def levenshtein_distance(left: str, right: str) -> int:
    """Edit distance with a two-row rolling buffer."""
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    # Keep the shorter string on the row axis for the smaller buffer.
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            cost = 0 if left_char == right_char else 1
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
            )
        previous = current
    return previous[-1]


def levenshtein_ratio(left: str, right: str) -> float:
    a, b = normalise(left), normalise(right)
    if not a and not b:
        return 1.0
    longest = max(len(a), len(b))
    if longest == 0:
        return 1.0
    return 1.0 - levenshtein_distance(a, b) / longest


def jaro(left: str, right: str) -> float:
    a, b = normalise(left), normalise(right)
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    window = max(len(a), len(b)) // 2 - 1
    window = max(window, 0)
    a_matched = [False] * len(a)
    b_matched = [False] * len(b)
    matches = 0
    for i, char in enumerate(a):
        start = max(0, i - window)
        end = min(i + window + 1, len(b))
        for j in range(start, end):
            if b_matched[j] or b[j] != char:
                continue
            a_matched[i] = True
            b_matched[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    transpositions = 0
    k = 0
    for i, matched in enumerate(a_matched):
        if not matched:
            continue
        while not b_matched[k]:
            k += 1
        if a[i] != b[k]:
            transpositions += 1
        k += 1
    transpositions //= 2
    return (
        matches / len(a) + matches / len(b) + (matches - transpositions) / matches
    ) / 3.0


def jaro_winkler(left: str, right: str, prefix_weight: float = 0.1) -> float:
    base = jaro(left, right)
    if base < 0.7:
        return base
    a, b = normalise(left), normalise(right)
    prefix = 0
    for left_char, right_char in zip(a, b, strict=False):
        if left_char != right_char or prefix == 4:
            break
        prefix += 1
    return base + prefix * prefix_weight * (1 - base)


METRICS = {
    "levenshtein": levenshtein_ratio,
    "jaro_winkler": jaro_winkler,
}


def similarity(left: str, right: str, metric: str = "levenshtein") -> float:
    try:
        fn = METRICS[metric]
    except KeyError:
        raise ValueError(
            f"Unknown similarity metric {metric!r}. Available: {', '.join(sorted(METRICS))}"
        ) from None
    return fn(left, right)


@dataclass(frozen=True)
class Comparison:
    """Why two values were judged similar, so a merge can be explained."""

    score: float
    metric: str
    left: str
    right: str
