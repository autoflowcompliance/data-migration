"""PII detection over single values and whole frames.

Every detector is deterministic and offline. Structured identifiers are
validated, not merely pattern-matched: a credit card must pass Luhn, an IBAN
must pass mod-97, a US SSN must have legal area/group/serial ranges. That is
what keeps a 16-digit order id from being reported (and masked) as a card.

Detectors return the exact span they matched so masking can rewrite only the
sensitive substring and leave surrounding prose intact.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import phonenumbers

from app_files.privacy.config import PrivacyConfig
from app_files.transforms import is_missing

# --------------------------------------------------------------------- patterns

EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
)

# A digit run, optionally grouped by single spaces, dots, dashes or nothing.
_CARD_CANDIDATE_RE = re.compile(r"(?<!\d)\d(?:[ \-.]?\d){12,18}(?!\d)")
_IBAN_RE = re.compile(r"(?<![A-Z0-9])[A-Z]{2}\d{2}[A-Z0-9]{11,30}(?![A-Z0-9])")
_SSN_RE = re.compile(r"(?<!\d)(\d{3})[- ]?(\d{2})[- ]?(\d{4})(?!\d)")
# US-style passport: a letter followed by eight digits, or two letters + seven.
_PASSPORT_RE = re.compile(r"(?<![A-Za-z0-9])(?:[A-Z]\d{8}|[A-Z]{2}\d{7})(?![A-Za-z0-9])")


@dataclass
class Detection:
    """One sensitive substring found in a value."""

    kind: str
    value: str
    start: int
    end: int
    label: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "value": self.value, "start": self.start, "end": self.end}


def luhn_valid(digits: str) -> bool:
    if not digits.isdigit() or len(digits) < 12:
        return False
    total = 0
    for index, char in enumerate(reversed(digits)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def iban_valid(candidate: str) -> bool:
    """ISO 13616 mod-97 check: move the first four chars to the end, map
    letters to 10-35, and require remainder 1."""
    compact = re.sub(r"\s+", "", candidate).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", compact):
        return False
    rearranged = compact[4:] + compact[:4]
    remainder = 0
    for char in rearranged:
        if char.isdigit():
            remainder = (remainder * 10 + int(char)) % 97
        else:
            remainder = (remainder * 100 + (ord(char) - 55)) % 97
    return remainder == 1


def ssn_valid(area: str, group: str, serial: str) -> bool:
    if area in {"000", "666"} or area.startswith("9"):
        return False
    return group != "00" and serial != "0000"


#: A dialable number has at least this many digits (shortest national numbers,
#: e.g. some 7-digit local formats, plus a little slack).
_MIN_PHONE_DIGITS = 7


def _has_phone_shaped_digits(text: str) -> bool:
    """Cheap gate before the phone parser, which is the whole cost of a scan.

    ``phonenumbers`` is expensive per value and the pipeline runs this over
    every cell. A value without enough digits to be a phone number cannot
    contain one, so it never reaches the parser. The gate is deliberately
    permissive — it only rejects the impossible, never a real number.
    """
    digits = 0
    for char in text:
        if char.isdigit():
            digits += 1
            if digits >= _MIN_PHONE_DIGITS:
                return True
    return False


def detect_value(value: Any, config: PrivacyConfig) -> list[Detection]:
    """Every detection in a single value, ordered by position."""
    if is_missing(value):
        return []
    text = str(value)
    found: list[Detection] = []

    if config.detectors.get("email", False):
        for match in EMAIL_RE.finditer(text):
            found.append(Detection("email", match.group(), match.start(), match.end(), "Email"))

    if config.detectors.get("credit_card", False):
        for match in _CARD_CANDIDATE_RE.finditer(text):
            digits = re.sub(r"\D", "", match.group())
            if luhn_valid(digits) and len(set(digits)) > 1:
                found.append(
                    Detection(
                        "credit_card", match.group(), match.start(), match.end(), "Credit card"
                    )
                )

    if config.detectors.get("iban", False):
        for match in _IBAN_RE.finditer(text):
            if iban_valid(match.group()):
                found.append(Detection("iban", match.group(), match.start(), match.end(), "IBAN"))

    if config.detectors.get("national_id", False):
        for match in _SSN_RE.finditer(text):
            if ssn_valid(*match.groups()):
                found.append(
                    Detection(
                        "national_id", match.group(), match.start(), match.end(), "National ID"
                    )
                )

    if config.detectors.get("passport", False):
        for match in _PASSPORT_RE.finditer(text):
            found.append(
                Detection("passport", match.group(), match.start(), match.end(), "Passport")
            )

    if config.detectors.get("phone", False) and _has_phone_shaped_digits(text):
        for phone_match in phonenumbers.PhoneNumberMatcher(text, config.region):
            found.append(
                Detection(
                    "phone", phone_match.raw_string, phone_match.start, phone_match.end, "Phone"
                )
            )

    for pattern in config.custom_patterns:
        for match in re.finditer(pattern.pattern, text):
            found.append(
                Detection(pattern.kind, match.group(), match.start(), match.end(), pattern.label)
            )

    return _resolve_overlaps(found)


def _resolve_overlaps(found: list[Detection]) -> list[Detection]:
    """Prefer the leftmost, then longest match, and drop anything it contains.

    Without this, a phone matcher can nibble a digit run out of a card number
    and the two strategies then fight over overlapping spans.
    """
    ordered = sorted(found, key=lambda d: (d.start, -(d.end - d.start)))
    kept: list[Detection] = []
    for detection in ordered:
        if any(detection.start < k.end and k.start < detection.end for k in kept):
            continue
        kept.append(detection)
    return kept


@dataclass
class ColumnFindings:
    column: str
    detections: list[Detection] = field(default_factory=list)

    @property
    def kinds(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for detection in self.detections:
            counts[detection.kind] = counts.get(detection.kind, 0) + 1
        return counts


@dataclass
class PIIReport:
    findings: dict[str, ColumnFindings] = field(default_factory=dict)
    rows_scanned: int = 0
    columns_scanned: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(len(f.detections) for f in self.findings.values())

    @property
    def columns_with_pii(self) -> list[str]:
        return [name for name, f in self.findings.items() if f.detections]

    def kind_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings.values():
            for kind, number in finding.kinds.items():
                counts[kind] = counts.get(kind, 0) + number
        return counts

    def affected_columns(self) -> dict[str, dict[str, int]]:
        """``{column: {kind: count}}`` — the shape the QA report consumes."""
        return {name: f.kinds for name, f in self.findings.items() if f.detections}

    def detections_frame(self) -> pd.DataFrame:
        rows = []
        for column, finding in self.findings.items():
            for detection in finding.detections:
                rows.append(
                    {
                        "column": column,
                        "kind": detection.kind,
                        "value": detection.value,
                        "start": detection.start,
                        "end": detection.end,
                    }
                )
        columns = ["column", "kind", "value", "start", "end"]
        return pd.DataFrame(rows, columns=columns)


def detect_frame(
    frame: pd.DataFrame,
    config: PrivacyConfig,
    columns: list[str] | None = None,
) -> PIIReport:
    """Scan ``columns`` (or every column) and report what was found.

    Detection never mutates the frame. It is safe to run it for reporting on
    data that will not be masked.
    """
    targets = list(frame.columns) if columns is None else [c for c in columns if c in frame.columns]
    report = PIIReport(rows_scanned=len(frame), columns_scanned=list(targets))
    for column in targets:
        finding = ColumnFindings(column=column)
        for item in _column_values(frame[column]):
            finding.detections.extend(detect_value(item, config))
        report.findings[column] = finding
    return report


def _column_values(series: pd.Series) -> Iterable[Any]:
    """Values worth scanning, skipping blanks and non-string scalars that
    cannot carry the patterns (numbers are scanned as text, but blanks are not)."""
    for value in series.tolist():
        if is_missing(value):
            continue
        yield value
