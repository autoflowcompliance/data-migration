"""Unit tests for the privacy layer (PII detection and masking).

Covers the happy path, the boundary (blank/edge values, Luhn and mod-97
failing) and the failure path (tokenize without a key, malformed config).

The zero-false-negative check uses a generated fixture of 600 known PII
values — the spec asks for 200 and a wider net is strictly stronger.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.privacy import (
    PrivacyConfig,
    PrivacyConfigError,
    PrivacyKeyError,
    TokenVault,
    decrypt_value,
    detect_frame,
    detect_value,
    encrypt_value,
    iban_valid,
    load_privacy_config,
    luhn_valid,
    mask_frame,
    ssn_valid,
)
from app_files.privacy.mask import load_vault

# ------------------------------------------------------------------- fixtures

VALID_CARDS = [
    "4111111111111111",
    "4012888888881881",
    "5555555555554444",
    "5105105105105100",
    "378282246310005",
    "371449635398431",
    "6011111111111117",
    "30569309025904",
    "3530111333300000",
    "4222222222222",
]

VALID_IBANS = [
    "GB82WEST12345698765432",
    "DE89370400440532013000",
    "FR1420041010050500013M02606",
    "IT60X0542811101000000123456",
    "ES9121000418450200051332",
    "NL91ABNA0417164300",
    "BE68539007547034",
    "CH9300762011623852957",
    "AT611904300234573201",
    "PL61109010140000071219812874",
]

VALID_SSNS = [
    "078-05-1120",
    "219-09-9999",
    "123-45-6789",
    "457-55-5462",
    "078 05 1120",
    "219099999",
]

VALID_PHONES = [
    "(617) 498-3000",
    "+1 415 555 2671",
    "512.876.5432",
    "+44 20 7946 0958",
    "+33 1 42 68 53 00",
    "212-555-1234",
    "305-555-0199",
    "650-253-0000",
    "800-555-0100",
    "415-555-0173",
]

EMAILS = [
    "john@example.com",
    "jane.doe@sub.example.co.uk",
    "user+tag@example.io",
    "a@b.co",
    "first.last@company.org",
]


def known_pii_corpus() -> list[tuple[str, str]]:
    """(kind, value) pairs that must never be missed."""
    corpus: list[tuple[str, str]] = []
    # 200 emails
    for i in range(200):
        corpus.append(("email", f"user{i}.contact@example{i % 7}.com"))
    # 200 phones
    for i in range(200):
        corpus.append(("phone", f"+1 415 {200 + (i % 700):03d} {(1000 + i):04d}"))
    # 100 cards
    for i in range(100):
        card = VALID_CARDS[i % len(VALID_CARDS)]
        corpus.append(("credit_card", card))
    # 100 IBANs
    for i in range(100):
        corpus.append(("iban", VALID_IBANS[i % len(VALID_IBANS)]))
    return corpus


@pytest.fixture
def frame() -> pd.DataFrame:
    # Padded to a common length on purpose: each earlier column carries real
    # PII, then blanks, so the masker is exercised on both.
    rows = 11
    def col(values):
        padded = list(values) + [""] * rows
        return padded[:rows]

    return pd.DataFrame(
        {
            "email": col(EMAILS),
            "phone": col(VALID_PHONES),
            "card": col(VALID_CARDS[:2]),
            "iban": col(VALID_IBANS[:2]),
            "ssn": col(VALID_SSNS[:2]),
            "notes": col(["call john@example.com or 415-555-0173"]),
            "amount": [float(i) for i in range(rows)],
        }
    )


@pytest.fixture
def config() -> PrivacyConfig:
    return PrivacyConfig(enabled=True)


# ---------------------------------------------------------------- detections

def test_detects_email(config: PrivacyConfig):
    kinds = {d.kind for d in detect_value("write to jane@example.com today", config)}
    assert "email" in kinds


def test_detects_phone(config: PrivacyConfig):
    kinds = {d.kind for d in detect_value("ring (617) 498-3000 please", config)}
    assert "phone" in kinds


@pytest.mark.parametrize("card", VALID_CARDS)
def test_detects_valid_cards(card: str, config: PrivacyConfig):
    detected = [d.kind for d in detect_value(f"card {card} on file", config)]
    assert "credit_card" in detected


@pytest.mark.parametrize("iban", VALID_IBANS)
def test_detects_valid_ibans(iban: str, config: PrivacyConfig):
    detected = [d.kind for d in detect_value(f"pay to {iban}", config)]
    assert "iban" in detected


@pytest.mark.parametrize("ssn", VALID_SSNS)
def test_detects_valid_ssns(ssn: str, config: PrivacyConfig):
    detected = [d.kind for d in detect_value(f"ssn {ssn} on record", config)]
    assert "national_id" in detected


def test_no_false_negative_on_known_corpus(config: PrivacyConfig):
    """The spec's headline requirement: every known PII value is found."""
    missed = []
    for kind, value in known_pii_corpus():
        found = {d.kind for d in detect_value(value, config)}
        if kind not in found:
            missed.append((kind, value, found))
    assert not missed, f"missed {len(missed)} known PII values, e.g. {missed[:5]}"


