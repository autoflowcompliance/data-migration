"""Install verifier: confirm the tool is usable before the buyer commits.

The fear this removes is "will this even work on my machine". Every check
answers one concrete question about the *running* installation, not about the
source tree: is the interpreter good enough, are the dependencies importable,
are the sample files present, is the output folder writable, is a port free,
and do the templates actually run.

Each check returns a :class:`Check` with a plain-English label, a pass/fail and
an actionable hint when it fails. ``verifier.run_checks()`` returns them all;
``render_text()`` prints the green/red report a user pastes into a support
message.
"""

from __future__ import annotations

import importlib
import socket
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = ROOT / "app_files" / "samples"
CONFIG_DIR = ROOT / "app_files" / "configs"

# (import name, what the user loses without it)
REQUIRED_IMPORTS = [
    ("pandas", "cleaning and mapping — nothing works without it"),
    ("yaml", "mapping configs cannot be read"),
    ("openpyxl", "Excel input and output"),
    ("pdfplumber", "bank statement PDF reading"),
    ("phonenumbers", "phone number standardisation"),
    ("chardet", "automatic CSV encoding detection"),
    ("frictionless", "the structural file check"),
    ("jinja2", "the HTML QA report"),
]

REQUIRED_SAMPLES = [
    "messy_contacts.csv",
    "messy_contacts.json",
    "employee_records.csv",
    "bank_statement.csv",
    "bank_statement.pdf",
    "ledger.csv",
]


@dataclass
class Check:
    """One verification step."""

    name: str
    passed: bool
    detail: str = ""
    hint: str = ""

    @property
    def mark(self) -> str:
        return "PASS" if self.passed else "FAIL"


@dataclass
class VerifyReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> list[Check]:
        return [check for check in self.checks if not check.passed]

    def summary(self) -> dict[str, object]:
        return {
            "ok": self.passed,
            "total": len(self.checks),
            "passed": sum(1 for check in self.checks if check.passed),
            "failed": [check.name for check in self.failures],
        }


def _check_python() -> Check:
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        return Check("Python version", True, f"Python {major}.{minor}")
    return Check(
        "Python version",
        False,
        f"Python {major}.{minor}",
        "This tool needs Python 3.10 or newer. Install a newer Python and re-run.",
    )


def _check_imports() -> list[Check]:
    checks = []
    for module, purpose in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
            checks.append(Check(f"Dependency: {module}", True, purpose))
        except Exception as exc:  # noqa: BLE001 - surfaced, never swallowed
            checks.append(
                Check(
                    f"Dependency: {module}",
                    False,
                    f"{type(exc).__name__}: {exc}",
                    f"Run: pip install -r requirements.txt  (missing library breaks {purpose})",
                )
            )
    return checks


def _check_samples() -> Check:
    if not SAMPLES_DIR.exists():
        return Check(
            "Sample files present",
            False,
            f"{SAMPLES_DIR} does not exist",
            "Re-download the tool; the samples folder ships with it.",
        )
    missing = [
        name
        for name in REQUIRED_SAMPLES
        if not (SAMPLES_DIR / name).exists() or (SAMPLES_DIR / name).stat().st_size == 0
    ]
    if missing:
        return Check(
            "Sample files present",
            False,
            f"missing: {', '.join(missing)}",
            "Re-download the tool; some sample files are missing or empty.",
        )
    return Check("Sample files present", True, f"{len(REQUIRED_SAMPLES)} sample files found")


def _check_configs() -> Check:
    configs = sorted(CONFIG_DIR.glob("*.yaml")) if CONFIG_DIR.exists() else []
    if len(configs) >= 1:
        return Check("Target configs present", True, f"{len(configs)} configs: {', '.join(p.stem for p in configs)}")
    return Check(
        "Target configs present",
        False,
        "no YAML configs found",
        f"Expected config files in {CONFIG_DIR}.",
    )


def _check_output_writable() -> Check:
    """Write a real file, then read it back and remove it."""
    for candidate in (ROOT / "output", Path(tempfile.gettempdir())):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".verify_write_probe"
            probe.write_text("ok", encoding="utf-8")
            content = probe.read_text(encoding="utf-8")
            probe.unlink()
            if content == "ok":
                return Check("Output folder writable", True, str(candidate))
        except Exception:  # noqa: BLE001 - try the next candidate
            continue
    return Check(
        "Output folder writable",
        False,
        "no writable output location",
        "Check folder permissions for the tool's install directory.",
    )


