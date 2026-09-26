"""Normalise postal addresses and currency amounts to a canonical form.

Two independent transforms, both opt-in and both recording what they changed so
the original survives in the lineage log.

Addresses are canonicalised without a paid geocoding service: US-style
addresses are split into the standard parts and reassembled in one shape, with
street-type and directional abbreviations expanded to their canonical form.
Anything that does not look like an address is returned unchanged rather than
mangled.

Currency conversion needs a rate. Rates are supplied by the caller — from a
config, an API, or a fixed table — and every converted amount records the rate
and the date it applied, so a converted figure is never a bare number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from app_files.transforms import is_missing

# ------------------------------------------------------------------ addresses

#: Street-type words and their canonical spelling.
STREET_TYPES = {
    "st": "Street", "str": "Street", "street": "Street",
    "ave": "Avenue", "av": "Avenue", "avenue": "Avenue",
    "blvd": "Boulevard", "boulevard": "Boulevard",
    "rd": "Road", "road": "Road",
    "dr": "Drive", "drive": "Drive",
    "ln": "Lane", "lane": "Lane",
    "ct": "Court", "court": "Court",
    "pl": "Place", "place": "Place",
    "sq": "Square", "square": "Square",
    "ter": "Terrace", "terrace": "Terrace",
    "pkwy": "Parkway", "parkway": "Parkway",
    "hwy": "Highway", "highway": "Highway",
    "cir": "Circle", "circle": "Circle",
    "way": "Way",
}

#: Directional words and their canonical abbreviation.
DIRECTIONS = {
    "north": "N", "n": "N",
    "south": "S", "s": "S",
    "east": "E", "e": "E",
    "west": "W", "w": "W",
    "northeast": "NE", "ne": "NE",
    "northwest": "NW", "nw": "NW",
    "southeast": "SE", "se": "SE",
    "southwest": "SW", "sw": "SW",
}

_UNIT_RE = re.compile(
    r"\b(apt|apartment|suite|ste|unit|#|floor|fl|bldg|building)\b\.?\s*([\w-]+)",
    re.IGNORECASE,
)
_US_TAIL_RE = re.compile(
    r"^(?P<city>.+?),?\s+(?P<state>[A-Za-z]{2})\s+(?P<zip>\d{5}(?:-\d{4})?)$"
)
_STREET_NUMBER_RE = re.compile(r"^(?P<number>\d+[A-Za-z]?)\s+(?P<rest>.+)$")


def _title(text: str) -> str:
    return " ".join(word[:1].upper() + word[1:].lower() for word in text.split())


def _canonical_unit(kind: str, value: str) -> str:
    kind = kind.lower()
    if kind in {"apt", "apartment", "#", "unit"}:
        return f"Apt {value}"
    if kind in {"suite", "ste"}:
        return f"Ste {value}"
    if kind in {"floor", "fl"}:
        return f"Fl {value}"
    return f"Bldg {value}"


_STATE_ZIP_TAIL_RE = re.compile(r"\s+(?P<state>[A-Za-z]{2})\s+(?P<zip>\d{5}(?:-\d{4})?)$")


def _split_comma_less(text: str) -> tuple[str, str]:
    """Split ``"5 Oak Rd Springfield IL 62704"`` into street and city tail.

    Without a comma the boundary is found by locating the last street-type word
    ("Rd"), which ends the street, and the trailing state+zip. Anything between
    them is the city. Returns ``(text, "")`` when the shape is not recognised,
    letting the caller fall back to leaving the value alone.
    """
    tail_match = _STATE_ZIP_TAIL_RE.search(text)
    if not tail_match:
        return text, ""
    prefix = text[: tail_match.start()].strip()
    tokens = prefix.split()
    boundary = None
    for position in range(len(tokens) - 1, -1, -1):
        if tokens[position].lower().strip(".") in STREET_TYPES:
            boundary = position
            break
    if boundary is None or boundary >= len(tokens) - 1:
        return text, ""
    street = " ".join(tokens[: boundary + 1])
    city = " ".join(tokens[boundary + 1 :])
    return street, f"{city} {tail_match.group('state')} {tail_match.group('zip')}"


def normalise_address(value: Any) -> str | None:
    """A US-style address in one canonical shape, or ``None`` if unrecognised.

    ``"123 north maple ave., springfield, il 62704"`` becomes
    ``"123 N Maple Avenue, Springfield, IL 62704"``. A value that lacks a
    street number, a street type, or a city/state/zip tail is returned as
    ``None`` so the caller can leave the original alone instead of guessing.
    A PO box is not a street address and is likewise left alone.
    """
    if is_missing(value):
        return None
    text = " ".join(str(value).split())
    text = text.replace(" ,", ",").replace(",.", ",").rstrip(".")
    if not text:
        return None

    # Split off the street segment before the first comma; a unit designator
    # lives inside it, not in the city tail. Without a comma, the boundary is
    # inferred from the street-type word and the trailing state+zip.
    if "," in text:
        head, _, tail_raw = text.partition(",")
        street_raw = head.strip()
        tail_raw = tail_raw.strip()
    else:
        street_raw, tail_raw = _split_comma_less(text)

    unit = ""
    unit_match = _UNIT_RE.search(street_raw)
    if unit_match:
        unit = _canonical_unit(unit_match.group(1), unit_match.group(2))
        street_raw = street_raw[: unit_match.start()].strip().rstrip(",")

    # City/State/Zip may be one comma-free run or already comma-separated.
    city = state = zipcode = ""
    tail_match = _US_TAIL_RE.match(tail_raw)
    if tail_match:
        city = tail_match.group("city")
        state = tail_match.group("state")
        zipcode = tail_match.group("zip")
    else:
        tail_parts = [part.strip() for part in tail_raw.split(",") if part.strip()]
        if len(tail_parts) >= 2:
            city = tail_parts[0]
            tail_match = _US_TAIL_RE.match(" ".join(tail_parts[1:]))
            if tail_match:
                state = tail_match.group("state")
                zipcode = tail_match.group("zip")
        elif tail_parts:
            tail_match = _US_TAIL_RE.match(tail_parts[0])
            if tail_match:
                city = tail_match.group("city")
                state = tail_match.group("state")
                zipcode = tail_match.group("zip")

    street_match = _STREET_NUMBER_RE.match(street_raw)
    if not street_match or not city or not state or not zipcode:
        return None

    number = street_match.group("number").upper()
    tokens = street_match.group("rest").split()
    if len(tokens) < 2:
        return None

    # Directional may sit either side of the street name ("N Main St" or
    # "Main St NW"); it can also follow the street type ("Pennsylvania Ave NW").
    trailing_direction = ""
    if tokens[-1].lower().strip(".") in DIRECTIONS:
        trailing_direction = DIRECTIONS[tokens[-1].lower().strip(".")]
        tokens = tokens[:-1]
    if len(tokens) < 2:
        return None
    street_type = STREET_TYPES.get(tokens[-1].lower().strip("."), "")
    if not street_type:
        return None
    name_tokens = tokens[:-1]

    leading_direction = ""
    if name_tokens and name_tokens[0].lower().strip(".") in DIRECTIONS:
        leading_direction = DIRECTIONS[name_tokens[0].lower().strip(".")]
        name_tokens = name_tokens[1:]
    if name_tokens and name_tokens[-1].lower().strip(".") in DIRECTIONS:
        trailing_direction = DIRECTIONS[name_tokens[-1].lower().strip(".")]
        name_tokens = name_tokens[:-1]

    street_name = _title(" ".join(name_tokens))
    if not street_name:
        return None

    # USPS canonical order is [number] [pre-direction] [name] [type] [post-direction].
    street = " ".join(part for part in (number, leading_direction, street_name) if part)
    street = f"{street} {street_type}"
    if trailing_direction:
        street = f"{street} {trailing_direction}"
    if unit:
        street = f"{street} {unit}"
    return f"{street}, {_title(city)}, {state.upper()} {zipcode}"


@dataclass
class AddressResult:
    frame: pd.DataFrame
    normalised: int = 0
    unchanged: int = 0

    def summary(self) -> dict[str, int]:
        return {"normalised": self.normalised, "unchanged": self.unchanged}


def normalise_addresses(
    frame: pd.DataFrame, column: str
) -> AddressResult:
    """Canonicalise one address column in place on a copy of the frame."""
    if column not in frame.columns:
        raise KeyError(f"Column {column!r} is not in the frame")
    result = frame.copy()
    normalised = 0
    unchanged = 0
    for index, value in result[column].items():
        canonical = normalise_address(value)
        if canonical is None:
            unchanged += 1
            continue
        if canonical != str(value):
            normalised += 1
        result.at[index, column] = canonical
    return AddressResult(frame=result, normalised=normalised, unchanged=unchanged)


# ------------------------------------------------------------------- currency

#: Minor units per major unit for currencies with non-100 subdivisions.
MINOR_UNITS = {
    "JPY": 0, "KRW": 0, "VND": 0, "CLP": 0, "ISK": 0,
    "BHD": 3, "KWD": 3, "OMR": 3, "TND": 3,
}

_CURRENCY_SYMBOLS = {
    "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₹": "INR", "CHF": "CHF",
}
_AMOUNT_RE = re.compile(r"^\s*(?P<sign>-|\()?\s*(?P<body>[\d,]*\.?\d+)\s*\)?\s*$")


@dataclass(frozen=True)
class ExchangeRate:
    """A rate with the date it applied, so a conversion is always attributable."""

    base: str
    quote: str
    rate: float
    as_of: date

    def __post_init__(self):
        if self.rate <= 0:
            raise ValueError(f"Exchange rate must be positive, got {self.rate}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExchangeRate:
        as_of = data.get("as_of")
        if isinstance(as_of, str):
            as_of = datetime.strptime(as_of, "%Y-%m-%d").date()
        elif as_of is None:
            as_of = date.today()
        return cls(
            base=str(data["base"]).upper(),
            quote=str(data["quote"]).upper(),
            rate=float(data["rate"]),
            as_of=as_of,
        )


class RateTable:
    """Rates between currencies, looked up directly or via a base currency."""

    def __init__(self, rates: list[ExchangeRate] | None = None):
        self._rates: dict[tuple[str, str], ExchangeRate] = {}
        for rate in rates or []:
            self.add(rate)

    def add(self, rate: ExchangeRate) -> None:
        self._rates[(rate.base, rate.quote)] = rate
        # A rate implies its inverse; deriving it keeps the table small.
        if (rate.quote, rate.base) not in self._rates:
            self._rates[(rate.quote, rate.base)] = ExchangeRate(
                base=rate.quote,
                quote=rate.base,
                rate=1.0 / rate.rate,
                as_of=rate.as_of,
            )

    def get(self, base: str, quote: str) -> ExchangeRate | None:
        base, quote = base.upper(), quote.upper()
        if base == quote:
            return ExchangeRate(base, quote, 1.0, date.today())
        return self._rates.get((base, quote))

    def convert(
        self, amount: float, base: str, quote: str
    ) -> tuple[float, ExchangeRate] | None:
        rate = self.get(base, quote)
        if rate is None:
            return None
        digits = MINOR_UNITS.get(quote.upper(), 2)
        converted = round(amount * rate.rate, digits)
        return converted, rate


def parse_amount(value: Any) -> tuple[float, str | None] | None:
    """Split ``"$1,234.56"`` into ``(1234.56, "USD")``.

    Returns ``None`` for anything that is not an amount, so a non-currency
    column left in the mapping is not silently zeroed.
    """
    if is_missing(value):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value), None
    text = str(value).strip()
    if not text:
        return None
    currency = None
    for symbol, code in _CURRENCY_SYMBOLS.items():
        if text.startswith(symbol):
            currency = code
            text = text[len(symbol) :]
            break
    else:
        code_match = re.match(r"^([A-Za-z]{3})\s*(.+)$", text)
        if code_match:
            currency = code_match.group(1).upper()
            text = code_match.group(2)
    match = _AMOUNT_RE.match(text)
    if not match:
        return None
    body = match.group("body").replace(",", "")
    try:
        amount = float(Decimal(body))
    except (InvalidOperation, ValueError):
        return None
    if match.group("sign") in {"-", "("}:
        amount = -amount
    return amount, currency


@dataclass
class CurrencyConversion:
    """What one column's conversion did, per row, with the rates used."""

    rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def converted(self) -> int:
        return sum(1 for row in self.rows if row["converted"])

    @property
    def failed(self) -> int:
        return sum(1 for row in self.rows if not row["converted"])

    def as_frame(self) -> pd.DataFrame:
        columns = ["row", "original", "amount", "from", "to", "rate", "as_of", "converted"]
        if not self.rows:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(self.rows, columns=columns)


