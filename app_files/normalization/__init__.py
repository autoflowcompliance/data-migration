"""Address and currency normalisation.

Two independent transforms for the cleaning layer:

``normalise_address``  one canonical postal shape, or ``None`` when the value
                       is not recognisably an address
``normalise_currency`` convert to a target currency, recording the rate and the
                       date it applied on every converted row

Neither guesses. An unrecognised address is left alone; an amount with no
currency is left alone and reported as failed rather than assumed.
"""

from app_files.normalization.engine import (
    DIRECTIONS,
    MINOR_UNITS,
    STREET_TYPES,
    AddressResult,
    CurrencyConversion,
    CurrencyResult,
    ExchangeRate,
    RateTable,
    normalise_address,
    normalise_addresses,
    normalise_currency,
    parse_amount,
)

__all__ = [
    "DIRECTIONS",
    "MINOR_UNITS",
    "STREET_TYPES",
    "AddressResult",
    "CurrencyConversion",
    "CurrencyResult",
    "ExchangeRate",
    "RateTable",
    "normalise_address",
    "normalise_addresses",
    "normalise_currency",
    "parse_amount",
]
