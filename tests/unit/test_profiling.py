"""Unit tests for the five profiling dimensions and the overall score."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.profiling import (
    DIMENSION_NAMES,
    dimensions,
    profile,
    scorecard_rows,
)


def test_five_dimensions_are_exposed():
    assert set(DIMENSION_NAMES) == {
        "completeness", "uniqueness", "validity", "consistency", "timeliness",
    }


# ------------------------------------------------------------- completeness
def test_completeness_is_100_for_a_full_frame():
    frame = pd.DataFrame({"a": ["x", "y"], "b": ["1", "2"]})
    assert dimensions.completeness(frame) == 100.0


def test_completeness_counts_nulls_and_blanks_as_missing():
    frame = pd.DataFrame({"a": ["x", None, ""], "b": ["1", "2", "3"]})
    # Only "x" is filled in column a; column b is fully filled: 4 of 6 = 66.7%.
    assert dimensions.completeness(frame) == 66.7


# --------------------------------------------------------------- uniqueness
def test_uniqueness_is_100_when_no_rows_repeat():
    frame = pd.DataFrame({"a": ["x", "y", "z"]})
    assert dimensions.uniqueness(frame) == 100.0


def test_uniqueness_penalises_duplicate_rows():
    frame = pd.DataFrame({"a": ["x", "x", "y", "y"]})
    assert dimensions.uniqueness(frame) == 50.0


# ----------------------------------------------------------------- validity
def test_validity_scores_format_columns():
    frame = pd.DataFrame(
        {
            "email": ["a@x.com", "b@x.com", "not-an-email", ""],
            "phone": ["+14155552671", "+14155552672", "+14155552673", "+14155552674"],
        }
    )
    # 6 of 7 checked cells pass; the blank email is counted as a failure here.
    assert dimensions.validity(frame) == pytest.approx(85.7, abs=0.1)


def test_validity_is_100_for_a_frame_with_no_format_columns():
    frame = pd.DataFrame({"notes": ["anything", "else"]})
    assert dimensions.validity(frame) == 100.0


# -------------------------------------------------------------- consistency
def test_consistency_rewards_a_single_case_convention():
    uniform = pd.DataFrame({"firstname": ["Ann", "Bob", "Cara"]})
    mixed = pd.DataFrame({"firstname": ["Ann", "BOB", "cara"]})
    assert dimensions.consistency(uniform) >= dimensions.consistency(mixed)


def test_consistency_checks_canonical_dates():
    good = pd.DataFrame({"createdate": ["2024-01-01", "2024-02-02"]})
    bad = pd.DataFrame({"createdate": ["31-Dec-24", "02/15/2024"]})
    assert dimensions.consistency(good) > dimensions.consistency(bad)


# --------------------------------------------------------------- timeliness
def test_timeliness_is_100_when_all_dates_are_inside_the_window():
    frame = pd.DataFrame({"date": ["2024-01-01", "2024-06-01", "2024-12-01"]})
    assert dimensions.timeliness(frame, start="2024-01-01", end="2024-12-31") == 100.0


def test_timeliness_penalises_dates_outside_the_window():
    frame = pd.DataFrame({"date": ["2024-01-01", "1999-01-01", "2024-06-01", "1999-06-01"]})
    assert dimensions.timeliness(frame, start="2024-01-01", end="2024-12-31") == 50.0


def test_timeliness_is_100_with_no_date_columns():
    assert dimensions.timeliness(pd.DataFrame({"notes": ["a", "b"]})) == 100.0


# ------------------------------------------------------------ overall profiler
def test_profile_returns_all_five_scores_in_range():
    frame = pd.DataFrame(
        {
            "firstname": ["Ann", "Bob", "Cara"],
            "email": ["a@x.com", "b@x.com", "c@x.com"],
            "createdate": ["2024-01-01", "2024-02-02", "2024-03-03"],
        }
    )
    result = profile(frame)
    assert set(result.scores) == set(DIMENSION_NAMES)
    for name, value in result.scores.items():
        assert 0.0 <= value <= 100.0, name
    assert 0.0 <= result.overall <= 100.0


def test_profile_scores_an_empty_frame_as_zero():
    result = profile(pd.DataFrame())
    assert all(value == 0.0 for value in result.scores.values())
    assert result.overall == 0.0
    assert result.row_count == 0


def test_profile_quality_degrades_with_dirty_data(clean_frame: pd.DataFrame):
    dirty = clean_frame.copy()
    dirty.loc[0, "email"] = "not-an-email"
    dirty.loc[1, "firstname"] = "BOB"
    assert profile(dirty).overall < profile(clean_frame).overall


def test_profile_as_dict_has_all_dimensions(clean_frame: pd.DataFrame):
    data = profile(clean_frame).as_dict()
    for name in DIMENSION_NAMES:
        assert name in data
    assert "overall" in data
    assert data["row_count"] == 3


def test_scorecard_rows_cover_every_dimension(clean_frame: pd.DataFrame):
    rows = scorecard_rows(profile(clean_frame))
    assert len(rows) == len(DIMENSION_NAMES)
    # The label is title-cased for display, so compare case-insensitively.
    assert {row["dimension"].lower() for row in rows} == set(DIMENSION_NAMES)
    for row in rows:
        assert {"dimension", "score", "band"} <= set(row)
        assert 0.0 <= row["score"] <= 100.0


def test_profile_of_employee_sample(samples_dir: Path):
    frame = pd.read_csv(samples_dir / "employee_records.csv", dtype=str, keep_default_na=False)
    result = profile(frame)
    for name in DIMENSION_NAMES:
        assert 0.0 <= result.scores[name] <= 100.0
    assert result.row_count == len(frame)