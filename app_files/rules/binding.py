"""Run a source through the pipeline *with the rules its config declares*.

Layer 4 can already run rules (``run_rules_for``) and Layer 4's builder can run
a caller's rules on top of a pipeline result (``run_with_rules``). Neither was
wired into an unattended run: a config's ``rules:`` block ran in the web UI but
not in the CLI or the batch engine, so a scheduled run reported the core
validator's issues only and read as clean while the buyer's own rules had
failures nobody saw.

This layer closes that gap without touching the pipeline. It runs
``run_pipeline`` exactly as before, then applies the config's rules through
``run_with_rules`` so failures land in the same issue list, the same QA report
and the same quality score. A run with no rules behaves identically to the
plain pipeline, so nothing that worked before changes behaviour.

Rules stay advisory by default: a failure is reported, not enforced. Pass
``strict=True`` to ``failures_exceed`` (or the CLI's ``--strict-rules``) to make
a declared failure fail the run.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.pipeline import PipelineResult, run_pipeline
from app_files.profiling import Profile, profile
from app_files.rules.cross_field import (
    CrossFieldRuleError,
    load_cross_field_rules,
)
from app_files.rules.engine import RuleResult, load_rules_for
from app_files.rules.execution import BuiltRuleRun, run_with_rules
from app_files.rules.schema import RuleConfigError


def _config_path(crm: str | Path) -> Path | None:
    """The YAML file a config name or path resolves to, or None."""
    path = Path(crm)
    if not path.exists():
        from app_files.mappers.schema import CONFIG_DIR

        path = CONFIG_DIR / f"{str(crm).strip().lower()}.yaml"
    return path if path.exists() else None


def _declared_rules(crm: str | Path) -> list[Any]:
    """The config's rules, or none when there is nothing usable to run."""
    try:
        return list(load_rules_for(crm))
    except RuleConfigError:
        return []


def _declared_cross_field_rules(crm: str | Path) -> list[Any]:
    """The config's ``cross_field:`` rules, or none."""
    path = _config_path(crm)
    if path is None:
        return []
    import yaml

    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    try:
        return list(load_cross_field_rules(data))
    except CrossFieldRuleError:
        return []


def _has_rules(crm: str | Path) -> bool:
    return bool(_declared_rules(crm) or _declared_cross_field_rules(crm))


def rules_home() -> Path:
    """Where the accepted rule YAML for a config-driven run is written.

    Honours ``AUTOFLOW_HOME`` for the same reason every other state-writing
    layer does: the repository working tree must stay clean.
    """
    override = os.getenv("AUTOFLOW_HOME")
    base = Path(override) if override else Path.home() / ".autoflow"
    return base / "rules"


def _rules_path(crm: str | Path) -> Path:
    name = Path(str(crm)).stem
    keep = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
    return rules_home() / f"{keep or 'rules'}.yaml"


def _as_built(result: PipelineResult) -> BuiltRuleRun:
    """Wrap a rule-less pipeline result so callers see one return type."""
    return BuiltRuleRun(
        result=result,
        rule_result=RuleResult(issues=[], rules_run=0),
        rules=[],
        unmatched_rules=[],
        rules_path=Path(),
        rules_yaml="",
        qa_report_html=result.qa_report_html,
        profile_result=profile(result.clean_frame),
    )


def apply_configured_rules(
    result: PipelineResult,
    crm: str | Path,
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
    rules_path: str | Path | None = None,
    run_structural_check: bool = True,
) -> BuiltRuleRun:
    """Apply ``crm``'s declared rules on top of an already-run pipeline result.

    The entry point for a caller (the CLI, the batch engine) that ran the
    pipeline itself and must not run it a second time — a second run would drop
    options like a cleaning config and change the output. Returns a
    ``BuiltRuleRun`` even when the config declares no rules, so the caller reads
    one shape.

    ``project_name`` and ``source_filename`` must be the values the pipeline was
    run with. Applying rules re-renders the QA report, and the reporter takes
    those as arguments — passing the defaults here would quietly replace the
    run's real header with a placeholder.
    """
    rules = _declared_rules(crm)
    cross_field_rules = _declared_cross_field_rules(crm)
    if not rules and not cross_field_rules:
        return BuiltRuleRun(
            result=result,
            rule_result=RuleResult(issues=[], rules_run=0),
            rules=[],
            unmatched_rules=[],
            rules_path=Path(),
            rules_yaml="",
            qa_report_html=result.qa_report_html,
            profile_result=profile(result.clean_frame),
        )
    return run_with_rules(
        result.clean_frame,
        rules,
        str(crm),
        rules_path=rules_path if rules_path is not None else _rules_path(crm),
        project_name=project_name,
        source_filename=source_filename,
        run_structural_check=run_structural_check,
        result=result,
        cross_field_rules=cross_field_rules,
    )


def run_configured(
    source: pd.DataFrame,
    crm: str | Path,
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
    rules_path: str | Path | None = None,
    run_structural_check: bool = True,
) -> BuiltRuleRun:
    """Run ``source``, then apply the rules ``crm``'s config declares.

    Returns a ``BuiltRuleRun`` either way, so a caller reads
    ``.rule_result``/``.summary()`` without branching on whether the config had
    rules. Falls back to the plain pipeline when there is nothing to run, which
    keeps the no-rules output byte-identical to the frozen pipeline.
    """
    rules = _declared_rules(crm)
    cross_field_rules = _declared_cross_field_rules(crm)
    if not rules and not cross_field_rules:
        return _as_built(
            run_pipeline(
                source,
                crm=crm,
                project_name=project_name,
                source_filename=source_filename,
                run_structural_check=run_structural_check,
            )
        )
    return run_with_rules(
        source,
        rules,
        str(crm),
        rules_path=rules_path if rules_path is not None else _rules_path(crm),
        project_name=project_name,
        source_filename=source_filename,
        run_structural_check=run_structural_check,
        cross_field_rules=cross_field_rules,
    )


def failures_exceed(run: BuiltRuleRun, max_failures: int = 0) -> bool:
    """True when the run's rule failures are over ``max_failures``.

    The hook for ``--strict-rules``: ``max_failures=0`` means any declared
    failure is too many.
    """
    return run.total_rule_failures > max_failures


def rule_report(run: BuiltRuleRun) -> dict[str, Any]:
    """A compact rule outcome for a summary line or a CSV row."""
    counts = run.rule_result.failures_by_rule or {}
    cross = run.cross_field_result
    return {
        "rules_declared": len(run.rules) + len(run.cross_field_rules),
        "rules_run": run.rule_result.rules_run + getattr(cross, "rules_run", 0),
        "rule_failures": run.rule_result.total_failures
        + len(getattr(cross, "issues", []) or []),
        "unmatched_rules": len(run.unmatched_rules) + len(run.unmatched_cross_field),
        "failures_by_rule": dict(counts),
    }


__all__ = [
    "apply_configured_rules",
    "Profile",
    "failures_exceed",
    "rule_report",
    "rules_home",
    "run_configured",
]
