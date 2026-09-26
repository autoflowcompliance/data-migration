"""Interface tests for the profiling extension: column statistics.

Written against the interface before the implementation, per the module
protocol. ``app_files.profiling.column_stats`` is the module under test; the
frozen ``profiler``/``dimensions``/``report``/``dimension_anomaly`` are not
touched and are exercised by their own tests.
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from app_files.profiling.column_stats import (
    ColumnStats,
    column_statistics,
    summarize_column,
)


@pytest.fixture
def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "amount": [10.0, 20.0, 30.0, 40.0, 1000.0],
            "city": ["Oslo", "Bergen", "Oslo", "", "Trondheim"],
            "note": ["ab", "abcd", "abcdef", None, "abcdefgh"],
            "joined": ["2024-01-01"] * 4 + [None],
        }
    )


# ------------------------------------------------------------------- numeric
def test_numeric_stats_carry_the_centre_and_spread(frame):
    stats = summarize_column(frame, "amount")
    assert stats.name == "amount"
    assert stats.kind == "numeric"
    assert stats.count == 5
    assert stats.missing == 0
    assert stats.distinct == 5
    assert stats.minimum == 10.0
    assert stats.maximum == 1000.0
    assert stats.mean == pytest.approx(220.0)
    assert stats.median == pytest.approx(30.0)


def test_numeric_quartiles_and_iqr(frame):
    stats = summarize_column(frame, "amount")
    # pandas' linear interpolation over [10,20,30,40,1000].
    assert stats.p25 == pytest.approx(20.0)
    assert stats.p75 == pytest.approx(40.0)
    assert stats.iqr == pytest.approx(20.0)


def test_std_is_population_free_of_nan(frame):
    stats = summarize_column(frame, "amount")
    assert stats.std is not None
    assert not math.isnan(stats.std)


# --------------------------------------------------------------- categorical
def test_categorical_stats_report_distinct_and_top_values(frame):
    stats = summarize_column(frame, "city")
    assert stats.kind == "categorical"
    assert stats.distinct == 3  # the blank is missing, not a value
    assert stats.missing == 1
    assert stats.missing_pct == pytest.approx(20.0)
    assert stats.top_values[0] == ("Oslo", 2)


def test_missing_pct_is_a_percentage_of_rows(frame):
    stats = summarize_column(frame, "joined")
    assert stats.missing == 1
    assert stats.missing_pct == pytest.approx(20.0)


# --------------------------------------------------------------------- text
def test_text_stats_measure_length(frame):
    stats = summarize_column(frame, "note")
    assert stats.min_length == 2
    assert stats.max_length == 8
    assert stats.mean_length == pytest.approx(5.0)


# ------------------------------------------------------------------- frame
def test_column_statistics_returns_one_entry_per_column(frame):
    stats = column_statistics(frame)
    assert [s.name for s in stats] == ["amount", "city", "note", "joined"]
    assert all(isinstance(s, ColumnStats) for s in stats)


def test_column_statistics_as_dict_is_serialisable(frame):
    payload = {s.name: s.as_dict() for s in column_statistics(frame)}
    assert payload["amount"]["kind"] == "numeric"
    assert payload["city"]["distinct"] == 3


def test_an_empty_frame_yields_no_statistics():
    assert column_statistics(pd.DataFrame()) == []


def test_an_all_blank_column_is_reported_not_crashed():
    stats = summarize_column(pd.DataFrame({"x": [None, "", None]}), "x")
    assert stats.count == 0
    assert stats.missing == 3
    assert stats.distinct == 0
    assert stats.mean is None


def test_an_unknown_column_raises():
    with pytest.raises(KeyError):
        summarize_column(pd.DataFrame({"x": [1]}), "nope")


def test_non_numeric_values_in_a_numeric_column_do_not_crash():
    stats = summarize_column(pd.DataFrame({"x": ["1", "two", "3"]}), "x")
    # "two" cannot be parsed, so the column is not numeric.
    assert stats.kind != "numeric"
    assert stats.count == 3


def test_boolean_column_is_categorical_not_numeric():
    stats = summarize_column(pd.DataFrame({"flag": [True, False, True]}), "flag")
    assert stats.kind == "categorical"
