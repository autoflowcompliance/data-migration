"""Golden file for Module 1: a known file in, known profiling out.

``orders.csv`` is a clean 12-row export with one deliberate outlier in
``amount`` (99999.00 against a 10-110 band). The golden pins the column
statistics, the inferred patterns and the outlier the three methods agree on.

Do not regenerate ``expected_profiling.json`` to make this green. If the
outlier stops being flagged, or a pattern stops being inferred, that is the
whole point of the module coming undone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from app_files.profiling.profiling_block import bind_profiling

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "profiling_columns"


@pytest.fixture(scope="module")
def observed() -> dict:
    config = json.loads((GOLDEN / "profiling.json").read_text(encoding="utf-8"))
    frame = pd.read_csv(GOLDEN / "orders.csv")
    binding = bind_profiling(frame, config)
    stats = {s.name: s.as_dict() for s in binding.statistics}
    return {
        "statistics": {
            name: {
                "kind": value["kind"],
                "count": value["count"],
                "missing": value["missing"],
                "distinct": value["distinct"],
                "minimum": value["minimum"],
                "maximum": value["maximum"],
                "mean": value["mean"],
                "median": value["median"],
                "iqr": value["iqr"],
            }
            for name, value in stats.items()
        },
        "patterns": {name: pattern.label for name, pattern in binding.patterns.items()},
        "outliers": {
            name: {
                "method": result.method,
                "count": result.count,
                "values": result.values,
            }
            for name, result in binding.outliers.items()
        },
    }


@pytest.fixture(scope="module")
def expected() -> dict:
    return json.loads((GOLDEN / "expected_profiling.json").read_text(encoding="utf-8"))


def test_statistics_match_the_golden(observed, expected):
    assert observed["statistics"] == expected["statistics"]


def test_patterns_match_the_golden(observed, expected):
    assert observed["patterns"] == expected["patterns"]


def test_outliers_match_the_golden(observed, expected):
    assert observed["outliers"] == expected["outliers"]


def test_the_outlier_is_the_amount_we_planted(observed):
    # Independent of the golden: the module must flag 99999.0, and only it.
    assert observed["outliers"]["amount"]["values"] == [99999.0]


def test_every_numeric_method_agrees_on_this_file():
    frame = pd.read_csv(GOLDEN / "orders.csv")
    for method in ("iqr", "zscore", "isolation_forest"):
        binding = bind_profiling(
            frame,
            {"profiling": {"outliers": {"enabled": True, "method": method}}},
        )
        assert binding.outliers["amount"].values == [99999.0], method


def test_the_golden_is_not_vacuous():
    """A file with the outlier removed must stop producing an outlier."""
    frame = pd.read_csv(GOLDEN / "orders.csv")
    frame = frame[frame["amount"] < 99999.0]
    binding = bind_profiling(frame, {"profiling": {"outliers": {"enabled": True}}})
    assert binding.outliers["amount"].count == 0
