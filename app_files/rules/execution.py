"""Run built rules through the real engine and merge the failures into a result.

Why this module exists: ``run_pipeline`` loads a mapping config and validates
the mapped frame, but it does **not** read or execute the config's ``rules:``
block. The rules are run separately, by the caller, via
:func:`app_files.rules.run_rules_for`. That is the existing contract — the main
web app follows it, and so do the tests — so the builder follows it too rather
than changing the frozen pipeline.

The consequences of getting this wrong are quiet and serious: a rule set that
runs but is never merged still renders a QA report that says "0 errors", which
reads as "your data is fine". :func:`apply_rules` is therefore the only
supported way to attach a run's rule failures, and it mutates the
``ValidationReport`` the reporter actually reads so the QA report, the issues
CSV and the quality score all agree.

The core pipeline is imported for use only. Nothing here is written back into
it.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.pipeline import PipelineResult, run_pipeline
from app_files.profiling import Profile, profile
from app_files.profiling.report import render_qa_report_with_profile
from app_files.reporters import render_qa_report
from app_files.rules.engine import RuleResult, run_rules
from app_files.rules.schema import Rule
from app_files.validators import frictionless_summary


@dataclass
class BuiltRuleRun:
    """A pipeline run with the buyer's built rules applied on top of it."""

    result: PipelineResult
    rule_result: RuleResult
    rules: list[Rule]
    unmatched_rules: list[str]
    rules_path: Path
    rules_yaml: str
    qa_report_html: str
    profile_result: Profile

    def summary(self) -> dict[str, Any]:
        """Pipeline summary plus the rule outcome, for the UI's metric row."""
        return {
            **self.result.summary(),
            **self.rule_result.summary(),
            "unmatched_rules": len(self.unmatched_rules),
        }

    def issues_frame(self) -> pd.DataFrame:
        """Every issue, core and rule-based, in one table."""
        return self.result.validation.issues_frame()

    def rules_frame(self) -> pd.DataFrame:
        """Per-rule failure counts, so a buyer can see which rule caught what."""
        counts = self.rule_result.failures_by_rule or {}
        unmatched = set(self.unmatched_rules)
        rows = [
            {
                "rule": rule.name,
                "field": rule.field,
                "type": rule.type,
                "severity": rule.severity,
                "failures": counts.get(rule.name, 0),
                "ran": "no" if rule.name in unmatched else "yes",
            }
            for rule in self.rules
        ]
        return pd.DataFrame(
            rows, columns=["rule", "field", "type", "severity", "failures", "ran"]
        )


def field_map(result: PipelineResult) -> dict[str, str]:
    """Map every source column name onto the field the mapper wrote it to.

    Rules are built against the columns the buyer sees in *their* file
    (``Email Address``), but the engine validates the *mapped* frame
    (``email``). Without this translation a rule silently matches no column and
    reports zero failures — which reads as "your data is fine".

    Target names are also mapped to themselves so a rule written against an
    already-mapped column keeps working.
    """
    mapping: dict[str, str] = {}
    log = result.mapping_log()
    if not log.empty and {"target_field", "source_column"} <= set(log.columns):
        for _, row in log.iterrows():
            source = str(row["source_column"] or "").strip()
            target = str(row["target_field"] or "").strip()
            if source and target:
                mapping[source] = target
                mapping.setdefault(source.lower(), target)
    for column in result.clean_frame.columns:
        mapping.setdefault(str(column), str(column))
    return mapping


def resolve_rules(
    result: PipelineResult, rules: Iterable[Rule]
) -> tuple[list[Rule], list[str]]:
    """Re-point each rule's field at the mapped column.

    Returns ``(resolved_rules, unmatched_names)``. A rule whose field is in
    neither the source nor the mapped frame is reported as unmatched rather
    than dropped silently.
    """
    mapping = field_map(result)
    mapped_columns = {str(c) for c in result.clean_frame.columns}
    resolved: list[Rule] = []
    unmatched: list[str] = []
    for rule in rules:
        target = mapping.get(rule.field) or mapping.get(rule.field.lower())
        if target is None or target not in mapped_columns:
            unmatched.append(rule.name)
            continue
        resolved.append(dataclasses.replace(rule, field=target))
    return resolved, unmatched


