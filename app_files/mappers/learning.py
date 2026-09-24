"""Learned mapping and schema drift detection.

Two independent facilities that both key off the shape of a source file.

**Learned mapping.** A mapping that worked once should not have to be redone
when the same file arrives again. A successful mapping is stored against a
fingerprint of the source's column names, and the next file with the same shape
is pre-filled from it with a confidence per field.

**Schema drift.** A new column, a removed column or a column whose values
changed type reaches the pipeline silently otherwise. Comparing the incoming
schema against the last one seen for that source reports the change before the
run proceeds.

State lives under ``AUTOFLOW_HOME`` so a deployment can point it at a writable
volume.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.mappers.schema import MappingConfig
from app_files.mappers.yaml_mapper import MappingResult, _best_source
from app_files.transforms import is_missing

# ------------------------------------------------------------------ storage


def state_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "mapping"


def _slug(text: str) -> str:
    keep = [ch if ch.isalnum() or ch in "-_." else "_" for ch in str(text)]
    return "".join(keep) or "unnamed"


# ------------------------------------------------------------- fingerprints


def normalise_column(name: Any) -> str:
    """A column name reduced to the form that identifies it across exports.

    "Email Address", "email_address" and "EmailAddress" are the same column
    from a mapping standpoint, so they collapse to "emailaddress".
    """
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def source_fingerprint(columns: Iterable[Any]) -> str:
    """A stable id for a set of column names, order-independent."""
    keys = sorted(normalise_column(column) for column in columns)
    digest = hashlib.sha256("|".join(keys).encode("utf-8")).hexdigest()
    return digest[:16]


# --------------------------------------------------------- learned mappings


@dataclass
class LearnedMapping:
    """A mapping that succeeded for a source shape, keyed by fingerprint."""

    fingerprint: str
    crm: str
    source_columns: list[str]
    pairs: dict[str, str] = field(default_factory=dict)
    times_seen: int = 1
    recorded_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "crm": self.crm,
            "source_columns": self.source_columns,
            "pairs": self.pairs,
            "times_seen": self.times_seen,
            "recorded_at": self.recorded_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LearnedMapping:
        return cls(
            fingerprint=str(data["fingerprint"]),
            crm=str(data.get("crm", "custom")),
            source_columns=[str(c) for c in data.get("source_columns", [])],
            pairs={str(k): str(v) for k, v in data.get("pairs", {}).items()},
            times_seen=int(data.get("times_seen", 1)),
            recorded_at=str(data.get("recorded_at", "")),
        )


@dataclass
class SuggestedField:
    """One pre-filled field plus how much to trust it."""

    target_field: str
    source_column: str | None
    confidence: float
    learned: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_field": self.target_field,
            "source_column": self.source_column,
            "confidence": round(self.confidence, 3),
            "learned": self.learned,
        }


@dataclass
class MappingSuggestion:
    fingerprint: str
    crm: str
    fields: list[SuggestedField]

    @property
    def is_learned(self) -> bool:
        return any(field.learned for field in self.fields)

    @property
    def mean_confidence(self) -> float:
        if not self.fields:
            return 0.0
        return round(sum(f.confidence for f in self.fields) / len(self.fields), 3)

    def summary(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "crm": self.crm,
            "learned": self.is_learned,
            "mean_confidence": self.mean_confidence,
            "fields": [field.as_dict() for field in self.fields],
        }


class MappingMemory:
    """A JSON store of learned mappings, keyed by source fingerprint."""

    def __init__(self, path: Path | None = None):
        self.path = path or state_dir() / "learned_mappings.json"

    def _read_all(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # A corrupt store must not break a run; it is a cache, not a record.
            return {}

    def _write_all(self, data: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save(
        self, frame: pd.DataFrame, result: MappingResult, crm: str | None = None
    ) -> LearnedMapping:
        """Store the mapping a run produced, keyed by the frame's shape."""
        fingerprint = source_fingerprint(frame.columns)
        pairs = {
            str(row["target_field"]): str(row["source_column"])
            for row in result.mapping_log().to_dict("records")
            if row.get("target_field") and row.get("source_column")
        }
        all_data = self._read_all()
        previous = all_data.get(fingerprint)
        times_seen = int(previous.get("times_seen", 0)) + 1 if previous else 1
        learned = LearnedMapping(
            fingerprint=fingerprint,
            crm=crm or (result.config.crm if result.config else "custom"),
            source_columns=[str(c) for c in frame.columns],
            pairs=pairs,
            times_seen=times_seen,
            recorded_at=datetime.now(timezone.utc).isoformat(),
        )
        all_data[fingerprint] = learned.as_dict()
        self._write_all(all_data)
        return learned

    def load(self, fingerprint: str) -> LearnedMapping | None:
        data = self._read_all().get(fingerprint)
        return LearnedMapping.from_dict(data) if data else None

    def for_frame(self, frame: pd.DataFrame) -> LearnedMapping | None:
        return self.load(source_fingerprint(frame.columns))

    def all(self) -> list[LearnedMapping]:
        return [LearnedMapping.from_dict(data) for data in self._read_all().values()]

    def clear(self) -> int:
        count = len(self._read_all())
        if self.path.exists():
            self.path.unlink()
        return count


