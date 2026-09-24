"""Layer 13 — Privacy: PII detection and masking.

A new sibling layer, not a change to the frozen core. It calls into
``app_files.transforms`` for missing-value semantics and otherwise stands
alone: nothing in cleaners, mappers, validators, auditors or reporters is
modified, and the layer is off unless a config turns it on.

    from app_files.privacy import PrivacyConfig, detect_frame, mask_frame

    config = PrivacyConfig(enabled=True, fields=[...])
    report = detect_frame(frame, config)      # report only, never mutates
    result = mask_frame(frame, config)        # new frame, input untouched

Every detector is deterministic and offline. Structured identifiers are
validated (Luhn, IBAN mod-97, SSN ranges) rather than pattern-matched alone.
"""

from app_files.privacy.config import (
    STRATEGIES,
    CustomPattern,
    FieldRule,
    PrivacyConfig,
    PrivacyConfigError,
    load_privacy_config,
)
from app_files.privacy.detect import (
    Detection,
    PIIReport,
    detect_frame,
    detect_value,
    iban_valid,
    luhn_valid,
    ssn_valid,
)
from app_files.privacy.mask import (
    MaskResult,
    PrivacyKeyError,
    TokenVault,
    decrypt_value,
    encrypt_value,
    load_vault,
    mask_frame,
)
from app_files.privacy.report import inject_pii_report, render_pii_report

__all__ = [
    "STRATEGIES",
    "CustomPattern",
    "Detection",
    "FieldRule",
    "MaskResult",
    "PIIReport",
    "PrivacyConfig",
    "PrivacyConfigError",
    "PrivacyKeyError",
    "TokenVault",
    "decrypt_value",
    "detect_frame",
    "detect_value",
    "encrypt_value",
    "iban_valid",
    "inject_pii_report",
    "load_privacy_config",
    "load_vault",
    "luhn_valid",
    "mask_frame",
    "render_pii_report",
    "ssn_valid",
]
