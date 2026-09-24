"""Read a config's ``matching:`` block into a :class:`MatchStrategy`.

``MatchStrategy.from_dict`` existed and had no caller outside the tests, so
tuning a reconciliation meant editing Python. The strategy is data, and the
config is where a buyer's data lives, so this module is the missing link
between the two. A config with no ``matching:`` block yields ``None`` and the
caller keeps the frozen amount-and-date behaviour, so nothing changes for a
config that never asked for a strategy.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app_files.mappers.schema import CONFIG_DIR, load_mapping_config
from app_files.services.bank_reconciliation.multiway import (
    MatchStrategy,
    MatchStrategyError,
)


class MatchStrategyConfigError(ValueError):
    """The ``matching:`` block is present but not usable."""


def _config_path(crm_or_path: str | Path) -> Path:
    path = Path(crm_or_path)
    if path.exists():
        return path
    return CONFIG_DIR / f"{str(crm_or_path).strip().lower()}.yaml"


def load_match_strategy(crm_or_path: str | Path) -> MatchStrategy | None:
    """Return the config's match strategy, or ``None`` when it declares none."""
    path = _config_path(crm_or_path)
    if not path.exists():
        # Reuse the mapping loader's error so an unknown template names the
        # known CRMs rather than leaking a bare FileNotFoundError.
        load_mapping_config(crm_or_path)
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    raw = data.get("matching")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise MatchStrategyConfigError("'matching' must be a mapping")
    try:
        return MatchStrategy.from_dict(raw)
    except MatchStrategyError as exc:
        raise MatchStrategyConfigError(str(exc)) from exc


def default_match_strategy(
    amount_column: str = "amount",
    date_column: str = "date",
    date_window_days: int = 2,
) -> MatchStrategy:
    """The behaviour a config that declares no strategy gets.

    Exposed so a caller can make "no strategy configured" explicit rather than
    branching on ``None`` in two places.
    """
    return MatchStrategy.amount_and_date(amount_column, date_column, date_window_days)


def describe_match_strategy(strategy: MatchStrategy | None) -> str:
    if strategy is None:
        return "amount_and_date (frozen default)"
    components = ", ".join(
        f"{component.type}:{component.column}@{component.weight}"
        for component in strategy.components
    )
    return f"{strategy.name} (threshold {strategy.threshold}; {components})"


__all__ = [
    "MatchStrategyConfigError",
    "default_match_strategy",
    "describe_match_strategy",
    "load_match_strategy",
]
