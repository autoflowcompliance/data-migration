"""Apply every block a config declares, in one canonical order.

The flat CLI and the batch engine each open-coded the same sequence — rules,
then privacy, then normalization, then dedupe — and ``migrate`` opened none of
them, so a config that declared a ``privacy:`` block wrote raw PII from that
path and a rehearsal reported no duplicates for a config that removes two.

This module is that sequence, once. It calls the existing per-layer bindings;
it does not reimplement them, and it does not touch the frozen pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.pipeline import PipelineResult


@dataclass
class ConfiguredBindings:
    """Every declared block, resolved against one pipeline result.

    A ``None`` field means the config did not declare that block, which is the
    caller's signal to write no artifact for it and change nothing.
    """

    built: Any
    privacy: Any | None
    normalization: Any | None
    dedupe: Any | None
    qa_report_html: str
    quality: Any | None = None

    @property
    def declared_rules(self) -> int:
        return len(self.built.rules) + len(self.built.cross_field_rules)

    def summary(self) -> dict[str, Any]:
        """Counts for a caller's console line, keyed by block."""
        result: dict[str, Any] = {
            "rules_run": self.built.total_rules_run,
            "rules_declared": self.declared_rules,
            "rule_failures": self.built.total_rule_failures,
        }
        if self.privacy is not None:
            result["privacy"] = self.privacy.summary()
        if self.normalization is not None:
            result["normalization"] = self.normalization.summary()
        if self.dedupe is not None:
            result["dedupe"] = self.dedupe.summary()
        if self.quality is not None:
            result["quality"] = self.quality.summary()
        return result


def apply_configured_bindings(
    result: PipelineResult,
    crm: str | Path,
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
    persist_rules: bool = True,
) -> ConfiguredBindings:
    """Apply the blocks ``crm`` declares, on top of an already-run result.

    Rules run first because they re-render the QA report; the PII card is then
    injected into that same HTML, so the caller writes one report that reflects
    both. Privacy, normalization and dedupe each work on a copy, so the
    pipeline's own ``clean_frame`` is never rewritten.

    ``persist_rules=False`` is for a rehearsal: it reports the rules without
    writing the accepted YAML to the state home.
    """
    from app_files.dedupe.binding import apply_configured_dedupe
    from app_files.normalization.binding import apply_configured_normalization
    from app_files.privacy.binding import apply_configured_privacy
    from app_files.privacy.report import inject_pii_report
    from app_files.rules.binding import apply_configured_rules

    built = apply_configured_rules(
        result,
        crm,
        project_name=project_name,
        source_filename=source_filename,
        persist_rules=persist_rules,
    )
    qa_html = built.qa_report_html

    privacy = apply_configured_privacy(result.clean_frame, crm)
    if privacy is not None:
        qa_html = inject_pii_report(
            qa_html, privacy.report, privacy.mask_result.summary()
        )

    return ConfiguredBindings(
        built=built,
        privacy=privacy,
        normalization=apply_configured_normalization(result.clean_frame, crm),
        dedupe=apply_configured_dedupe(result.clean_frame, crm),
        qa_report_html=qa_html,
        quality=_configured_quality(result.clean_frame, crm),
    )


def _configured_quality(frame: pd.DataFrame, crm: str | Path) -> Any | None:
    """Resolve a config's ``quality:`` block against the frame, or ``None``.

    The block is read from the same file the other bindings read, so one config
    drives them all. Profiling runs only when a block is declared — an unbound
    config pays nothing and writes nothing.
    """
    from app_files.quality.binding import bind_quality

    declared = _declared_blocks(crm)
    if "quality" not in declared:
        return None
    return bind_quality(frame, declared)


def _declared_blocks(crm: str | Path) -> dict[str, Any]:
    """The raw config mapping for ``crm``, or an empty mapping if unreadable."""
    path = Path(crm)
    if not path.exists():
        return {}
    try:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - an unreadable config is the caller's error
        return {}


def write_bound_deliverables(
    bindings: ConfiguredBindings, outdir: str | Path
) -> dict[str, Path]:
    """Write the artifacts a declared block implies, and nothing else.

    A config that declares no block writes no extra file, so its output is
    byte-identical to a run that never had this helper.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    if bindings.declared_rules or bindings.privacy is not None:
        written["qa_report"] = _write_text(outdir / "qa_report.html", bindings.qa_report_html)
    if bindings.privacy is not None:
        written["masked_data"] = _write_csv(outdir / "masked_data.csv", bindings.privacy.masked_frame)
        written["privacy_report"] = _write_text(
            outdir / "privacy_report.html", bindings.privacy.report_html
        )
    if bindings.normalization is not None:
        written["normalized_data"] = _write_csv(
            outdir / "normalized_data.csv", bindings.normalization.frame
        )
        conversions = bindings.normalization.conversions_frame()
        if not conversions.empty:
            written["currency_conversions"] = _write_csv(
                outdir / "currency_conversions.csv", conversions
            )
    if bindings.dedupe is not None:
        written["deduped_data"] = _write_csv(
            outdir / "deduped_data.csv", bindings.dedupe.frame
        )
        merges = bindings.dedupe.merges_frame()
        if not merges.empty:
            written["duplicates_removed"] = _write_csv(
                outdir / "duplicates_removed.csv", merges
            )
    if bindings.quality is not None:
        import json

        written["quality_report"] = _write_text(
            outdir / "quality_report.json",
            json.dumps(bindings.quality.summary(), indent=2, default=str),
        )
    return written


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_csv(path: Path, frame: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


__all__ = [
    "ConfiguredBindings",
    "apply_configured_bindings",
    "write_bound_deliverables",
]