def apply_rules(
    result: PipelineResult, rules: Iterable[Rule]
) -> tuple[RuleResult, list[str]]:
    """Run ``rules`` against the mapped frame and merge failures into ``result``.

    Fields are translated to their mapped names first (see :func:`resolve_rules`).
    The issues are appended to the same list the core validator fills, so the
    rendered QA report, ``issues_frame()`` and the quality score all reflect them
    without any change to the reporter.
    """
    resolved, unmatched = resolve_rules(result, rules)
    outcome = run_rules(result.clean_frame, resolved)
    if outcome.issues:
        result.validation.issues.extend(outcome.issues)
    return outcome, unmatched


def write_rules_file(rules_yaml: str, path: str | Path = "workspace/rules.yaml") -> Path:
    """Write the builder's YAML to disk, creating the folder if needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rules_yaml, encoding="utf-8")
    return target


def _rerender(
    result: PipelineResult,
    profile_result: Profile,
    project_name: str,
    source_filename: str,
    structural: dict[str, Any] | None,
) -> str:
    """Render the QA report from the result's *current* issues.

    Called after merging, so the report shows the rule failures. Mirrors the
    argument list the pipeline itself passes to ``render_qa_report``, including
    the caller's project name, filename and structural summary — re-rendering
    must not silently drop the header details the first render had.
    """
    html = render_qa_report(
        report=result.validation,
        mapping_log=result.mapping_log(),
        cleaning_log=result.cleaning_log(),
        mapped=result.clean_frame,
        project_name=project_name,
        source_filename=source_filename,
        crm=result.mapping_config.crm,
        structural=structural,
    )
    return render_qa_report_with_profile(html, result.clean_frame, profile_result)


def run_with_rules(
    source: pd.DataFrame,
    rules: Iterable[Rule],
    crm: str,
    rules_path: str | Path = "workspace/rules.yaml",
    project_name: str = "Data migration",
    source_filename: str = "upload.csv",
    run_structural_check: bool = True,
    result: PipelineResult | None = None,
) -> BuiltRuleRun:
    """Clean, map, validate, then apply ``rules`` and re-render the report.

    ``crm`` still selects the mapping config — the buyer's rules are additive on
    top of it, not a replacement for it.

    Pass ``result`` when the caller has already run the pipeline with options
    this function does not take (a cleaning config, say). The supplied result is
    used as-is instead of running the pipeline again, so those options survive.
    """
    rules = list(rules)
    if result is None:
        result = run_pipeline(
            source,
            crm=crm,
            project_name=project_name,
            source_filename=source_filename,
            run_structural_check=run_structural_check,
        )
    outcome, unmatched = apply_rules(result, rules)
    profile_result = profile(result.clean_frame)
    structural = (
        structural_check(result.clean_frame) if run_structural_check else None
    )
    html = _rerender(result, profile_result, project_name, source_filename, structural)

    from app_files.rules.builder import rules_to_yaml

    yaml_text = rules_to_yaml([_rule_to_dict(rule) for rule in rules])
    written = write_rules_file(yaml_text, rules_path)

    return BuiltRuleRun(
        result=result,
        rule_result=outcome,
        rules=rules,
        unmatched_rules=unmatched,
        rules_path=written,
        rules_yaml=yaml_text,
        qa_report_html=html,
        profile_result=profile_result,
    )


def _rule_to_dict(rule: Rule) -> dict[str, Any]:
    """Round-trip a rule back to the mapping it was built from."""
    payload: dict[str, Any] = {
        "name": rule.name,
        "field": rule.field,
        "type": rule.type,
        "severity": rule.severity,
    }
    if rule.type == "regex":
        payload["pattern"] = rule.pattern
    elif rule.type == "length":
        for key, value in (
            ("exactly", rule.exactly),
            ("min_length", rule.min_length),
            ("max_length", rule.max_length),
        ):
            if value is not None:
                payload[key] = value
    elif rule.type == "range":
        for key, value in (("min", rule.min), ("max", rule.max)):
            if value is not None:
                payload[key] = value
    elif rule.type == "list_of_values":
        payload["values"] = list(rule.values)
    if rule.message:
        payload["message"] = rule.message
    return payload


def structural_check(frame: pd.DataFrame) -> dict[str, Any] | None:
    """The Frictionless summary for a frame, or None if it cannot be produced."""
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "mapped.csv"
        frame.to_csv(path, index=False)
        try:
            return frictionless_summary(path)
        except Exception:  # noqa: BLE001 - a structural check is never fatal
            return None
