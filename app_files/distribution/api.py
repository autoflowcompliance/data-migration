"""REST API for the tool.

Five endpoints, all of which do real work by calling the same pipeline the CLI
and the UI call. There is no second implementation of cleaning or validation
behind this API.

    GET  /health      status and version
    POST /validate    run the rules and report pass/fail per rule
    POST /clean       run the pipeline and return the cleaned data
    POST /profile     run the pipeline and return the five quality scores
    POST /reconcile   reconcile a statement against a ledger

Uploads are ``multipart/form-data`` with a ``file`` field, so a plain
``curl -F`` works. The FastAPI app is built by ``create_app()`` so tests can
construct it directly and the same object can be served by uvicorn.
"""

from __future__ import annotations

import io
import json
from typing import Any

import pandas as pd
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from app_files.ingestion import UnsupportedFormatError, read_any
from app_files.lineage import LineageTracker
from app_files.observability import MetricsRegistry, read_trend
from app_files.pipeline import run_pipeline
from app_files.profiling import profile

VERSION = "1.0"


class BadRequest(Exception):
    """Raised for a request the API cannot act on; rendered as HTTP 400."""


async def _read_upload(request: Request, field: str = "file") -> tuple[bytes, str]:
    """Pull one uploaded file out of a multipart request."""
    form = await request.form()
    upload = form.get(field)
    if upload is None:
        keys = ", ".join(form.keys()) or "(none)"
        raise BadRequest(f"No '{field}' upload found. Form fields received: {keys}")
    if isinstance(upload, str):
        raise BadRequest(f"'{field}' must be a file upload, not a text field.")
    data = await upload.read()
    if not data:
        raise BadRequest(f"The uploaded file '{upload.filename}' is empty.")
    return data, upload.filename or "upload.csv"


def _frame_from_bytes(data: bytes, filename: str) -> pd.DataFrame:
    try:
        return read_any(data, filename=filename)
    except UnsupportedFormatError as exc:
        raise BadRequest(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surfaced as 400, not a 500 traceback
        raise BadRequest(f"Could not read '{filename}': {type(exc).__name__}: {exc}") from exc


def _form_value(form: Any, key: str, default: str) -> str:
    value = form.get(key, default)
    return value if isinstance(value, str) else default


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, float) and value != value:
        return None
    return str(value)


# --------------------------------------------------------------------- routes
async def health(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "version": VERSION,
            "configs": _configs(),
            "formats": ["csv", "excel", "json", "sql"],
        }
    )


async def health_deep(request: Request) -> JSONResponse:
    """Full health: liveness plus readiness (configs load, output writable)."""
    from app_files.observability import full_health

    report = full_health()
    return JSONResponse(report, status_code=200 if report["ok"] else 503)


async def metrics(request: Request) -> Response:
    """Prometheus text exposition for a scrape."""
    registry = MetricsRegistry()
    for entry in read_trend():
        registry.record_run(
            status="succeeded",
            quality=float(entry.get("quality_score", 0.0)),
            rows=int(entry.get("rows_out", 0)),
            config=str(entry.get("config", "")),
        )
    return Response(registry.render(), media_type="text/plain; version=0.0.4")


async def connectors_endpoint(request: Request) -> JSONResponse:
    """Every connector, with which ones have credentials configured."""
    from app_files.distribution.connectors import credential_report

    return JSONResponse({"connectors": credential_report()})


async def formats_endpoint(request: Request) -> JSONResponse:
    """Output formats: the built-ins plus any registered plugins."""
    from app_files.output import FORMATS, available_formats, plugin_report

    return JSONResponse(
        {
            "builtin": sorted(FORMATS),
            "plugins": plugin_report(),
            "available": available_formats(),
        }
    )


async def privacy_endpoint(request: Request) -> JSONResponse:
    """Detect personal data in an uploaded file, and optionally mask it."""
    form = await request.form()
    data, filename = await _read_upload(request)
    frame = _frame_from_bytes(data, filename)

    from app_files.privacy import MaskPlan, detect_personal_data, mask_personal_data

    report = detect_personal_data(frame)
    payload: dict[str, Any] = {"report": report.as_dict()}

    mask_raw = _form_value(form, "mask", "")
    if mask_raw:
        # ``mask`` is a JSON object: {"modes": {...}, "columns": {...}}.
        try:
            plan_data = json.loads(mask_raw)
        except json.JSONDecodeError as exc:
            raise BadRequest(f"'mask' is not valid JSON: {exc}") from exc
        plan = MaskPlan(
            modes=plan_data.get("modes", {}), columns=plan_data.get("columns", {})
        )
        result = mask_personal_data(frame, report, plan)
        payload["masked"] = result.as_dict()
        payload["masked_rows"] = len(result.frame)
    return JSONResponse(payload)


