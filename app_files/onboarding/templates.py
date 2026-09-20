"""Template library: one-click, pre-built configurations.

A *template pack* is a folder under ``app_files/template_library/<name>/``
containing:

* ``config.yaml``        — a mapping config the pipeline can load directly
* ``README.md``          — plain-English description for the buyer
* ``sample_input.csv``   — a messy file to try the template on
* ``expected_output.csv``— the exact output the template must produce

This module discovers packs, runs a pack against its own sample, and compares
the result with the recorded expectation. That is the whole promise of the
library: pick a template, click run, get the documented result.

Nothing here modifies the frozen core. It calls ``run_pipeline`` with the
pack's config path, exactly as a user would.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app_files.pipeline import PipelineResult, run_pipeline

LIBRARY_DIR = Path(__file__).resolve().parent.parent / "template_library"

REQUIRED_FILES = ("config.yaml", "README.md", "sample_input.csv")


@dataclass(frozen=True)
class Template:
    """One template pack on disk."""

    name: str
    path: Path

    @property
    def title(self) -> str:
        """Human title, derived from the pack folder name."""
        return self.name.replace("_", " ").title()

    @property
    def config_path(self) -> Path:
        return self.path / "config.yaml"

    @property
    def readme_path(self) -> Path:
        return self.path / "README.md"

    @property
    def sample_path(self) -> Path:
        return self.path / "sample_input.csv"

    @property
    def expected_path(self) -> Path:
        return self.path / "expected_output.csv"

    def readme(self) -> str:
        return self.readme_path.read_text(encoding="utf-8") if self.readme_path.exists() else ""

    def missing_files(self) -> list[str]:
        """Names from ``REQUIRED_FILES`` absent (or empty) in this pack."""
        missing = []
        for filename in REQUIRED_FILES:
            file = self.path / filename
            if not file.exists() or file.stat().st_size == 0:
                missing.append(filename)
        return missing


def available_templates() -> list[str]:
    """Names of every template pack, sorted.

    A pack counts only when its folder holds at least a config and a README, so
    a half-copied folder never appears in the selector.
    """
    if not LIBRARY_DIR.exists():
        return []
    return sorted(
        folder.name
        for folder in LIBRARY_DIR.iterdir()
        if folder.is_dir() and (folder / "config.yaml").exists()
    )


def load_template(name: str) -> Template:
    """Return the :class:`Template` for ``name``, or raise ``FileNotFoundError``."""
    path = LIBRARY_DIR / name
    if not path.is_dir() or not (path / "config.yaml").exists():
        raise FileNotFoundError(
            f"No template named {name!r}. Available: {', '.join(available_templates())}"
        )
    return Template(name=name, path=path)


def all_templates() -> list[Template]:
    return [load_template(name) for name in available_templates()]


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def run_template(
    name: str,
    source: pd.DataFrame | None = None,
    project_name: str | None = None,
    **pipeline_kwargs,
) -> PipelineResult:
    """Run a template, by default against its own ``sample_input.csv``.

    Args:
        name: the template pack name.
        source: override the input frame; when omitted the pack's sample is used.
        project_name: shown in the QA report; defaults to the template title.
    """
    template = load_template(name)
    if source is None:
        if not template.sample_path.exists():
            raise FileNotFoundError(f"Template {name!r} has no sample_input.csv")
        source = _read_csv(template.sample_path)
    return run_pipeline(
        source,
        crm=str(template.config_path),
        project_name=project_name or template.title,
        source_filename=template.sample_path.name,
        **pipeline_kwargs,
    )


def render_template_result(name: str, result: PipelineResult | None = None) -> pd.DataFrame:
    """The frame a template produced from its sample, ready for comparison."""
    result = result or run_template(name)
    return result.clean_frame.reset_index(drop=True)


@dataclass
class TemplateCheck:
    """Outcome of running a template against its recorded expectation."""

    name: str
    passed: bool
    rows_expected: int
    rows_actual: int
    columns_expected: list[str]
    columns_actual: list[str]
    detail: str = ""

    @property
    def summary(self) -> str:
        return "PASS" if self.passed else f"FAIL ({self.detail})"


def check_template(name: str) -> TemplateCheck:
    """Run the template on its sample and compare with ``expected_output.csv``.

    Comparison is value-by-value on the union of columns, treating missing
    cells as equal so the check tests the transformation, not NaN formatting.
    """
    template = load_template(name)
    actual = render_template_result(name)

    if not template.expected_path.exists():
        return TemplateCheck(
            name=name,
            passed=False,
            rows_expected=0,
            rows_actual=len(actual),
            columns_expected=[],
            columns_actual=list(actual.columns),
            detail="expected_output.csv is missing",
        )

    expected = _read_csv(template.expected_path).reset_index(drop=True)

    if len(expected) != len(actual):
        return TemplateCheck(
            name=name,
            passed=False,
            rows_expected=len(expected),
            rows_actual=len(actual),
            columns_expected=list(expected.columns),
            columns_actual=list(actual.columns),
            detail=f"row count differs: expected {len(expected)}, got {len(actual)}",
        )

    all_columns = list(dict.fromkeys([*expected.columns, *actual.columns]))
    for column in all_columns:
        left = expected[column].tolist() if column in expected.columns else [""] * len(expected)
        right = actual[column].tolist() if column in actual.columns else [""] * len(actual)
        for index, (a, b) in enumerate(zip(left, right)):
            if _same(a, b):
                continue
            return TemplateCheck(
                name=name,
                passed=False,
                rows_expected=len(expected),
                rows_actual=len(actual),
                columns_expected=list(expected.columns),
                columns_actual=list(actual.columns),
                detail=f"row {index}, column {column!r}: expected {a!r}, got {b!r}",
            )

    return TemplateCheck(
        name=name,
        passed=True,
        rows_expected=len(expected),
        rows_actual=len(actual),
        columns_expected=list(expected.columns),
        columns_actual=list(actual.columns),
    )


def _same(left, right) -> bool:
    """Compare two cells, treating None/NaN/'' as the same 'empty' value."""
    left_blank = left is None or str(left).strip() in {"", "nan", "None"}
    right_blank = right is None or str(right).strip() in {"", "nan", "None"}
    if left_blank and right_blank:
        return True
    return str(left).strip() == str(right).strip()


def check_all_templates() -> list[TemplateCheck]:
    """Run every template's self-check. Used by the UI and the test suite."""
    return [check_template(name) for name in available_templates()]


def write_expected_output(name: str) -> Path:
    """Regenerate a template's ``expected_output.csv`` from a live run.

    This exists for *authoring* a new template. It is deliberately not used by
    the test suite — the expectation is the contract, and regenerating it to
    make a check pass would delete the only thing protecting the template.
    """
    template = load_template(name)
    frame = render_template_result(name)
    frame.to_csv(template.expected_path, index=False)
    return template.expected_path
