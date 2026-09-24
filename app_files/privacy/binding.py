"""Bind a config's ``privacy:`` block into an attended run.

The privacy layer (detection, masking, tokens, the report card) was complete
and tested, and the docs said a ``privacy:`` block could sit in a CRM config
"alongside ``fields:`` and ``rules:``". No run path ever read that block: the
masking only happened if a caller imported :mod:`app_files.privacy` and drove
it by hand. So a config-declared intent to mask PII survived to the output
unmasked, which is the one failure mode a compliance-adjacent tool must not
have.

This module closes that gap the same way :mod:`app_files.rules.binding` closed
the rules gap. It runs ``run_pipeline``/rules exactly as before and then, only
when the config declares privacy, masks the frame the pipeline produced and
adds the privacy card to the report. A config with no ``privacy:`` block is
untouched, so nothing that worked before changes behaviour.

Masking produces a *new* frame; the pipeline's own output is never rewritten.
The caller decides which deliverable carries the masked data — the CLI writes
it beside the original so an unmasked run stays byte-identical.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from app_files.mappers.schema import CONFIG_DIR
from app_files.privacy.config import PrivacyConfig, PrivacyConfigError
from app_files.privacy.detect import PIIReport, detect_frame
from app_files.privacy.mask import MaskResult, mask_frame
from app_files.privacy.report import inject_pii_report


def _config_path(crm: str | Path) -> Path | None:
    """The YAML file a config name or path resolves to, or None."""
    path = Path(crm)
    if not path.exists():
        path = CONFIG_DIR / f"{str(crm).strip().lower()}.yaml"
    return path if path.exists() else None


def privacy_block(crm: str | Path) -> dict[str, Any] | None:
    """The raw ``privacy:`` mapping a config declares, or None."""
    path = _config_path(crm)
    if path is None:
        return None
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    block = data.get("privacy") if isinstance(data, dict) else None
    return block if isinstance(block, dict) else None


def declared_privacy_config(crm: str | Path) -> PrivacyConfig | None:
    """The parsed privacy config a CRM config declares, or None.

    ``enabled`` defaults to True in the class, but a block only reaches here
    because the config asked for it; an explicit ``enabled: false`` still
    disables it and is honoured by the caller.
    """
    block = privacy_block(crm)
    if block is None:
        return None
    try:
        return PrivacyConfig.from_dict({"privacy": block})
    except PrivacyConfigError:
        raise


@dataclass
class PrivacyOutcome:
    """The result of masking one frame, in the shape a caller writes out."""

    report: PIIReport
    mask_result: MaskResult
    config: PrivacyConfig
    report_html: str = ""
    columns_masked: list[str] = field(default_factory=list)

    @property
    def masked_frame(self) -> pd.DataFrame:
        return self.mask_result.frame

    @property
    def total_detected(self) -> int:
        return self.report.total

    @property
    def total_masked(self) -> int:
        return self.mask_result.total_masked

    def summary(self) -> dict[str, Any]:
        return {
            "detected": self.total_detected,
            "masked": self.total_masked,
            "by_kind": self.report.kind_counts(),
            "by_strategy": dict(self.mask_result.strategy_counts),
            "columns": list(self.report.columns_with_pii),
        }

    def detections_frame(self) -> pd.DataFrame:
        return self.report.detections_frame()


def apply_privacy(frame: pd.DataFrame, config: PrivacyConfig) -> PrivacyOutcome:
    """Detect and mask ``frame`` with an already-resolved config.

    Detection runs first so the report covers every match, including matches in
    columns whose strategy is ``none`` (a column that may be reported but not
    rewritten). ``mask_frame`` then rewrites what the strategy allows.
    """
    report = detect_frame(frame, config)
    result = mask_frame(frame, config)
    outcome = PrivacyOutcome(
        report=report,
        mask_result=result,
        config=config,
        columns_masked=list(report.columns_with_pii),
    )
    outcome.report_html = inject_pii_report("", report, result.summary())
    return outcome


def apply_configured_privacy(
    frame: pd.DataFrame, crm: str | Path
) -> PrivacyOutcome | None:
    """Mask ``frame`` with ``crm``'s declared privacy block, or None.

    None means the config declares no privacy, which is the signal to a caller
    that it must write no privacy artifacts and change no existing output.
    """
    config = declared_privacy_config(crm)
    if config is None or not config.enabled:
        return None
    return apply_privacy(frame, config)


__all__ = [
    "PrivacyOutcome",
    "apply_configured_privacy",
    "apply_privacy",
    "declared_privacy_config",
    "privacy_block",
]