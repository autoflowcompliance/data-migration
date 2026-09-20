"""PDF and HTML-dashboard exports.

Two formats the frozen output layer does not have, added as new writers beside
it rather than inside it. ``write_pdf`` and ``write_html`` return a ``Path`` and
accept the same arguments as the existing writers, so they can be called in the
same loop.

PDF generation uses ``reportlab`` (pure Python, no system libraries) because the
target user is on Windows with nothing installed. A missing ``reportlab`` raises
a message naming the install command rather than an ImportError traceback. The
HTML dashboard is always available and needs nothing.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.profiling import profile
from app_files.utilities.fix_summary import FixSummary

_SHEET_LIMIT = 2000


def _require_reportlab() -> tuple[Any, Any, Any, Any]:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise RuntimeError(
            "PDF export needs the reportlab library. Install it with: pip install reportlab"
        ) from exc
    return (colors, (A4, landscape), getSampleStyleSheet, (Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle))


def write_pdf(
    frame: pd.DataFrame,
    path: str | Path,
    title: str = "Data migration report",
    summary: FixSummary | None = None,
    project_name: str = "",
    source_filename: str = "",
) -> Path:
    """Write a formatted PDF: summary, quality scores, then the data table."""
    colors, (A4, landscape), getSampleStyleSheet, (Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle) = _require_reportlab()

    target = Path(path)
    if target.suffix.lower() != ".pdf":
        target = target.with_suffix(".pdf")
    target.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    story: list[Any] = [Paragraph(html.escape(title), styles["Title"])]
    if project_name or source_filename:
        story.append(
            Paragraph(html.escape(f"{project_name} — {source_filename}".strip(" —")), styles["Normal"])
        )
    story.append(Spacer(1, 12))

    if summary is not None:
        story.append(Paragraph("What was fixed", styles["Heading2"]))
        story.append(Paragraph(html.escape(summary.paragraph()), styles["Normal"]))
        story.append(Spacer(1, 10))

    prof = profile(frame)
    story.append(Paragraph("Data quality score", styles["Heading2"]))
    score_rows = [["Dimension", "Score (out of 100)"], ["Overall", f"{prof.overall:.1f}"]]
    score_rows += [[name.title(), f"{value:.1f}"] for name, value in prof.scores.items()]
    story.append(_table(score_rows, colors, Table, TableStyle, Paragraph, styles))
    story.append(Spacer(1, 12))

    if prof.notes:
        story.append(Paragraph("Notes", styles["Heading2"]))
        for note in prof.notes:
            story.append(Paragraph("• " + html.escape(str(note)), styles["Normal"]))
        story.append(Spacer(1, 12))

    story.append(Paragraph("Cleaned data", styles["Heading2"]))
    shown = frame.head(_SHEET_LIMIT)
    data_rows = [[str(c) for c in shown.columns]] + [
        [str(value) for value in row] for row in shown.itertuples(index=False)
    ]
    story.append(_table(data_rows, colors, Table, TableStyle, Paragraph, styles))
    if len(frame) > _SHEET_LIMIT:
        story.append(
            Paragraph(
                f"Showing the first {_SHEET_LIMIT} of {len(frame)} rows. "
                "The full data is in the accompanying CSV.",
                styles["Normal"],
            )
        )

    document = SimpleDocTemplate(str(target), pagesize=landscape(A4), title=title)
    document.build(story)
    return target


def _table(rows: list[list[str]], colors, Table, TableStyle, Paragraph, styles) -> Any:
    display = [[Paragraph(html.escape(str(cell)), styles["BodyText"]) for cell in row] for row in rows]
    widths = None
    if display:
        columns = len(display[0])
        widths = [None] * columns
    table = Table(display, repeatRows=1, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


_DASHBOARD_STYLE = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;
     background:#f9fafb;color:#111827;}
.wrap{max-width:1150px;margin:0 auto;padding:28px;}
h1{font-size:22px;margin:0 0 4px;}
h2{font-size:15px;margin:28px 0 10px;text-transform:uppercase;letter-spacing:.05em;color:#6b7280;}
.lead{color:#6b7280;font-size:13px;margin:0 0 18px;}
.hero{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:20px;
      display:flex;gap:28px;align-items:center;flex-wrap:wrap;}
.big{font-size:52px;font-weight:800;line-height:1;}
.dims{display:flex;gap:14px;flex-wrap:wrap;}
.dim{min-width:120px;}
.bar{height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden;margin-top:4px;}
.bar span{display:block;height:100%;background:#2563eb;}
.dim .k{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#6b7280;}
.dim .v{font-size:15px;font-weight:700;}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;
      border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;}
th,td{border-bottom:1px solid #eef0f3;padding:6px 8px;text-align:left;}
th{background:#f3f4f6;font-weight:600;}
ul{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 14px 14px 30px;font-size:13px;}
.foot{margin-top:22px;font-size:12px;color:#6b7280;}
"""


