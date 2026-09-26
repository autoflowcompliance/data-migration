"""Masking strategies for detected PII.

Four strategies, chosen per field (and optionally per kind):

``redact``   replace the match with a fixed marker.
``hash``     deterministic HMAC-SHA256 digest — the same value always maps to
             the same digest, so two masked tables still join on that column,
             but the original is not recoverable.
``tokenize`` reversible given the key: a deterministic token backed by an
             encrypted vault, so it joins *and* can be resolved back.
``partial``  keep only the last four characters.

Only the matched span is rewritten, so a phone number inside a free-text note
is masked while the surrounding prose survives.

Reversible tokenization is the only strategy that needs a key. Without one it
refuses rather than silently degrading to an irreversible form.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.privacy.config import PrivacyConfig
from app_files.privacy.detect import ColumnFindings, Detection, PIIReport, detect_value

REDACTION = "[REDACTED]"
TOKEN_PREFIX = "PII_"
#: Chars kept visible by the ``partial`` strategy.
PARTIAL_KEEP = 4


class PrivacyKeyError(RuntimeError):
    """Raised when tokenization is requested with no key available."""


# ------------------------------------------------------------------ keyed crypto


def _derive(key: str, label: bytes) -> bytes:
    return hmac.new(key.encode("utf-8"), label, hashlib.sha256).digest()


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """HMAC-SHA256 in counter mode: a PRF, not a home-grown cipher."""
    blocks = bytearray()
    counter = 0
    while len(blocks) < length:
        blocks.extend(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
        counter += 1
    return bytes(blocks[:length])


def encrypt_value(plaintext: str, key: str) -> str:
    enc_key = _derive(key, b"vault-enc")
    mac_key = _derive(key, b"vault-mac")
    nonce = secrets.token_bytes(8)
    body = plaintext.encode("utf-8")
    ciphertext = bytes(
        a ^ b for a, b in zip(body, _keystream(enc_key, nonce, len(body)), strict=True)
    )
    tag = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()[:16]
    return base64.urlsafe_b64encode(nonce + tag + ciphertext).decode("ascii")


def decrypt_value(blob: str, key: str) -> str:
    enc_key = _derive(key, b"vault-enc")
    mac_key = _derive(key, b"vault-mac")
    raw = base64.urlsafe_b64decode(blob.encode("ascii"))
    nonce, tag, ciphertext = raw[:8], raw[8:24], raw[24:]
    expected = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(tag, expected):
        raise PrivacyKeyError("Vault entry failed its integrity check (wrong key or tampering)")
    body = bytes(
        a ^ b
        for a, b in zip(ciphertext, _keystream(enc_key, nonce, len(ciphertext)), strict=True)
    )
    return body.decode("utf-8")


@dataclass
class TokenVault:
    """Deterministic tokens mapped to encrypted originals.

    The token is ``HMAC(key, value)`` so it is stable across runs and joins
    work; the original is sealed separately so the vault file alone is not
    readable without the key. The vault is written only when it is added to.
    """

    key: str
    path: Path | None = None
    entries: dict[str, str] = field(default_factory=dict)

    def token_for(self, value: str) -> str:
        digest = _derive(self.key, b"token:" + value.encode("utf-8")).hex()[:16]
        token = f"{TOKEN_PREFIX}{digest}"
        if token not in self.entries:
            self.entries[token] = encrypt_value(value, self.key)
        return token

    def original_for(self, token: str) -> str:
        try:
            blob = self.entries[token]
        except KeyError:
            raise PrivacyKeyError(f"No vault entry for token {token!r}") from None
        return decrypt_value(blob, self.key)

    def save(self) -> Path | None:
        if self.path is None:
            return None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"entries": self.entries}, indent=2, sort_keys=True)
        self.path.write_text(payload, encoding="utf-8")
        os.chmod(self.path, 0o600)
        return self.path


def load_vault(path: str | Path, key: str) -> TokenVault:
    location = Path(path)
    if location.exists():
        data = json.loads(location.read_text(encoding="utf-8"))
    else:
        data = {"entries": {}}
    return TokenVault(key=key, path=location, entries=data.get("entries", {}))


# ------------------------------------------------------------------- strategies


def _hash_value(value: str, salt: str) -> str:
    pepper = salt.encode("utf-8")
    return hashlib.sha256(pepper + value.encode("utf-8")).hexdigest()


def _partial_value(value: str) -> str:
    stripped = value.strip()
    if len(stripped) <= PARTIAL_KEEP:
        return "*" * len(stripped)
    return "*" * (len(stripped) - PARTIAL_KEEP) + stripped[-PARTIAL_KEEP:]


def text_of(value: Any) -> str:
    """Render a cell as the text detection scanned, preserving blankness.

    ``NaN``/``None`` must not become the literal string ``"nan"`` — a masked
    frame should keep its blanks blank.
    """
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value)


def apply_strategy(
    value: str,
    detection: Detection,
    strategy: str,
    column: str,
    config: PrivacyConfig,
    vault: TokenVault | None,
) -> str:
    if strategy == "redact":
        return REDACTION
    if strategy == "hash":
        return _hash_value(value, config.salt_for(column) or "")
    if strategy == "partial":
        return _partial_value(value)
    if strategy == "tokenize":
        if vault is None:
            raise PrivacyKeyError(
                "tokenize requires a key: set privacy.token_key, privacy.token_key_env, "
                f"or the {config.token_key_env} environment variable"
            )
        return vault.token_for(value)
    raise ValueError(f"Unknown strategy {strategy!r}")


@dataclass
class MaskResult:
    frame: pd.DataFrame
    report: PIIReport
    vault: TokenVault | None = None
    masked_counts: dict[str, int] = field(default_factory=dict)
    strategy_counts: dict[str, int] = field(default_factory=dict)

    @property
    def total_masked(self) -> int:
        return sum(self.masked_counts.values())

    def summary(self) -> dict[str, Any]:
        return {
            "masked_total": self.total_masked,
            "by_kind": dict(self.masked_counts),
            "by_strategy": dict(self.strategy_counts),
            "columns": self.report.columns_with_pii,
        }


def _mask_text(
    text: str,
    detections: list[Detection],
    column: str,
    config: PrivacyConfig,
    vault: TokenVault | None,
) -> tuple[str, dict[str, int], dict[str, int]]:
    """Rewrite one cell, right-to-left so earlier spans keep their offsets."""
    by_kind: dict[str, int] = {}
    by_strategy: dict[str, int] = {}
    out = text
    for detection in sorted(detections, key=lambda d: d.start, reverse=True):
        strategy = config.strategy_for(column, detection.kind)
        if strategy == "none":
            continue
        replacement = apply_strategy(
            detection.value, detection, strategy, column, config, vault
        )
        out = out[: detection.start] + replacement + out[detection.end :]
        by_kind[detection.kind] = by_kind.get(detection.kind, 0) + 1
        by_strategy[strategy] = by_strategy.get(strategy, 0) + 1
    return out, by_kind, by_strategy


def mask_frame(
    frame: pd.DataFrame,
    config: PrivacyConfig,
    columns: list[str] | None = None,
) -> MaskResult:
    """Detect and mask PII in ``frame``, returning a new frame.

    The input frame is not modified. Masking is idempotent in the sense that
    re-running detection over the result reports none of the masked kinds.
    """
    if not config.enabled:
        return MaskResult(frame=frame.copy(), report=PIIReport())

    targets = list(frame.columns) if columns is None else [c for c in columns if c in frame.columns]
    vault: TokenVault | None = None
    if any(
        config.strategy_for(column, kind) == "tokenize"
        for column in targets
        for kind in _possible_kinds(config)
    ):
        key = config.resolve_token_key()
        if key is None:
            raise PrivacyKeyError(
                "tokenize requires a key: set privacy.token_key, privacy.token_key_env, "
                f"or the {config.token_key_env} environment variable"
            )
        vault = TokenVault(key=key, path=Path(config.vault_path) if config.vault_path else None)

    result_frame = frame.copy()
    report = PIIReport(rows_scanned=len(frame), columns_scanned=list(targets))
    masked_counts: dict[str, int] = {}
    strategy_counts: dict[str, int] = {}

    # One pass per column: detect, record the report, and rewrite in place.
    for column in targets:
        finding = ColumnFindings(column=column)
        by_row: dict[int, list[Detection]] = {}
        for row_index, value in enumerate(frame[column].tolist()):
            found = detect_value(value, config)
            if found:
                finding.detections.extend(found)
                by_row[row_index] = found
        report.findings[column] = finding
        if not by_row:
            continue
        # The column may be non-object dtype; masking introduces strings.
        result_frame[column] = result_frame[column].astype(object)
        # Positional label: get_loc may return a slice for duplicate names.
        location = list(result_frame.columns).index(column)
        for row_index, detections in by_row.items():
            new_value, by_kind, by_strategy = _mask_text(
                text_of(frame[column].iloc[row_index]), detections, column, config, vault
            )
            result_frame.iat[row_index, location] = new_value
            for kind, number in by_kind.items():
                masked_counts[kind] = masked_counts.get(kind, 0) + number
            for strategy, number in by_strategy.items():
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + number

    if vault is not None and vault.path is not None:
        vault.save()

    return MaskResult(
        frame=result_frame,
        report=report,
        vault=vault,
        masked_counts=masked_counts,
        strategy_counts=strategy_counts,
    )


def _possible_kinds(config: PrivacyConfig) -> list[str]:
    return config.enabled_kinds()