def suggest_mapping(
    frame: pd.DataFrame, config: MappingConfig, memory: MappingMemory
) -> MappingSuggestion:
    """Pre-fill a mapping for ``frame`` against ``config``.

    A field stored for this source shape keeps its learned column at full
    confidence when that column is still present. Otherwise the existing alias
    matcher runs, and its score becomes the confidence — so a repeat file maps
    with no intervention and a drifted one still gets a ranked guess.
    """
    learned = memory.for_frame(frame)
    columns = [str(column) for column in frame.columns]
    present = {normalise_column(column) for column in columns}
    fields: list[SuggestedField] = []
    for target in config.fields:
        stored = learned.pairs.get(target.name) if learned else None
        if stored and normalise_column(stored) in present:
            fields.append(
                SuggestedField(target.name, stored, 1.0, learned=True)
            )
            continue
        source, score = _best_source(target, columns)
        fields.append(SuggestedField(target.name, source, float(score), learned=False))
    return MappingSuggestion(
        fingerprint=source_fingerprint(frame.columns),
        crm=config.crm,
        fields=fields,
    )


# ----------------------------------------------------------- schema drift

#: Coarse column types, ordered so a widening can be recognised.
TYPE_ORDER = ["empty", "boolean", "integer", "number", "date", "string"]


def infer_column_type(series: pd.Series) -> str:
    """A coarse type from the values actually present, blanks ignored.

    Deliberately conservative: a column is only ``integer`` if every non-blank
    value is an integer. One stray "n/a" makes it a string, which is the
    honest answer and avoids an all-string column being called numeric.
    """
    values = [value for value in series if not is_missing(value)]
    if not values:
        return "empty"
    integer = number = boolean = True
    for value in values:
        if isinstance(value, bool):
            # A bool is the only thing that keeps ``boolean`` true.
            integer = number = False
            continue
        boolean = False
        if isinstance(value, int):
            continue
        if isinstance(value, float):
            if not float(value).is_integer():
                integer = False
            continue
        text = str(value).strip()
        # A leading "+" followed by a longer run of digits is a phone number,
        # not a quantity. "+3" is a signed number; "+14155552671" is not.
        if text.startswith("+") and re.fullmatch(r"\+\d{7,}", text.replace(" ", "")):
            integer = number = False
            continue
        try:
            parsed = float(text.replace(",", ""))
        except (TypeError, ValueError):
            integer = number = False
            continue
        if not parsed.is_integer():
            integer = False
    if boolean:
        return "boolean"
    if number and integer:
        return "integer"
    if number:
        return "number"
    if all(_looks_like_date(value) for value in values):
        return "date"
    return "string"


def _looks_like_date(value: Any) -> bool:
    if isinstance(value, (datetime, pd.Timestamp)):
        return True
    text = str(value).strip()
    if len(text) < 6:
        return False
    return bool(
        re.match(r"^\d{4}-\d{2}-\d{2}", text)
        or re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", text)
    )


def schema_of(frame: pd.DataFrame) -> dict[str, str]:
    return {str(column): infer_column_type(frame[column]) for column in frame.columns}


