"""Privacy detection and masking."""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.privacy import (
    MaskPlan,
    PrivacyError,
    detect_personal_data,
    mask_personal_data,
)

CONTACTS = pd.DataFrame(
    {
        "email": ["ann@x.com", "bob@x.com"],
        "phone_number": ["5551234567", "5559876543"],
        "first_name": ["Ann", "Bob"],
        "notes": ["called", "emailed"],
    }
)


def test_email_and_phone_columns_are_detected():
    report = detect_personal_data(CONTACTS)
    classes = report.classes()
    assert "email" in classes
    assert "phone" in classes


def test_detection_works_on_values_even_when_the_name_is_opaque():
    frame = pd.DataFrame({"field_7": ["a@x.com", "b@x.com", "c@x.com"]})
    report = detect_personal_data(frame)
    assert report.classes()["email"] == ["field_7"]


def test_a_name_only_signal_is_still_detected():
    frame = pd.DataFrame({"email": ["", ""]})
    report = detect_personal_data(frame)
    assert report.classes()["email"] == ["email"]


def test_a_non_personal_column_is_left_alone():
    report = detect_personal_data(CONTACTS)
    assert "notes" not in {c.column for c in report.columns}


def test_sparse_value_matches_do_not_trigger_detection():
    frame = pd.DataFrame({"ref": ["a@x.com", "not an email", "also not", "nope", "plain"]})
    report = detect_personal_data(frame, min_confidence=0.6)
    assert "ref" not in {c.column for c in report.columns}


def test_a_government_id_column_is_classified():
    frame = pd.DataFrame({"ssn": ["123-45-6789", "987-65-4321"]})
    report = detect_personal_data(frame)
    assert report.classes()["government_id"] == ["ssn"]


def test_an_ip_column_is_classified():
    frame = pd.DataFrame({"client_ip": ["10.0.0.1", "192.168.1.2"]})
    report = detect_personal_data(frame)
    assert report.classes()["ip_address"] == ["client_ip"]


def test_report_serialises_and_renders():
    report = detect_personal_data(CONTACTS)
    assert report.as_dict()["personal_columns"] == len(report.columns)
    assert "Personal data detected" in report.render_text()


def test_no_personal_data_is_an_honest_empty_report():
    frame = pd.DataFrame({"sku": ["A1", "B2"], "qty": [1, 2]})
    report = detect_personal_data(frame)
    assert report.columns == []
    assert report.render_text() == "No personal data columns detected."


def test_confidence_is_reported_per_column():
    report = detect_personal_data(CONTACTS)
    email = next(c for c in report.columns if c.data_class == "email")
    assert email.confidence == 1.0


# ------------------------------------------------------------------ masking
def test_drop_removes_the_column_by_default():
    report = detect_personal_data(CONTACTS)
    result = mask_personal_data(CONTACTS, report, MaskPlan())
    assert "email" not in result.frame.columns
    assert "phone_number" not in result.frame.columns
    assert "first_name" not in result.frame.columns


def test_masking_does_not_mutate_the_input():
    report = detect_personal_data(CONTACTS)
    mask_personal_data(CONTACTS, report, MaskPlan())
    assert "email" in CONTACTS.columns


def test_hash_mode_is_deterministic_and_reversible_in_principle():
    report = detect_personal_data(CONTACTS)
    first = mask_personal_data(CONTACTS, report, MaskPlan(modes={"email": "hash"}))
    second = mask_personal_data(CONTACTS, report, MaskPlan(modes={"email": "hash"}))
    assert first.frame["email"].tolist() == second.frame["email"].tolist()
    assert first.frame["email"].iloc[0] != "ann@x.com"
    assert len(first.frame["email"].iloc[0]) == 32


def test_a_different_salt_changes_the_hash():
    report = detect_personal_data(CONTACTS)
    plan = MaskPlan(modes={"email": "hash"})
    a = mask_personal_data(CONTACTS, report, plan, salt="one")
    b = mask_personal_data(CONTACTS, report, plan, salt="two")
    assert a.frame["email"].iloc[0] != b.frame["email"].iloc[0]


def test_redact_mode_keeps_the_shape_only():
    report = detect_personal_data(CONTACTS)
    result = mask_personal_data(CONTACTS, report, MaskPlan(modes={"email": "redact"}))
    assert result.frame["email"].iloc[0] == "[redacted:9]"


def test_partial_mode_keeps_the_last_two_characters():
    report = detect_personal_data(CONTACTS)
    result = mask_personal_data(CONTACTS, report, MaskPlan(modes={"email": "partial"}))
    assert result.frame["email"].iloc[0].endswith("om")


def test_a_column_specific_mode_overrides_the_class_default():
    report = detect_personal_data(CONTACTS)
    plan = MaskPlan(modes={"email": "drop"}, columns={"email": "redact"})
    result = mask_personal_data(CONTACTS, report, plan)
    assert "email" in result.frame.columns
    assert result.frame["email"].iloc[0].startswith("[redacted")


def test_blank_values_are_left_blank():
    frame = pd.DataFrame({"email": ["a@x.com", ""]})
    report = detect_personal_data(frame)
    result = mask_personal_data(frame, report, MaskPlan(modes={"email": "hash"}))
    assert result.frame["email"].iloc[1] == ""


def test_an_unknown_mode_is_a_clear_error():
    report = detect_personal_data(CONTACTS)
    with pytest.raises(PrivacyError, match="Unknown masking mode"):
        mask_personal_data(CONTACTS, report, MaskPlan(modes={"email": "scramble"}))


def test_the_action_log_records_every_change():
    report = detect_personal_data(CONTACTS)
    result = mask_personal_data(CONTACTS, report, MaskPlan())
    logged = {action["column"]: action["mode"] for action in result.actions}
    assert logged["email"] == "drop"
    assert logged["phone_number"] == "drop"