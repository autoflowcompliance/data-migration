"""Data contracts: declare what "good data" means, then enforce it every run.

A contract is a YAML file naming a dataset and the expectations for its fields::

    contract: hubspot_contacts
    version: "1.0"
    fields:
      email:
        required: true
        format: email
        unique: true
      phone:
        format: e164
      createdate:
        format: iso8601
        max_age_days: 730

Enforcement reuses the existing rule engine rather than growing a second one,
so contract failures land in the same issues list, the same issues CSV and the
same QA report as every other problem. Every supported `format` is checked with
the same helper the cleaner uses, so a contract can never demand something the
tool cannot itself produce.

``check_contract(frame, path)`` returns a :class:`ContractResult` with a clear
pass/fail and per-field failures. It never mutates the frame.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from app_files.transforms import is_missing, is_valid_email, is_valid_phone, to_iso_date

CONTRACT_DIR = Path(__file__).resolve().parent.parent / "contracts"

SUPPORTED_FORMATS = ("email", "e164", "iso8601", "url", "number", "integer")

_FIELD_KEYS = {
    "required",
    "unique",
    "format",
    "min",
    "max",
    "min_length",
    "max_length",
    "max_age_days",
    "allowed",
    "message",
}


class ContractError(ValueError):
    """Raised when a contract file is malformed, so it fails loudly on load."""


@dataclass
class FieldExpectation:
    name: str
    required: bool = False
    unique: bool = False
    format: str | None = None
    min: float | None = None
    max: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    max_age_days: int | None = None
    allowed: list[Any] = field(default_factory=list)
    message: str | None = None

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any] | None) -> "FieldExpectation":
        if data is None:
            return cls(name=name)
        if not isinstance(data, dict):
            raise ContractError(f"Field {name!r} must map to a set of expectations, not {type(data).__name__}")
        unknown = set(data) - _FIELD_KEYS
        if unknown:
            raise ContractError(
                f"Field {name!r} has unknown keys: {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(_FIELD_KEYS))}"
            )
        fmt = data.get("format")
        if fmt is not None and fmt not in SUPPORTED_FORMATS:
            raise ContractError(
                f"Field {name!r} asks for format {fmt!r}, which is not supported. "
                f"Choose one of: {', '.join(SUPPORTED_FORMATS)}"
            )
        return cls(
            name=name,
            required=bool(data.get("required", False)),
            unique=bool(data.get("unique", False)),
            format=fmt,
            min=data.get("min"),
            max=data.get("max"),
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            max_age_days=data.get("max_age_days"),
            allowed=list(data.get("allowed", []) or []),
            message=data.get("message"),
        )


@dataclass
class Contract:
    contract: str
    version: str = "1.0"
    description: str = ""
    fields: list[FieldExpectation] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Contract":
        if not isinstance(data, dict):
            raise ContractError("A contract must be a mapping with a 'contract' name and a 'fields' map")
        fields_raw = data.get("fields")
        if fields_raw is None:
            raise ContractError("A contract needs a 'fields' mapping")
        if not isinstance(fields_raw, dict):
            raise ContractError("'fields' must be a mapping of column name to expectations")
        return cls(
            contract=str(data.get("contract", "unnamed")),
            version=str(data.get("version", "1.0")),
            description=str(data.get("description", "")),
            fields=[FieldExpectation.from_dict(name, body) for name, body in fields_raw.items()],
        )

    def field_names(self) -> list[str]:
        return [f.name for f in self.fields]


def load_contract(source: str | Path) -> Contract:
    """Load a contract by name (``contacts``) or by explicit path."""
    path = Path(source)
    if not path.exists():
        candidate = CONTRACT_DIR / f"{str(source).strip().lower()}.yaml"
        if candidate.exists():
            path = candidate
        else:
            raise FileNotFoundError(
                f"No contract for {source!r}. Looked at {path} and {candidate}."
            )
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return Contract.from_dict(data)


def available_contracts() -> list[str]:
    if not CONTRACT_DIR.exists():
        return []
    return sorted(p.stem for p in CONTRACT_DIR.glob("*.yaml"))


# ------------------------------------------------------------------ checking
@dataclass
class ContractFailure:
    field: str
    row: int
    check: str
    message: str

    def as_row(self) -> dict[str, Any]:
        return {"field": self.field, "row": self.row, "check": self.check, "message": self.message}


@dataclass
class ContractResult:
    contract: str
    failures: list[ContractFailure] = field(default_factory=list)
    fields_checked: int = 0
    rows_checked: int = 0

    @property
    def passed(self) -> bool:
        return not self.failures

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def by_field(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for failure in self.failures:
            counts[failure.field] = counts.get(failure.field, 0) + 1
        return counts

    def failures_frame(self) -> pd.DataFrame:
        columns = ["field", "row", "check", "message"]
        if not self.failures:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([f.as_row() for f in self.failures], columns=columns)

    def summary(self) -> dict[str, Any]:
        return {
            "contract": self.contract,
            "status": self.status,
            "fields_checked": self.fields_checked,
            "rows_checked": self.rows_checked,
            "failures": len(self.failures),
            "failures_by_field": self.by_field(),
        }


def _today() -> dt.date:
    return dt.date.today()


def check_contract(
    frame: pd.DataFrame,
    contract: str | Path | Contract,
    today: dt.date | None = None,
) -> ContractResult:
    """Enforce ``contract`` against ``frame``.

    A field absent from the frame fails only when it is ``required``; otherwise
    it is skipped, because a contract shared across several exports cannot
    assume every column is present.

    Args:
        frame: the mapped output to check.
        contract: a name, path, or already-loaded :class:`Contract`.
        today: reference date for ``max_age_days``; injectable for tests.
    """
    loaded = contract if isinstance(contract, Contract) else load_contract(contract)
    reference = today or _today()
    result = ContractResult(contract=loaded.contract, rows_checked=len(frame))

    for expectation in loaded.fields:
        name = expectation.name
        if name not in frame.columns:
            if expectation.required:
                result.failures.append(
                    ContractFailure(
                        field=name,
                        row=-1,
                        check="column_present",
                        message=expectation.message
                        or f"Contract requires column '{name}', which is missing from the output",
                    )
                )
            continue

        result.fields_checked += 1
        series = frame[name]

        if expectation.unique:
            result.failures.extend(_check_unique(series, name, expectation))

        for index, value in series.items():
            if is_missing(value):
                if expectation.required:
                    result.failures.append(
                        ContractFailure(
                            field=name,
                            row=int(index),
                            check="required",
                            message=expectation.message or f"'{name}' is required but empty",
                        )
                    )
                # Blank values skip format/range checks: emptiness is the
                # completeness check's job, and counting it twice inflates
                # every failure number in the report.
                continue

            failure = _check_value(value, name, int(index), expectation, reference)
            if failure is not None:
                result.failures.append(failure)

    return result


def _check_value(
    value: Any,
    name: str,
    index: int,
    expectation: FieldExpectation,
    reference: dt.date,
) -> ContractFailure | None:
    if expectation.format and not _matches_format(value, expectation.format, reference, expectation):
        return ContractFailure(
            field=name,
            row=index,
            check=f"format:{expectation.format}",
            message=expectation.message or _format_message(name, value, expectation),
        )

    if expectation.allowed and str(value).strip().lower() not in {
        str(item).strip().lower() for item in expectation.allowed
    }:
        return ContractFailure(
            field=name,
            row=index,
            check="allowed",
            message=expectation.message
            or f"'{value}' is not one of the allowed values for '{name}'",
        )

    number = _number_or_none(value)
    if expectation.min is not None and (number is None or number < expectation.min):
        return ContractFailure(
            field=name, row=index, check="min",
            message=expectation.message or f"'{value}' is below the minimum {expectation.min} for '{name}'",
        )
    if expectation.max is not None and (number is None or number > expectation.max):
        return ContractFailure(
            field=name, row=index, check="max",
            message=expectation.message or f"'{value}' is above the maximum {expectation.max} for '{name}'",
        )

    text = str(value).strip()
    if expectation.min_length is not None and len(text) < expectation.min_length:
        return ContractFailure(
            field=name, row=index, check="min_length",
            message=expectation.message or f"'{name}' must be at least {expectation.min_length} characters",
        )
    if expectation.max_length is not None and len(text) > expectation.max_length:
        return ContractFailure(
            field=name, row=index, check="max_length",
            message=expectation.message or f"'{name}' must be at most {expectation.max_length} characters",
        )

    return None


def _matches_format(value: Any, fmt: str, reference: dt.date, expectation: FieldExpectation) -> bool:
    if fmt == "email":
        return is_valid_email(value)
    if fmt == "e164":
        return is_valid_phone(value)
    if fmt == "url":
        text = str(value).strip().lower()
        return text.startswith(("http://", "https://")) and "." in text
    if fmt == "number":
        return _number_or_none(value) is not None
    if fmt == "integer":
        number = _number_or_none(value)
        return number is not None and float(number).is_integer()
    if fmt == "iso8601":
        iso = to_iso_date(value)
        if not iso or not str(iso).startswith(("1", "2")) or len(str(iso)) != 10:
            return False
        try:
            parsed = dt.date.fromisoformat(str(iso))
        except ValueError:
            return False
        if expectation.max_age_days is not None:
            age = (reference - parsed).days
            if age > expectation.max_age_days:
                return False
        return True
    return True


def _format_message(name: str, value: Any, expectation: FieldExpectation) -> str:
    if expectation.format == "iso8601" and expectation.max_age_days is not None:
        return (
            f"'{name}' value {value!r} is not a recent ISO 8601 date "
            f"(must be within {expectation.max_age_days} days)"
        )
    return f"'{name}' value {value!r} is not in {expectation.format} format"


def _check_unique(series: pd.Series, name: str, expectation: FieldExpectation) -> list[ContractFailure]:
    failures: list[ContractFailure] = []
    seen: dict[str, int] = {}
    for index, value in series.items():
        if is_missing(value):
            continue
        key = str(value).strip().lower()
        if key in seen:
            failures.append(
                ContractFailure(
                    field=name,
                    row=int(index),
                    check="unique",
                    message=expectation.message
                    or f"'{name}' value {value!r} duplicates row {seen[key]}",
                )
            )
        else:
            seen[key] = int(index)
    return failures


def _number_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return None if value != value else float(value)
    import re

    text = str(value).strip().replace(",", "")
    text = re.sub(r"[^0-9.\-]", "", text)
    if not text or text in {"-", ".", "-."}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def render_contract_html(result: ContractResult) -> str:
    """A small standalone contract report, safe to email."""
    rows = "".join(
        f"<tr><td>{f.field}</td><td>{f.row}</td><td>{f.check}</td><td>{f.message}</td></tr>"
        for f in result.failures
    ) or '<tr><td colspan="4" class="ok">No violations</td></tr>'
    colour = "#047857" if result.passed else "#b91c1c"
    return (
        "<html><head><meta charset='utf-8'><title>Data contract report</title>"
        "<style>body{font-family:sans-serif;padding:24px;color:#111827;}"
        "table{border-collapse:collapse;width:100%;font-size:13px;}"
        "th,td{border-bottom:1px solid #e5e7eb;padding:6px 8px;text-align:left;}"
        "th{background:#f3f4f6;}.ok{color:#047857;}</style></head><body>"
        f"<h1>Data contract: {result.contract}</h1>"
        f"<p style='color:{colour};font-weight:600;'>{result.status}</p>"
        f"<p>{result.fields_checked} field(s) checked across {result.rows_checked} row(s); "
        f"{len(result.failures)} violation(s).</p>"
        f"<table><tr><th>Field</th><th>Row</th><th>Check</th><th>Message</th></tr>{rows}</table>"
        "</body></html>"
    )