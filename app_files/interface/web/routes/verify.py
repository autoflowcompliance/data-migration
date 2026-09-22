"""Route ``/verify`` — prove the install actually works.

A client who has just unzipped a folder has no way to tell a working install
from a broken one until they try their own data. This page runs the core
pipeline on a bundled sample, checks the writers and the licence, and reports
each result separately so a failure points at the layer at fault.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web import state
from app_files.interface.web import theme
from app_files.interface.web.layout import page_shell
from app_files.licensing import current_mode, license_path
from app_files.output import to_bytes
from app_files.profiling import profile
from app_files.pipeline import run_pipeline

NAV = [
    ("Home", "/demo"),
    ("Settings", "/settings"),
    ("Buy", "/buy"),
    ("Verify", "/verify"),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def run_checks() -> list[Check]:
    """Exercise the real code paths and report each one."""
    checks: list[Check] = [
        Check("Python version", sys.version_info >= (3, 10), sys.version.split()[0])
    ]

    licence, limits = current_mode()
    # An absent licence is a valid demo install, not a fault. A licence file
    # that exists but does not verify *is* a fault — something is wrong with
    # the key or the file, and the buyer should know before they run real data.
    if licence.valid:
        checks.append(Check("Licence", True, f"Licensed to {licence.email}"))
    elif license_path().exists():
        checks.append(Check("Licence", False, licence.reason or "licence is invalid"))
    else:
        checks.append(Check("Licence", True, "none installed — demo mode is expected"))
    checks.append(
        Check(
            "Feature set",
            True,
            "full" if not limits.demo else "demo (row/file/format limits apply)",
        )
    )

    # Ingestion + pipeline on a real sample.
    try:
        frame = state.load_sample("messy_contacts.csv")
        checks.append(
            Check("Ingestion — CSV", not frame.empty, f"{len(frame)} rows, {len(frame.columns)} cols")
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(Check("Ingestion — CSV", False, str(exc)))
        frame = None

    result = None
    if frame is not None:
        try:
            result = run_pipeline(frame, crm="hubspot", run_structural_check=False)
            checks.append(
                Check("Pipeline — clean, map, validate", True, f"{len(result.clean_frame)} rows out")
            )
        except Exception as exc:  # noqa: BLE001
            checks.append(Check("Pipeline — clean, map, validate", False, str(exc)))

    if result is not None:
        try:
            score = profile(result.clean_frame).overall
            checks.append(Check("Profiling", True, f"overall {score}%"))
        except Exception as exc:  # noqa: BLE001
            checks.append(Check("Profiling", False, str(exc)))

        for fmt in ("csv", "json", "sql"):
            try:
                payload = to_bytes(result.clean_frame, fmt)
                checks.append(
                    Check(f"Writer — {fmt.upper()}", bool(payload.data), f"{len(payload.data):,} bytes")
                )
            except Exception as exc:  # noqa: BLE001
                checks.append(Check(f"Writer — {fmt.upper()}", False, str(exc)))
        try:
            payload = to_bytes(result.clean_frame, "excel")
            checks.append(Check("Writer — EXCEL", bool(payload.data), f"{len(payload.data):,} bytes"))
        except Exception as exc:  # noqa: BLE001
            checks.append(Check("Writer — EXCEL", False, str(exc)))

    try:
        from app_files.batch import run_batch

        checks.append(Check("Batch layer importable", callable(run_batch), ""))
    except Exception as exc:  # noqa: BLE001
        checks.append(Check("Batch layer importable", False, str(exc)))

    checks.append(
        Check(
            "Sample files present",
            len(state.available_samples()) > 0,
            f"{len(state.available_samples())} sample(s)",
        )
    )
    return checks


@ui.page("/verify")
def verify_page() -> None:
    theme.inject_theme()

    with page_shell(NAV, active="/verify"):
        c.page_header("Verify installation", "Checks the install end to end.")
        table = ui.column().classes("w-full gap-2")

        def refresh() -> None:
            table.clear()
            results = run_checks()
            with table:
                for check in results:
                    with ui.row().classes("items-center gap-3 w-full"):
                        ui.icon("check_circle" if check.passed else "error").style(
                            f"color:{theme.TEAL if check.passed else theme.DANGER}"
                        )
                        ui.label(check.name).classes("font-medium w-72")
                        ui.label(check.detail).classes("text-sm").style(f"color:{theme.SLATE}")
                passed = sum(1 for check in results if check.passed)
                if passed == len(results):
                    ui.notify(f"All {passed} checks passed.", type="positive")
                else:
                    ui.notify(
                        f"{passed} of {len(results)} checks passed.", type="warning"
                    )

        theme.button("Run checks", on_click=refresh).mark(
            "run-verify"
        )
        refresh()