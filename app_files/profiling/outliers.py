"""Outlier detection: IQR fences, z-scores, and an isolation forest.

Three methods, one result shape, so a caller can compare them without learning
three vocabularies. None of them needs a dependency the project does not
already have: the isolation forest is implemented here over numpy rather than
pulled from scikit-learn, because ``requirements.txt`` is what CI installs and
adding scikit-learn there would put a build-time dependency on a wheel for
every deployment.

Each method is deliberately conservative on a degenerate column. A constant
column has zero spread, and both the IQR fence and the z-score divide by that
spread — so they return nothing rather than a division-by-zero or a false
positive on every row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

METHODS = ("iqr", "zscore", "isolation_forest")

# Default fences. 1.5 is Tukey's convention; 3.0 is the usual "far out" cut.
_DEFAULT_IQR_K = 1.5
_DEFAULT_Z_K = 3.0
# Contamination is the share of rows an isolation forest expects to be
# anomalous. It sets the score threshold, so the method flags *that share* of
# the column by construction — it is a policy, not a parameter to tune per
# file. The default is deliberately small: "1 row in 100" reads as rare, where
# 5% of a 12,000-row column would be 600 flags and read as noise. A caller who
# wants the tail rather than the rare should use ``iqr`` or ``zscore``.
_DEFAULT_CONTAMINATION = 0.01


@dataclass
class OutlierResult:
    """The outliers found in one column by one method."""

    method: str = "iqr"
    column: str = ""
    indices: list[int] = field(default_factory=list)
    values: list[float] = field(default_factory=list)
    scores: dict[int, float] = field(default_factory=dict)
    lower_bound: float | None = None
    upper_bound: float | None = None
    k: float | None = None

    @property
    def count(self) -> int:
        return len(self.indices)

    def as_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "column": self.column,
            "count": self.count,
            "indices": self.indices,
            "values": self.values,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "k": self.k,
        }


def _numeric_series(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """``(positions, values)`` for the parseable entries, dropping the rest.

    A non-numeric value is skipped, not raised on: a column with one stray
    "n/a" still has outliers worth finding.
    """
    coerced = pd.to_numeric(series, errors="coerce")
    mask = coerced.notna()
    positions = pd.Series(range(len(series)))[mask]
    return positions, coerced[mask].astype(float)


def _result(method: str, positions: pd.Series, values: pd.Series, **extra) -> OutlierResult:
    return OutlierResult(
        method=method,
        indices=[int(index) for index in positions.index],
        values=[round(float(value), 6) for value in values],
        **extra,
    )


def iqr_outliers(
    series: pd.Series, *, k: float = _DEFAULT_IQR_K, column: str = ""
) -> OutlierResult:
    """Tukey fences: a value outside ``[p25 - k*iqr, p75 + k*iqr]``.

    The fence, not the raw quartiles, is what makes this robust on a small
    sample: with few points the quartiles move, so a wide ``k`` is the honest
    way to ask for fewer flags.
    """
    positions, values = _numeric_series(series)
    if len(values) == 0:
        return OutlierResult(method="iqr", column=column, k=k)
    p25 = float(values.quantile(0.25))
    p75 = float(values.quantile(0.75))
    iqr = p75 - p25
    lower = p25 - k * iqr
    upper = p75 + k * iqr
    if iqr == 0:
        # Zero spread: every value sits on the fence, so nothing is outside it.
        return OutlierResult(
            method="iqr", column=column, k=k, lower_bound=lower, upper_bound=upper
        )
    mask = (values < lower) | (values > upper)
    return _result(
        "iqr", positions[mask], values[mask], column=column,
        lower_bound=round(lower, 6), upper_bound=round(upper, 6), k=k,
    )


def zscore_outliers(
    series: pd.Series, *, k: float = _DEFAULT_Z_K, column: str = ""
) -> OutlierResult:
    """Values more than ``k`` standard deviations from the mean."""
    positions, values = _numeric_series(series)
    if len(values) == 0:
        return OutlierResult(method="zscore", column=column, k=k)
    mean = float(values.mean())
    std = float(values.std(ddof=0))
    if std == 0:
        return OutlierResult(method="zscore", column=column, k=k)
    scores = (values - mean) / std
    mask = scores.abs() > k
    result = _result("zscore", positions[mask], values[mask], column=column, k=k)
    result.scores = {
        int(index): round(float(score), 6)
        for index, score in scores[mask].items()
    }
    return result


def isolation_forest_outliers(
    series: pd.Series,
    *,
    n_trees: int = 100,
    sample_size: int | None = None,
    contamination: float = _DEFAULT_CONTAMINATION,
    seed: int = 0,
    column: str = "",
) -> OutlierResult:
    """An isolation forest over the column's numeric values.

    An isolation forest isolates a point by splitting the data at random and
    counting how many splits it takes to separate that point. An outlier is
    isolated in few splits, so a short path length is the anomaly signal.

    The score is ``0.5 - 2 ** (-mean_path / c(n))`` in the standard
    formulation, which lands in ``[-0.5, 0.5]``: near ``0.5`` is anomalous and
    near ``0`` (or negative) is normal. The threshold is the
    ``1 - contamination`` quantile of the scores, so ``contamination`` is the
    share of rows the method is allowed to call anomalous.

    Args:
        n_trees: ensemble size. More trees means a steadier score.
        sample_size: points per tree; defaults to ``min(256, n)``, the
            original paper's subsample, which is what keeps the cost linear.
        seed: fixed so a run is reproducible. An anomaly flag that changes
            between identical runs is not usable as a gate.
    """
    positions, values = _numeric_series(series)
    if len(values) == 0:
        return OutlierResult(method="isolation_forest", column=column)
    data = values.to_numpy(dtype=float).reshape(-1, 1)
    if len(data) < 2 or float(data.std()) == 0:
        # One point, or no spread to split on.
        return OutlierResult(method="isolation_forest", column=column)

    rng = np.random.default_rng(seed)
    size = sample_size or min(256, len(data))
    size = max(2, min(size, len(data)))
    depth_limit = int(np.ceil(np.log2(size)))
    paths = np.zeros(len(data), dtype=float)

    for _ in range(n_trees):
        sample = data[rng.choice(len(data), size=size, replace=False)]
        paths += _tree_depths(data, sample, depth_limit, rng)

    mean_path = paths / n_trees
    normaliser = _average_path_length(size)
    # The standard score: 2 ** (-E(h) / c(n)). A point isolated in few splits
    # has a small E(h), so the exponent is near zero and the score approaches
    # 1.0; a point buried among neighbours scores near 0.5 or below. Higher is
    # more anomalous.
    scores = np.power(2.0, -mean_path / normaliser)
    threshold = float(np.quantile(scores, 1.0 - contamination))
    mask = scores >= threshold
    # A quantile threshold always flags *something*; on a column with no real
    # anomaly that would be a false positive. Require the point to also score
    # above 0.5, the formulation's boundary between "normal" and "anomalous".
    mask &= scores > 0.5

    result = OutlierResult(
        method="isolation_forest", column=column, k=contamination
    )
    result.indices = [int(index) for index in positions[mask].index]
    result.values = [round(float(value), 6) for value in values[mask]]
    result.scores = {
        int(index): round(float(score), 6)
        for index, score in zip(positions.index, scores)
    }
    return result


def _tree_depths(
    data: np.ndarray, sample: np.ndarray, depth_limit: int, rng: np.random.Generator
) -> np.ndarray:
    """The isolation depth of every point in ``data`` under one random tree.

    The tree is built once from the subsample, then every point is descended
    through it level by level in numpy. That is ``depth`` vectorised passes per
    tree rather than a Python walk per point, which is the difference between
    a usable method and a 12,000-row column taking over a minute.
    """
    nodes = _build_tree(sample[:, 0], depth_limit, rng)
    split, left, right, leaf_size = nodes
    values = data[:, 0]

    depths = np.zeros(len(values), dtype=float)
    current = np.full(len(values), 0, dtype=int)  # node index; root is 0
    depth = np.zeros(len(values), dtype=float)
    done = np.zeros(len(values), dtype=bool)

    for _ in range(depth_limit + 2):
        pending = np.flatnonzero(~done)
        if pending.size == 0:
            break
        node = current[pending]
        is_leaf = left[node] < 0
        if is_leaf.any():
            finished = pending[is_leaf]
            depths[finished] = depth[finished] + _average_path_length_array(
                leaf_size[node[is_leaf]]
            )
            done[finished] = True
        descending = pending[~is_leaf]
        if descending.size:
            going_left = values[descending] < split[current[descending]]
            current[descending] = np.where(
                going_left, left[current[descending]], right[current[descending]]
            )
            depth[descending] += 1

    return depths


def _build_tree(
    sample: np.ndarray, depth_limit: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build a random isolation tree over ``sample`` as parallel arrays.

    Returns ``(split, left, right, leaf_size)``. A node with ``left == -1`` is a
    leaf and ``leaf_size`` is the number of sample points that reached it,
    which is what the path-length correction is computed from.
    """
    split: list[float] = []
    left: list[int] = []
    right: list[int] = []
    leaf_size: list[int] = []

    def add(values: np.ndarray, depth: int) -> int:
        index = len(split)
        split.append(float("nan"))
        left.append(-1)
        right.append(-1)
        leaf_size.append(0)

        if depth >= depth_limit or len(values) <= 1:
            leaf_size[index] = len(values)
            return index
        span = float(values.max() - values.min())
        if span <= 0:
            leaf_size[index] = len(values)
            return index
        cut = float(rng.uniform(values.min(), values.max()))
        lower = values[values < cut]
        upper = values[values >= cut]
        if len(lower) == 0 or len(upper) == 0:
            leaf_size[index] = len(values)
            return index
        split[index] = cut
        left[index] = add(lower, depth + 1)
        right[index] = add(upper, depth + 1)
        return index

    add(sample, 0)
    return (
        np.array(split, dtype=float),
        np.array(left, dtype=int),
        np.array(right, dtype=int),
        np.array(leaf_size, dtype=int),
    )


