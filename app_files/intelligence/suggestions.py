"""Smart suggestions: read the profile, then say the useful next thing.

After profiling, the tool already knows which columns are sparse, which are
duplicated, which values fail their format, and how old the dates are. This
module turns those facts into ranked, actionable advice::

    87% of phone numbers are missing — flag these 6 rows for review, or fill
    them from a secondary source?

Every suggestion is produced by a rule that inspects the actual numbers, and
each carries the measurement it came from. Two different files therefore
produce different suggestions, and a suggestion never appears for a problem the
data does not have. Each one offers a concrete next action that maps onto a
feature the tool really has.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.profiling import profile
from app_files.transforms import is_missing, is_valid_email, is_valid_phone


@dataclass
class Suggestion:
    """One piece of advice, with the evidence behind it."""

    title: str
    detail: str
    field: str = ""
    severity: str = "info"
    measurement: float = 0.0
    action: str = ""
    """The concrete thing to do, phrased as the tool's own feature."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "field": self.field,
            "severity": self.severity,
            "detail": self.detail,
            "measurement": round(self.measurement, 4),
            "action": self.action,
        }

    def sentence(self) -> str:
        return f"{self.detail} {self.action}".strip()


@dataclass
class SuggestionSet:
    suggestions: list[Suggestion] = field(default_factory=list)
    overall_score: float = 0.0
    dimensions: dict[str, float] = field(default_factory=dict)

    @property
    def empty(self) -> bool:
        return not self.suggestions

    def top(self, n: int = 3) -> list[Suggestion]:
        return self.suggestions[:n]

    def frame(self) -> pd.DataFrame:
        columns = ["title", "field", "severity", "detail", "measurement", "action"]
        if not self.suggestions:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([s.as_dict() for s in self.suggestions], columns=columns)

    def summary(self) -> dict[str, Any]:
        return {
            "count": len(self.suggestions),
            "fields": [s.field for s in self.suggestions if s.field],
            "overall_score": self.overall_score,
            "dimensions": self.dimensions,
        }


# Thresholds, named so the reason a suggestion appeared is auditable.
HIGH_MISSING = 0.30
SOME_MISSING = 0.05
LOW_DIMENSION = 70.0
_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _null_rate(frame: pd.DataFrame, column: str) -> float:
    if column not in frame.columns or len(frame) == 0:
        return 0.0
    missing = sum(1 for value in frame[column] if is_missing(value))
    return missing / len(frame)


def _missing_rows(frame: pd.DataFrame, column: str) -> int:
    return sum(1 for value in frame[column] if is_missing(value))


def _invalid_rows(frame: pd.DataFrame, column: str, kind: str) -> int:
    """Rows whose non-blank value fails its format. Blanks are not counted here
    — they are a completeness problem, and counting them twice would inflate
    the advice."""
    checker = is_valid_email if kind == "email" else is_valid_phone
    total = 0
    for value in frame[column]:
        if is_missing(value):
            continue
        if not checker(value):
            total += 1
    return total


def _column_named(frame: pd.DataFrame, *fragments: str) -> str | None:
    for column in frame.columns:
        lowered = str(column).lower()
        if any(fragment in lowered for fragment in fragments):
            return str(column)
    return None