def _check_port(port: int = 8501) -> Check:
    """The web UI binds here. A busy port is the most common first-run failure."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        in_use = sock.connect_ex(("127.0.0.1", port)) == 0
    if in_use:
        return Check(
            f"Port {port} available",
            False,
            f"something is already listening on {port}",
            f"Close the other app, or start the tool with a different port: "
            f"python -m streamlit run app_files/interface/web/app.py --server.port 8502",
        )
    return Check(f"Port {port} available", True, "free")


def _check_templates() -> Check:
    """Prove the template library actually runs, not just that folders exist."""
    try:
        from app_files.onboarding.templates import available_templates, check_template

        names = available_templates()
        if not names:
            return Check(
                "Template library runs",
                False,
                "no templates found",
                "Re-download the tool; the template library ships with it.",
            )
        failing = [name for name in names if not check_template(name).passed]
        if failing:
            return Check(
                "Template library runs",
                False,
                f"{len(failing)} template(s) failed: {', '.join(failing)}",
                "A template produced unexpected output. Report it; do not edit the expectation.",
            )
        return Check("Template library runs", True, f"all {len(names)} templates produce their documented output")
    except Exception as exc:  # noqa: BLE001
        return Check(
            "Template library runs",
            False,
            f"{type(exc).__name__}: {exc}",
            "Re-install dependencies with: pip install -r requirements.txt",
        )


def _check_core_pipeline() -> Check:
    """The end-to-end path, on a known-messy file, with a known result."""
    try:
        import pandas as pd

        from app_files.pipeline import run_pipeline

        sample = SAMPLES_DIR / "messy_contacts.csv"
        if not sample.exists():
            return Check("Core pipeline runs", False, "sample missing", "Re-download the tool.")
        frame = pd.read_csv(sample, dtype=str, keep_default_na=False)
        result = run_pipeline(frame, crm="hubspot", source_filename=sample.name)
        summary = result.summary()
        observed = f"{summary['rows_in']} rows in, {summary['rows_out']} out, score {summary['quality_score']}%"
        if summary["rows_in"] == 7 and summary["rows_out"] == 6:
            return Check("Core pipeline runs", True, observed)
        return Check(
            "Core pipeline runs",
            False,
            f"unexpected result: {observed}",
            "Expected 7 rows in and 6 out. This install is not behaving like a clean one.",
        )
    except Exception as exc:  # noqa: BLE001
        return Check(
            "Core pipeline runs",
            False,
            f"{type(exc).__name__}: {exc}",
            "Run: python -m pytest -q  to see the full failure.",
        )


def run_checks(include_templates: bool = True, port: int = 8501) -> VerifyReport:
    """Run every check and return the report.

    ``include_templates`` and the pipeline check are the slow ones (a pipeline
    run takes a moment); everything else is instant.
    """
    checks: list[Check] = [_check_python()]
    checks.extend(_check_imports())
    checks.append(_check_samples())
    checks.append(_check_configs())
    checks.append(_check_output_writable())
    checks.append(_check_port(port))
    if include_templates:
        checks.append(_check_templates())
    checks.append(_check_core_pipeline())
    return VerifyReport(checks=checks)


def render_text(report: VerifyReport | None = None) -> str:
    """A plain-text green/red report, safe to paste into a support message."""
    report = report or run_checks()
    lines = ["AutoFlow install check", "=" * 40]
    for check in report.checks:
        lines.append(f"[{check.mark}] {check.name}: {check.detail}")
        if not check.passed and check.hint:
            lines.append(f"        -> {check.hint}")
    lines.append("=" * 40)
    summary = report.summary()
    if report.passed:
        lines.append(f"All clear — {summary['passed']} of {summary['total']} checks passed.")
    else:
        lines.append(
            f"{summary['passed']} of {summary['total']} checks passed. "
            f"Fix the FAIL lines above and run this check again."
        )
    return "\n".join(lines)


def main() -> int:  # pragma: no cover - thin CLI shim
    """``python -m app_files.onboarding.verifier`` entry point."""
    report = run_checks()
    print(render_text(report))
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())