"""The ``normalization:`` block in a config must bind in a run.

The engine had thorough unit tests, but nothing asserted a config could turn it
on — which is how the module ended up with zero callers outside itself. These
tests drive the binding directly; the integration module drives it through the
real CLI.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from app_files.normalization.binding import (
    NormalizationConfigError,
    apply_configured_normalization,
    apply_normalization,
    normalization_block,
)


@pytest.fixture
def orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "address": [
                "123 north maple ave., springfield, il 62704",
                "456 S Oak St, Springfield, IL 62704",
            ],
            "amount": ["€1,000.00", "$250.00"],
        }
    )


def _write_config(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "crm.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_block_is_none_without_the_key(tmp_path):
    path = _write_config(tmp_path, "crm: X\nfields: []\n")
    assert normalization_block(path) is None


def test_configured_normalization_is_none_without_the_block(tmp_path, orders):
    path = _write_config(tmp_path, "crm: X\n")
    assert apply_configured_normalization(orders, path) is None


def test_an_explicit_disable_is_honoured(tmp_path, orders):
    path = _write_config(tmp_path, "crm: X\nnormalization:\n  enabled: false\n")
    assert apply_configured_normalization(orders, path) is None


def test_addresses_are_canonicalised(tmp_path, orders):
    path = _write_config(
        tmp_path, "crm: X\nnormalization:\n  addresses:\n    - column: address\n"
    )
    outcome = apply_configured_normalization(orders, path)
    assert outcome is not None
    assert outcome.addresses_normalised == 2
    assert outcome.frame.loc[0, "address"] == "123 N Maple Avenue, Springfield, IL 62704"
    assert outcome.frame.loc[1, "address"] == "456 S Oak Street, Springfield, IL 62704"


def test_the_input_frame_is_untouched(tmp_path, orders):
    path = _write_config(
        tmp_path, "crm: X\nnormalization:\n  addresses:\n    - column: address\n"
    )
    before = orders.copy(deep=True)
    apply_configured_normalization(orders, path)
    pd.testing.assert_frame_equal(orders, before)


def test_currency_converts_and_records_the_rate_and_date(tmp_path, orders):
    path = _write_config(
        tmp_path,
        "crm: X\n"
        "normalization:\n"
        "  currency:\n"
        "    target: USD\n"
        "    columns: [amount]\n"
        "    rates:\n"
        "      - {base: EUR, quote: USD, rate: 1.08, as_of: 2026-01-15}\n",
    )
    outcome = apply_configured_normalization(orders, path)
    assert outcome is not None
    assert outcome.conversions_frame().shape[0] == 2
    eur = outcome.conversions_frame().iloc[0]
    assert eur["from"] == "EUR"
    assert eur["to"] == "USD"
    assert eur["rate"] == 1.08
    assert eur["as_of"] == "2026-01-15"
    assert eur["original"] == "€1,000.00"


def test_a_bare_amount_is_reported_not_assumed(tmp_path):
    """A number with no currency must not be silently read as the target."""
    frame = pd.DataFrame({"amount": ["250.00"]})
    path = _write_config(
        tmp_path,
        "crm: X\nnormalization:\n  currency:\n    target: USD\n    columns: [amount]\n",
    )
    outcome = apply_configured_normalization(frame, path)
    assert outcome is not None
    assert outcome.amounts_converted == 0
    assert outcome.amounts_failed == 1
    assert not outcome.conversions_frame().iloc[0]["converted"]


def test_source_currency_override_converts_bare_amounts(tmp_path):
    frame = pd.DataFrame({"amount": ["100"]})
    path = _write_config(
        tmp_path,
        "crm: X\n"
        "normalization:\n"
        "  currency:\n"
        "    target: USD\n"
        "    columns: [amount]\n"
        "    source_currency: EUR\n"
        "    rates:\n"
        "      - {base: EUR, quote: USD, rate: 1.10, as_of: 2026-02-01}\n",
    )
    outcome = apply_configured_normalization(frame, path)
    assert outcome is not None
    assert outcome.amounts_converted == 1
    assert outcome.frame.loc[0, "amount"] == 110.0


def test_rate_file_is_resolved_relative_to_the_config(tmp_path, orders):
    (tmp_path / "rates.yaml").write_text(
        "rates:\n  - {base: EUR, quote: USD, rate: 1.08, as_of: 2026-01-15}\n",
        encoding="utf-8",
    )
    # Config lives in a subdirectory; the rate file is beside it.
    sub = tmp_path / "cfg"
    sub.mkdir()
    path = sub / "crm.yaml"
    path.write_text(
        "crm: X\n"
        "normalization:\n"
        "  currency:\n"
        "    target: USD\n"
        "    columns: [amount]\n"
        "    rate_file: ../rates.yaml\n",
        encoding="utf-8",
    )
    outcome = apply_configured_normalization(orders, path)
    assert outcome is not None
    # The EUR row converts; the USD row is an identity conversion, not a failure.
    assert outcome.amounts_converted == 2
    assert outcome.amounts_failed == 0


def test_a_missing_rate_file_raises(tmp_path, orders):
    path = _write_config(
        tmp_path,
        "crm: X\nnormalization:\n  currency:\n    target: USD\n"
        "    columns: [amount]\n    rate_file: nope.yaml\n",
    )
    with pytest.raises(NormalizationConfigError):
        apply_configured_normalization(orders, path)


def test_unknown_keys_raise(tmp_path, orders):
    path = _write_config(tmp_path, "crm: X\nnormalization:\n  addresses: []\n  nope: 1\n")
    with pytest.raises(NormalizationConfigError):
        apply_configured_normalization(orders, path)


def test_address_and_currency_together(tmp_path, orders):
    path = _write_config(
        tmp_path,
        "crm: X\n"
        "normalization:\n"
        "  addresses:\n"
        "    - column: address\n"
        "  currency:\n"
        "    target: USD\n"
        "    columns: [amount]\n"
        "    rates:\n"
        "      - {base: EUR, quote: USD, rate: 1.08, as_of: 2026-01-15}\n",
    )
    outcome = apply_configured_normalization(orders, path)
    assert outcome is not None
    assert outcome.addresses_normalised == 2
    assert outcome.amounts_converted == 2
    assert outcome.summary()["currency_columns"] == ["amount"]


def test_a_direct_apply_takes_the_block_not_a_file(orders):
    outcome = apply_normalization(
        orders,
        {"addresses": [{"column": "address"}]},
        Path.cwd(),
    )
    assert outcome.addresses_normalised == 2


def test_conversions_frame_is_empty_without_currency(orders):
    outcome = apply_normalization(orders, {"addresses": [{"column": "address"}]}, Path.cwd())
    assert outcome.conversions_frame().empty
    assert next(iter(outcome.conversions_frame().columns)) == "column"


def test_exchange_rate_rejects_a_non_positive_rate(tmp_path):
    from app_files.normalization import ExchangeRate

    with pytest.raises(ValueError):
        ExchangeRate(base="EUR", quote="USD", rate=0, as_of=date(2026, 1, 1))
