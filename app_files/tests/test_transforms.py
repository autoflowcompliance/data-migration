from data_migration_tool.transforms import (
    expand_scientific_notation,
    is_valid_email,
    is_valid_phone,
    normalize_unicode,
    phone_e164,
    to_iso_date,
    trim_whitespace,
)


def test_phone_e164_handles_common_formats():
    for value in ["(555) 123-4567", "555.123.4567", "5551234567", "555-123-4567"]:
        assert phone_e164(value) == "+15551234567"


def test_phone_e164_keeps_international_numbers():
    assert phone_e164("+33 1 42 68 53 00") == "+33142685300"


def test_phone_e164_returns_original_when_unparseable():
    assert phone_e164("call me") == "call me"


def test_dates_normalize_to_iso():
    assert to_iso_date("12/31/24") == "2024-12-31"
    assert to_iso_date("2024-12-31") == "2024-12-31"
    assert to_iso_date("31-Dec-24") == "2024-12-31"
    assert to_iso_date("31/12/2024") == "2024-12-31"


def test_dates_with_day_first_parameter():
    # Test day-first parsing
    assert to_iso_date("04/03/2026", day_first=True) == "2026-03-04"  # April 3rd
    assert to_iso_date("04/03/2026", day_first=False) == "2026-04-03"  # March 4th


def test_scientific_notation_expands():
    assert expand_scientific_notation("4.05E+14") == "405000000000000"
    assert expand_scientific_notation("ABC123") == "ABC123"


def test_whitespace_and_unicode():
    assert trim_whitespace("  John   Smith ") == "John Smith"
    assert normalize_unicode("Café Müller") == "Cafe Muller"


def test_validity_helpers():
    assert is_valid_email("john@email.com")
    assert not is_valid_email("not-an-email")
    assert is_valid_phone("+14155552671")
    assert not is_valid_phone("555-000")