def _average_path_length_array(sizes: np.ndarray) -> np.ndarray:
    """``_average_path_length`` over an array of leaf sizes."""
    unique, inverse = np.unique(sizes, return_inverse=True)
    table = np.array([_average_path_length(int(size)) for size in unique], dtype=float)
    return table[inverse]


def _average_path_length(n: int) -> float:
    """``c(n)``, the expected path length of an unsuccessful BST search."""
    if n <= 1:
        return 0.0
    if n == 2:
        return 1.0
    return 2.0 * (np.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)


def detect_outliers(
    series: pd.Series, *, method: str = "iqr", column: str = "", **kwargs: Any
) -> OutlierResult:
    """Dispatch to the named method.

    Args:
        method: one of ``iqr``, ``zscore``, ``isolation_forest``.
        column: the column's name, carried into the result for reporting.
        **kwargs: passed through (``k``, ``seed``, ``contamination``, …).
    """
    key = str(method).strip().lower()
    if key not in METHODS:
        raise ValueError(
            f"Unknown outlier method {method!r}; known methods: {', '.join(METHODS)}"
        )
    if key == "iqr":
        return iqr_outliers(series, column=column, **kwargs)
    if key == "zscore":
        return zscore_outliers(series, column=column, **kwargs)
    return isolation_forest_outliers(series, column=column, **kwargs)
