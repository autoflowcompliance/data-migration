"""Additional API routes for the layers the original five did not expose.

The existing endpoints (``/health``, ``/validate``, ``/clean``, ``/profile``,
``/reconcile``) call the same pipeline the CLI and UI call. These routes
follow that rule: each one is a thin adapter over an existing layer, with no
second implementation of anything.

    POST /map        suggest a mapping for an uploaded file
    POST /mask       detect and mask PII in an uploaded file
    POST /lineage    return the lineage events for a run
    POST /quality    judge an uploaded file against a quality SLA
    GET  /audit      read the immutable audit log
    POST /schedule   compute the next fire times for a cron expression

Registration is a separate function so ``distribution/api.py`` stays as it was
and the app can opt into these routes. That keeps the original five endpoints
byte-identical for any existing consumer.
"""

from __future__ import annotations

import json
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app_files.distribution.api import (
    BadRequest,
    _form_value,
    _frame_from_bytes,
    _read_upload,
)
from app_files.governance import AccessDenied, Permission, Principal, Role, require
from app_files.mappers import load_mapping_config, suggest_mapping
from app_files.mappers.learning import MappingMemory


async def map_endpoint(request: Request) -> JSONResponse:
    """Suggest a mapping for the uploaded file's schema.

    Reads the learned-mapping store when ``AUTOFLOW_HOME`` is set, so a file
    whose shape has been seen before comes back pre-filled at full confidence.
    """
    form = await request.form()
    data, filename = await _read_upload(request)
    crm = _form_value(form, "crm", "hubspot")
    frame = _frame_from_bytes(data, filename)
    try:
        config = load_mapping_config(crm)
    except Exception as exc:  # noqa: BLE001
        raise BadRequest(f"Unknown target system {crm!r}: {exc}") from exc

    memory = MappingMemory()
    suggestion = suggest_mapping(frame, config, memory)
    learned = memory.for_frame(frame)
    return JSONResponse(
        {
            "status": "ok",
            "crm": config.crm,
            "fingerprint": suggestion.fingerprint,
            "learned": suggestion.is_learned,
            "mean_confidence": suggestion.mean_confidence,
            "times_seen": learned.times_seen if learned else 0,
            "source_columns": [str(column) for column in frame.columns],
            "fields": [field.as_dict() for field in suggestion.fields],
        }
    )


async def mask_endpoint(request: Request) -> JSONResponse:
    """Detect PII in the uploaded file and return a masked copy.

    Detection and masking are the existing privacy layer's functions; this only
    adapts the upload to a frame and the result back to JSON.
    """
    form = await request.form()
    data, filename = await _read_upload(request)
    frame = _frame_from_bytes(data, filename)
    from app_files.privacy import (
        FieldRule,
        PrivacyConfig,
        detect_frame,
        mask_frame,
    )

    requested = _form_value(form, "fields", "").strip()
    columns = [name.strip() for name in requested.split(",") if name.strip()]
    if not columns:
        columns = [str(column) for column in frame.columns]
    strategy = _form_value(form, "strategy", "redact")
    config = PrivacyConfig(
        enabled=True,
        fields=[FieldRule(column=name, strategy=strategy) for name in columns],
    )

    report = detect_frame(frame, config, columns=columns)
    result = mask_frame(frame, config, columns=columns)
    return JSONResponse(
        {
            "status": "ok",
            "rows": int(len(result.frame)),
            "columns": [str(column) for column in result.frame.columns],
            "detections": int(report.total),
            "masked_values": int(result.total_masked),
            "columns_with_pii": list(report.columns_with_pii),
            "by_kind": {str(k): int(v) for k, v in report.kind_counts().items()},
            "by_strategy": {str(k): int(v) for k, v in result.strategy_counts.items()},
            "data": [
                {str(k): _safe(v) for k, v in row.items()}
                for row in result.frame.to_dict(orient="records")
            ],
        }
    )


def _safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


async def lineage_endpoint(request: Request) -> JSONResponse:
    """Return the lineage events for a run over the uploaded file."""
    form = await request.form()
    data, filename = await _read_upload(request)
    crm = _form_value(form, "crm", "hubspot")
    frame = _frame_from_bytes(data, filename)

    from app_files.lineage import LineageTracker
    from app_files.pipeline import run_pipeline

    tracker = LineageTracker()
    run_pipeline(frame, crm=crm, lineage_tracker=tracker, source_filename=filename)
    events = tracker.to_frame()
    return JSONResponse(
        {
            "status": "ok",
            "events": int(tracker.total_events),
            "columns": [str(column) for column in events.columns],
            "data": json.loads(events.to_json(orient="records")) if len(events) else [],
        }
    )


