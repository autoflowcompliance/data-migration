"""The ``privacy:`` block in a config must bind in a run, not just be readable.

The privacy layer had unit and pipeline tests, but no test asserted that a
config declaring ``privacy:`` actually caused masking during a run — which is
how the block came to be documented and yet never bound. These tests drive the
binding directly, and the integration module drives it through the real CLI.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.privacy.binding import (
    apply_configured_privacy,
    apply_privacy,
    declared_privacy_config,
    privacy_block,
)
from app_files.privacy.config import PrivacyConfig, PrivacyConfigError


@pytest.fixture
def pii_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "email": ["ann@example.com", "bob@example.com"],
            "phone": ["(617) 498-3000", "512.876.5432"],
            "notes": ["Call ann@example.com", "nothing here"],
        }
    )


def _write_config(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "crm.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_privacy_block_reads_the_declared_mapping(tmp_path):
    path = _write_config(
        tmp_path,
        "crm: X\nprivacy:\n  default_strategy: redact\n",
    )
    assert privacy_block(path) == {"default_strategy": "redact"}


def test_privacy_block_is_none_without_the_key(tmp_path):
    path = _write_config(tmp_path, "crm: X\nfields: []\n")
    assert privacy_block(path) is None


def test_declared_config_is_none_when_absent(tmp_path):
    path = _write_config(tmp_path, "crm: X\n")
    assert declared_privacy_config(path) is None


def test_declared_config_parses_fields_and_strategy(tmp_path):
    path = _write_config(
        tmp_path,
        "crm: X\n"
        "privacy:\n"
        "  default_strategy: redact\n"
        "  fields:\n"
        "    - column: email\n"
        "      strategy: hash\n",
    )
    config = declared_privacy_config(path)
    assert config is not None
    assert config.default_strategy == "redact"
    assert config.fields[0].column == "email"
    assert config.strategy_for("email", "email") == "hash"


def test_a_malformed_block_raises_rather_than_silently_off(tmp_path):
    """A privacy block that cannot be parsed must not be ignored: an ignored
    block means PII reaches the output while the run looks fine."""
    path = _write_config(tmp_path, "crm: X\nprivacy:\n  default_strategy: nope\n")
    with pytest.raises(PrivacyConfigError):
        declared_privacy_config(path)


def test_apply_configured_privacy_is_none_without_a_block(tmp_path, pii_frame):
    path = _write_config(tmp_path, "crm: X\n")
    assert apply_configured_privacy(pii_frame, path) is None


def test_apply_configured_privacy_respects_an_explicit_disable(tmp_path, pii_frame):
    path = _write_config(
        tmp_path, "crm: X\nprivacy:\n  enabled: false\n  fields:\n    - column: email\n"
    )
    assert apply_configured_privacy(pii_frame, path) is None


def test_apply_privacy_masks_per_column_strategy(pii_frame):
    config = PrivacyConfig.from_dict(
        {
            "privacy": {
                "default_strategy": "redact",
                "fields": [
                    {"column": "email", "strategy": "hash"},
                    {"column": "phone", "strategy": "partial"},
                ],
            }
        }
    )
    outcome = apply_privacy(pii_frame, config)
    masked = outcome.masked_frame
    # hash is deterministic: stable across runs, and not the original.
    assert masked.at[0, "email"] != "ann@example.com"
    assert len(str(masked.at[0, "email"])) == 64
    # partial keeps the last four as asterisks plus the digits.
    assert str(masked.at[0, "phone"]).endswith("3000")
    assert masked.at[0, "phone"] != "(617) 498-3000"
    # default strategy applies to the unlisted column, including in free text.
    assert "[REDACTED]" in str(masked.at[0, "notes"])


def test_apply_privacy_leaves_the_input_frame_untouched(pii_frame):
    config = PrivacyConfig.from_dict({"privacy": {"fields": [{"column": "email"}]}})
    before = pii_frame.copy(deep=True)
    apply_privacy(pii_frame, config)
    pd.testing.assert_frame_equal(pii_frame, before)


def test_apply_privacy_reports_every_detection(pii_frame):
    config = PrivacyConfig.from_dict({"privacy": {"fields": [{"column": "email"}]}})
    outcome = apply_privacy(pii_frame, config)
    assert outcome.total_detected == outcome.total_masked
    assert outcome.total_masked > 0
    assert "email" in outcome.summary()["columns"]


def test_apply_privacy_writes_a_usable_report_card(pii_frame):
    config = PrivacyConfig.from_dict({"privacy": {"fields": [{"column": "email"}]}})
    outcome = apply_privacy(pii_frame, config)
    assert outcome.report_html
    assert "privacy" in outcome.report_html.lower()


def test_masking_is_idempotent_with_hash_strategy(pii_frame):
    """Two tables masked with the same salt still join on the hash column."""
    config = PrivacyConfig.from_dict(
        {"privacy": {"hash_salt": "s", "fields": [{"column": "email", "strategy": "hash"}]}}
    )
    once = apply_privacy(pii_frame, config).masked_frame
    twice = apply_privacy(once, config).masked_frame
    pd.testing.assert_series_equal(once["email"], twice["email"])


def test_detections_are_reported_before_masking_finds_them():
    """The detection frame carries the original span, so a buyer can audit
    what was found without seeing the masked output alone."""
    frame = pd.DataFrame({"email": ["ann@example.com"]})
    config = PrivacyConfig.from_dict({"privacy": {"fields": [{"column": "email"}]}})
    detections = apply_privacy(frame, config).detections_frame()
    assert list(detections.columns) == ["column", "kind", "value", "start", "end"]
    assert detections.iloc[0]["value"] == "ann@example.com"
