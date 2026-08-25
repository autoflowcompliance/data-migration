import pandas as pd
import pytest

from data_migration_tool.auditors import audit_import


def test_audit_detects_mismatches_and_missing_records():
    expected = pd.DataFrame(
        {
            "email": ["a@x.com", "b@x.com", "c@x.com"],
            "firstname": ["Ann", "Bob", "Cara"],
            "phone": ["+15551234567", "+15559876543", "+14155552671"],
        }
    )
    exported = pd.DataFrame(
        {
            "email": ["a@x.com", "b@x.com", "d@x.com"],
            "firstname": ["Ann", "Robert", "Dan"],
            "phone": ["+15551234567", "+15559876543", "+13035550100"],
        }
    )
    audit = audit_import(expected, exported, key="email")
    stats = audit.stats()
    assert stats["missing_records"] == 1
    assert stats["unexpected_records"] == 1
    assert stats["mismatches_by_field"]["firstname"] == 1
    assert stats["mismatches_by_field"]["phone"] == 0
    assert audit.mismatches.iloc[0]["imported"] == "Robert"


def test_audit_requires_the_key_in_both_files():
    with pytest.raises(KeyError):
        audit_import(pd.DataFrame({"a": [1]}), pd.DataFrame({"a": [1]}), key="email")