async def audit_endpoint(request: Request) -> JSONResponse:
    """Read the immutable audit log. Read-only: writing is not an API action."""
    from app_files.collaboration.audit_trail import read_log

    limit = int(request.query_params.get("limit", "100"))
    entries = read_log()
    recent = entries[-limit:] if limit > 0 else entries
    return JSONResponse(
        {
            "status": "ok",
            "entries": len(recent),
            "total": len(entries),
            "data": recent,
        }
    )


async def schedule_endpoint(request: Request) -> JSONResponse:
    """Compute the next fire times for a cron expression without waiting."""
    from datetime import datetime, timezone

    from app_files.batch.orchestration import CronSchedule

    expression = request.query_params.get("expression", "").strip()
    if not expression:
        raise BadRequest("Pass ?expression=*/15+*+*+*+*")
    count = int(request.query_params.get("count", "5"))
    try:
        schedule = CronSchedule(expression)
    except ValueError as exc:
        raise BadRequest(str(exc)) from exc
    upcoming = schedule.upcoming(count, datetime.now(timezone.utc))
    return JSONResponse(
        {
            "status": "ok",
            "expression": expression,
            "count": len(upcoming),
            "next": [moment.isoformat() for moment in upcoming],
        }
    )


async def metrics_endpoint(request: Request) -> Response:
    """Prometheus exposition. Text, not JSON: that is what a scraper expects."""
    from app_files.observability import render_prometheus

    return Response(
        render_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


async def ready_endpoint(request: Request) -> JSONResponse:
    """Readiness: can this process serve traffic right now?"""
    from app_files.observability import readiness

    report = readiness()
    return JSONResponse(report.as_dict(), status_code=report.http_status)


async def live_endpoint(request: Request) -> JSONResponse:
    """Liveness: deliberately dependency-free, so a restart loop cannot start."""
    from app_files.observability import liveness

    report = liveness()
    return JSONResponse(report.as_dict(), status_code=report.http_status)


def _principal_from_request(request: Request) -> Principal:
    """Read the caller's role and scope from headers.

    The header carries a declared role, not a credential: authentication is the
    deployment's job and lands here as an authenticated principal. The point of
    this route is that authorization is enforced once, centrally, rather than
    being re-implemented per endpoint.
    """
    role = request.headers.get("X-DataFlow-Role", "viewer")
    scope = request.headers.get("X-DataFlow-Scope", "")
    name = request.headers.get("X-DataFlow-User", "")
    unknown = False
    try:
        parsed = Role(str(role).lower())
    except ValueError:
        parsed = Role.VIEWER
        unknown = True
    return Principal(name=name, role=parsed, scope=scope, authenticated=not unknown)


async def users_endpoint(request: Request) -> JSONResponse:
    """An admin-only read. A viewer gets 403, not an empty list."""
    principal = _principal_from_request(request)
    try:
        require(principal, Permission.MANAGE_USERS)
    except AccessDenied as exc:
        return JSONResponse({"status": "denied", "error": str(exc)}, status_code=403)
    return JSONResponse(
        {
            "status": "ok",
            "caller": {"name": principal.name, "role": principal.role.value},
            "roles": [role.value for role in Role],
        }
    )


async def tenants_endpoint(request: Request) -> JSONResponse:
    """List tenants and their disk usage. Admin-only, like every tenant action."""
    from app_files.tenancy import TenantRegistry

    principal = _principal_from_request(request)
    try:
        require(principal, Permission.MANAGE_TENANTS)
    except AccessDenied as exc:
        return JSONResponse({"status": "denied", "error": str(exc)}, status_code=403)

    registry = TenantRegistry()
    tenants = registry.list()
    include_usage = request.query_params.get("usage", "").lower() in {"1", "true", "yes"}
    return JSONResponse(
        {
            "status": "ok",
            "count": len(tenants),
            "tenants": [
                {**tenant.as_dict(), **({"usage": tenant.usage()} if include_usage else {})}
                for tenant in tenants
            ],
        }
    )


async def backup_endpoint(request: Request) -> JSONResponse:
    """Create a tenant backup, or verify an existing one.

    ``?action=create`` writes a new archive; ``?action=verify`` checks a named
    archive against its embedded manifest. A create is the only mutating admin
    action here, and it is gated the same way.
    """
    from app_files.tenancy import BackupError, TenantRegistry, create_backup, verify_backup

    principal = _principal_from_request(request)
    try:
        require(principal, Permission.MANAGE_TENANTS)
    except AccessDenied as exc:
        return JSONResponse({"status": "denied", "error": str(exc)}, status_code=403)

    action = request.query_params.get("action", "create").lower()
    registry = TenantRegistry()
    if action == "create":
        tenant_id = request.query_params.get("tenant", "").strip()
        if not tenant_id:
            raise BadRequest("Pass ?tenant=<id>")
        tenant = registry.get(tenant_id)
        backup = create_backup(tenant)
        return JSONResponse({"status": "ok", **backup.as_dict()})
    if action == "verify":
        path = request.query_params.get("path", "").strip()
        if not path:
            raise BadRequest("Pass ?path=<archive>")
        try:
            manifest = verify_backup(path)
        except BackupError as exc:
            return JSONResponse({"status": "invalid", "error": str(exc)}, status_code=409)
        return JSONResponse(
            {"status": "ok", "tenant": manifest.tenant,
             "files": manifest.file_count, "created_at": manifest.created_at}
        )
    raise BadRequest(f"Unknown action {action!r}. Use create or verify.")


def _as_number(value: Any) -> Any:
    """Turn a form value into a number, leaving anything else untouched.

    Form fields arrive as strings, so ``sla_completeness=0.5`` is the text
    ``"0.5"``. Without this the SLA would refuse every floor a caller sent and
    report a type error instead of a verdict. A value that is not numeric is
    passed through so the SLA raises the specific complaint (ambiguous, out of
    range) rather than a generic one.
    """
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    try:
        text = str(value).strip()
        if text.lower() in {"true", "false"}:
            return value
        number = float(text)
    except (TypeError, ValueError):
        return value
    return int(number) if number.is_integer() and "." not in text else number


async def quality_endpoint(request: Request) -> JSONResponse:
    """Judge an uploaded file against a quality SLA.

    The five scores are the existing Layer 5 ``profile``; the floors come from
    the request so a caller can check a file without a config file on disk. An
    upload with no floors declared has nothing to enforce and passes, which is
    the same answer the CLI gives for a config with no ``quality:`` block.
    """
    form = await request.form()
    data, filename = await _read_upload(request)
    frame = _frame_from_bytes(data, filename)

    from app_files.core import ConfigError
    from app_files.profiling import profile
    from app_files.quality import Action, QualitySLA, evaluate_sla

    block: dict[str, Any] = {}
    floors = {
        name: _form_value(form, f"sla_{name}", None)
        for name in ("completeness", "uniqueness", "validity", "consistency", "timeliness")
    }
    declared = {
        name: _as_number(value) for name, value in floors.items() if value is not None
    }
    if declared:
        block["sla"] = declared

    action = _form_value(form, "regression_action", None)
    threshold = _form_value(form, "regression_threshold", None)
    regression: dict[str, Any] = {}
    if action is not None:
        regression["action"] = action
    if threshold is not None:
        regression["threshold"] = _as_number(threshold)
    if regression:
        block["regression"] = regression

    try:
        sla = QualitySLA.from_block(block.get("sla") or {})
        resolved_action = Action.parse(regression.get("action", Action.default().value))
    except ConfigError as exc:
        raise BadRequest(str(exc)) from exc

    result = profile(frame)
    verdict = evaluate_sla(result, sla)
    return JSONResponse(
        {
            "status": "ok",
            "passed": verdict.passed,
            "scores": {name: round(float(value), 1) for name, value in result.scores.items()},
            "overall": round(float(result.overall), 1),
            "sla_declared": sla.as_dict(),
            "breaches": verdict.summary()["breaches"],
            "skipped": verdict.skipped,
            "action": resolved_action.value,
        }
    )


def register_extra_routes(app: Any) -> Any:
    """Add the extra routes to an existing Starlette app. Idempotent."""
    from starlette.routing import Route

    existing = {
        getattr(route, "path", None) for route in getattr(app, "routes", [])
    }
    additions = [
        Route("/map", map_endpoint, methods=["POST"]),
        Route("/quality", quality_endpoint, methods=["POST"]),
        Route("/mask", mask_endpoint, methods=["POST"]),
        Route("/lineage", lineage_endpoint, methods=["POST"]),
        Route("/audit", audit_endpoint, methods=["GET"]),
        Route("/schedule", schedule_endpoint, methods=["GET"]),
        Route("/metrics", metrics_endpoint, methods=["GET"]),
        Route("/ready", ready_endpoint, methods=["GET"]),
        Route("/live", live_endpoint, methods=["GET"]),
        Route("/users", users_endpoint, methods=["GET"]),
        Route("/tenants", tenants_endpoint, methods=["GET"]),
        Route("/backup", backup_endpoint, methods=["POST"]),
    ]
    for route in additions:
        if route.path not in existing:
            app.routes.append(route)
    return app