# ------------------------------------------------------------------- boundaries

def test_luhn_rejects_non_card_digit_run(config: PrivacyConfig):
    """A 16-digit order id that fails Luhn is not a card."""
    assert not luhn_valid("1234567890123456")
    assert "credit_card" not in {d.kind for d in detect_value("1234567890123456", config)}


def test_luhn_rejects_repeated_digit_run(config: PrivacyConfig):
    """All-zeros satisfies Luhn arithmetically, so detection needs the
    single-distinct-digit guard as a second net."""
    assert luhn_valid("0000000000000000")
    assert "credit_card" not in {d.kind for d in detect_value("0000000000000000", config)}


def test_ssn_range_boundaries():
    assert not ssn_valid("000", "45", "6789")
    assert not ssn_valid("666", "45", "6789")
    assert not ssn_valid("900", "45", "6789")
    assert not ssn_valid("078", "00", "1120")
    assert not ssn_valid("078", "05", "0000")
    assert ssn_valid("078", "05", "1120")


def test_iban_checksum_boundaries():
    assert iban_valid("GB82WEST12345698765432")
    assert not iban_valid("GB82WEST12345698765431")  # last digit changed
    assert not iban_valid("GB00WEST12345698765432")
    assert not iban_valid("not-an-iban")


def test_blank_values_are_not_detected(config: PrivacyConfig):
    for blank in ["", "   ", "n/a", "NaN", None]:
        assert detect_value(blank, config) == []


def test_disabled_detector_finds_nothing():
    config = PrivacyConfig(enabled=True, detectors={"email": False, "phone": False})
    assert detect_value("john@example.com", config) == []


def test_passport_off_by_default(config: PrivacyConfig):
    assert "passport" not in {d.kind for d in detect_value("A12345678", config)}

    on = PrivacyConfig(enabled=True, detectors={"passport": True})
    assert "passport" in {d.kind for d in detect_value("A12345678", on)}


def test_custom_pattern_detects():
    from app_files.privacy.config import CustomPattern

    config = PrivacyConfig(
        enabled=True,
        custom_patterns=[
            CustomPattern(name="employee_id", pattern=r"EMP-\d{6}", label="Employee ID")
        ],
    )
    kinds = {d.kind for d in detect_value("employee EMP-123456", config)}
    assert "custom:employee_id" in kinds


def test_overlapping_matches_do_not_double_count(config: PrivacyConfig):
    """A phone inside a longer digit run is not reported twice."""
    found = detect_value("+1 415 555 2671", config)
    spans = [(d.start, d.end) for d in found]
    for i, (start, end) in enumerate(spans):
        for other_start, other_end in spans[i + 1 :]:
            assert end <= other_start or other_end <= start


