"""Interface tests for the profiling extension: pattern inference.

Written before the implementation. ``infer_pattern`` proposes a regex that
covers every value in a column, plus a label a human recognises. The
distinction that matters: a column that is *all* emails is an email column, and
one that merely *contains* an email is not.
"""

from __future__ import annotations

import re

import pandas as pd
import pytest

from app_files.profiling.patterns import (
    InferredPattern,
    infer_column_pattern,
    infer_pattern,
    match_rate,
)


# ------------------------------------------------------------------- labels
def test_a_column_of_emails_is_labelled_email():
    pattern = infer_pattern(pd.Series(["a@x.com", "b@y.org", "c@z.net"]))
    assert pattern.label == "email"
    assert pattern.coverage == 1.0


def test_a_column_of_iso_dates_is_labelled_date():
    pattern = infer_pattern(pd.Series(["2024-01-01", "2024-06-30", "2025-12-31"]))
    assert pattern.label == "date"
    assert pattern.coverage == 1.0


def test_a_column_of_integers_is_labelled_integer():
    pattern = infer_pattern(pd.Series(["1", "42", "1000"]))
    assert pattern.label == "integer"


def test_a_column_of_uuids_is_labelled_uuid():
    values = [
        "123e4567-e89b-12d3-a456-426614174000",
        "123e4567-e89b-12d3-a456-426614174001",
    ]
    assert infer_pattern(pd.Series(values)).label == "uuid"


def test_a_column_of_currency_is_labelled_currency():
    assert infer_pattern(pd.Series(["$1.00", "$20.50", "$300.00"])).label == "currency"


def test_an_unrecognised_column_falls_back_to_text():
    assert infer_pattern(pd.Series(["hello world", "some prose", "a sentence"])).label == "text"


# --------------------------------------------------------------- the regex
def test_the_regex_actually_matches_every_value():
    values = ["AB-1234", "CD-5678", "EF-9012"]
    pattern = infer_pattern(pd.Series(values))
    compiled = re.compile(pattern.regex)
    assert all(compiled.fullmatch(value) for value in values)


def test_the_regex_is_anchored_so_it_does_not_match_a_substring():
    pattern = infer_pattern(pd.Series(["AB-1234", "CD-5678"]))
    compiled = re.compile(pattern.regex)
    assert compiled.fullmatch("xxAB-1234yy") is None


def test_an_email_column_is_not_matched_by_a_bare_text_pattern():
    pattern = infer_pattern(pd.Series(["a@x.com", "b@y.org"]))
    compiled = re.compile(pattern.regex)
    assert compiled.fullmatch("not an email") is None


# -------------------------------------------------------------- coverage
def test_coverage_is_the_share_of_non_blank_values_matched():
    # One value breaks the shape, so coverage is 2/3.
    pattern = infer_pattern(pd.Series(["AB-1234", "CD-5678", "nonsense"]))
    assert pattern.coverage == pytest.approx(2 / 3, abs=1e-6)


def test_blanks_are_excluded_from_coverage():
    pattern = infer_pattern(pd.Series(["AB-1234", "", None, "CD-5678"]))
    assert pattern.coverage == 1.0
    assert pattern.sampled == 2


def test_an_all_blank_column_reports_no_pattern():
    pattern = infer_pattern(pd.Series([None, "", None]))
    assert pattern.label == "text"
    assert pattern.coverage == 0.0
    assert pattern.sampled == 0


def test_match_rate_scores_a_candidate_regex_against_a_series():
    series = pd.Series(["AB-1234", "CD-5678", "nope"])
    assert match_rate(r"^[A-Z]{2}-\d{4}$", series) == pytest.approx(2 / 3, abs=1e-6)


# ------------------------------------------------------------------- frame
def test_infer_column_pattern_returns_one_per_column():
    frame = pd.DataFrame({"id": ["AB-1234", "CD-5678"], "who": ["a@x.com", "b@y.org"]})
    patterns = infer_column_pattern(frame)
    assert [p.name for p in patterns] == ["id", "who"]
    assert all(isinstance(p, InferredPattern) for p in patterns)


def test_inferred_pattern_is_serialisable():
    payload = infer_pattern(pd.Series(["a@x.com"])).as_dict()
    assert payload["label"] == "email"
    assert "regex" in payload and "coverage" in payload


def test_pattern_inference_is_bounded_on_a_wide_column():
    # 10k distinct values must not turn into a 10k-branch alternation.
    series = pd.Series([f"value-{i}" for i in range(10_000)])
    pattern = infer_pattern(series)
    assert len(pattern.regex) < 2000
