"""Address canonicalisation and currency conversion."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app_files.normalization import (
    ExchangeRate,
    RateTable,
    normalise_address,
    normalise_addresses,
    normalise_currency,
    parse_amount,
)


class TestAddressNormalisation:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("123 north maple ave., springfield, il 62704",
             "123 N Maple Avenue, Springfield, IL 62704"),
            ("456 S Oak St, Springfield, IL 62704",
             "456 S Oak Street, Springfield, IL 62704"),
            ("789 Main Street Suite 200, Chicago, IL 60601",
             "789 Main Street Ste 200, Chicago, IL 60601"),
            ("12 Elm Rd Apt 4, Peoria, IL 61602",
             "12 Elm Road Apt 4, Peoria, IL 61602"),
            ("1600 Pennsylvania Ave NW, Washington, DC 20500",
             "1600 Pennsylvania Avenue NW, Washington, DC 20500"),
            ("1 E 161st St, Bronx, NY 10451",
             "1 E 161st Street, Bronx, NY 10451"),
            ("123 N Main St, Springfield, IL 62704",
             "123 N Main Street, Springfield, IL 62704"),
            ("500 West 42nd Street, New York, NY 10036",
             "500 W 42nd Street, New York, NY 10036"),
        ],
    )
    def test_canonical_forms(self, raw, expected):
        assert normalise_address(raw) == expected

    def test_five_input_formats_converge(self):
        """The spec's criterion: five formats, one canonical output."""
        variants = [
            "123 north maple ave., springfield, il 62704",
            "123 N. Maple Ave, Springfield, IL 62704",
            "123 N Maple Avenue, Springfield, IL 62704",
            "123 n maple ave springfield il 62704",
            "123  N  Maple  Ave.,  Springfield,  IL  62704",
        ]
        outputs = {normalise_address(value) for value in variants}
        assert len(outputs) == 1
        assert outputs.pop() == "123 N Maple Avenue, Springfield, IL 62704"

    @pytest.mark.parametrize(
        "raw",
        [
            "PO Box 123, Springfield, IL 62704",
            "bogus value",
            "Main Street, Springfield, IL 62704",
            "123 Main Street",
            "",
            None,
        ],
    )
    def test_unrecognised_returns_none(self, raw):
        assert normalise_address(raw) is None

    def test_zip_plus_four_is_kept(self):
        assert normalise_address("1 Main St, Boston, MA 02108-1234") == (
            "1 Main Street, Boston, MA 02108-1234"
        )

    def test_commas_missing_still_parse(self):
        assert normalise_address("5 Oak Rd Springfield IL 62704") == (
            "5 Oak Road, Springfield, IL 62704"
        )


class TestNormaliseAddressesFrame:
    def test_only_recognised_rows_change(self):
        frame = pd.DataFrame(
            {"address": ["123 north maple ave., springfield, il 62704", "PO Box 1, X, IL 62704"]}
        )
        result = normalise_addresses(frame, "address")
        assert result.normalised == 1
        assert result.unchanged == 1
        assert result.frame.at[0, "address"] == "123 N Maple Avenue, Springfield, IL 62704"
        assert result.frame.at[1, "address"] == "PO Box 1, X, IL 62704"

    def test_input_is_not_mutated(self):
        frame = pd.DataFrame({"address": ["1 Main St, Boston, MA 02108"]})
        before = frame.copy(deep=True)
        normalise_addresses(frame, "address")
        pd.testing.assert_frame_equal(frame, before)

    def test_missing_column_raises(self):
        with pytest.raises(KeyError):
            normalise_addresses(pd.DataFrame({"a": [1]}), "address")


class TestParseAmount:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("$1,234.56", (1234.56, "USD")),
            ("€99.99", (99.99, "EUR")),
            ("£10", (10.0, "GBP")),
            ("EUR 99.99", (99.99, "EUR")),
            ("(50.00)", (-50.0, None)),
            ("-3.5", (-3.5, None)),
            ("1234", (1234.0, None)),
            (42, (42.0, None)),
            (3.5, (3.5, None)),
        ],
    )
    def test_parses(self, raw, expected):
        assert parse_amount(raw) == expected

    @pytest.mark.parametrize("raw", ["not money", "", None, "abc123def"])
    def test_unparseable_returns_none(self, raw):
        assert parse_amount(raw) is None


