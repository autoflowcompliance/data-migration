"""Mapping configuration: the target CRM template and how to reach it."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"


@dataclass
class TargetField:
    name: str
    type: str = "string"
    required: bool = False
    unique: bool = False
    transform: str | None = None
    source: str | None = None
    """Explicit source column; when unset the aliases drive auto-mapping."""
    sources: list[str] = field(default_factory=list)
    """Several source columns joined with ``separator`` (e.g. full name)."""
    separator: str = " "
    aliases: list[str] = field(default_factory=list)
    default: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TargetField:
        known = set(cls.__dataclass_fields__)
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"Unknown field keys: {', '.join(sorted(unknown))}")
        return cls(**data)


@dataclass
class MappingConfig:
    crm: str
    version: str = "1.0"
    fields: list[TargetField] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MappingConfig:
        return cls(
            crm=data.get("crm", "custom"),
            version=str(data.get("version", "1.0")),
            fields=[TargetField.from_dict(item) for item in data.get("fields", [])],
        )

    def required_fields(self) -> list[str]:
        return [f.name for f in self.fields if f.required]

    def unique_fields(self) -> list[str]:
        return [f.name for f in self.fields if f.unique]


def load_mapping_config(crm_or_path: str | Path) -> MappingConfig:
    """Load a mapping config by CRM name (``hubspot``) or by explicit path."""
    path = Path(crm_or_path)
    if not path.exists():
        path = CONFIG_DIR / f"{str(crm_or_path).strip().lower()}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"No mapping config for {crm_or_path!r}. Known CRMs: {', '.join(available_crms())}"
        )
    with open(path, encoding="utf-8") as handle:
        return MappingConfig.from_dict(yaml.safe_load(handle) or {})


def available_crms() -> list[str]:
    return sorted(p.stem for p in CONFIG_DIR.glob("*.yaml"))