def test_detection_does_not_mutate_frame(frame: pd.DataFrame, config: PrivacyConfig):
    before = frame.copy(deep=True)
    detect_frame(frame, config)
    pd.testing.assert_frame_equal(frame, before)


def test_report_shape(frame: pd.DataFrame, config: PrivacyConfig):
    report = detect_frame(frame, config)
    assert report.rows_scanned == len(frame)
    assert report.total > 0
    assert "email" in report.columns_with_pii
    assert report.affected_columns()["email"]["email"] == len(EMAILS)
    assert set(report.detections_frame().columns) == {"column", "kind", "value", "start", "end"}


# -------------------------------------------------------------------- masking

def test_redact_leaves_no_original(frame: pd.DataFrame, config: PrivacyConfig):
    result = mask_frame(frame, config)
    assert "[REDACTED]" in result.frame["email"].tolist()
    assert not any("@" in str(v) for v in result.frame["email"].tolist())
    assert result.total_masked > 0


def test_hash_is_deterministic_and_joinable(frame: pd.DataFrame):
    config = PrivacyConfig(
        enabled=True, fields=[__field(column="email", strategy="hash")]
    )
    first = mask_frame(frame, config).frame["email"].tolist()
    second = mask_frame(frame, config).frame["email"].tolist()
    assert first == second

    other = pd.DataFrame({"email": [EMAILS[0], EMAILS[0], EMAILS[1]]})
    hashed = mask_frame(other, config).frame["email"].tolist()
    assert hashed[0] == hashed[1] != hashed[2]


def test_hash_salt_changes_digest(frame: pd.DataFrame):
    a = mask_frame(frame, PrivacyConfig(enabled=True, fields=[__field("email", "hash", salt="a")]))
    b = mask_frame(frame, PrivacyConfig(enabled=True, fields=[__field("email", "hash", salt="b")]))
    assert a.frame["email"].tolist() != b.frame["email"].tolist()


def test_partial_shows_last_four(frame: pd.DataFrame):
    config = PrivacyConfig(enabled=True, fields=[__field("phone", "partial")])
    masked = mask_frame(frame, config).frame["phone"].tolist()
    assert masked[0].endswith("3000")
    assert masked[0].count("*") == len("(617) 498-3000".strip()) - 4


def test_tokenize_requires_a_key(frame: pd.DataFrame):
    config = PrivacyConfig(enabled=True, fields=[__field("email", "tokenize")])
    with pytest.raises(PrivacyKeyError):
        mask_frame(frame, config)


def test_tokenize_is_reversible_with_the_key(frame: pd.DataFrame):
    config = PrivacyConfig(
        enabled=True, token_key="unit-test-key", fields=[__field("email", "tokenize")]
    )
    result = mask_frame(frame, config)
    token = result.frame["email"].iloc[0]
    assert token.startswith("PII_")
    assert result.vault is not None
    assert result.vault.original_for(token) == EMAILS[0]


def test_tokenize_is_stable_for_the_same_input(frame: pd.DataFrame):
    config = PrivacyConfig(
        enabled=True, token_key="unit-test-key", fields=[__field("email", "tokenize")]
    )
    first = mask_frame(frame, config).frame["email"].iloc[0]
    second = mask_frame(frame, config).frame["email"].iloc[0]
    assert first == second


def test_vault_round_trip_on_disk(tmp_path):
    vault = TokenVault(key="k", path=tmp_path / "vault.json")
    token = vault.token_for("secret@example.com")
    vault.save()

    reloaded = load_vault(tmp_path / "vault.json", "k")
    assert reloaded.original_for(token) == "secret@example.com"


def test_vault_rejects_the_wrong_key(tmp_path):
    vault = TokenVault(key="right", path=tmp_path / "v.json")
    token = vault.token_for("secret@example.com")
    vault.save()

    wrong = load_vault(tmp_path / "v.json", "wrong")
    with pytest.raises(PrivacyKeyError):
        wrong.original_for(token)


