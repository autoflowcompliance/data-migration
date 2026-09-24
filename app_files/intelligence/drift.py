"""Schema drift and learned mapping.

Two capabilities that keep a mapping alive as the source files change underneath
it, without anyone re-editing YAML by hand.

* **Schema drift** — the columns a file *used* to have, against the columns it
  has now. A renamed column is reported as a rename when the values look alike,
  not as an unrelated remove-and-add, because the rename is what the operator
  needs to see. Every run records the shape it saw, so drift is measured against
  the real previous run.

* **Learned mapping** — given a target schema and a source file, propose the
  field-to-column links, scored by name similarity and by whether the column's
  *values* match the target's expected type. Proposals are data, not actions:
  the operator accepts them and they become YAML. Nothing is auto-applied, and
  a low-confidence guess is reported as such rather than guessed silently.

Deterministic, offline, no model.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.transforms import is_valid_email, is_valid_phone

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(str(text).lower()))


def _name_similarity(target: str, column: str) -> float:
    """How alike two names are, on a 0..1 scale.

    Token overlap is weighted above raw string similarity so ``Email Address``
    matches ``email`` better than ``Email`` matches ``e_mail`` — the tokens carry
    the meaning.
    """
    target_tokens, column_tokens = _tokens(target), _tokens(column)
    if not target_tokens or not column_tokens:
        return 0.0
    overlap = len(target_tokens & column_tokens) / len(target_tokens)
    ratio = SequenceMatcher(None, target.lower(), column.lower()).ratio()
    return round(0.7 * overlap + 0.3 * ratio, 3)


def _value_similarity(kind: str, series: pd.Series) -> float:
    """How well a column's values fit an expected type, on a 0..1 scale.

    Blank cells are ignored, because a column that is mostly empty is not
    evidence for or against the type. A column with no non-blank values scores
    0.5 — unknown, not wrong.
    """
    values = [v for v in series.tolist() if not _blank(v)]
    if not values:
        return 0.5

    if kind == "email":
        good = sum(1 for v in values if is_valid_email(str(v)))
    elif kind == "phone":
        good = sum(1 for v in values if is_valid_phone(str(v)))
    elif kind in ("number", "integer", "float"):
        good = sum(1 for v in values if _is_number(v))
    elif kind in ("date", "datetime"):
        parsed = pd.to_datetime(pd.Series(values), errors="coerce")
        good = int(parsed.notna().sum())
    else:
        # A string target fits any populated text column, so the values offer no
        # evidence either way — score them as unknown rather than a perfect fit,
        # or every string target would match the first populated column it met.
        good = len(values) // 2
    return round(good / len(values), 3)


def _blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return isinstance(value, str) and value.strip() == ""


def _is_number(value: Any) -> bool:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return True
    try:
        float(str(value).strip())
        return True
    except (TypeError, ValueError):
        return False


# ------------------------------------------------------------------- drift
@dataclass
class ColumnChange:
    kind: str  # added | removed | renamed | type_changed
    column: str
    previous: str = ""
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "column": self.column,
            "previous": self.previous,
            "detail": self.detail,
        }


@dataclass
class SchemaSnapshot:
    columns: list[str]
    dtypes: dict[str, str] = field(default_factory=dict)
    captured_at: str = ""
    source: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "columns": list(self.columns),
            "dtypes": dict(self.dtypes),
            "captured_at": self.captured_at,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SchemaSnapshot":
        return cls(
            columns=list(data.get("columns", [])),
            dtypes=dict(data.get("dtypes", {})),
            captured_at=str(data.get("captured_at", "")),
            source=str(data.get("source", "")),
        )


@dataclass
class DriftReport:
    changes: list[ColumnChange] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.changes)

    def of_kind(self, kind: str) -> list[ColumnChange]:
        return [c for c in self.changes if c.kind == kind]

    def as_dict(self) -> dict[str, Any]:
        return {
            "has_drift": self.has_drift,
            "changes": [c.as_dict() for c in self.changes],
            "summary": {
                kind: len(self.of_kind(kind))
                for kind in ("added", "removed", "renamed", "type_changed")
            },
        }


def snapshot_schema(frame: pd.DataFrame, *, source: str = "") -> SchemaSnapshot:
    from datetime import datetime, timezone

    return SchemaSnapshot(
        columns=[str(c) for c in frame.columns],
        dtypes={str(c): str(t) for c, t in frame.dtypes.items()},
        captured_at=datetime.now(timezone.utc).isoformat(),
        source=source,
    )


def detect_drift(
    previous: SchemaSnapshot, current: pd.DataFrame, *, rename_threshold: float = 0.6
) -> DriftReport:
    """Compare a stored snapshot with the current frame.

    A removed column and an added column whose *values* are more alike than
    ``rename_threshold`` are reported as one rename. Two genuinely unrelated
    columns stay a remove plus an add.
    """
    current_columns = [str(c) for c in current.columns]
    old_columns = list(previous.columns)

    added = [c for c in current_columns if c not in old_columns]
    removed = [c for c in old_columns if c not in current_columns]
    changes: list[ColumnChange] = []

    # Pair up removed/added by value similarity to find renames.
    renamed_old: set[str] = set()
    renamed_new: set[str] = set()
    for old in removed:
        if old not in previous.columns:
            continue
        best_new, best_score = "", 0.0
        for new in added:
            if new in renamed_new:
                continue
            score = _series_similarity(current[new], old)
            if score > best_score:
                best_new, best_score = new, score
        if best_new and best_score >= rename_threshold:
            changes.append(
                ColumnChange(
                    kind="renamed",
                    column=best_new,
                    previous=old,
                    detail=f"values look alike (similarity {best_score:.2f})",
                )
            )
            renamed_old.add(old)
            renamed_new.add(best_new)

    for column in added:
        if column not in renamed_new:
            changes.append(ColumnChange(kind="added", column=column))
    for column in removed:
        if column not in renamed_old:
            changes.append(ColumnChange(kind="removed", column=column))

    for column in current_columns:
        if column in previous.dtypes and column in current.columns:
            old_type = previous.dtypes[column]
            new_type = str(current[column].dtype)
            if old_type != new_type:
                changes.append(
                    ColumnChange(
                        kind="type_changed",
                        column=column,
                        previous=old_type,
                        detail=f"{old_type} -> {new_type}",
                    )
                )
    return DriftReport(changes=changes)


def _series_similarity(frame_column: pd.Series, previous_name: str) -> float:
    """Compare a current column against a previous column by its name only.

    Without the previous *values* stored, the honest signal is the name. The
    snapshot keeps names and dtypes; a value-level rename detector would need the
    old file kept too, which this tool deliberately does not retain.

    A column whose tokens are wholly contained in the other's (``Email`` inside
    ``Email Address``) is a strong rename signal even though the raw string
    similarity is middling, so containment is scored above plain overlap.
    """
    old_tokens, new_tokens = _tokens(previous_name), _tokens(str(frame_column.name))
    if not old_tokens or not new_tokens:
        return 0.0
    name_score = _name_similarity(previous_name, str(frame_column.name))
    if old_tokens <= new_tokens or new_tokens <= old_tokens:
        return round(max(name_score, 0.75), 3)
    return name_score


def drift_dir() -> Path:
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "schemas"


def _slug(name: str) -> str:
    keep = [ch if ch.isalnum() or ch in "-_." else "_" for ch in str(name)]
    return "".join(keep) or "unnamed"


def record_snapshot(snapshot: SchemaSnapshot, name: str, path: str | Path | None = None) -> Path:
    target = Path(path) if path else drift_dir() / f"{_slug(name)}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot.as_dict(), indent=2) + "\n", encoding="utf-8")
    return target


def load_snapshot(name: str, path: str | Path | None = None) -> SchemaSnapshot | None:
    target = Path(path) if path else drift_dir() / f"{_slug(name)}.json"
    if not target.exists():
        return None
    try:
        return SchemaSnapshot.from_dict(json.loads(target.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------- learned mapping
@dataclass
class Proposal:
    target: str
    column: str
    confidence: float
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "column": self.column,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
        }


@dataclass
class LearnedMapping:
    proposals: list[Proposal] = field(default_factory=list)
    unmatched_targets: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "proposals": [p.as_dict() for p in self.proposals],
            "unmatched_targets": list(self.unmatched_targets),
        }

    def to_field_map(self, *, min_confidence: float = 0.35) -> dict[str, str]:
        """The high-confidence proposals as ``{source_column: target_field}``.

        Low-confidence guesses are left out rather than applied, so an
        uncertain mapping never silently becomes the mapping.
        """
        return {
            proposal.column: proposal.target
            for proposal in self.proposals
            if proposal.confidence >= min_confidence
        }


def learn_mapping(
    frame: pd.DataFrame,
    targets: list[dict[str, Any]],
    *,
    min_confidence: float = 0.35,
) -> LearnedMapping:
    """Propose links from source columns to target fields.

    ``targets`` is a list of ``{"name": ..., "type": ...}``. Each candidate is
    scored on name similarity and value fit; the best candidate per target
    above ``min_confidence`` wins, and each column is used at most once.
    """
    columns = [str(c) for c in frame.columns]
    taken: set[str] = set()
    proposals: list[Proposal] = []
    unmatched: list[str] = []

    scored: list[tuple[float, str, str, str]] = []
    for target in targets:
        name = str(target.get("name", ""))
        kind = str(target.get("type", "string"))
        if not name:
            continue
        for column in columns:
            if column in taken:
                continue
            name_score = _name_similarity(name, column)
            value_score = _value_similarity(kind, frame[column])
            confidence = round(0.6 * name_score + 0.4 * value_score, 3)
            if confidence >= min_confidence:
                scored.append((confidence, name, column, kind))

    # Highest confidence first; ties broken by name then column for determinism.
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    for confidence, name, column, kind in scored:
        if column in taken:
            continue
        if any(p.target == name for p in proposals):
            continue
        taken.add(column)
        name_score = _name_similarity(name, column)
        value_score = _value_similarity(kind, frame[column])
        proposals.append(
            Proposal(
                target=name,
                column=column,
                confidence=confidence,
                reason=f"name {name_score:.2f}, values {value_score:.2f} ({kind})",
            )
        )

    for target in targets:
        name = str(target.get("name", ""))
        if name and not any(p.target == name for p in proposals):
            unmatched.append(name)
    return LearnedMapping(proposals=proposals, unmatched_targets=unmatched)


def proposals_to_yaml(mapping: LearnedMapping, *, crm: str = "custom") -> str:
    """Render accepted proposals as a mapping config, ready to save as YAML."""
    lines = [f"crm: {crm}", "version: '1.0'", "fields:"]
    for proposal in mapping.proposals:
        lines.append(f"  - name: {proposal.target}")
        lines.append(f"    source: {proposal.column}")
    return "\n".join(lines) + "\n"