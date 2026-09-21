"""Unit tests for the purchase flow's payment details and per-buyer reference."""

from __future__ import annotations

from app_files.interface.web.routes.buy import (
    PAYMENT,
    PAYMENT_DEFAULTS,
    buy_reference,
    missing_payment_details,
)


def test_no_real_banking_details_are_committed():
    """The module must ship placeholders, never account numbers.

    Reading the bank details from the environment is the whole point of this
    module: a real account number in source control is a permanent leak, since
    rewriting history does not un-publish it.
    """
    for field, value in PAYMENT.items():
        assert value in PAYMENT_DEFAULTS.values(), (
            f"{field!r} is a literal value ({value!r}); it must come from the "
            "environment or a placeholder default"
        )


def test_missing_payment_details_reports_every_unset_variable():
    from app_files.interface.web.routes.buy import _ENV_KEYS

    assert set(missing_payment_details({})) == set(_ENV_KEYS.values())


def test_missing_payment_details_is_empty_when_all_are_set():
    env = {
        "PAYMENT_BENEFICIARY_NAME": "A",
        "PAYMENT_BANK_NAME": "B",
        "PAYMENT_ACCOUNT_NUMBER": "C",
        "PAYMENT_BRANCH_CODE": "D",
        "PAYMENT_SWIFT_CODE": "E",
        "PAYMENT_CONFIRM_EMAIL": "F",
        "PAYMENT_REFERENCE": "G",
        "PAYMENT_AMOUNT_USD": "H",
    }
    assert missing_payment_details(env) == []


def test_reference_is_unique_per_buyer():
    """The regression: one static reference made payments unreconcilable.

    Every buyer was told to pay with ``DF-2026-001``, so two incoming
    transfers could not be told apart.
    """
    assert buy_reference("jane@example.com") != buy_reference("john@example.com")


def test_reference_is_stable_and_case_insensitive():
    """The same buyer must get the same code on a repeat visit.

    The code is derived from the address, so it has to survive a differently
    cased email rather than issuing a second reference for one customer.
    """
    assert buy_reference("Jane@Example.com") == buy_reference("jane@example.com")


def test_reference_has_the_documented_shape():
    reference = buy_reference("jane@example.com")
    assert reference.startswith("DF-")
    assert len(reference) == len("DF-") + 6
    assert reference[3:].isalnum() and reference[3:] == reference[3:].upper()


def test_reference_falls_back_when_no_email_is_present():
    """A missing email must not produce a bare ``DF-`` with nothing after it."""
    assert buy_reference("") == PAYMENT["reference"]
    assert buy_reference("   ") == PAYMENT["reference"]
