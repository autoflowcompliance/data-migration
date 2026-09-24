"""Layer 15 — observability.

Three things an operator needs and the tool did not have: numbers they can
scrape, alerts when a run goes wrong, and a readiness signal that reflects the
dependencies rather than just "the process is up".

Nothing here reaches into the pipeline. Each piece is fed by the caller, so an
existing run keeps working whether or not anyone observes it.
"""

from __future__ import annotations

from app_files.observability.alerting import (
    CONDITIONS,
    DURATION_BREACH,
    FAILURE,
    QUALITY_DROP,
    SLA_BREACH,
    Alert,
    AlertChannel,
    AlertRule,
    AlertSeverity,
    AlertSink,
    EmailChannel,
    SlackChannel,
    TeamsChannel,
    WebhookChannel,
    build_alert,
    evaluate_alerts,
    notify_alert,
)
from app_files.observability.health import (
    Check,
    CheckResult,
    HealthReport,
    HealthStatus,
    liveness,
    readiness,
    run_checks,
)
from app_files.observability.metrics import (
    QUALITY_SCORE,
    ROWS_PROCESSED,
    RUN_DURATION_SECONDS,
    RUN_FAILURES_TOTAL,
    RUNS_TOTAL,
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
    default_registry,
    record_run,
    render_prometheus,
)

__all__ = [
    "CONDITIONS",
    "DURATION_BREACH",
    "FAILURE",
    "QUALITY_DROP",
    "QUALITY_SCORE",
    "ROWS_PROCESSED",
    "RUNS_TOTAL",
    "RUN_DURATION_SECONDS",
    "RUN_FAILURES_TOTAL",
    "SLA_BREACH",
    "Alert",
    "AlertChannel",
    "AlertRule",
    "AlertSeverity",
    "AlertSink",
    "Check",
    "CheckResult",
    "Counter",
    "EmailChannel",
    "Gauge",
    "HealthReport",
    "HealthStatus",
    "Histogram",
    "MetricsRegistry",
    "SlackChannel",
    "TeamsChannel",
    "WebhookChannel",
    "build_alert",
    "default_registry",
    "evaluate_alerts",
    "liveness",
    "notify_alert",
    "readiness",
    "record_run",
    "render_prometheus",
    "run_checks",
]
