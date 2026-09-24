"""The admin console: one place that answers "what is this install doing".

An operator running this for a team needs to see, without reading logs:

* **runs** — recent pipeline runs, from the same trend log the metrics endpoint
  reads, so the console and Prometheus cannot disagree;
* **tenants** — every tenant this install knows, and how many audit entries each
  one holds, so a noisy or idle tenant is visible;
* **plugins and formats** — what output formats are registered;
* **connectors** — which providers have credentials, and which are missing;
* **health** — the same liveness/readiness checks the health endpoint reports.

It is deliberately render-only and read-only: the console presents state, it
does not change it. Actions go through the routes that own them (settings,
templates), so an operator privilege is not smuggled in through a dashboard.

The output is a JSON document plus an HTML page rendered from it, so the same
data drives an API consumer and a human.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app_files.observability import full_health, read_trend, summarise_trend


@dataclass
class AdminSnapshot:
    runs: list[dict[str, Any]] = field(default_factory=list)
    trend: dict[str, Any] = field(default_factory=dict)
    tenants: list[dict[str, Any]] = field(default_factory=list)
    formats: dict[str, Any] = field(default_factory=dict)
    connectors: list[dict[str, Any]] = field(default_factory=list)
    health: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "runs": list(self.runs),
            "trend": dict(self.trend),
            "tenants": list(self.tenants),
            "formats": dict(self.formats),
            "connectors": list(self.connectors),
            "health": dict(self.health),
        }


def _tenant_rows() -> list[dict[str, Any]]:
    from app_files.platform.tenancy import list_tenants, read_audit, tenants_dir

    rows: list[dict[str, Any]] = []
    for name in list_tenants():
        audit = tenants_dir() / name / "audit" / "audit.jsonl"
        rows.append(
            {
                "id": name,
                "audit_entries": len(read_audit(audit)),
                "created": audit.exists(),
            }
        )
    return rows


def snapshot(*, tenant: str = "", limit: int = 20) -> AdminSnapshot:
    """Collect the console's state. Read-only; never raises for missing state."""
    entries = read_trend(tenant)
    recent = list(reversed(entries))[: max(1, limit)]

    from app_files.output import FORMATS, available_formats, plugin_report

    try:
        from app_files.distribution.connectors import credential_report

        connectors = credential_report()
    except Exception as exc:  # noqa: BLE001 - the console must still render
        connectors = [{"provider": "unavailable", "detail": str(exc)}]

    health = full_health()

    return AdminSnapshot(
        runs=recent,
        trend=summarise_trend(entries).as_dict(),
        tenants=_tenant_rows(),
        formats={
            "builtin": sorted(FORMATS),
            "plugins": plugin_report(),
            "available": available_formats(),
        },
        connectors=connectors,
        health=health,
    )


def render_admin_html(state: AdminSnapshot) -> str:
    """Render the snapshot as a single self-contained page."""
    from html import escape

    def rows(items: list[dict[str, Any]], columns: list[str]) -> str:
        if not items:
            return "<tr><td colspan='{0}'>Nothing yet.</td></tr>".format(len(columns))
        body = []
        for item in items:
            cells = "".join(
                f"<td>{escape(str(item.get(column, '')))}</td>" for column in columns
            )
            body.append(f"<tr>{cells}</tr>")
        return "".join(body)

    runs = [
        {
            "config": entry.get("config", ""),
            "rows": entry.get("rows_out", entry.get("rows", "")),
            "quality": entry.get("quality_score", ""),
            "when": entry.get("timestamp", entry.get("recorded_at", "")),
        }
        for entry in state.runs
    ]
    ready = "yes" if state.health.get("ok") else "no"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Admin console</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #20242b; }}
 h1 {{ font-size: 1.4rem; }}
 h2 {{ font-size: 1.05rem; margin-top: 2rem; }}
 table {{ border-collapse: collapse; width: 100%; }}
 th, td {{ text-align: left; padding: .35rem .5rem; border-bottom: 1px solid #e6e1d7; }}
 th {{ font-weight: 600; color: #6b6459; }}
</style></head>
<body>
<h1>Admin console</h1>
<p>Ready: <strong>{ready}</strong></p>
<h2>Recent runs</h2>
<table><tr><th>Config</th><th>Rows</th><th>Quality</th><th>When</th></tr>
{rows(runs, ["config", "rows", "quality", "when"])}</table>
<h2>Tenants</h2>
<table><tr><th>Tenant</th><th>Audit entries</th></tr>
{rows(state.tenants, ["id", "audit_entries"])}</table>
<h2>Connectors</h2>
<table><tr><th>Provider</th><th>Ready</th><th>Missing</th></tr>
{rows(
    [
        {
            "provider": c.get("provider", ""),
            "ready": c.get("ready", ""),
            "missing": ", ".join(c.get("missing", [])) if isinstance(c.get("missing"), list) else c.get("missing", ""),
        }
        for c in state.connectors
    ],
    ["provider", "ready", "missing"],
)}</table>
<h2>Output formats</h2>
<p>{escape(', '.join(state.formats.get('available', [])))}</p>
</body></html>"""


def write_admin_snapshot(state: AdminSnapshot, path: str) -> str:
    """Write the rendered console to ``path`` and return the path."""
    from pathlib import Path

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_admin_html(state), encoding="utf-8")
    return str(target)