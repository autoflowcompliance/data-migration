"""The "What Was Fixed" summary: one plain-English paragraph per run.

A non-technical buyer does not want a table. They want to read one paragraph and
know the tool worked::

    Removed 1 duplicate row. Standardised 6 dates from 3 different formats.
    Fixed 5 phone numbers to international format. Flagged 1 record for manual
    review. Your data is now 67% clean and ready for import.

Every number in that paragraph comes from the run's own artefacts — the cleaning
log, the lineage events, the issues list and the validation summary. Nothing is
hardcoded, and an action that did not happen produces no sentence.

``write_summary(result)`` returns the paragraphs; ``render_summary_html`` wraps
them in a standalone card for the top of a report.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class FixSummary:
    """Structured facts behind the paragraph, plus the prose."""

    rows_in: int = 0
    rows_out: int = 0
    duplicates_removed: int = 0
    dates_standardised: int = 0
    date_formats_seen: int = 0
    phones_fixed: int = 0
    emails_normalised: int = 0
    names_split: int = 0
    values_trimmed: int = 0
    flagged_for_review: int = 0
    errors: int = 0
    warnings: int = 0
    quality_score: float = 0.0
    sentences: list[str] = field(default_factory=list)

    def paragraph(self) -> str:
        return " ".join(self.sentences)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "duplicates_removed": self.duplicates_removed,
            "dates_standardised": self.dates_standardised,
            "phones_fixed": self.phones_fixed,
            "emails_normalised": self.emails_normalised,
            "names_split": self.names_split,
            "values_trimmed": self.values_trimmed,
            "flagged_for_review": self.flagged_for_review,
            "errors": self.errors,
            "warnings": self.warnings,
            "quality_score": self.quality_score,
            "paragraph": self.paragraph(),
        }


def _count_actions(events: list[Any], action: str) -> int:
    total = 0
    for event in events:
        value = event.get("action", "") if isinstance(event, dict) else getattr(event, "action", "")
        if str(value) == action:
            total += 1
    return total


def _events(result: Any) -> list[Any]:
    tracker = getattr(result, "lineage", None)
    if tracker is None:
        return []
    return list(getattr(tracker, "events", []))


def _distinct_date_formats(original: pd.DataFrame, column: str) -> int:
    """How many different date spellings appear in a column.

    Counts shape, not exact value: ``12/31/24`` and ``01/05/24`` are one format,
    ``31-Dec-24`` another. That is the number the buyer cares about.
    """
    if column not in original.columns:
        return 0
    shapes = set()
    for value in original[column]:
        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "nat"}:
            continue
        shape = "".join("9" if ch.isdigit() else "A" if ch.isalpha() else ch for ch in text)
        shapes.add(shape)
    return len(shapes)


def _issues_frame(result: Any) -> pd.DataFrame:
    validation = getattr(result, "validation", None)
    if validation is None:
        return pd.DataFrame()
    try:
        return validation.issues_frame()
    except Exception:  # noqa: BLE001 - a summary must never break a run
        return pd.DataFrame()


def write_summary(result: Any, original: pd.DataFrame | None = None) -> FixSummary:
    """Derive the plain-English summary from one pipeline result.

    Args:
        result: a ``PipelineResult`` (lineage enabled for the richest summary).
        original: the frame that went in; used only to count date formats.
    """
    summary = result.summary() if hasattr(result, "summary") else {}
    events = _events(result)

    fix = FixSummary(
        rows_in=int(summary.get("rows_in", 0)),
        rows_out=int(summary.get("rows_out", 0)),
        duplicates_removed=int(summary.get("duplicates_removed", 0)),
        flagged_for_review=int(summary.get("rows_to_review", 0) or summary.get("to_review", 0) or 0),
        errors=int(summary.get("errors", 0)),
        warnings=int(summary.get("warnings", 0)),
        quality_score=float(summary.get("quality_score", 0.0)),
    )

    issues = _issues_frame(result)
    if not issues.empty and "row" in issues.columns:
        fix.flagged_for_review = int(issues["row"].nunique())

    # Which fields actually changed, so each sentence is earned.
    changed_date_fields = set()
    for event in events:
        action = str(event.get("action", "") if isinstance(event, dict) else getattr(event, "action", ""))
        field_name = str(event.get("field", "") if isinstance(event, dict) else getattr(event, "field", ""))
        if action.startswith("map:") and "date" in field_name.lower():
            changed_date_fields.add(field_name)
        if action.startswith("clean") and "date" in field_name.lower():
            changed_date_fields.add(field_name)

    fix.dates_standardised = sum(
        1 for event in events
        if "date" in str(event.get("field", "") if isinstance(event, dict) else getattr(event, "field", "")).lower()
    )
    fix.phones_fixed = sum(
        1 for event in events
        if "phone" in str(event.get("field", "") if isinstance(event, dict) else getattr(event, "field", "")).lower()
        and str(event.get("after", "") if isinstance(event, dict) else getattr(event, "after", "")).startswith("+")
    )
    fix.emails_normalised = _count_actions(events, "map:email_lowercase") + _count_actions(events, "map:lower_case")
    fix.names_split = _count_actions(events, "map:split_full_name_first") + _count_actions(
        events, "map:split_full_name_last"
    )
    fix.values_trimmed = _count_actions(events, "map:trim") + _count_actions(events, "clean")

    if original is not None:
        date_columns = [c for c in original.columns if "date" in str(c).lower()]
        fix.date_formats_seen = max(
            (_distinct_date_formats(original, column) for column in date_columns), default=0
        )

    fix.sentences = _sentences(fix)
    return fix


def _sentences(fix: FixSummary) -> list[str]:
    """Build the paragraph, including only sentences backed by a real count."""
    out: list[str] = []
    if fix.duplicates_removed:
        noun = "row" if fix.duplicates_removed == 1 else "rows"
        out.append(f"Removed {fix.duplicates_removed} duplicate {noun}.")
    if fix.dates_standardised:
        formats = f" across {fix.date_formats_seen} different formats" if fix.date_formats_seen > 1 else ""
        out.append(f"Standardised {fix.dates_standardised} date value(s){formats} to ISO 8601.")
    if fix.phones_fixed:
        out.append(f"Converted {fix.phones_fixed} phone number(s) to international (E.164) format.")
    if fix.emails_normalised:
        out.append(f"Normalised {fix.emails_normalised} email/name value(s) to lower case.")
    if fix.names_split:
        out.append(f"Split {fix.names_split} combined name value(s) into first and last names.")
    if fix.flagged_for_review:
        noun = "record" if fix.flagged_for_review == 1 else "records"
        out.append(f"Flagged {fix.flagged_for_review} {noun} for manual review.")
    if not out:
        out.append("No changes were needed — every value was already clean.")

    if fix.quality_score:
        out.append(
            f"Your data is now {fix.quality_score:.0f}% clean"
            + (" and ready for import." if fix.quality_score >= 70 else ".")
        )
    return out


_STYLE = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;padding:20px;}
.card{max-width:760px;border:1px solid #e5e7eb;border-left:4px solid #2563eb;
      border-radius:8px;padding:16px 20px;background:#fff;}
h2{margin:0 0 8px;font-size:15px;text-transform:uppercase;letter-spacing:.05em;color:#6b7280;}
p{margin:0;font-size:15px;line-height:1.55;color:#111827;}
.meta{margin-top:10px;font-size:12px;color:#6b7280;}
"""


def render_summary_html(fix: FixSummary, title: str = "What was fixed") -> str:
    """A standalone card for the top of any report. No external resources."""
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>{_STYLE}</style></head><body>"
        "<div class='card'>"
        f"<h2>{html.escape(title)}</h2>"
        f"<p>{html.escape(fix.paragraph())}</p>"
        f"<div class='meta'>{fix.rows_in} rows in → {fix.rows_out} rows out · "
        f"{fix.errors} error(s) · {fix.warnings} warning(s) · "
        f"quality score {fix.quality_score:.1f}%</div>"
        "</div></body></html>"
    )


def render_summary_markdown(fix: FixSummary) -> str:
    return fix.paragraph()


def summary_frame(fix: FixSummary) -> pd.DataFrame:
    """The facts as a one-row frame, for CSV output."""
    return pd.DataFrame([fix.as_dict()])