@dataclass
class CurrencyResult:
    frame: pd.DataFrame
    conversions: CurrencyConversion = field(default_factory=CurrencyConversion)

    def summary(self) -> dict[str, Any]:
        return {
            "converted": self.conversions.converted,
            "failed": self.conversions.failed,
        }


def normalise_currency(
    frame: pd.DataFrame,
    column: str,
    target: str,
    rates: RateTable,
    source_currency: str | None = None,
) -> CurrencyResult:
    """Convert a currency column to ``target``, recording every rate used.

    ``source_currency`` overrides the per-value currency (for a column of bare
    numbers whose currency is known from context). A value with no currency and
    no override is left alone and counted as failed, rather than being assumed
    to be in the target.
    """
    if column not in frame.columns:
        raise KeyError(f"Column {column!r} is not in the frame")
    target = target.upper()
    result = frame.copy()
    conversion = CurrencyConversion()
    for index, value in frame[column].items():
        parsed = parse_amount(value)
        if parsed is None:
            conversion.rows.append(
                {
                    "row": index, "original": value, "amount": None,
                    "from": source_currency or "", "to": target,
                    "rate": None, "as_of": None, "converted": False,
                }
            )
            continue
        amount, currency = parsed
        currency = (source_currency or currency or "").upper()
        if not currency:
            conversion.rows.append(
                {
                    "row": index, "original": value, "amount": amount,
                    "from": "", "to": target, "rate": None, "as_of": None,
                    "converted": False,
                }
            )
            continue
        outcome = rates.convert(amount, currency, target)
        if outcome is None:
            conversion.rows.append(
                {
                    "row": index, "original": value, "amount": amount,
                    "from": currency, "to": target, "rate": None,
                    "as_of": None, "converted": False,
                }
            )
            continue
        converted, rate = outcome
        result.at[index, column] = converted
        conversion.rows.append(
            {
                "row": index, "original": value, "amount": converted,
                "from": currency, "to": target, "rate": rate.rate,
                "as_of": rate.as_of.isoformat(), "converted": True,
            }
        )
    return CurrencyResult(frame=result, conversions=conversion)