class TestExchangeRate:
    def test_negative_rate_rejected(self):
        with pytest.raises(ValueError, match="positive"):
            ExchangeRate("EUR", "USD", -1.0, date(2024, 1, 1))

    def test_from_dict_parses_date(self):
        rate = ExchangeRate.from_dict(
            {"base": "eur", "quote": "usd", "rate": 1.1, "as_of": "2024-06-01"}
        )
        assert rate.base == "EUR"
        assert rate.as_of == date(2024, 6, 1)

    def test_from_dict_defaults_to_today(self):
        rate = ExchangeRate.from_dict({"base": "EUR", "quote": "USD", "rate": 1.1})
        # A range rather than equality: an equal-to-today assertion is flaky
        # across midnight.
        assert (date.today() - rate.as_of).days in (0, 1)


class TestRateTable:
    def test_inverse_is_derived(self):
        table = RateTable([ExchangeRate("EUR", "USD", 1.25, date(2024, 1, 1))])
        outcome = table.convert(100.0, "USD", "EUR")
        assert outcome is not None
        converted, rate = outcome
        assert converted == 80.0
        assert rate.rate == pytest.approx(0.8)

    def test_identity_conversion(self):
        table = RateTable()
        outcome = table.convert(10.0, "USD", "USD")
        assert outcome is not None
        assert outcome[0] == 10.0

    def test_missing_rate_returns_none(self):
        assert RateTable().convert(1.0, "EUR", "JPY") is None

    def test_zero_decimal_currency_rounds_to_whole_units(self):
        table = RateTable([ExchangeRate("USD", "JPY", 150.0, date(2024, 1, 1))])
        outcome = table.convert(10.567, "USD", "JPY")
        assert outcome is not None
        assert outcome[0] == 1585.0  # no fractional yen


class TestNormaliseCurrency:
    def _table(self):
        return RateTable(
            [
                ExchangeRate("EUR", "USD", 1.10, date(2024, 6, 1)),
                ExchangeRate("GBP", "USD", 1.27, date(2024, 6, 1)),
            ]
        )

    def test_three_currencies_converge_to_one(self):
        """The spec's criterion: three currencies, one output, with a rate trail."""
        frame = pd.DataFrame({"amount": ["€100.00", "£50.00", "$25.00"]})
        result = normalise_currency(frame, "amount", "USD", self._table())
        assert list(result.frame["amount"]) == [110.0, 63.5, 25.0]
        assert result.conversions.converted == 3

    def test_conversion_records_rate_and_date(self):
        frame = pd.DataFrame({"amount": ["€100.00"]})
        result = normalise_currency(frame, "amount", "USD", self._table())
        row = result.conversions.as_frame().iloc[0]
        assert row["from"] == "EUR"
        assert row["to"] == "USD"
        assert row["rate"] == 1.10
        assert row["as_of"] == "2024-06-01"

    def test_amount_without_currency_is_left_alone_and_counted_failed(self):
        frame = pd.DataFrame({"amount": ["1234"]})
        result = normalise_currency(frame, "amount", "USD", self._table())
        assert result.frame.at[0, "amount"] == "1234"
        assert result.conversions.failed == 1

    def test_source_currency_overrides_bare_numbers(self):
        frame = pd.DataFrame({"amount": ["100", "50"]})
        result = normalise_currency(frame, "amount", "USD", self._table(), source_currency="EUR")
        assert list(result.frame["amount"]) == [110.0, 55.0]

    def test_unconvertible_currency_is_left_alone(self):
        frame = pd.DataFrame({"amount": ["¥100"]})
        result = normalise_currency(frame, "amount", "USD", self._table())
        assert result.conversions.failed == 1
        assert result.frame.at[0, "amount"] == "¥100"

    def test_garbage_row_is_not_zeroed(self):
        frame = pd.DataFrame({"amount": ["€10.00", "not money"]})
        result = normalise_currency(frame, "amount", "USD", self._table())
        assert result.frame.at[1, "amount"] == "not money"
        assert result.summary() == {"converted": 1, "failed": 1}

    def test_input_is_not_mutated(self):
        frame = pd.DataFrame({"amount": ["€100.00"]})
        before = frame.copy(deep=True)
        normalise_currency(frame, "amount", "USD", self._table())
        pd.testing.assert_frame_equal(frame, before)

    def test_missing_column_raises(self):
        with pytest.raises(KeyError):
            normalise_currency(pd.DataFrame({"a": [1]}), "amount", "USD", self._table())
