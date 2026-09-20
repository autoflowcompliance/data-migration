"""Shareable report: one self-contained HTML file you can email or attach.

The pipeline already renders a QA report. What it cannot do is be handed to
someone else safely: it may reference an external stylesheet, it has no record of
which data it describes, and it does not include the comparison or the fix
summary.

``build_shareable_report(result, comparison, summary)`` produces a single file
with everything inlined — styles as a ``<style>`` block, data as embedded HTML
tables, no scripts and no remote URLs — plus a provenance block naming the source
file, the config and the tool version. That block is what makes an emailed
report defensible: the recipient can see exactly which run produced it.

``has_external_references`` inspects the output and reports any absolute URL, so
the claim "this file needs no internet" is checkable rather than asserted.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

TOOL_VERSION = "1.0"

_URL_PATTERN = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.I)


@dataclass
class Provenance:
    """Where a report came from."""

    source_filename: str = ""
    project_name: str = ""
    crm: str = ""
    rows_in: int = 0
    rows_out: int = 0
    quality_score: float = 0.0
    generated_at: str = ""
    tool_version: str = TOOL_VERSION
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "source_filename": self.source_filename,
            "project_name": self.project_name,
            "crm": self.crm,
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "quality_score": round(self.quality_score, 1),
            "generated_at": self.generated_at,
            "tool_version": self.tool_version,
        }
        payload.update(self.extra)
        return payload


_STYLE = """
:root{color-scheme:light;}
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;
     background:#f9fafb;color:#111827;}