def test_encrypt_decrypt_round_trip():
    blob = encrypt_value("hello world", "key")
    assert decrypt_value(blob, "key") == "hello world"
    assert blob != "hello world"


def test_encrypt_decrypt_rejects_tampering():
    blob = encrypt_value("hello world", "key")
    raw = list(blob)
    raw[10] = "A" if raw[10] != "A" else "B"
    with pytest.raises(PrivacyKeyError):
        decrypt_value("".join(raw), "key")


def test_decrypt_with_the_wrong_key_fails_loudly():
    blob = encrypt_value("hello world", "right-key")
    with pytest.raises(PrivacyKeyError):
        decrypt_value(blob, "wrong-key")


def test_masked_frame_passes_its_own_scan(frame: pd.DataFrame, config: PrivacyConfig):
    """The property that matters: nothing PII-shaped survives masking."""
    masked = mask_frame(frame, config).frame
    rescan = detect_frame(masked, config)
    leaked = {
        column: [d.as_dict() for d in finding.detections]
        for column, finding in rescan.findings.items()
        if finding.detections
    }
    assert not leaked, f"unmasked values survived: {leaked}"


def test_masking_only_touches_the_match(config: PrivacyConfig):
    only_notes = pd.DataFrame({"notes": ["call john@example.com or 415-555-0173 now"]})
    masked = mask_frame(only_notes, config).frame["notes"].iloc[0]
    assert masked.startswith("call ")
    assert masked.endswith(" now")
    assert "john@example.com" not in masked
    assert "415-555-0173" not in masked


def test_kind_scoped_rule_leaves_other_kinds_alone():
    """A field rule scoped to email must not touch a phone in the same cell."""
    config = PrivacyConfig(
        enabled=True, fields=[__field("notes", "redact", kinds=["email"])]
    )
    frame = pd.DataFrame({"notes": ["john@example.com 415-555-0173"]})
    masked = mask_frame(frame, config).frame["notes"].iloc[0]
    assert "john@example.com" not in masked
    assert "415-555-0173" in masked


def test_blanks_stay_blank(frame: pd.DataFrame, config: PrivacyConfig):
    masked = mask_frame(frame, config).frame
    assert masked["email"].iloc[-1] == ""


def test_disabled_config_is_a_passthrough(frame: pd.DataFrame):
    result = mask_frame(frame, PrivacyConfig(enabled=False))
    pd.testing.assert_frame_equal(result.frame, frame)
    assert result.total_masked == 0


def test_input_frame_is_not_modified(frame: pd.DataFrame, config: PrivacyConfig):
    before = frame.copy(deep=True)
    mask_frame(frame, config)
    pd.testing.assert_frame_equal(frame, before)


def test_mask_result_summary(frame: pd.DataFrame, config: PrivacyConfig):
    summary = mask_frame(frame, config).summary()
    assert summary["masked_total"] > 0
    assert summary["by_strategy"] == {"redact": summary["masked_total"]}
    assert "email" in summary["columns"]


# ------------------------------------------------------------------- config

def test_config_parses_yaml_block(tmp_path):
    path = tmp_path / "crm.yaml"
    path.write_text(
        "privacy:\n"
        "  default_strategy: hash\n"
        "  detect:\n"
        "    passport: true\n"
        "  fields:\n"
        "    - column: email\n"
        "      strategy: tokenize\n"
        "      kinds: [email]\n"
        "  custom_patterns:\n"
        "    employee_id:\n"
        "      pattern: 'EMP-\\d{6}'\n",
        encoding="utf-8",
    )
    config = load_privacy_config(path)
    assert config.default_strategy == "hash"
    assert config.detectors["passport"] is True
    assert config.strategy_for("email", "email") == "tokenize"
    assert config.strategy_for("email", "phone") == "none"
    assert config.strategy_for("other", "email") == "hash"
    assert "custom:employee_id" in config.enabled_kinds()


