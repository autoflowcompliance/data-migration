"""Sample data generator: messy test data for any schema.

A buyer should be able to try the tool before uploading anything real. This
generates deliberately messy CSVs — missing values, mixed date formats,
malformed emails and phones, duplicate rows, inconsistent casing — from a named
profile or from a schema the caller supplies.

Randomness is seeded, so ``generate("hubspot_contacts", rows=50, seed=7)`` always
produces the same file. That makes the generator usable in tests and makes a
bug reproducible from a seed rather than "it happened once".

The mess is not uniform: each corruption is applied with its own probability, so
a generated file exercises every cleaner while still having clean rows.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable

import pandas as pd

# Columns whose values get specific, targeted corruption.
_EMAILS = ["john@email.com", "JANE.DOE@Example.COM", " emile@ex-ample.fr ", "bob.jones@umbrella.com",
           "carlos@example.com", "sue@", "@nope.com", "no-at-sign.com", "mary@site.co.uk"]
_PHONES = ["(617) 498-3000", "512.876.5432", "+33 1 42 68 53 00", "+1 (415) 987-6543",
           "415-720-0137", "12345", "555-", "+44 20 7946 0958"]
_DATES = ["12/31/24", "2024-03-04", "31-Dec-24", "2024/02/17", "03/04/2024", "Jan 5, 2024", "", "not a date"]
_FIRST = ["John", "jane", "EMILE", "Bob", "carlos", " Mary ", "A.", "Sue"]
_LAST = ["Smith", "Doe", "Martin", "Jones", "Garcia", "OBrien", "van der Berg", ""]
_COMPANIES = ["Acme Inc", "acme inc.", "Umbrella Corp", "  Globex  ", "Initech", ""]
_COUNTRIES = ["USA", "usa", "France", "FR", "United States", "UK", ""]
_STATUSES = ["lead", "Lead", "customer", "Customer", "churned", ""]


@dataclass
class Field:
    """One column in a generated file."""

    name: str
    kind: str = "text"
    """One of: text, email, phone, date, number, choice, id, first_name, last_name, company, country, status."""
    choices: list[Any] = field(default_factory=list)
    null_rate: float = 0.1
    messy_rate: float = 0.25
    min_value: float = 0
    max_value: float = 1000


@dataclass
class Profile:
    """A named schema."""

    name: str
    fields: list[Field]
    description: str = ""


PROFILES: dict[str, Profile] = {
    "hubspot_contacts": Profile(
        name="hubspot_contacts",
        description="CRM contacts with the usual mess: mixed dates, phones and casing.",
        fields=[
            Field("First Name", "first_name", null_rate=0.05),
            Field("Last Name", "last_name", null_rate=0.1),
            Field("Email Address", "email", null_rate=0.15, messy_rate=0.3),
            Field("Phone 1", "phone", null_rate=0.15, messy_rate=0.35),
            Field("Company", "company", null_rate=0.2),
            Field("Created Date", "date", null_rate=0.1, messy_rate=0.5),
            Field("Country", "country", null_rate=0.15),
            Field("Lifecycle Stage", "status", null_rate=0.2),
        ],
    ),
    "salesforce_leads": Profile(
        name="salesforce_leads",
        description="Leads with duplicate rows and inconsistent casing.",
        fields=[
            Field("FirstName", "first_name"),
            Field("LastName", "last_name", null_rate=0.05),
            Field("Email", "email", null_rate=0.1, messy_rate=0.3),
            Field("Phone", "phone", null_rate=0.2, messy_rate=0.3),
            Field("Company", "company", null_rate=0.05),
            Field("Status", "status", null_rate=0.1),
            Field("LeadSource", "choice", choices=["Web", "web", "Referral", "Cold Call", ""]),
        ],
    ),
    "bank_transactions": Profile(
        name="bank_transactions",
        description="Statement lines with accounting-style amounts.",
        fields=[
            Field("Date", "date", null_rate=0.02, messy_rate=0.4),
            Field("Description", "text", null_rate=0.02),
            Field("Amount", "number", null_rate=0.02, min_value=-2000, max_value=2000),
            Field("Reference", "id", null_rate=0.1),
        ],
    ),
    "ecommerce_products": Profile(
        name="ecommerce_products",
        description="Product catalogue with mixed SKUs and prices.",
        fields=[
            Field("SKU", "id", null_rate=0.02),
            Field("Product Name", "text", null_rate=0.02),
            Field("Price", "number", min_value=1, max_value=500),
            Field("Category", "choice", choices=["Electronics", "electronics", "Home", "Toys", ""]),
            Field("Stock", "number", min_value=0, max_value=500),
        ],
    ),
    "invoice_line_items": Profile(
        name="invoice_line_items",
        description="Invoice lines with quantities and unit prices.",
        fields=[
            Field("Invoice No", "id", null_rate=0.02),
            Field("Description", "text", null_rate=0.05),
            Field("Quantity", "number", min_value=1, max_value=20),
            Field("Unit Price", "number", min_value=1, max_value=300),
            Field("Line Total", "number", min_value=1, max_value=6000),
        ],
    ),
}


def available_profiles() -> list[str]:
    return sorted(PROFILES)


def _choose(rng: random.Random, values: list[Any]) -> Any:
    return values[rng.randrange(len(values))]


def _messy_value(rng: random.Random, field: Field) -> Any:
    """One value for a field, with the field's own mess applied."""
    if rng.random() < field.null_rate:
        return ""
    kind = field.kind
    if kind == "email":
        value = _choose(rng, _EMAILS)
        if rng.random() < field.messy_rate and " " not in value:
            value = value.upper() if rng.random() < 0.5 else f"  {value} "
        return value
    if kind == "phone":
        return _choose(rng, _PHONES)
    if kind == "date":
        if rng.random() < field.messy_rate:
            return _choose(rng, _DATES)
        return _choose(rng, _DATES[:5])
    if kind == "first_name":
        return _choose(rng, _FIRST)
    if kind == "last_name":
        return _choose(rng, _LAST)
    if kind == "company":
        return _choose(rng, _COMPANIES)
    if kind == "country":
        return _choose(rng, _COUNTRIES)
    if kind == "status":
        return _choose(rng, _STATUSES)
    if kind == "choice":
        return _choose(rng, field.choices or ["", "A", "B"])
    if kind == "id":
        return f"{rng.choice('ABCDEF')}{rng.randrange(100000, 999999)}"
    if kind == "number":
        value = round(rng.uniform(field.min_value, field.max_value), 2)
        if rng.random() < field.messy_rate:
            if rng.random() < 0.5:
                return f"${value:,.2f}"
            return f"({abs(value):.2f})" if value < 0 else f"{value:,.2f}"
        return value
    return _choose(rng, ["alpha", "Beta", "gamma ", " Delta", f"item-{rng.randrange(100)}"])


