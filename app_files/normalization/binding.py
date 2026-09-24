"""Bind a config's ``normalization:`` block into an attended run.

The normalisation engine (address canonicalisation, currency conversion with a
recorded rate and date) was complete and tested in isolation, but no run read a
config's ``normalization:`` block — the module had zero callers outside itself.
A buyer could write the block, run the tool, and see un-normalised addresses and
mixed currencies in the output with no warning.

This binding follows the same shape as :mod:`app_files.privacy.binding`: it
never rewrites the pipeline's own output. It normalises a copy, writes it as
``normalized_data.csv`` beside ``clean_data.csv``, and records every currency
conversion (original, rate, date) so the change is attributable. A config with
no ``normalization:`` block writes nothing extra and behaves exactly as before.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from app_files.mappers.schema import CONFIG_DIR
from app_files.normalization.engine import (
    AddressResult,
    CurrencyResult,
    ExchangeRate,
    RateTable,
    normalise_addresses,
    normalise_currency,
)


class NormalizationConfigError(ValueError):
    """A ``normalization:`` block that cannot be understood."""


def _config_path(crm: str | Path) -> Path | None:
    path = Path(crm)
    if not path.exists():
        path = CONFIG_DIR / f"{str(crm).strip().lower()}.yaml"
    return path if path.exists() else None


def normalization_block(crm: str | Path) -> dict[str, Any] | None:
    """The raw ``normalization:`` mapping a config declares, or None."""
    path = _config_path(crm)
    if path is None:
        return None
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    block = data.get("normalization") if isinstance(data, dict) else None
    return block if isinstance(block, dict) else None


def _rate_table(block: dict[str, Any], config_dir: Path) -> RateTable:
    rates: list[ExchangeRate] = []

    raw_file = block.get("rate_file")
    if raw_file:
        rate_path = Path(str(raw_file))
        if not rate_path.is_absolute():
            rate_path = config_dir / rate_path
        if not rate_path.exists():
            raise NormalizationConfigError(f"rate_file not found: {rate_path}")
        with open(rate_path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        entries = data.get("rates", data) if isinstance(data, dict) else data
        for entry in entries or []:
            rates.append(ExchangeRate.from_dict(entry))

    for entry in block.get("rates", []) or []:
        rates.append(ExchangeRate.from_dict(entry))

    return RateTable(rates)


@dataclass
class NormalizationOutcome:
    """The normalised frame plus the audit trail of what changed."""

    frame: pd.DataFrame
    address_results: dict[str, AddressResult] = field(default_factory=dict)
    currency_results: dict[str, CurrencyResult] = field(default_factory=dict)

    @property
    def addresses_normalised(self) -> int:
        return sum(result.normalised for result in self.address_results.values())

    @property
    def amounts_converted(self) -> int:
        return sum(result.conversions.converted for result in self.currency_results.values())

    @property
    def amounts_failed(self) -> int:
        return sum(result.conversions.failed for result in self.currency_results.values())

    def conversions_frame(self) -> pd.DataFrame:
        """Every attempted conversion, tagged with its column.

        The date and rate on each row are what make a converted amount
        defensible later: without them the number is just a different number.
        """
        columns = [
            "column", "row", "original", "amount", "from", "to",
            "rate", "as_of", "converted",
        ]
        frames = []
        for column, result in self.currency_results.items():
            frame = result.conversions.as_frame()
            if frame.empty:
                continue
            frame = frame.copy()
            frame.insert(0, "column", column)
            frames.append(frame)
        if not frames:
            return pd.DataFrame(columns=columns)
        return pd.concat(frames, ignore_index=True)[columns]

    def summary(self) -> dict[str, Any]:
        return {
            "addresses_normalised": self.addresses_normalised,
            "amounts_converted": self.amounts_converted,
            "amounts_failed": self.amounts_failed,
            "address_columns": list(self.address_results),
            "currency_columns": list(self.currency_results),
        }


def apply_normalization(
    frame: pd.DataFrame, block: dict[str, Any], config_dir: Path
) -> NormalizationOutcome:
    """Normalise ``frame`` per a resolved ``normalization:`` block.

    ``config_dir`` anchors a relative ``rate_file`` so the config and its rates
    travel together.
    """
    if not isinstance(block, dict):
        raise NormalizationConfigError(
            f"'normalization' must be a mapping, got {type(block).__name__}"
        )
    unknown = set(block) - {"enabled", "addresses", "currency", "rates", "rate_file"}
    if unknown:
        raise NormalizationConfigError(
            f"normalization block has unknown keys: {', '.join(sorted(unknown))}. "
            f"Allowed: enabled, addresses, currency, rates, rate_file"
        )

    outcome = NormalizationOutcome(frame=frame.copy())

    raw_addresses = block.get("addresses", []) or []
    if not isinstance(raw_addresses, list):
        raise NormalizationConfigError("'addresses' must be a list of column names")
    for entry in raw_addresses:
        column = entry.get("column") if isinstance(entry, dict) else entry
        if not column:
            raise NormalizationConfigError("Each address entry needs a 'column'")
        result = normalise_addresses(outcome.frame, str(column))
        outcome.frame = result.frame
        outcome.address_results[str(column)] = result

    currency = block.get("currency")
    if currency is not None:
        if not isinstance(currency, dict):
            raise NormalizationConfigError("'currency' must be a mapping")
        target = currency.get("target")
        if not target:
            raise NormalizationConfigError("currency needs a 'target'")
        columns = currency.get("columns")
        if columns is None:
            columns = [currency["column"]] if currency.get("column") else []
        if not isinstance(columns, list) or not columns:
            raise NormalizationConfigError("currency needs 'column' or 'columns'")
        rates = _rate_table(currency, config_dir)
        source_currency = currency.get("source_currency")
        for column in columns:
            result = normalise_currency(
                outcome.frame, str(column), str(target), rates,
                source_currency=str(source_currency) if source_currency else None,
            )
            outcome.frame = result.frame
            outcome.currency_results[str(column)] = result

    return outcome


def apply_configured_normalization(
    frame: pd.DataFrame, crm: str | Path
) -> NormalizationOutcome | None:
    """Normalise ``frame`` with ``crm``'s declared block, or None.

    None is the signal to a caller that it must write no normalisation
    artifacts and change no existing output.
    """
    block = normalization_block(crm)
    if block is None:
        return None
    if block.get("enabled") is False:
        return None
    path = _config_path(crm)
    config_dir = path.parent if path is not None else Path.cwd()
    return apply_normalization(frame, block, config_dir)


__all__ = [
    "NormalizationConfigError",
    "NormalizationOutcome",
    "apply_configured_normalization",
    "apply_normalization",
    "normalization_block",
]