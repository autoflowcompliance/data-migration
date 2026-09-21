"""Guided setup wizard: five steps, no YAML, no terminal.

The wizard is a small state machine so the logic is testable without a browser.
The web interface renders it; this module owns the steps, the validation and
the persisted "setup complete" flag.

State file: ``~/.autoflow/setup.json`` (override with ``AUTOFLOW_HOME``). The
flag exists so a returning user is not shown the wizard again, and so
"Restart wizard" has something to clear.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

STEPS: tuple[str, ...] = (
    "Upload your file",
    "Pick a template",
    "Preview what will change",
    "Run",
    "Download results",
)

STEP_COUNT = len(STEPS)


def state_dir() -> Path:
    """Where the setup flag lives. ``AUTOFLOW_HOME`` overrides for tests."""
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override)
    return Path.home() / ".autoflow"


def state_file() -> Path:
    return state_dir() / "setup.json"


@dataclass
class WizardState:
    """Everything the wizard remembers between steps."""

    step: int = 0
    completed: bool = False
    template: str | None = None
    source_filename: str | None = None
    output_format: str = "csv"

    # ------------------------------------------------------------- navigation
    @property
    def step_name(self) -> str:
        index = min(max(self.step, 0), STEP_COUNT - 1)
        return STEPS[index]

    @property
    def is_first(self) -> bool:
        return self.step <= 0

    @property
    def is_last(self) -> bool:
        return self.step >= STEP_COUNT - 1

    def can_advance(self) -> tuple[bool, str]:
        """Whether "Next" is allowed from the current step, and why not if not.

        Steps 1-3 need something to work with; the preview step needs a run to
        preview. Guarding here (not in the UI) is what makes the flow testable.
        """
        if self.step == 0 and not self.source_filename:
            return False, "Upload a file first."
        if self.step == 1 and not self.template:
            return False, "Choose a template (or leave the default) to continue."
        if self.step == 2 and self.run_summary is None:
            return False, "Nothing has been run yet, so there is nothing to preview."
        return True, ""

    def next(self) -> "WizardState":
        ok, _ = self.can_advance()
        if ok and not self.is_last:
            self.step += 1
        return self

    def back(self) -> "WizardState":
        if not self.is_first:
            self.step -= 1
        return self

    def finish(self) -> "WizardState":
        """Mark setup done and persist it, so the wizard stops showing."""
        self.completed = True
        self.step = STEP_COUNT - 1
        self.save()
        return self

    def restart(self) -> "WizardState":
        self.step = 0
        self.completed = False
        return self

    # The run summary is attached by the UI after step 4; it is not persisted
    # because it holds a DataFrame.
    run_summary: dict[str, Any] | None = field(default=None, repr=False)

    # -------------------------------------------------------------- persistence
    def save(self) -> Path:
        path = state_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload.pop("run_summary", None)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls) -> "WizardState":
        path = state_file()
        if not path.exists():
            return cls()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return cls()
        if not isinstance(payload, dict):
            return cls()
        payload.pop("run_summary", None)
        known = {f for f in cls.__dataclass_fields__ if f != "run_summary"}
        return cls(**{key: value for key, value in payload.items() if key in known})

    @classmethod
    def reset(cls) -> "WizardState":
        """Clear the persisted flag — this is what "Restart wizard" calls."""
        path = state_file()
        if path.exists():
            path.unlink()
        return cls()


def should_show_wizard() -> bool:
    """True on a fresh install, or after the user asked to see it again."""
    return not WizardState.load().completed


def restart_wizard() -> WizardState:
    """Forget that setup finished, so the wizard shows on the next render."""
    return WizardState.reset()


def steps_text() -> list[dict[str, Any]]:
    """Step names and plain-English instructions, for rendering and testing."""
    return [
        {
            "number": 1,
            "name": STEPS[0],
            "instruction": "Choose the file you want to clean. CSV, Excel, JSON and PDF are all accepted.",
        },
        {
            "number": 2,
            "name": STEPS[1],
            "instruction": "Pick a template from the list, or keep the one already selected. "
                           "The template decides the target columns and the rules.",
        },
        {
            "number": 3,
            "name": STEPS[2],
            "instruction": "See exactly what will change before committing: rows in, rows out, "
                           "duplicates removed and the issues found.",
        },
        {
            "number": 4,
            "name": STEPS[3],
            "instruction": "Run the migration. This takes a few seconds and never changes your original file.",
        },
        {
            "number": 5,
            "name": STEPS[4],
            "instruction": "Download the clean data, the QA report and the list of issues.",
        },
    ]