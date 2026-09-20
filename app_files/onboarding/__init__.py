"""Layer 8 — Onboarding.

Removes the "I can't run this" objection: a template library a non-technical
buyer can pick from, a wizard that walks through five steps, an install verifier
that proves the tool works on this machine, and a desktop launcher that starts
the app without a terminal.

Calls into the frozen core; never modifies it.
"""

from app_files.onboarding.templates import (
    Template,
    TemplateCheck,
    all_templates,
    available_templates,
    check_all_templates,
    check_template,
    load_template,
    render_template_result,
    run_template,
    write_expected_output,
)
from app_files.onboarding.verifier import (
    Check,
    VerifyReport,
    render_text,
    run_checks,
)
from app_files.onboarding.wizard import (
    STEPS,
    STEP_COUNT,
    WizardState,
    restart_wizard,
    should_show_wizard,
    steps_text,
)

__all__ = [
    "STEPS",
    "STEP_COUNT",
    "Check",
    "Template",
    "TemplateCheck",
    "VerifyReport",
    "WizardState",
    "all_templates",
    "available_templates",
    "check_all_templates",
    "check_template",
    "load_template",
    "render_template_result",
    "render_text",
    "restart_wizard",
    "run_checks",
    "run_template",
    "should_show_wizard",
    "steps_text",
    "write_expected_output",
]