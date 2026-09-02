"""Quality validation: completeness, uniqueness, validity, consistency."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.mappers import MappingConfig
from app_files.transforms import is_missing, is_valid_email, is_valid_phone, to_iso_date


@dataclass
class Issue:
    row: int
    field: str
    check: str
    severity: str
    message: str


@dataclass
class ValidationReport:
    issues: list[Issue] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)
    unique_fields: list[str] = field(default_factory=list)
    date_format: str = "%Y-%m-%d"
    total_records: int = 0

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def flagged_rows(self) -> set[int]:
        return {issue.row for issue in self.issues}

    @property
    def quality_score(self) -> float:
        if not self.issues:
            return 100.0
        total = max(self.total_records, 1)
        flagged = len(self.flagged_rows)
        return round((total - flagged) / total * 100, 1)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    def summary(self) -> dict[str, Any]:
        return {
            "total_records": max(self.total_records, 1),
            "quality_score": self.quality_score,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "records_to_review": len(self.flagged_rows),
        }

    def checks(self) -> dict[str, dict[str, int]]:
        checks: dict[str, dict[str, int]] = {}
        for issue in self.issues:
            if issue.check not in checks:
                checks[issue.check] = {"passed": 0, "failed": 0}
            checks[issue.check]["failed"] += 1
        return checks

    def issues_frame(self) -> pd.DataFrame:
        if not self.issues:
            return pd.DataFrame(columns=["row", "field", "check", "severity", "message"])
        return pd.DataFrame(
            [
                {
                    "row": issue.row + 2,  # +2 for header + 1-indexed
                    "field": issue.field,
                    "check": issue.check,
                    "severity": issue.severity,
                    "message": issue.message,
                }
                for issue in self.issues
            ]
        )


def validate_data(
    frame: pd.DataFrame,
    config: MappingConfig,
    date_format: str = "%Y-%m-%d",
    default_region: str = "US",
) -> ValidationReport:
    report = ValidationReport(
        required_fields=config.required_fields(),
        unique_fields=config.unique_fields(),
        date_format=date_format,
        total_records=len(frame),
    )

    for idx, row in frame.iterrows():
        # Check required fields
        for field in report.required_fields:
            if field in frame.columns and is_missing(row[field]):
                report.issues.append(
                    Issue(
                        row=idx,
                        field=field,
                        check="completeness",
                        severity="error",
                        message=f"Required field '{field}' is empty",
                    )
                )

        # Check unique fields
        for field in report.unique_fields:
            if field in frame.columns:
                value = row[field]
                if not is_missing(value):
                    duplicates = frame[frame[field] == value]
                    if len(duplicates) > 1:
                        report.issues.append(
                            Issue(
                                row=idx,
                                field=field,
                                check="uniqueness",
                                severity="error",
                                message=f"Value '{value}' is not unique in field '{field}'",
                            )
                        )

        # Check field validity
        for field in frame.columns:
            value = row[field]
            if is_missing(value):
                continue

            # Email validation
            if "email" in field.lower() and not is_valid_email(value):
                report.issues.append(
                    Issue(
                        row=idx,
                        field=field,
                        check="validity",
                        severity="error",
                        message=f"Invalid email format: '{value}'",
                    )
                )

            # Phone validation
            if "phone" in field.lower() and not is_valid_phone(value, default_region):
                report.issues.append(
                    Issue(
                        row=idx,
                        field=field,
                        check="validity",
                        severity="warning",
                        message=f"Invalid phone format: '{value}'",
                    )
                )

            # Date validation
            if "date" in field.lower():
                try:
                    to_iso_date(value, date_format)
                except Exception:
                    report.issues.append(
                        Issue(
                            row=idx,
                            field=field,
                            check="consistency",
                            severity="warning",
                            message=f"Date format inconsistent with {date_format}: '{value}'",
                        )
                    )

    return report