async def compliance_endpoint(request: Request) -> JSONResponse:
    """The compliance posture this install can actually verify."""
    from app_files.platform import assess_compliance

    return JSONResponse(assess_compliance().as_dict())


async def admin_endpoint(request: Request) -> JSONResponse:
    """The read-only admin snapshot: runs, tenants, connectors, formats, health."""
    from app_files.admin import snapshot

    tenant = request.query_params.get("tenant", "")
    return JSONResponse(snapshot(tenant=tenant).as_dict())


async def deployment_endpoint(request: Request) -> JSONResponse:
    """Validate a named deployment profile against this environment."""
    profile = request.query_params.get("profile", "container")
    from app_files.platform.deployment import DeploymentError, validate_deployment

    try:
        report = validate_deployment(profile)
    except DeploymentError as exc:
        raise BadRequest(str(exc)) from exc
    return JSONResponse(report.as_dict())


async def dry_run_endpoint(request: Request) -> JSONResponse:
    """Describe what a run would write, without writing anything."""
    form = await request.form()
    data, filename = await _read_upload(request)
    frame = _frame_from_bytes(data, filename)
    crm = _form_value(form, "crm", "hubspot")
    output_format = _form_value(form, "format", "csv")

    from app_files.safety import dry_run

    plan = dry_run(frame, crm, output_format=output_format)
    return JSONResponse(plan.as_dict())


async def alerts_endpoint(request: Request) -> JSONResponse:
    """Evaluate the alert rules against a posted run summary."""
    body = await request.json()
    summary = body.get("summary", body) if isinstance(body, dict) else {}
    rules = _parse_alert_rules(body.get("rules")) if isinstance(body, dict) else None

    from app_files.observability import AlertRule, evaluate_alerts

    if rules is None:
        rules = [
            AlertRule(name="run-failed", kind="failure", severity="critical"),
            AlertRule(name="low-quality", kind="quality_below", threshold=80, severity="warning"),
            AlertRule(name="slow-run", kind="duration_above", threshold=120, severity="warning"),
        ]
    alerts = evaluate_alerts(rules, summary)
    return JSONResponse({"alerts": [alert.as_dict() for alert in alerts]})


def _parse_alert_rules(raw: Any) -> list[Any] | None:
    if not isinstance(raw, list):
        return None
    from app_files.observability import AlertRule

    return [
        AlertRule(
            name=str(item.get("name", "rule")),
            kind=str(item.get("kind", "failure")),
            threshold=float(item.get("threshold", 0)),
            severity=str(item.get("severity", "warning")),
            channels=list(item.get("channels", [])),
        )
        for item in raw
        if isinstance(item, dict)
    ]


def _configs() -> list[str]:
    try:
        from app_files.mappers import available_crms

        return available_crms()
    except Exception:  # noqa: BLE001
        return []


async def validate(request: Request) -> JSONResponse:
    """Run the config's rules and report pass/fail."""
    form = await request.form()
    data, filename = await _read_upload(request)
    crm = _form_value(form, "crm", "hubspot")
    frame = _frame_from_bytes(data, filename)

    tracker = LineageTracker()
    result = run_pipeline(frame, crm=crm, lineage_tracker=tracker, source_filename=filename)
    issues = result.validation.issues_frame()
    summary = result.summary()
    by_rule = {}
    if not issues.empty and "rule" in issues.columns:
        by_rule = issues["rule"].value_counts().to_dict()

    passed = int(summary.get("errors", 0)) == 0
    return JSONResponse(
        {
            "status": "pass" if passed else "fail",
            "rows": summary.get("rows_in", 0),
            "errors": summary.get("errors", 0),
            "warnings": summary.get("warnings", 0),
            "failures_by_rule": {str(k): int(v) for k, v in by_rule.items()},
            "issues": json.loads(issues.to_json(orient="records")) if not issues.empty else [],
        },
        status_code=200,
    )


async def clean(request: Request) -> JSONResponse:
    """Run the pipeline and return the cleaned rows as JSON."""
    form = await request.form()
    data, filename = await _read_upload(request)
    crm = _form_value(form, "crm", "hubspot")
    frame = _frame_from_bytes(data, filename)

    result = run_pipeline(frame, crm=crm, source_filename=filename)
    records = [
        {str(k): _json_safe(v) for k, v in row.items()}
        for row in result.clean_frame.to_dict(orient="records")
    ]
    summary = result.summary()
    return JSONResponse(
        {
            "status": "ok",
            "rows_in": summary.get("rows_in", 0),
            "rows_out": len(records),
            "duplicates_removed": summary.get("duplicates_removed", 0),
            "quality_score": summary.get("quality_score", 0.0),
            "columns": [str(c) for c in result.clean_frame.columns],
            "data": records,
        }
    )


