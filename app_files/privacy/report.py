"""Rendering for the privacy layer: a standalone HTML summary and the
structured blocks that the QA report can embed.

The QA reporter is part of the frozen core, so this module renders *around* it
rather than modifying it — the same pattern the profiling layer uses.
"""

from __future__ import annotations

import html
from typing import Any

from app_files.privacy.detect import PIIReport

STYLES = """
.pii-card { border: 1px solid #d7dbe0; border-radius: 10px; padding: 16px 20px;
  font-family: -apple-system, Segoe UI, Roboto, sans-serif; color: #1c2430; }
.pii-card h2 { margin: 0 0 4px; font-size: 17px; }
.pii-card p.lede { margin: 0 0 14px; color: #5b6675; font-size: 13px; }
.pii-card table { border-collapse: collapse; width: 100%; font-size: 13px; }
.pii-card th, .pii-card td { text-align: left; padding: 6px 10px;
  border-bottom: 1px solid #eceff3; }
.pii-card th { color: #5b6675; font-weight: 600; }
.pii-total { display: inline-block; margin-right: 8px; padding: 2px 8px;
  border-radius: 20px; background: #fdecea; color: #a3271b; font-weight: 600; }
.pii-none { color: #1d7a4d; font-weight: 600; }
"""


def _esc(value: Any) -> str:
    return html.escape(str(value))


def render_pii_report(report: PIIReport, masked: dict[str, Any] | None = None) -> str:
    """A self-contained HTML card. ``masked`` is a :meth:`MaskResult.summary`
    when masking was applied, to distinguish found-and-masked from found-only."""
    rows = []
    for column, counts in sorted(report.affected_columns().items()):
        detail = ", ".join(f"{kind} ×{n}" for kind, n in sorted(counts.items()))
        rows.append(f"<tr><td>{_esc(column)}</td><td>{_esc(detail)}</td></tr>")

    if report.total == 0:
        body = '<p class="pii-none">No personal data detected.</p>'
    else:
        body = (
            f'<p><span class="pii-total">{report.total} match'
            f'{"es" if report.total != 1 else ""}</span></p>'
            "<table><thead><tr><th>Column</th><th>Detected</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )

    masked_line = ""
    if masked is not None:
        total = masked.get("masked_total", 0)
        by_strategy = ", ".join(
            f"{name} ×{n}" for name, n in sorted(masked.get("by_strategy", {}).items())
        )
        masked_line = (
            f'<p class="lede">Masked {total} value{"" if total == 1 else "s"}'
            f'{f" ({_esc(by_strategy)})" if by_strategy else ""}.</p>'
        )

    return (
        f"<style>{STYLES}</style>"
        '<div class="pii-card">'
        "<h2>Privacy scan</h2>"
        f'<p class="lede">Scanned {report.rows_scanned} row'
        f'{"" if report.rows_scanned == 1 else "s"} across '
        f'{len(report.columns_scanned)} column'
        f'{"" if len(report.columns_scanned) == 1 else "s"}.</p>'
        f"{masked_line}{body}"
        "</div>"
    )


def inject_pii_report(
    base_html: str, report: PIIReport, masked: dict[str, Any] | None = None
) -> str:
    """Append the privacy card to an already-rendered QA report.

    Appending, not rewriting: the frozen reporter's HTML is left byte-intact,
    which ``tests/integration/test_privacy_pipeline.py`` pins by comparing the
    base report before and after.
    """
    return base_html + "\n" + render_pii_report(report, masked)