def generate(
    profile: str | Profile = "hubspot_contacts",
    rows: int = 50,
    seed: int = 42,
    duplicate_rate: float = 0.1,
    fields: list[Field] | None = None,
) -> pd.DataFrame:
    """Generate a messy frame. Deterministic for a given ``seed``."""
    if isinstance(profile, Profile):
        spec = profile
    elif profile in PROFILES:
        spec = PROFILES[profile]
    elif profile == "custom":
        spec = Profile(name="custom", fields=fields or [])
    else:
        raise ValueError(
            f"Unknown profile {profile!r}. Available: {', '.join(available_profiles())}, or 'custom'."
        )

    if not spec.fields:
        raise ValueError("A custom profile needs at least one Field.")

    rng = random.Random(seed)
    records = [
        {field_.name: _messy_value(rng, field_) for field_ in spec.fields}
        for _ in range(rows)
    ]
    frame = pd.DataFrame(records, columns=[f.name for f in spec.fields])

    # Duplicate whole rows, since duplicate removal is a headline feature and a
    # file without any would not exercise it.
    if rows and duplicate_rate > 0:
        count = max(1, int(rows * duplicate_rate))
        dupes = frame.sample(n=min(count, len(frame)), random_state=seed)
        frame = pd.concat([frame, dupes], ignore_index=True)

    return frame


def generate_csv(
    path: str,
    profile: str | Profile = "hubspot_contacts",
    rows: int = 50,
    seed: int = 42,
) -> str:
    """Write a generated frame to ``path`` and return the path."""
    frame = generate(profile, rows=rows, seed=seed)
    frame.to_csv(path, index=False)
    return str(path)


def generate_bytes(profile: str | Profile = "hubspot_contacts", rows: int = 50, seed: int = 42) -> bytes:
    """The generated CSV as bytes, for feeding straight into the pipeline."""
    return generate(profile, rows=rows, seed=seed).to_csv(index=False).encode("utf-8")


def schema_description(profile: str) -> dict[str, Any]:
    """Human-readable schema, for the UI to show before generating."""
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile {profile!r}. Available: {', '.join(available_profiles())}")
    spec = PROFILES[profile]
    return {
        "name": spec.name,
        "description": spec.description,
        "columns": [
            {"name": f.name, "kind": f.kind, "may_be_blank": f.null_rate > 0}
            for f in spec.fields
        ],
    }


def corrupt(frame: pd.DataFrame, rate: float = 0.3, seed: int = 0) -> pd.DataFrame:
    """Introduce mess into an existing frame, for before/after demonstrations."""
    rng = random.Random(seed)
    out = frame.copy()
    for column in out.columns:
        for index in out.index:
            if rng.random() >= rate:
                continue
            value = out.at[index, column]
            roll = rng.random()
            if roll < 0.33:
                out.at[index, column] = ""
            elif roll < 0.66:
                out.at[index, column] = f"  {value} "
            else:
                out.at[index, column] = str(value).upper()
    return out