async def profile_endpoint(request: Request) -> JSONResponse:
    """Return the five quality scores for the file as uploaded."""
    data, filename = await _read_upload(request)
    frame = _frame_from_bytes(data, filename)
    prof = profile(frame)
    return JSONResponse(
        {
            "status": "ok",
            "rows": prof.row_count,
            "columns": prof.column_count,
            "overall": round(prof.overall, 1),
            "scores": {k: round(v, 1) for k, v in prof.scores.items()},
            "applicable": sorted(prof.applicable),
            "notes": list(prof.notes),
        }
    )


async def reconcile(request: Request) -> JSONResponse:
    """Reconcile a statement against a ledger. Both are uploads.

    The service works on raw CSV bytes and needs to be told which column holds
    the date and which holds the amount, because a statement can call them
    anything. Both are accepted as form fields so the same endpoint serves a
    bank export and a hand-made ledger.
    """
    form = await request.form()
    statement_data, statement_name = await _read_upload(request, "statement")
    ledger_upload = form.get("ledger")
    if ledger_upload is None or isinstance(ledger_upload, str):
        raise BadRequest("A 'ledger' file upload is required alongside 'statement'.")
    ledger_data = await ledger_upload.read()
    ledger_name = ledger_upload.filename or "ledger.csv"

    tolerance = int(_form_value(form, "tolerance", "2"))
    bank_date = _form_value(form, "bank_date_col", "Date")
    bank_amount = _form_value(form, "bank_amount_col", "Amount")
    ledger_date = _form_value(form, "ledger_date_col", bank_date)
    ledger_amount = _form_value(form, "ledger_amount_col", bank_amount)

    from app_files.services.bank_reconciliation.reconciler import (
        UnreadableStatementError,
        run_reconciliation,
    )

    try:
        result = run_reconciliation(
            statement_data,
            ledger_data,
            bank_date_col=bank_date,
            bank_amount_col=bank_amount,
            ledger_date_col=ledger_date,
            ledger_amount_col=ledger_amount,
            date_tolerance_days=tolerance,
        )
    except UnreadableStatementError as exc:
        raise BadRequest(str(exc)) from exc
    except KeyError as exc:
        raise BadRequest(
            f"Column {exc} was not found. Pass bank_date_col / bank_amount_col "
            f"(and ledger_date_col / ledger_amount_col if they differ)."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise BadRequest(f"Could not reconcile: {type(exc).__name__}: {exc}") from exc

    summary = result.get("summary", {})
    return JSONResponse(
        {
            "status": "ok",
            "matched": summary.get("matched", len(result.get("matches", []))),
            "missing_from_books": summary.get("missing_from_books", 0),
            "never_cleared": summary.get("recorded_but_never_cleared", 0),
            "bank_transactions": summary.get("bank_transactions", 0),
            "ledger_transactions": summary.get("ledger_transactions", 0),
            "tolerance_days": tolerance,
        }
    )


async def _bad_request(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"status": "error", "error": str(exc)}, status_code=400)


async def _unsupported_format(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"status": "error", "error": str(exc)}, status_code=415)


async def _server_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        {"status": "error", "error": f"{type(exc).__name__}: {exc}"}, status_code=500
    )


def create_app() -> Starlette:
    """Build the ASGI app. Tests call this directly."""
    app = Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/health/deep", health_deep, methods=["GET"]),
            Route("/metrics", metrics, methods=["GET"]),
            Route("/connectors", connectors_endpoint, methods=["GET"]),
            Route("/formats", formats_endpoint, methods=["GET"]),
            Route("/compliance", compliance_endpoint, methods=["GET"]),
            Route("/admin", admin_endpoint, methods=["GET"]),
            Route("/deployment", deployment_endpoint, methods=["GET"]),
            Route("/validate", validate, methods=["POST"]),
            Route("/clean", clean, methods=["POST"]),
            Route("/profile", profile_endpoint, methods=["POST"]),
            Route("/privacy", privacy_endpoint, methods=["POST"]),
            Route("/reconcile", reconcile, methods=["POST"]),
            Route("/dry-run", dry_run_endpoint, methods=["POST"]),
            Route("/alerts", alerts_endpoint, methods=["POST"]),
        ],
        exception_handlers={
            BadRequest: _bad_request,
            UnsupportedFormatError: _unsupported_format,

            Exception: _server_error,
        },
    )
    return app


app = create_app()


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - server shim
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the AutoFlow REST API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8600)
    args = parser.parse_args(argv)
    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())