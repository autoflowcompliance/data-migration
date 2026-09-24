"""Privacy controls: detect and mask the personal data a file carries.

A migration of contact data moves personal information, and a buyer
increasingly has to answer "what did you do with the PII". This layer scans a
frame for the columns that look personal, classifies what kind of data each
holds, and can mask or drop it, recording what it did.

Detection is by column name *and* by value shape, because a column called
``field_7`` full of email addresses is still email addresses. Masking is
irreversible by design — it is a shred, not a scramble with a key lying around —
and the mode is chosen per data class, so an email can be hashed for join
purposes while a phone number is simply dropped.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app_files.transforms import is_valid_email, is_valid_phone

# Data classes, in the order a report presents them.
EMAIL = "email"
PHONE = "phone"
NAME = "name"
ADDRESS = "address"
GOVERNMENT_ID = "government_id"
CARD_NUMBER = "card_number"
IP_ADDRESS = "ip_address"
DATE_OF_BIRTH = "date_of_birth"

_NAME_TOKENS = {
    EMAIL: {"email", "e-mail", "mail", "emailaddr", "emailaddress"},
    PHONE: {"phone", "mobile", "cell", "telephone", "tel", "fax", "contactnumber"},
    NAME: {"name", "firstname", "lastname", "fullname", "surname", "givenname", "contact"},
    ADDRESS: {"address", "street", "city", "town", "postcode", "zip", "postal", "country"},
    GOVERNMENT_ID: {"ssn", "nino", "nationalid", "taxid", "passport", "governmentid"},
    CARD_NUMBER: {"card", "creditcard", "cardnumber", "pan", "iban", "accountnumber"},
    IP_ADDRESS: {"ip", "ipaddress", "clientip", "remoteip"},
    DATE_OF_BIRTH: {"dob", "birthdate", "dateofbirth", "birthday"},
}

_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_SSN = re.compile(r"^\d{3}-?\d{2}-?\d{4}$")
_CARD = re.compile(r"^(?:\d[ -]?){12,18}\d$")


class PrivacyError(ValueError):
    """Raised for a privacy configuration the tool cannot act on."""


@dataclass
class DetectedColumn:
    column: str
    data_class: str
    basis: str  # name | values | mixed
    non_blank: int
    matching: int

    @property
    def confidence(self) -> float:
        return round(self.matching / self.non_blank, 3) if self.non_blank else 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "data_class": self.data_class,
            "basis": self.basis,
            "non_blank": self.non_blank,
            "matching": self.matching,
            "confidence": self.confidence,
        }


@dataclass
class PrivacyReport:
    columns: list[DetectedColumn] = field(default_factory=list)

    def classes(self) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        for column in self.columns:
            grouped.setdefault(column.data_class, []).append(column.column)
        return grouped

    def as_dict(self) -> dict[str, Any]:
        return {
            "columns": [c.as_dict() for c in self.columns],
            "by_class": self.classes(),
            "personal_columns": len(self.columns),
        }

    def render_text(self) -> str:
        if not self.columns:
            return "No personal data columns detected."
        lines = ["Personal data detected:", ""]
        for data_class, columns in sorted(self.classes().items()):
            lines.append(f"  {data_class}: {', '.join(columns)}")
        return "\n".join(lines)


def _blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return isinstance(value, str) and value.strip() == ""


def _value_class(value: Any) -> str:
    text = str(value).strip()
    if is_valid_email(text):
        return EMAIL
    if _IPV4.match(text):
        return IP_ADDRESS
    if _SSN.match(text):
        return GOVERNMENT_ID
    if _CARD.match(text):
        return CARD_NUMBER
    if is_valid_phone(text):
        return PHONE
    return ""


def _name_class(column: str) -> str:
    tokens = re.split(r"[^a-z0-9]+", str(column).lower())
    joined = "".join(tokens)
    for data_class, keywords in _NAME_TOKENS.items():
        if joined in keywords or any(token in keywords for token in tokens if token):
            return data_class
    return ""


def detect_personal_data(frame: pd.DataFrame, *, min_confidence: float = 0.6) -> PrivacyReport:
    """Find the columns that carry personal data.

    A column is included when its name says so, or when at least
    ``min_confidence`` of its non-blank values match one data class. Name and
    values can disagree (``contact_email`` full of phone numbers); the value
    evidence wins, because that is what is actually in the file.
    """
    report = PrivacyReport()
    for column in map(str, frame.columns):
        series = frame[column]
        non_blank = int(series.map(lambda v: not _blank(v)).sum())
        described = _name_class(column)

        counts: dict[str, int] = {}
        for value in series.tolist():
            if _blank(value):
                continue
            found = _value_class(value)
            if found:
                counts[found] = counts.get(found, 0) + 1

        best_class, best_count = "", 0
        for data_class, count in counts.items():
            if count > best_count:
                best_class, best_count = data_class, count

        if non_blank and best_class and best_count / non_blank >= min_confidence:
            basis = "values" if not described or described != best_class else "mixed"
            report.columns.append(
                DetectedColumn(
                    column=column,
                    data_class=best_class,
                    basis=basis,
                    non_blank=non_blank,
                    matching=best_count,
                )
            )
        elif described:
            report.columns.append(
                DetectedColumn(
                    column=column,
                    data_class=described,
                    basis="name",
                    non_blank=non_blank,
                    matching=best_count,
                )
            )
    return report


MODES = ("drop", "hash", "redact", "partial")


def _hash_value(value: Any, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
    return digest[:32]


def _redact_value(value: Any) -> str:
    text = str(value)
    return f"[redacted:{len(text)}]"


def _partial_value(value: Any) -> str:
    """Keep a little: the last two characters, for a human to recognise.

    Enough to let a support agent confirm "yes, that is the right record"
    without exposing the value itself.
    """
    text = str(value)
    if len(text) <= 2:
        return "*" * len(text)
    return "*" * (len(text) - 2) + text[-2:]


@dataclass
class MaskPlan:
    modes: dict[str, str] = field(default_factory=dict)
    """data_class -> one of MODES."""
    columns: dict[str, str] = field(default_factory=dict)
    """column -> mode, overriding the per-class default."""

    def mode_for(self, data_class: str, column: str) -> str:
        return self.columns.get(column) or self.modes.get(data_class) or "drop"


@dataclass
class MaskResult:
    frame: pd.DataFrame
    actions: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"actions": list(self.actions), "columns": list(self.frame.columns)}


def mask_personal_data(
    frame: pd.DataFrame,
    report: PrivacyReport,
    plan: MaskPlan,
    *,
    salt: str = "dataflow",
) -> MaskResult:
    """Apply the plan, returning a new frame and an action log.

    The input frame is not modified. A drop removes the column; hash, redact and
    partial replace each non-blank value. Deleting the column is the only mode
    that guarantees the original cannot be recovered, so it is the default.
    """
    output = frame.copy()
    actions: list[dict[str, Any]] = []
    for detected in report.columns:
        column = detected.column
        if column not in output.columns:
            continue
        mode = plan.mode_for(detected.data_class, column)
        if mode not in MODES:
            raise PrivacyError(
                f"Unknown masking mode {mode!r} for {column!r}. Choose one of: {', '.join(MODES)}."
            )
        if mode == "drop":
            output = output.drop(columns=[column])
        elif mode == "hash":
            output[column] = output[column].map(
                lambda v: v if _blank(v) else _hash_value(v, salt)
            )
        elif mode == "redact":
            output[column] = output[column].map(
                lambda v: v if _blank(v) else _redact_value(v)
            )
        else:
            output[column] = output[column].map(
                lambda v: v if _blank(v) else _partial_value(v)
            )
        actions.append(
            {
                "column": column,
                "data_class": detected.data_class,
                "mode": mode,
            }
        )
    return MaskResult(frame=output, actions=actions)
