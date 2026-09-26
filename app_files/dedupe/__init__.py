"""Fuzzy duplicate detection, a sibling to the cleaner's exact dedupe.

The frozen cleaner removes rows that are byte-identical on the chosen columns.
This layer removes rows that *describe the same thing* without being identical,
and records every merge. It never modifies `cleaners/`.

    from app_files.dedupe import FuzzyRule, fuzzy_dedupe

    rule = FuzzyRule(columns=["first_name", "last_name"], threshold=0.9)
    result = fuzzy_dedupe(frame, rule)
    result.duplicates_removed
    result.merges_frame()          # one row per merge, with the score
"""

from app_files.dedupe.engine import (
    DEFAULT_METRIC,
    DEFAULT_THRESHOLD,
    ClusterTooLargeError,
    DedupeConfigError,
    FuzzyDedupeResult,
    FuzzyRule,
    Merge,
    find_fuzzy_duplicates,
    fuzzy_dedupe,
)
from app_files.dedupe.similarity import (
    METRICS,
    jaro,
    jaro_winkler,
    levenshtein_distance,
    levenshtein_ratio,
    similarity,
)

__all__ = [
    "DEFAULT_METRIC",
    "DEFAULT_THRESHOLD",
    "METRICS",
    "ClusterTooLargeError",
    "DedupeConfigError",
    "FuzzyDedupeResult",
    "FuzzyRule",
    "Merge",
    "find_fuzzy_duplicates",
    "fuzzy_dedupe",
    "jaro",
    "jaro_winkler",
    "levenshtein_distance",
    "levenshtein_ratio",
    "similarity",
]
