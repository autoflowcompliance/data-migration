"""Render a QA report that includes the five-dimension scorecard.

The core reporter's ``render_qa_report`` is frozen, so rather than modify it
this module calls it and injects the scorecard section into the HTML it
returns. The template only emits the scorecard when a ``scorecard`` variable is
present — which the core renderer never supplies — so existing report output
stays byte-for-byte identical and this remains purely additive.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app_files.profiling.profiler import Profile, profile, scorecard_rows


def _scorecard_html(profile_result: Profile) -> str:
    rows = scorecard_rows(profile_result)
    bars = []
    for row in rows:
        width = max(0.0, min(100.0, float(row["score"])))
        bars.append(
            '<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
            f'<div style="flex:0 0 130px;font-size:13px;color:#6b7280;">{row["dimension"]}</div>'
            '<div style="flex:1;background:#f3f4f6;border-radius:5px;height:14px;overflow:hidden;">'
            f'<div style="height:100%;width:{width}%;background:'
            f'{_band_colour(row["band"])};"></div></div>'
            f'<div style="flex:0 0 46px;text-align:right;font-size:13px;font-weight:600;">'
            f'{row["score"]}</div></div>'
        )
    notes = ""
    if profile_result.notes:
        items = "".join(f"<li>{note}</li>" for note in profile_result.notes)
        notes = f'<ul style="color:#6b7280;font-size:13px;">{items}</ul>'
    return (
        "<h2>Quality scorecard</h2>"
        f'<p style="color:#6b7280;font-size:13px;">Five independent dimensions, each scored '
        f"0&ndash;100. Overall quality: <strong>{profile_result.overall}%</strong>.</p>"
        f'<div>{"".join(bars)}</div>{notes}'
    )


def _band_colour(band: str) -> str:
    return {"ok": "#047857", "warn": "#d97706", "bad": "#dc2626"}.get(band, "#047857")


def render_qa_report_with_profile(
    base_html: str, frame: pd.DataFrame, profile_result: Profile | None = None
) -> str:
    """Inject a scorecard into an already-rendered QA report.

    Args:
        base_html: output of the core ``render_qa_report``.
        frame: the frame that was profiled (usually the mapped output).
        profile_result: reuse an existing profile instead of recomputing.
    """
    result = profile_result or profile(frame)
    block = _scorecard_html(result)
    marker = "<h2>Issue details</h2>"
    if marker in base_html:
        return base_html.replace(marker, f"{block}\n{marker}", 1)
    # Fallback: append before the footer if the marker moved.
    return base_html.replace("</div>\n</body>", f"{block}</div>\n</body>", 1)


def profile_and_render(
    base_html: str,
    frame: pd.DataFrame,
    **profile_kwargs: Any,
) -> tuple[str, Profile]:
    """Profile ``frame`` and return ``(html_with_scorecard, profile)``."""
    result = profile(frame, **profile_kwargs)
    return render_qa_report_with_profile(base_html, frame, result), result