.wrap{max-width:1150px;margin:0 auto;padding:28px;}
h1{font-size:23px;margin:0 0 4px;}
h2{font-size:15px;margin:28px 0 10px;text-transform:uppercase;letter-spacing:.05em;color:#6b7280;}
.prov{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 18px;
      font-size:13px;display:flex;gap:26px;flex-wrap:wrap;margin:14px 0 6px;}
.prov div span{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.04em;
      color:#6b7280;}
.hero{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:18px 20px;
      font-size:14px;line-height:1.6;}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;
      border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;margin-bottom:8px;}
th,td{border-bottom:1px solid #eef0f3;padding:6px 8px;text-align:left;vertical-align:top;}
th{background:#f3f4f6;font-weight:600;}
tr.removed td{background:#fee2e2;color:#7f1d1d;}
td.changed{background:#fef3c7;font-weight:600;}
.foot{margin-top:24px;font-size:12px;color:#6b7280;}
.report{margin-top:8px;}
.report-embed{border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;background:#fff;}
"""


def render_shareable_report(
    title: str = "Data migration report",
    provenance: Provenance | None = None,
    summary_paragraph: str = "",
    qa_report_html: str = "",
    comparison_html: str = "",
    cleaned: pd.DataFrame | None = None,
    issues: pd.DataFrame | None = None,
    row_limit: int = 300,
) -> str:
    """Build the single self-contained HTML file.

    Any HTML passed in is reduced to its ``<body>`` so that nested reports do not
    drag their own ``<head>``, scripts or stylesheets along — which is how an
    externally-hosted asset would otherwise leak in.
    """
    provenance = provenance or Provenance()
    if not provenance.generated_at:
        provenance.generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    blocks: list[str] = []

    if summary_paragraph:
        blocks.append(
            "<h2>What was fixed</h2>"
            f"<div class='hero'>{html.escape(summary_paragraph)}</div>"
        )

    if provenance.quality_score:
        blocks.append(
            "<h2>Quality score</h2>"
            f"<div class='hero'><strong style='font-size:30px;'>{provenance.quality_score:.0f}%</strong> "
            f"of {provenance.rows_out} output rows from {provenance.rows_in} input rows</div>"
        )

    if comparison_html:
        blocks.append("<h2>Before and after</h2>" + _body_of(comparison_html))

    if qa_report_html:
        blocks.append("<h2>Quality assurance report</h2>" + _body_of(qa_report_html))

    if cleaned is not None and not cleaned.empty:
        blocks.append("<h2>Cleaned data</h2>" + _frame_table(cleaned, row_limit, "Cleaned data"))

    if issues is not None and not issues.empty:
        blocks.append("<h2>Issues</h2>" + _frame_table(issues, row_limit, "Issues"))

    provenance_cells = "".join(
        f"<div><span>{html.escape(str(key).replace('_', ' '))}</span>{html.escape(str(value))}</div>"
        for key, value in provenance.as_dict().items()
    )

    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{html.escape(title)}</title><style>{_STYLE}</style></head><body><div class='wrap'>"
        f"<h1>{html.escape(title)}</h1>"
        f"<p class='foot'>A single file. No internet connection, scripts or "
        f"additional downloads are needed to read it.</p>"
        f"<div class='prov'>{provenance_cells}</div>"
        + "".join(blocks)
        + "<p class='foot'>Produced by AutoFlow. This report describes the exact run "
        "named above; a different run may produce different numbers.</p>"
        "</div></body></html>"
    )


def _body_of(fragment: str) -> str:
    """Strip everything outside ``<body>``, dropping head-level assets."""
    match = re.search(r"<body[^>]*>(.*)</body>", fragment, re.I | re.S)
    inner = match.group(1) if match else fragment
    inner = re.sub(r"<script.*?</script>", "", inner, flags=re.I | re.S)
    inner = re.sub(r"<link[^>]*>", "", inner, flags=re.I)
    inner = re.sub(r"<style.*?</style>", "", inner, flags=re.I | re.S)
    return f"<div class='report-embed'>{inner}</div>"


def _frame_table(frame: pd.DataFrame, limit: int, label: str) -> str:
    shown = frame.head(limit)
    header = "".join(f"<th>{html.escape(str(c))}</th>" for c in shown.columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>"
        for row in shown.itertuples(index=False)
    )
    note = (
        f"<p class='foot'>Showing {len(shown)} of {len(frame)} {label.lower()} rows.</p>"
        if len(frame) > limit else ""
    )
    return f"<table><tr>{header}</tr>{body}</table>{note}"


def external_references(html_text: str) -> list[str]:
    """Absolute URLs the file would fetch: the check behind "works offline"."""
    found = []
    for url in _URL_PATTERN.findall(html_text):
        lowered = url.strip().lower()
        if lowered.startswith(("http://", "https://", "//")):
            found.append(url)
    return sorted(set(found))


def has_external_references(html_text: str) -> bool:
    return bool(external_references(html_text))


def write_shareable_report(path: str | Path, **kwargs: Any) -> Path:
    target = Path(path)
    if target.suffix.lower() not in {".html", ".htm"}:
        target = target.with_suffix(".html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_shareable_report(**kwargs), encoding="utf-8")
    return target


def build_from_result(
    result: Any,
    comparison_html: str = "",
    summary_paragraph: str = "",
    source_filename: str = "",
    project_name: str = "",
    crm: str = "",
    issues: pd.DataFrame | None = None,
    title: str = "Data migration report",
) -> str:
    """Assemble a shareable report straight from a ``PipelineResult``."""
    summary = result.summary() if hasattr(result, "summary") else {}
    provenance = Provenance(
        source_filename=source_filename,
        project_name=project_name,
        crm=crm or getattr(getattr(result, "mapping_config", None), "crm", ""),
        rows_in=int(summary.get("rows_in", 0)),
        rows_out=int(summary.get("rows_out", 0)),
        quality_score=float(summary.get("quality_score", 0.0)),
    )
    if issues is None:
        try:
            issues = result.validation.issues_frame()
        except Exception:  # noqa: BLE001
            issues = None
    return render_shareable_report(
        title=title,
        provenance=provenance,
        summary_paragraph=summary_paragraph,
        qa_report_html=getattr(result, "qa_report_html", "") or "",
        comparison_html=comparison_html,
        cleaned=result.clean_frame,
        issues=issues,
    )