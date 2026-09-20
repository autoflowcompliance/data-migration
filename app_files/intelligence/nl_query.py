"""Natural language queries: filter a frame by asking a question in English.

"show me rows where the email is invalid" becomes a real DataFrame filter, and
the tool tells you which filter it applied so the answer can be checked::

    rows where the email is invalid
      -> email is not a valid email address
      3 of 7 rows matched

This is a deterministic parser, not a language model. That is a deliberate
choice for this audience: a query that silently misinterprets "over 500" as
"under 500" is worse than one that says "I did not understand that". So when the
sentence cannot be parsed the caller gets ``understood=False`` and the reason,
never a silent full-table result.

Supported shapes:

* validity — "invalid", "not valid", "malformed", "blank", "missing", "empty"
* equality — "email is bob@x.com", "status equals lead"
* uniqueness — "duplicate emails"
* comparison — "amount > 500", "amount over 500", "quantity at least 3"
* membership — "country is one of USA, France, UK"
* contains — "company contains acme"
* bare field — "show me the email" (selects the column)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dataclass_field
from typing import Any, Callable

import pandas as pd

from app_files.transforms import is_missing, is_valid_email, is_valid_phone, to_iso_date

_KEYWORDS = {"show", "me", "rows", "row", "where", "the", "a", "an", "all", "is", "are", "was",
             "were", "with", "that", "have", "has", "find", "list", "give", "get", "display",
             "please", "and", "or", "of", "in", "on", "to", "for"}

_COMPARISONS: list[tuple[str, str]] = [
    (r">=|at least|no less than|greater than or equal", ">="),
    (r"<=|at most|no more than|less than or equal", "<="),
    (r"(?<![<>])>|over|above|more than|greater than|exceeds?", ">"),
    (r"(?<![<>])<|under|below|less than|fewer than", "<"),
    (r"!=|not equal|different from", "!="),
    (r"=|equals?|is exactly|==|is equal to", "=="),
]

_VALIDITY_BAD = r"invalid|not valid|malformed|bad|broken|wrong format|incorrect"
_BLANK = r"\b(blank|empty|missing|null|absent)\b"


class QueryError(ValueError):
    """Raised when no supported filter can be derived from the sentence."""


@dataclass
class QueryResult:
    """The rows a question selected, plus how they were selected."""

    text: str
    frame: pd.DataFrame
    understood: bool = True
    explanation: str = ""
    field: str = ""
    operation: str = ""
    matched: int = 0
    total: int = 0
    reason: str = ""
    columns_requested: list[str] = dataclass_field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "understood": self.understood,
            "operation": self.operation,
            "field": self.field,
            "matched": self.matched,
            "total": self.total,
            "explanation": self.explanation,
            "reason": self.reason,
        }

    def as_text(self) -> str:
        if not self.understood:
            return f"I could not turn that into a filter. {self.reason}"
        return f"{self.matched} of {self.total} rows matched — {self.explanation}"


def _match_field(text: str, available: list[str]) -> str | None:
    """Longest column name that appears in the sentence, alias-aware."""
    lowered = text.lower()
    aliases = {
        "email": ("email", "e-mail", "mail"),
        "phone": ("phone", "mobile", "telephone", "cell"),
        "date": ("date", "createdate", "created"),
        "name": ("name", "lastname", "firstname"),
        "amount": ("amount", "value", "total"),
        "country": ("country",),
        "state": ("state", "province"),
        "city": ("city", "town"),
        "company": ("company", "organisation", "organization"),
    }
    for column in sorted(available, key=len, reverse=True):
        if re.search(r"\b" + re.escape(str(column).lower()) + r"\b", lowered):
            return str(column)
    for column in available:
        for alias in aliases:
            if alias in str(column).lower():
                for word in aliases[alias]:
                    if re.search(r"\b" + re.escape(word) + r"s?\b", lowered):
                        return str(column)
    return None


def _validity_column(text: str, available: list[str]) -> str | None:
    """Which column a validity question is about, if any."""
    return _match_field(text, available)


def _checker_for(column: str) -> Callable[[Any], bool]:
    lowered = str(column).lower()
    if "email" in lowered or "mail" in lowered:
        return is_valid_email
    if "phone" in lowered or "mobile" in lowered or "tel" in lowered:
        return is_valid_phone
    if "date" in lowered or "created" in lowered:
        return lambda value: bool(to_iso_date(value))
    return lambda value: not is_missing(value)


def _number(text: str) -> float | None:
    match = re.search(r"(-?\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def _to_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    text = re.sub(r"[^0-9.\-]", "", text)
    try:
        return float(text)
    except ValueError:
        return None


def query(text: str, frame: pd.DataFrame) -> QueryResult:
    """Answer ``text`` against ``frame``.

    Never raises for an unparseable sentence: it returns ``understood=False`` so
    the UI can say "I did not understand" instead of showing the whole table and
    implying it answered.
    """
    available = [str(c) for c in frame.columns]
    lowered = text.strip().lower()

    if frame is None:
        return QueryResult(text=text, frame=pd.DataFrame(), understood=False,
                           reason="There is no data loaded yet.")

    # -- column selection: "show me the email column"
    if re.search(r"\b(columns?|fields?)\b", lowered) and not re.search(r"\bwhere\b", lowered):
        picked = [c for c in available if re.search(r"\b" + re.escape(c.lower()) + r"\b", lowered)]
        if picked:
            return QueryResult(
                text=text, frame=frame[picked], understood=True,
                explanation=f"showing column(s) {', '.join(picked)}",
                matched=len(frame), total=len(frame), columns_requested=picked,
                operation="select",
            )

    # -- duplicates: "duplicate emails"
    if re.search(r"\b(duplicate|duplicated|repeated)\b", lowered):
        column = _match_field(lowered, available)
        if column:
            mask = frame[column].astype(str).str.strip().str.lower().duplicated(keep=False)
            mask &= frame[column].map(lambda v: not is_missing(v))
            return _result(text, frame, mask, column, "duplicate",
                           f"{column} appears more than once", available)

    # -- blanks: "rows with a missing email"
    if re.search(_BLANK, lowered):
        column = _match_field(lowered, available)
        if column:
            mask = frame[column].map(is_missing)
            return _result(text, frame, mask, column, "is_blank",
                           f"{column} is empty", available)

    # -- validity: "rows where the email is invalid"
    if re.search(_VALIDITY_BAD, lowered):
        column = _match_field(lowered, available)
        if column:
            checker = _checker_for(column)
            mask = frame[column].map(lambda v: (not is_missing(v)) and (not checker(v)))
            return _result(text, frame, mask, column, "is_invalid",
                           f"{column} is not a valid value for its type", available)

    # -- membership: "country is one of a, b"
    membership = re.search(r"\b(?:one of|in the list|either)\b\s*(.+)", lowered)
    if membership:
        column = _match_field(lowered, available)
        if column:
            values = [v.strip(" .;'\"") for v in re.split(r",|/|\bor\b", membership.group(1)) if v.strip()]
            mask = frame[column].astype(str).str.strip().str.lower().isin([v.lower() for v in values])
            return _result(text, frame, mask, column, "in_list",
                           f"{column} is one of {values}", available)

    # -- contains: "company contains acme"
    contains = re.search(r"\b(contains?|includes?|starts? with|ends? with)\b\s*['\"]?([\w@.\- ]+)", lowered)
    if contains:
        column = _match_field(lowered, available)
        if column:
            needle = contains.group(2).strip().strip("'\"")
            if contains.group(1).startswith("starts"):
                mask = frame[column].astype(str).str.lower().str.startswith(needle.lower())
                op = "starts_with"
            elif contains.group(1).startswith("ends"):
                mask = frame[column].astype(str).str.lower().str.endswith(needle.lower())
                op = "ends_with"
            else:
                mask = frame[column].astype(str).str.lower().str.contains(re.escape(needle.lower()), na=False)
                op = "contains"
            return _result(text, frame, mask, column, op,
                           f"{column} {op.replace('_', ' ')} {needle!r}", available)

    # -- comparison / equality
    # The operator pattern is wrapped in a non-capturing group: without it, the
    # alternation binds so the trailing capture group attaches only to the last
    # alternative, and "amount over 500" yields no captured operand at all.
    for pattern, operator in _COMPARISONS:
        match = re.search(r"(?:" + pattern + r")\s*['\"]?([\w@.\-+:/ ]+)", lowered)
        if not match:
            continue
        column = _match_field(lowered, available)
        if not column:
            continue
        raw = (match.group(1) or "").strip().strip("'\"")
        raw = re.split(r"\s+(?:and|or|rows?|where)\b", raw)[0].strip()
        numeric = _number(raw)
        if numeric is not None and operator in {">", "<", ">=", "<="}:
            mask = frame[column].map(lambda v: _compare(_to_number(v), operator, numeric))
            return _result(text, frame, mask, column, operator,
                           f"{column} {operator} {numeric:g}", available)
        if not raw:
            continue
        mask = frame[column].astype(str).str.strip().str.lower() == raw.lower()
        return _result(text, frame, mask, column, "==", f"{column} equals {raw!r}", available)

    # -- "not" as a negation of the above didn't match; try a bare field select.
    column = _match_field(lowered, available)
    if column:
        return QueryResult(
            text=text, frame=frame[[column]], understood=True,
            explanation=f"showing column {column} (no filter recognised)",
            field=column, operation="select", matched=len(frame), total=len(frame),
            columns_requested=[column],
        )

    return QueryResult(
        text=text, frame=frame.iloc[0:0], understood=False,
        reason=(
            "Try one of: 'rows where the email is invalid', 'phone is blank', "
            "'amount over 500', 'country is one of USA, France', "
            "'company contains acme', 'duplicate emails'."
        ),
    )


def _compare(value: float | None, operator: str, target: float) -> bool:
    if value is None:
        return False
    if operator == ">":
        return value > target
    if operator == "<":
        return value < target
    if operator == ">=":
        return value >= target
    if operator == "<=":
        return value <= target
    if operator == "!=":
        return value != target
    return value == target


def _result(
    text: str,
    frame: pd.DataFrame,
    mask: Any,
    column: str,
    operation: str,
    explanation: str,
    available: list[str],
) -> QueryResult:
    mask = pd.Series(mask, index=frame.index).fillna(False).astype(bool)
    selected = frame[mask]
    return QueryResult(
        text=text,
        frame=selected,
        understood=True,
        explanation=explanation,
        field=column,
        operation=operation,
        matched=len(selected),
        total=len(frame),
    )


def answer(text: str, frame: pd.DataFrame) -> str:
    """One-line answer, for a CLI or a chat box."""
    return query(text, frame).as_text()