"""Compare what the client exported from the CRM against what we delivered."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from ..transforms import is_missing


@dataclass
class AuditResult:
    expected_records: int
    imported_records: int
    missing_keys: list[str] = field(default_factory=list)
    unexpected_keys: list[str] = field(default_factory=list)
    mismatches: pd.DataFrame = field(default_factory=pd.DataFrame)
    mismatches_by_field: dict[str, int] = field(default_factory=dict)

    def stats(self) -> dict[str, object]:
        return {
            "expected_records": self.expected_records,
            "imported_records": self.imported_records,
            "missing_records": len(self.missing_keys),
            "unexpected_records": len(self.unexpected_keys),
            "mismatched_values": int(len(self.mismatches)),
            "mismatches_by_field": self.mismatches_by_field,
        }


def _normalize(series: pd.Series) -> pd.Series:
    return series.map(lambda v: "" if is_missing(v) else str(v).strip())


def audit_import(
    expected: pd.DataFrame,
    exported: pd.DataFrame,
    key: str,
    fields: list[str] | None = None,
) -> AuditResult:
    """Diff ``exported`` against ``expected`` on ``key``, field by field."""
    for name, frame in (("expected", expected), ("exported", exported)):
        if key not in frame.columns:
            raise KeyError(f"Key column '{key}' is missing from the {name} file")

    compared = [
        column
        for column in (fields or expected.columns)
        if column != key and column in exported.columns and column in expected.columns
    ]

    left = expected.copy()
    right = exported.copy()
    left[key] = _normalize(left[key])
    right[key] = _normalize(right[key])

    expected_keys = set(left[key]) - {""}
    exported_keys = set(right[key]) - {""}

    merged = left.merge(right, on=key, suffixes=("_expected", "_imported"))
    rows: list[dict[str, object]] = []
    by_field: dict[str, int] = {}
    for column in compared:
        left_values = _normalize(merged[f"{column}_expected"])
        right_values = _normalize(merged[f"{column}_imported"])
        differing = merged.index[left_values != right_values]
        by_field[column] = len(differing)
        for index in differing:
            rows.append(
                {
                    "key": merged.at[index, key],
                    "field": column,
                    "expected": left_values[index],
                    "imported": right_values[index],
                }
            )

    return AuditResult(
        expected_records=len(left),
        imported_records=len(right),
        missing_keys=sorted(expected_keys - exported_keys),
        unexpected_keys=sorted(exported_keys - expected_keys),
        mismatches=pd.DataFrame(rows, columns=["key", "field", "expected", "imported"]),
        mismatches_by_field=by_field,
    )
