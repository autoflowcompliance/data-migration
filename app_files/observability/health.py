"""Liveness and readiness for orchestration platforms.

The distinction matters to a restart loop. Liveness answers "is this process
alive" and should stay green even when a dependency is down, because restarting
the process will not fix Postgres. Readiness answers "can this process serve
traffic" and should go red when something it needs is unavailable, so the
platform stops routing to it without killing it.

Checks are functions that return a :class:`CheckResult`. They are passed in
rather than imported, so this module does not know or care what the
dependencies are.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pandas as pd


class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class CheckResult:
    """Outcome of one dependency check."""

    name: str
    healthy: bool
    detail: str = ""
    required: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "healthy": self.healthy,
            "detail": self.detail,
            "required": self.required,
        }


Check = Callable[[], "CheckResult | bool | str"]


def _coerce(name: str, produced: CheckResult | bool | str, required: bool) -> CheckResult:
    if isinstance(produced, CheckResult):
        return produced
    if isinstance(produced, bool):
        return CheckResult(name, produced, required=required)
    return CheckResult(name, False, str(produced), required=required)


CheckSpec = tuple[str, Check] | tuple[str, Check, bool]


def run_checks(checks: Iterable[CheckSpec]) -> list[CheckResult]:
    """Run each check, turning an exception into an unhealthy result.

    A check that raises is a failed check, not a failed health endpoint: the
    whole point is to report the failure, so the failure must not propagate.
    """
    results: list[CheckResult] = []
    for item in checks:
        name, check = item[0], item[1]
        required = item[2] if len(item) > 2 else True
        try:
            produced = check()
        except Exception as exc:  # noqa: BLE001 - a failing check is the report
            produced = f"{type(exc).__name__}: {exc}"
        results.append(_coerce(name, produced, required))
    return results


@dataclass
class HealthReport:
    """A liveness or readiness verdict, with the evidence behind it."""

    status: HealthStatus
    checks: list[CheckResult] = field(default_factory=list)
    kind: str = "readiness"

    @property
    def healthy(self) -> bool:
        return self.status is not HealthStatus.UNHEALTHY

    @property
    def http_status(self) -> int:
        return 200 if self.healthy else 503

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "kind": self.kind,
            "checks": [check.as_dict() for check in self.checks],
        }

    def render(self) -> str:
        lines = [f"{self.kind}: {self.status.value}"]
        for check in self.checks:
            marker = "ok" if check.healthy else "FAIL"
            requirement = "" if check.required else " (optional)"
            lines.append(f"  [{marker}] {check.name}{requirement} {check.detail}".rstrip())
        return "\n".join(lines)


def _status_from(results: list[CheckResult]) -> HealthStatus:
    if any(not check.healthy and check.required for check in results):
        return HealthStatus.UNHEALTHY
    if any(not check.healthy for check in results):
        return HealthStatus.DEGRADED
    return HealthStatus.OK


def liveness() -> HealthReport:
    """The process is running. Deliberately dependency-free.

    A liveness probe that fails when a database is down causes a restart loop
    that cannot help. This only asserts the interpreter is executing code.
    """
    return HealthReport(HealthStatus.OK, [CheckResult("process", True)], kind="liveness")


def readiness(
    checks: Iterable[CheckSpec] = (),
    extra: Iterable[CheckSpec] = (),
) -> HealthReport:
    """Can the process serve traffic? Fails when a required dependency is down."""
    all_checks: list[CheckSpec] = [("builtin", _builtins)]
    all_checks.extend(checks)
    all_checks.extend(extra)
    results = run_checks(all_checks)
    return HealthReport(_status_from(results), results, kind="readiness")


def _builtins() -> CheckResult:
    """The one dependency every run has: pandas can build a frame."""
    frame = pd.DataFrame({"ok": [1]})
    return CheckResult("pandas", bool(frame.shape == (1, 1)), "frame construction")


__all__ = [
    "Check",
    "CheckResult",
    "HealthReport",
    "HealthStatus",
    "liveness",
    "readiness",
    "run_checks",
]
