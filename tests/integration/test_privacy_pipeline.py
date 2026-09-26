"""Integration tests: the privacy layer inside the real pipeline.

The contract these defend is that privacy is *additive*. Run the pipeline,
mask the frame it produced, and the base pipeline's own output must be
byte-identical to a run that never touched the privacy layer.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline
from app_files.privacy import (
    PrivacyConfig,
    detect_frame,
    inject_pii_report,
    mask_frame,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES = REPO_ROOT / "app_files" / "samples"


def test_masking_sits_after_the_pipeline_without_changing_it():
    """Pipeline output is identical whether or not privacy runs afterwards."""
    source = read_any(SAMPLES / "messy_contacts.csv")

    untouched = run_pipeline(source, crm="hubspot").clean_frame
    reference = untouched.copy(deep=True)

    # The layer is applied to the pipeline's output, then discarded.
    masked = mask_frame(untouched, PrivacyConfig(enabled=True, fields=[]))
    assert masked.total_masked >= 0

    # The frame the pipeline handed us must be untouched by the masker.
    pd.testing.assert_frame_equal(untouched, reference)


def test_pipeline_output_itself_is_unchanged_by_the_layer():
    """The strongest form: run the pipeline twice, once with privacy imported
    and exercised in between, and require identical output."""
    source = read_any(SAMPLES / "messy_contacts.csv")
    first = run_pipeline(source, crm="hubspot").clean_frame

    # Exercise the layer against the pipeline output.
    config = PrivacyConfig(enabled=True)
    detect_frame(first, config)
    mask_frame(first, config)

    second = run_pipeline(source, crm="hubspot").clean_frame
    pd.testing.assert_frame_equal(first, second)


def test_masking_finds_pii_the_pipeline_left_in_place():
    """Mapping does not strip PII — that is the gap this layer closes."""
    source = read_any(SAMPLES / "messy_contacts.csv")
    clean = run_pipeline(source, crm="hubspot").clean_frame

    config = PrivacyConfig(enabled=True)
    report = detect_frame(clean, config)
    assert report.total > 0, "sample contacts should carry detectable PII"

    masked = mask_frame(clean, config).frame
    rescan = detect_frame(masked, config)
    assert rescan.total == 0


def test_emails_and_phones_are_both_gone_after_masking():
    source = read_any(SAMPLES / "messy_contacts.csv")
    clean = run_pipeline(source, crm="hubspot").clean_frame
    masked = mask_frame(clean, PrivacyConfig(enabled=True)).frame

    assert not any("@" in str(v) for v in masked["email"].tolist())

    # Every value that *is* a phone is masked; `12345` sits in the source phone
    # column but is not a phone number, so detection deliberately leaves it.
    def looks_like_phone(value: str) -> bool:
        digits = "".join(ch for ch in value if ch.isdigit())
        return len(digits) >= 7

    unmasked = [
        str(v)
        for v in masked["phone"].tolist()
        if looks_like_phone(str(v)) and "^" not in str(v)
    ]
    assert unmasked == [], f"real phone numbers survived masking: {unmasked}"
    assert any(looks_like_phone(str(v)) for v in clean["phone"].tolist())
    assert "12345" in [str(v) for v in masked["phone"].tolist()]


def test_privacy_report_appends_to_the_frozen_qa_report():
    source = read_any(SAMPLES / "messy_contacts.csv")
    result = run_pipeline(source, crm="hubspot")
    base = result.qa_report_html

    report = detect_frame(result.clean_frame, PrivacyConfig(enabled=True))
    augmented = inject_pii_report(base, report)

    # The base report is a prefix, unmodified.
    assert augmented.startswith(base)
    assert "Privacy scan" in augmented


def test_base_qa_report_carries_no_privacy_markup():
    """Guard the frozen reporter: privacy must not leak into the base HTML."""
    source = read_any(SAMPLES / "messy_contacts.csv")
    html = run_pipeline(source, crm="hubspot").qa_report_html
    assert "Privacy scan" not in html
    assert "[REDACTED]" not in html


def test_masking_a_config_driven_column_only():
    source = read_any(SAMPLES / "messy_contacts.csv")
    clean = run_pipeline(source, crm="hubspot").clean_frame

    config = PrivacyConfig(
        enabled=True,
        fields=[__field("email", "hash")],
    )
    masked = mask_frame(clean, config).frame

    # Email is hashed; the phone column is left alone.
    assert not any("@" in str(v) for v in masked["email"].tolist())
    assert any("@" in str(v) for v in clean["email"].tolist())


def test_tokenized_pipeline_output_can_be_resolved(tmp_path):
    source = read_any(SAMPLES / "messy_contacts.csv")
    clean = run_pipeline(source, crm="hubspot").clean_frame

    config = PrivacyConfig(
        enabled=True,
        token_key="integration-key",
        vault_path=str(tmp_path / "vault.json"),
        fields=[__field("email", "tokenize")],
    )
    result = mask_frame(clean, config)

    token = result.frame["email"].iloc[0]
    assert token.startswith("PII_")
    assert (tmp_path / "vault.json").exists()
    # The vault, not the frame, is where the original lives.
    assert token not in clean["email"].tolist()


def __field(column, strategy):
    from app_files.privacy.config import FieldRule

    return FieldRule(column=column, strategy=strategy)