def render_dashboard_html(
    frame: pd.DataFrame,
    title: str = "Data quality dashboard",
    summary: FixSummary | None = None,
    source_filename: str = "",
    project_name: str = "",
    row_limit: int = 500,
) -> str:
    """A standalone dashboard: score, dimensions, fix summary, notes, data."""
    prof = profile(frame)
    dimensions = "".join(
        f"<div class='dim'><div class='k'>{html.escape(name)}</div>"
        f"<div class='v'>{value:.1f}</div>"
        f"<div class='bar'><span style='width:{max(0, min(100, value)):.1f}%'></span></div></div>"
        for name, value in prof.scores.items()
    )
    notes = "".join(f"<li>{html.escape(str(note))}</li>" for note in prof.notes) or "<li>No notes.</li>"
    fix_block = ""
    if summary is not None:
        fix_block = (
            "<h2>What was fixed</h2>"
            f"<div class='hero'><p style='margin:0;font-size:14px;line-height:1.55;'>"
            f"{html.escape(summary.paragraph())}</p></div>"
        )
    shown = frame.head(row_limit)
    header = "".join(f"<th>{html.escape(str(c))}</th>" for c in shown.columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>"
        for row in shown.itertuples(index=False)
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>{_DASHBOARD_STYLE}</style></head><body><div class='wrap'>"
        f"<h1>{html.escape(title)}</h1>"
        f"<p class='lead'>{html.escape(project_name)} {html.escape(source_filename)} · "
        f"{len(frame)} rows · {len(frame.columns)} columns</p>"
        "<div class='hero'><div><div class='big'>"
        f"{prof.overall:.0f}<span style='font-size:20px;'>%</span></div>"
        "<div class='k' style='font-size:11px;color:#6b7280;'>overall quality</div></div>"
        f"<div class='dims'>{dimensions}</div></div>"
        f"{fix_block}"
        "<h2>What we noticed</h2>"
        f"<ul>{notes}</ul>"
        "<h2>Cleaned data</h2>"
        f"<table><tr>{header}</tr>{body}</table>"
        f"<p class='foot'>Showing {len(shown)} of {len(frame)} rows. "
        "This file is self-contained: it needs no internet connection to open.</p>"
        "</div></body></html>"
    )


def write_html(
    frame: pd.DataFrame,
    path: str | Path,
    title: str = "Data quality dashboard",
    summary: FixSummary | None = None,
    source_filename: str = "",
    project_name: str = "",
) -> Path:
    target = Path(path)
    if target.suffix.lower() not in {".html", ".htm"}:
        target = target.with_suffix(".html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_dashboard_html(
            frame, title=title, summary=summary,
            source_filename=source_filename, project_name=project_name,
        ),
        encoding="utf-8",
    )
    return target


def write_any_extended(
    frame: pd.DataFrame,
    base_path: str | Path,
    output_format: str,
    summary: FixSummary | None = None,
    source_filename: str = "",
    project_name: str = "",
    title: str = "Data migration report",
) -> Path:
    """Write in any supported format, including the two added here.

    Formats the frozen layer already handles are delegated to it unchanged, so
    csv/excel/json/sql keep producing byte-identical output.
    """
    key = str(output_format).strip().lower()
    if key in {"pdf", "html", "htm", "dashboard"}:
        if key == "pdf":
            return write_pdf(
                frame, base_path, title=title, summary=summary,
                project_name=project_name, source_filename=source_filename,
            )
        return write_html(
            frame, base_path, title=title, summary=summary,
            source_filename=source_filename, project_name=project_name,
        )
    from app_files.output import write_any

    return write_any(frame, base_path, key)


EXTENDED_FORMATS = ["csv", "excel", "json", "sql", "pdf", "html"]


def available_formats() -> list[str]:
    return list(EXTENDED_FORMATS)