@dataclass(frozen=True)
class ColumnChange:
    column: str
    kind: str
    before_type: str | None = None
    after_type: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "kind": self.kind,
            "before_type": self.before_type,
            "after_type": self.after_type,
        }


@dataclass
class SchemaDrift:
    changes: list[ColumnChange] = field(default_factory=list)

    @property
    def added(self) -> list[str]:
        return [change.column for change in self.changes if change.kind == "added"]

    @property
    def removed(self) -> list[str]:
        return [change.column for change in self.changes if change.kind == "removed"]

    @property
    def retyped(self) -> list[str]:
        return [change.column for change in self.changes if change.kind == "retyped"]

    @property
    def has_drift(self) -> bool:
        return bool(self.changes)

    def summary(self) -> dict[str, Any]:
        return {
            "has_drift": self.has_drift,
            "added": self.added,
            "removed": self.removed,
            "retyped": self.retyped,
            "changes": [change.as_dict() for change in self.changes],
        }

    def render_html(self) -> str:
        if not self.has_drift:
            return "<div class='schema-drift'><p>No schema change.</p></div>"
        dash = "\u2014"
        rows = "".join(
            f"<tr><td>{change.column}</td><td>{change.kind}</td>"
            f"<td>{change.before_type or dash}</td>"
            f"<td>{change.after_type or dash}</td></tr>"
            for change in self.changes
        )
        return (
            "<div class='schema-drift alert'>"
            f"<p>Schema changed: {len(self.added)} added, {len(self.removed)} removed, "
            f"{len(self.retyped)} retyped.</p>"
            "<table><thead><tr><th>Column</th><th>Change</th><th>Before</th>"
            f"<th>After</th></tr></thead><tbody>{rows}</tbody></table></div>"
        )


def detect_drift(known: dict[str, str], current: dict[str, str]) -> SchemaDrift:
    """Compare a known schema against a current one, by normalised name.

    Names are matched on their normalised form so a rename from
    ``email_address`` to ``Email Address`` is not reported as a removal plus an
    addition.
    """
    known_by_key = {normalise_column(name): (name, kind) for name, kind in known.items()}
    current_by_key = {normalise_column(name): (name, kind) for name, kind in current.items()}
    changes: list[ColumnChange] = []
    for key, (name, kind) in current_by_key.items():
        if key not in known_by_key:
            changes.append(ColumnChange(name, "added", None, kind))
            continue
        before_kind = known_by_key[key][1]
        if before_kind != kind and not _compatible(before_kind, kind):
            changes.append(ColumnChange(name, "retyped", before_kind, kind))
    for key, (name, kind) in known_by_key.items():
        if key not in current_by_key:
            changes.append(ColumnChange(name, "removed", kind, None))
    changes.sort(key=lambda change: (change.kind, change.column))
    return SchemaDrift(changes=changes)


def _compatible(before: str, after: str) -> bool:
    """Integer to number is a widening, not a drift worth flagging."""
    if before == "empty" or after == "empty":
        return True
    return {before, after} == {"integer", "number"}


class SchemaRegistry:
    """Remembers the last schema seen per source."""

    def __init__(self, path: Path | None = None):
        self.path = path or state_dir() / "schemas.json"

    def _read_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def remember(self, source: str, frame: pd.DataFrame) -> None:
        all_data = self._read_all()
        all_data[source] = {
            "schema": schema_of(frame),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(all_data, indent=2), encoding="utf-8")

    def known(self, source: str) -> dict[str, str] | None:
        entry = self._read_all().get(source)
        if not entry:
            return None
        return {str(k): str(v) for k, v in entry.get("schema", {}).items()}

    def check(self, source: str, frame: pd.DataFrame) -> SchemaDrift:
        """Drift for ``frame`` against the remembered schema for ``source``.

        An unknown source has nothing to compare against and reports no drift.
        """
        known = self.known(source)
        if known is None:
            return SchemaDrift()
        return detect_drift(known, schema_of(frame))

    def clear(self, source: str | None = None) -> int:
        all_data = self._read_all()
        if source is None:
            count = len(all_data)
            if self.path.exists():
                self.path.unlink()
            return count
        if source in all_data:
            del all_data[source]
            self.path.write_text(json.dumps(all_data, indent=2), encoding="utf-8")
            return 1
        return 0