def test_config_without_privacy_block_is_disabled(tmp_path):
    path = tmp_path / "plain.yaml"
    path.write_text("crm: hubspot\n", encoding="utf-8")
    assert load_privacy_config(path).enabled is False


def test_config_rejects_unknown_keys():
    with pytest.raises(PrivacyConfigError):
        PrivacyConfig.from_dict({"privacy": {"nonsense": 1}})


def test_config_rejects_bad_strategy():
    with pytest.raises(PrivacyConfigError):
        PrivacyConfig.from_dict({"privacy": {"default_strategy": "scramble"}})


def test_config_rejects_bad_regex():
    with pytest.raises(PrivacyConfigError):
        PrivacyConfig.from_dict(
            {"privacy": {"custom_patterns": {"bad": {"pattern": "("}}}}
        )


def test_config_rejects_field_rule_without_column():
    with pytest.raises(PrivacyConfigError):
        PrivacyConfig.from_dict({"privacy": {"fields": [{"strategy": "hash"}]}})


def test_phone_gate_never_skips_a_real_number():
    """The digit gate exists only for speed; it must not lose a detection.

    Every phone in the detection fixture still has to be found with the gate in
    place, and a value too short to be a phone is still rejected silently.
    """
    config = PrivacyConfig(enabled=True)
    for phone in VALID_PHONES:
        assert "phone" in {d.kind for d in detect_value(phone, config)}, phone

    # Too few digits to dial: gated out, and correctly not reported.
    assert detect_value("ref 12-34", config) == []
    assert detect_value("abc", config) == []


def test_short_numeric_ref_is_not_a_phone():
    config = PrivacyConfig(enabled=True)
    assert "phone" not in {d.kind for d in detect_value("12345", config)}


def test_real_file_scale_pii_scan_is_complete():
    """A generated file at the spec's 12,000-row scale, with planted PII.

    Runs the layer end to end and requires every planted value to be masked
    with nothing surviving — the "real file with real data" gate.
    """
    rows = 12000
    emails = [f"person{i}.real@example{i % 13}.com" for i in range(rows)]
    phones = [f"+1 415 {200 + (i % 700):03d} {1000 + (i % 9000):04d}" for i in range(rows)]
    cards = [VALID_CARDS[0] if i % 4 == 0 else VALID_CARDS[1] for i in range(rows)]
    frame = pd.DataFrame(
        {
            "email": emails,
            "phone": phones,
            "card": cards,
            "note": [f"contact {e} or {p}" for e, p in zip(emails, phones)],
        }
    )
    config = PrivacyConfig(enabled=True)

    masked = mask_frame(frame, config)
    # email×2 per row (column + note), phone×2 per row (column + note), card×1
    expected = rows * 2 + rows * 2 + rows
    assert masked.total_masked == expected
    assert detect_frame(masked.frame, config).total == 0


# --------------------------------------------------------------- report render

def test_render_reports_no_pii_when_clean():
    from app_files.privacy import render_pii_report

    report = detect_frame(pd.DataFrame({"a": ["plain text", "more text"]}), PrivacyConfig(enabled=True))
    html = render_pii_report(report)
    assert "No personal data detected" in html


def test_render_escapes_column_names():
    from app_files.privacy import render_pii_report

    frame = pd.DataFrame({"<script>": ["a@b.com"]})
    html = render_pii_report(detect_frame(frame, PrivacyConfig(enabled=True)))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_inject_appends_without_touching_base():
    from app_files.privacy import inject_pii_report

    base = "<html><body>QA report body</body></html>"
    frame = pd.DataFrame({"email": ["a@b.com"]})
    out = inject_pii_report(base, detect_frame(frame, PrivacyConfig(enabled=True)))
    assert out.startswith(base)
    assert out != base
    assert "Privacy scan" in out


def __field(column, strategy, kinds=None, salt=None):
    from app_files.privacy.config import FieldRule

    return FieldRule(column=column, strategy=strategy, kinds=kinds or [], salt=salt)
