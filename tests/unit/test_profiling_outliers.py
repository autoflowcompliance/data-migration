"""Interface tests for the profiling extension: outlier detection.

Written before the implementation. Three methods share one result shape so a
caller can compare them without learning three vocabularies:

* IQR — a value outside ``[p25 - k*iqr, p75 + k*iqr]``.
* z-score — a value more than ``k`` standard deviations from the mean.
* isolation forest — an ensemble that isolates outliers by random splits.

The IQR and z-score boundaries are asserted by hand-computed arithmetic so a
future refactor cannot quietly move the threshold.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app_files.profiling.outliers import (
    OutlierResult,
    detect_outliers,
    iqr_outliers,
    isolation_forest_outliers,
    zscore_outliers,
)


@pytest.fixture
def with_outlier() -> pd.Series:
    # 10 tight values around 20-29, then a single 1000.
    return pd.Series([20.0, 21, 22, 23, 24, 25, 26, 27, 28, 29, 1000.0])


# ---------------------------------------------------------------------- IQR
def test_iqr_flags_the_obvious_outlier(with_outlier):
    result = iqr_outliers(with_outlier)
    assert 10 in result.indices
    assert result.count == 1


def test_iqr_bounds_are_the_hand_computed_fences():
    # [1,2,3,4,5]: p25=2, p75=4, iqr=2, fences at 2-1.5*2=-1 and 4+1.5*2=7.
    result = iqr_outliers(pd.Series([1.0, 2, 3, 4, 5]))
    assert result.lower_bound == pytest.approx(-1.0)
    assert result.upper_bound == pytest.approx(7.0)


def test_iqr_respects_a_wider_multiplier():
    series = pd.Series([1.0, 2, 3, 4, 5, 100.0])
    # Fences for this series: p25=2.25, p75=4.75, iqr=2.5, so the upper fence
    # is 4.75 + k*2.5. At k=1.5 that is 8.5 and 100 is out; at k=50 it is
    # 129.75 and 100 is back inside.
    assert iqr_outliers(series, k=1.5).count == 1
    assert iqr_outliers(series, k=50.0).count == 0


def test_iqr_on_a_constant_column_finds_nothing():
    result = iqr_outliers(pd.Series([5.0, 5.0, 5.0, 5.0]))
    assert result.count == 0


# ------------------------------------------------------------------ z-score
def test_zscore_flags_the_obvious_outlier(with_outlier):
    result = zscore_outliers(with_outlier, k=3.0)
    assert 10 in result.indices


def test_zscore_threshold_is_in_standard_deviations():
    # mean 0, std 1.58; the 4.0 is ~2.53 deviations out, so k=2 catches it and
    # k=3 does not.
    series = pd.Series([-1.0, -0.5, 0.0, 0.5, 1.0, 4.0])
    assert 5 in zscore_outliers(series, k=2.0).indices
    assert 5 not in zscore_outliers(series, k=3.0).indices


def test_zscore_on_a_constant_column_finds_nothing():
    # Zero spread would divide by zero; it must return empty, not raise.
    assert zscore_outliers(pd.Series([3.0, 3.0, 3.0]), k=3.0).count == 0


# --------------------------------------------------------- isolation forest
def test_isolation_forest_flags_the_obvious_outlier(with_outlier):
    result = isolation_forest_outliers(with_outlier, seed=0)
    assert 10 in result.indices


def test_isolation_forest_is_deterministic_for_a_seed(with_outlier):
    first = isolation_forest_outliers(with_outlier, seed=7)
    second = isolation_forest_outliers(with_outlier, seed=7)
    assert first.indices == second.indices


def test_isolation_forest_on_a_constant_column_finds_nothing():
    assert isolation_forest_outliers(pd.Series([2.0] * 20), seed=0).count == 0


def test_isolation_forest_scores_are_in_a_bounded_range(with_outlier):
    # The standard formulation scores in (0, 1]: near 1.0 is anomalous.
    result = isolation_forest_outliers(with_outlier, seed=0)
    assert all(0.0 < score <= 1.0 for score in result.scores.values())
    assert result.scores[10] > 0.5  # the planted outlier is the anomalous one


# ---------------------------------------------------------------- dispatch
def test_detect_outliers_dispatches_by_method(with_outlier):
    assert detect_outliers(with_outlier, method="iqr").method == "iqr"
    assert detect_outliers(with_outlier, method="zscore").method == "zscore"
    assert (
        detect_outliers(with_outlier, method="isolation_forest").method
        == "isolation_forest"
    )


def test_an_unknown_method_is_refused(with_outlier):
    with pytest.raises(ValueError, match="method"):
        detect_outliers(with_outlier, method="crystal-ball")


def test_result_reports_the_values_flagged_not_just_the_count(with_outlier):
    result = iqr_outliers(with_outlier)
    assert 1000.0 in result.values
    assert len(result.values) == result.count


def test_a_result_is_serialisable(with_outlier):
    payload = iqr_outliers(with_outlier).as_dict()
    assert payload["method"] == "iqr"
    assert payload["count"] == 1


def test_non_numeric_values_are_skipped_not_crashed():
    result = iqr_outliers(pd.Series(["1", "2", "three", "4", "100"]))
    # "three" is unparseable; the rest still yield the outlier.
    assert result.count >= 1


def test_contamination_caps_the_share_flagged_on_a_normal_column():
    """Found on a real 12k-row export: contamination is a fraction, not a count.

    A normal column has no anomaly, so whatever the method flags is a false
    positive — and the quantile threshold flags exactly the declared share.
    The default has to be small enough that "1 in 100" does not read as noise
    on a real file.
    """
    rng = np.random.default_rng(7)
    normal = pd.Series(rng.normal(500, 50, 12_000))
    result = isolation_forest_outliers(normal, seed=0)
    assert result.count <= 120  # the default 1% ceiling, not 5% (600)


def test_isolation_forest_is_fast_enough_for_a_real_column():
    """A 12,000-row column must not take a minute; the vectorised tree is why."""
    import time

    rng = np.random.default_rng(7)
    normal = pd.Series(rng.normal(500, 50, 12_000))
    start = time.monotonic()
    isolation_forest_outliers(normal, seed=0)
    assert time.monotonic() - start < 10.0


def test_a_planted_outlier_still_scores_highest_on_a_large_column():
    rng = np.random.default_rng(7)
    values = rng.normal(500, 50, 12_000)
    values[4211] = 9_999_999.0
    result = isolation_forest_outliers(pd.Series(values), seed=0)
    assert result.scores[4211] == max(result.scores.values())