def suggest(frame: pd.DataFrame, top_n: int = 5) -> SuggestionSet:
    """Derive ranked suggestions from the frame's own profile."""
    if frame is None or frame.empty:
        return SuggestionSet()

    prof = profile(frame)
    dimensions = {name: round(value, 1) for name, value in prof.scores.items()}
    result = SuggestionSet(overall_score=round(prof.overall, 1), dimensions=dimensions)

    # 1. Very sparse columns: the completeness story.
    sparse: list[tuple[str, float, int]] = []
    for column in map(str, frame.columns):
        rate = _null_rate(frame, column)
        if rate >= SOME_MISSING:
            sparse.append((column, rate, _missing_rows(frame, column)))
    sparse.sort(key=lambda item: item[1], reverse=True)

    for column, rate, missing in sparse[:3]:
        if rate >= HIGH_MISSING:
            result.suggestions.append(
                Suggestion(
                    title=f"{column} is mostly empty",
                    field=column,
                    severity="error",
                    measurement=rate,
                    detail=(
                        f"{rate * 100:.0f}% of {column} values are missing "
                        f"({missing} of {len(frame)} rows)."
                    ),
                    action=(
                        "Flag these rows for review, or fill them from a secondary "
                        "source before importing."
                    ),
                )
            )
        else:
            result.suggestions.append(
                Suggestion(
                    title=f"{column} has gaps",
                    field=column,
                    severity="warning",
                    measurement=rate,
                    detail=(
                        f"{rate * 100:.0f}% of {column} values are missing "
                        f"({missing} of {len(frame)} rows)."
                    ),
                    action="Check whether those rows should be imported at all.",
                )
            )

    # 2. Format failures that survived cleaning.
    email_column = _column_named(frame, "email", "mail")
    if email_column:
        bad = _invalid_rows(frame, email_column, "email")
        if bad:
            result.suggestions.append(
                Suggestion(
                    title="Some emails are still invalid",
                    field=email_column,
                    severity="warning",
                    measurement=bad / max(len(frame), 1),
                    detail=f"{bad} {email_column} value(s) are not valid email addresses.",
                    action="Open the issues list, fix them at source, then re-run.",
                )
            )

    phone_column = _column_named(frame, "phone", "mobile", "tel")
    if phone_column:
        bad = _invalid_rows(frame, phone_column, "phone")
        if bad:
            result.suggestions.append(
                Suggestion(
                    title="Some phone numbers are not in E.164 form",
                    field=phone_column,
                    severity="warning",
                    measurement=bad / max(len(frame), 1),
                    detail=f"{bad} {phone_column} value(s) could not be standardised.",
                    action="Check the default region setting, then re-run.",
                )
            )

    # 3. Weak profiling dimensions, named so the buyer knows what to fix.
    for dimension, value in sorted(prof.scores.items(), key=lambda kv: kv[1]):
        if value >= LOW_DIMENSION:
            continue
        label = dimension.replace("_", " ")
        result.suggestions.append(
            Suggestion(
                title=f"{label.title()} is the weakest dimension",
                severity="warning",
                measurement=value / 100.0,
                detail=f"{label.title()} scored {value:.1f} out of 100.",
                action=(
                    "Start here — improving it lifts the overall score the most."
                ),
            )
        )

    # 4. Duplicates, using the profile's uniqueness figure rather than re-deriving it.
    uniqueness = float(prof.scores.get("uniqueness", 100.0))
    if uniqueness < 100.0:
        result.suggestions.append(
            Suggestion(
                title="Duplicate rows were found",
                severity="warning",
                measurement=(100.0 - uniqueness) / 100.0,
                detail=f"Uniqueness scored {uniqueness:.1f} out of 100.",
                action="The duplicates are already removed in the output; check the diff to see which.",
            )
        )

    # 5. Timeliness, so stale data is not silently accepted.
    timeliness = float(prof.scores.get("timeliness", 100.0))
    if timeliness < LOW_DIMENSION:
        result.suggestions.append(
            Suggestion(
                title="Dates look stale",
                severity="info",
                measurement=(100.0 - timeliness) / 100.0,
                detail=f"Timeliness scored {timeliness:.1f} out of 100.",
                action="Confirm you exported a current extract rather than an archived one.",
            )
        )

    # Rank: severity first, then size of the problem.
    result.suggestions.sort(
        key=lambda s: (_SEVERITY_ORDER.get(s.severity, 3), -s.measurement)
    )
    result.suggestions = result.suggestions[:top_n]
    return result


def suggestion_texts(frame: pd.DataFrame, top_n: int = 3) -> list[str]:
    """The suggestion sentences, for display or testing."""
    return [s.sentence() for s in suggest(frame, top_n=top_n).suggestions]


def render_suggestions_html(suggestion_set: SuggestionSet) -> str:
    """A standalone suggestions card. No external resources."""
    if suggestion_set.empty:
        body = "<p class='ok'>No issues found worth flagging.</p>"
    else:
        items = "".join(
            f"<li class='{s.severity}'><strong>{s.title}</strong> "
            f"<span class='why'>{s.detail}</span> "
            f"<span class='do'>{s.action}</span></li>"
            for s in suggestion_set.suggestions
        )
        body = f"<ul>{items}</ul>"
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Suggestions</title>"
        "<style>body{font-family:sans-serif;padding:20px;color:#111827;}"
        "ul{list-style:none;padding:0;}li{border-left:4px solid #e5e7eb;padding:8px 14px;"
        "margin-bottom:8px;background:#fff;}li.error{border-color:#dc2626;}"
        "li.warning{border-color:#f59e0b;}li.info{border-color:#0ea5e9;}"
        ".why{color:#6b7280;font-size:13px;}.do{display:block;font-size:13px;color:#111827;"
        "margin-top:4px;}.ok{color:#047857;font-weight:600;}</style></head><body>"
        f"<h1>Suggestions</h1><p>Quality score {suggestion_set.overall_score:.1f}%</p>"
        f"{body}</body></html>"
    )