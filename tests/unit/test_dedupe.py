"""Fuzzy deduplication: metrics, thresholds, blocking, and the safety cap."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.dedupe import (
    ClusterTooLargeError,
    DedupeConfigError,
    FuzzyRule,
    find_fuzzy_duplicates,
    fuzzy_dedupe,
    jaro,
    jaro_winkler,
    levenshtein_distance,
    levenshtein_ratio,
    similarity,
)

# 25 realistic distinct names. Each gets a one-character variant, so a correct
# run removes exactly 25 rows and never merges across two different names.
NAMES = [
    "Katherine", "Michael", "Christopher", "Elizabeth", "Alexander",
    "Frederick", "Gwendolyn", "Nathaniel", "Priscilla", "Sebastian",
    "Theodore", "Victoria", "Bernadette", "Cornelius", "Dominique",
    "Evangeline", "Florence", "Gregory", "Henrietta", "Ignatius",
    "Josephine", "Kimberly", "Leonardo", "Marguerite", "Nicholas",
]


class TestMetrics:
    def test_levenshtein_distance_known_values(self):
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "abc") == 0

    def test_levenshtein_ratio_bounds(self):
        assert levenshtein_ratio("same", "same") == 1.0
        assert levenshtein_ratio("abcd", "xyzq") == 0.0
        assert 0.0 < levenshtein_ratio("John", "Jon") < 1.0

    def test_metrics_are_case_and_space_insensitive(self):
        assert levenshtein_ratio("John Smith", "  john   smith ") == 1.0

    def test_jaro_winkler_beats_levenshtein_on_names(self):
        """The reason Jaro-Winkler is the default for names."""
        assert jaro_winkler("John", "Jon") > levenshtein_ratio("John", "Jon")
        assert jaro_winkler("John", "Jon") > 0.9

    def test_jaro_winkler_handles_transposition(self):
        assert jaro_winkler("Martha", "Marhta") > 0.95

    def test_jaro_identical_and_empty(self):
        assert jaro("abc", "abc") == 1.0
        assert jaro("", "abc") == 0.0

    def test_unknown_metric_names_the_alternatives(self):
        with pytest.raises(ValueError, match="jaro_winkler"):
            similarity("a", "b", "cosine")

    def test_similarity_round_trips_through_the_registry(self):
        assert similarity("John", "Jon", "levenshtein") == levenshtein_ratio("John", "Jon")
        assert similarity("John", "Jon", "jaro_winkler") == jaro_winkler("John", "Jon")


class TestFuzzyRule:
    def test_string_columns_become_a_list(self):
        rule = FuzzyRule.from_dict({"columns": "email"})
        assert rule.columns == ["email"]

    def test_missing_columns_rejected(self):
        with pytest.raises(DedupeConfigError, match="columns"):
            FuzzyRule.from_dict({"threshold": 0.9})

    def test_out_of_range_threshold_rejected(self):
        with pytest.raises(DedupeConfigError, match="threshold"):
            FuzzyRule.from_dict({"columns": ["a"], "threshold": 0})
        with pytest.raises(DedupeConfigError, match="threshold"):
            FuzzyRule.from_dict({"columns": ["a"], "threshold": 1.5})

    def test_unknown_metric_rejected(self):
        with pytest.raises(DedupeConfigError, match="metric"):
            FuzzyRule.from_dict({"columns": ["a"], "metric": "cosine"})

    def test_unknown_key_rejected(self):
        with pytest.raises(DedupeConfigError, match="unknown"):
            FuzzyRule.from_dict({"columns": ["a"], "treshold": 0.9})

    def test_default_metric_is_jaro_winkler(self):
        assert FuzzyRule.from_dict({"columns": ["a"]}).metric == "jaro_winkler"


class TestSpecCriteria:
    """The two worked examples the specification names."""

    def test_jon_smith_dedupes_at_085(self):
        frame = pd.DataFrame({"first": ["John", "Jon"], "last": ["Smith", "Smith"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["first", "last"], threshold=0.85))
        assert result.rows_out == 1
        assert result.duplicates_removed == 1

    def test_jon_smith_survives_at_095(self):
        frame = pd.DataFrame({"first": ["John", "Jon"], "last": ["Smith", "Smith"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["first", "last"], threshold=0.95))
        assert result.rows_out == 2
        assert result.duplicates_removed == 0

    def test_fifty_near_duplicate_fixture_merges_exactly(self):
        """25 distinct names, each with one variant: 25 merges, none across names."""
        rows = []
        for name in NAMES:
            rows.append({"first": name, "last": "Aaronson"})
            rows.append({"first": name[:-1] + chr(ord(name[-1]) + 1), "last": "Aaronson"})
        frame = pd.DataFrame(rows)
        result = fuzzy_dedupe(
            frame, FuzzyRule(columns=["first", "last"], threshold=0.9)
        )
        assert result.rows_in == 50
        assert result.duplicates_removed == 25
        assert result.rows_out == 25

        positions = {index: position for position, index in enumerate(frame.index)}
        for merge in result.merges:
            assert abs(positions[merge.kept_index] - positions[merge.dropped_index]) == 1


class TestDuplicates:
    def test_identical_rows_merge_regardless_of_threshold(self):
        frame = pd.DataFrame({"name": ["same", "same"], "city": ["x", "x"]})
        # A threshold of 1.0 that only exact duplicates can satisfy.
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name", "city"], threshold=1.0))
        assert result.duplicates_removed == 1

    def test_company_suffix_variation_merges(self):
        frame = pd.DataFrame({"name": ["Acme Inc", "Acme, Inc"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.9))
        assert result.duplicates_removed == 1

    def test_distinct_rows_are_kept(self):
        frame = pd.DataFrame({"name": ["Alpha", "Beta", "Gamma"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.9))
        assert result.duplicates_removed == 0
        assert result.rows_out == 3

    def test_short_values_are_compared_exactly(self):
        """Three-letter strings must not fuzzy-match each other."""
        frame = pd.DataFrame({"code": ["Ann", "Ana", "Amy"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["code"], threshold=0.9))
        assert result.duplicates_removed == 0

    def test_blank_values_do_not_merge_rows(self):
        frame = pd.DataFrame({"name": ["Alice", "Bob"], "note": [None, None]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name", "note"], threshold=0.5))
        assert result.duplicates_removed == 0

    def test_require_all_false_matches_on_one_column(self):
        frame = pd.DataFrame({"name": ["John", "Jane"], "city": ["Springfield", "Springfield"]})
        strict = fuzzy_dedupe(frame, FuzzyRule(columns=["name", "city"], threshold=0.9))
        loose = fuzzy_dedupe(
            frame,
            FuzzyRule(columns=["name", "city"], threshold=0.9, require_all=False),
        )
        assert strict.duplicates_removed == 0
        assert loose.duplicates_removed == 1


class TestBlockingAndScale:
    def test_blocking_limits_comparisons_on_a_large_frame(self):
        """O(n^2) on 2000 rows is 2M pairs; blocking must do far fewer."""
        frame = pd.DataFrame({"name": [f"UniqueName{i:05d}" for i in range(2000)]})
        merges, compared = find_fuzzy_duplicates(
            frame, FuzzyRule(columns=["name"], threshold=0.99)
        )
        assert merges == []
        assert compared < 200_000

    def test_matches_across_a_sorted_position_gap(self):
        """Blocking must not require the duplicate to be adjacent."""
        # All-distinct initial letters: no shared prefix for Jaro-Winkler to
        # latch onto, so only the John/Jon pair can match.
        filler = [
            "apple", "bridge", "cactus", "dolphin", "ember", "falcon",
            "granite", "harbor", "igloo", "jasmine", "kettle", "lantern",
            "meadow", "nectar", "orchard", "pebble", "quartz", "ribbon",
            "saffron", "timber", "umbrella", "violin", "walnut", "xylophone",
            "yarrow", "zephyr",
        ]
        frame = pd.DataFrame({"name": ["John", *filler, "Jon"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.85))
        assert result.duplicates_removed == 1
        assert result.merges[0].kept_index == 0
        assert result.merges[0].dropped_index == len(frame) - 1

    def test_empty_frame(self):
        result = fuzzy_dedupe(pd.DataFrame({"name": []}), FuzzyRule(columns=["name"]))
        assert result.rows_out == 0
        assert result.merges_frame().empty

    def test_missing_column_raises(self):
        frame = pd.DataFrame({"name": ["a"]})
        with pytest.raises(DedupeConfigError, match="not in frame"):
            fuzzy_dedupe(frame, FuzzyRule(columns=["absent"]))


class TestSafetyCap:
    def test_prefix_shaped_column_would_collapse_without_a_cap(self):
        """Jaro-Winkler rates shared prefixes high; this is the documented trap."""
        frame = pd.DataFrame({"id": [f"Customer{i:02d}Record" for i in range(6)]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["id"], threshold=0.9))
        assert result.rows_out < 6  # collapsed, and every merge is recorded

    def test_cap_stops_the_collapse_with_a_clear_error(self):
        frame = pd.DataFrame({"id": [f"Customer{i:02d}Record" for i in range(6)]})
        with pytest.raises(ClusterTooLargeError, match="max_cluster_size"):
            fuzzy_dedupe(
                frame,
                FuzzyRule(columns=["id"], threshold=0.9, max_cluster_size=5),
            )

    def test_cap_permits_a_legitimate_merge(self):
        frame = pd.DataFrame({"name": ["John Smith", "Jon Smith"]})
        result = fuzzy_dedupe(
            frame, FuzzyRule(columns=["name"], threshold=0.85, max_cluster_size=2)
        )
        assert result.duplicates_removed == 1


class TestResultContract:
    def test_merges_are_auditable(self):
        frame = pd.DataFrame({"name": ["John", "Jon"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.85))
        merges = result.merges_frame()
        assert list(merges.columns) == ["kept_row", "dropped_row", "score", "metric", "reason"]
        assert merges.iloc[0]["reason"] == "fuzzy match"
        assert merges.iloc[0]["metric"] == "jaro_winkler"

    def test_summary_reports_the_counts(self):
        frame = pd.DataFrame({"name": ["John", "Jon", "Zoe"]})
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.85))
        summary = result.summary()
        assert summary["rows_in"] == 3
        assert summary["rows_out"] == 2
        assert summary["duplicates_removed"] == 1

    def test_input_frame_is_not_mutated(self):
        frame = pd.DataFrame({"name": ["John", "Jon"]})
        before = frame.copy(deep=True)
        fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.85))
        pd.testing.assert_frame_equal(frame, before)

    def test_keep_last_is_refused(self):
        frame = pd.DataFrame({"name": ["John", "Jon"]})
        with pytest.raises(DedupeConfigError, match="keep='first'"):
            fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.85), keep="last")

    def test_output_index_is_reset(self):
        frame = pd.DataFrame({"name": ["John", "Jon", "Zoe"]}, index=[10, 20, 30])
        result = fuzzy_dedupe(frame, FuzzyRule(columns=["name"], threshold=0.85))
        assert list(result.frame.index) == [0, 1]
