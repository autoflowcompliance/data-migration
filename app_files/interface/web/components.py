"""Reusable NiceGUI widgets.

Every page composes these rather than re-styling raw elements, so a change to
the visual language happens in one file.
"""

from __future__ import annotations

from html import escape
from typing import Callable, Iterable, Sequence

import pandas as pd
from nicegui import ui

from app_files.interface.web import theme


def page_header(title: str, subtitle: str = "") -> None:
    """Standard page title block."""
    ui.html(f'<h1 class="dr-page-title">{escape(title)}</h1>')
    if subtitle:
        ui.html(f'<p class="dr-page-sub">{escape(subtitle)}</p>')


def metric_card(value, label: str, colour: str | None = None) -> None:
    """A single metric card."""
    style = f" style='color:{colour}'" if colour else ""
    ui.html(
        f'<div class="dr-card"><div class="dr-value"{style}>{escape(str(value))}</div>'
        f'<div class="dr-label">{escape(label)}</div></div>'
    )


def metric_row(cards: Sequence[tuple]) -> None:
    """A row of cards. Each entry is ``(value, label)`` or ``(value, label, colour)``."""
    inner = ""
    for card in cards:
        value, label = card[0], card[1]
        colour = card[2] if len(card) > 2 else None
        style = f" style='color:{colour}'" if colour else ""
        inner += (
            f'<div class="dr-card"><div class="dr-value"{style}>{escape(str(value))}</div>'
            f'<div class="dr-label">{escape(label)}</div></div>'
        )
    ui.html(f'<div class="dr-cards">{inner}</div>')


def score_badge(score: float, suffix: str = "") -> None:
    """Colour-coded score badge: green 90+, amber 70-89, red below."""
    band = theme.score_band(score)
    text = f"{score}{suffix}"
    ui.html(f'<span class="dr-badge {band}">{escape(str(text))}</span>')


def demo_badge(text: str = "Demo mode") -> None:
    ui.html(f'<span class="dr-badge demo">{escape(text)}</span>')


def scorecard(scores: dict[str, float]) -> None:
    """Vertical bars, one per quality dimension."""
    rows = ""
    for name, score in scores.items():
        width = max(0.0, min(100.0, float(score)))
        rows += (
            '<div class="dr-scorecard-row">'
            f'<div class="dr-scorecard-name">{escape(name.title())}</div>'
            '<div class="dr-track" style="flex:1">'
            f'<div class="dr-fill" style="width:{width}%;background:{theme.score_colour(score)}"></div>'
            "</div>"
            f'<div class="dr-scorecard-value">{score}</div></div>'
        )
    ui.html(rows)


def score_bar(score: float, width: int = 90) -> None:
    """A single inline score bar."""
    value = max(0.0, min(100.0, float(score)))
    ui.html(
        f'<div class="dr-track" style="width:{width}px">'
        f'<div class="dr-fill" style="width:{value}%;background:{theme.score_colour(score)}"></div></div>'
    )


def progress_checklist(steps: Iterable[str], current: int) -> None:
    """A live checklist. Steps before ``current`` are done, ``current`` is active."""
    items = ""
    for index, step in enumerate(steps):
        state = "done" if index < current else "active" if index == current else ""
        marker = "✓" if index < current else "•"
        items += f'<li class="{state}"><span>{marker}</span><span>{escape(step)}</span></li>'
    ui.html(f'<ul class="dr-checklist">{items}</ul>')


def download_card(
    label: str,
    icon: str,
    on_click: Callable[[], None],
    description: str = "",
) -> None:
    """A row with a label on the left and a download button on the right."""
    with ui.row().classes("dr-download items-center w-full"):
        with ui.column().classes("gap-0"):
            ui.label(label).classes("dr-download-label")
            if description:
                ui.label(description).classes("text-xs text-gray-500")
        ui.space()
        ui.button(icon=icon, on_click=on_click).props("flat round")


def empty_state(
    icon: str,
    title: str,
    message: str,
    action_label: str | None = None,
    on_action: Callable[[], None] | None = None,
) -> None:
    """A pleasant empty state, optionally with a call to action."""
    with ui.column().classes("dr-empty w-full items-center"):
        ui.icon(icon).classes("text-4xl text-gray-400")
        ui.html(f'<div class="dr-empty-title">{escape(title)}</div>')
        ui.label(message).classes("text-sm text-gray-500 text-center")
        if action_label and on_action:
            ui.button(action_label, on_click=on_action).props("unelevated no-caps")


def file_table(frame, columns: Sequence[str] | None = None, limit: int = 200) -> None:
    """Render a frame as a table, coercing Arrow-hostile object columns first."""
    safe = arrow_safe(frame).head(limit)
    if columns:
        keep = [c for c in columns if c in safe.columns]
        if keep:
            safe = safe[keep]
    ui.table(
        columns=[{"name": str(c), "label": str(c).replace("_", " ").title(), "field": str(c),
                  "align": "left"} for c in safe.columns],
        rows=[{str(k): ("" if pd.isna(v) else v) for k, v in record.items()}
              for record in safe.to_dict("records")],
        row_key=str(safe.columns[0]) if len(safe.columns) else "row",
    ).classes("w-full").props("dense flat bordered wrap-cells")


def arrow_safe(frame):
    """Coerce object columns so a table can always serialize them.

    The mapper emits a ``confidence`` column of floats *and* blanks. Mixing
    numbers with text in one column makes the serializer fail, and
    stringifying is lossless for display.
    """
    safe = frame.copy()
    for column in safe.columns:
        if safe[column].dtype != object:
            continue
        blank = safe[column].map(is_blank)
        non_blank = safe[column][~blank]
        if non_blank.empty:
            continue
        numeric = pd.to_numeric(non_blank, errors="coerce").notna()
        if numeric.any() and (blank.any() or not numeric.all()):
            safe[column] = safe[column].map(lambda v: "" if is_blank(v) else str(v))
    return safe


def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return str(value).strip() == ""


def nav_bar(links: Sequence[tuple[str, str]], active: str = "") -> None:
    """Top navigation. Each entry is ``(label, route)``."""
    with ui.row().classes("items-center gap-1 w-full").style(
        f"background:{theme.SIDEBAR};padding:10px 24px;"
    ):
        ui.label("DataReady").classes("text-white font-bold text-lg mr-6")
        for label, route in links:
            colour = theme.PRIMARY if route == active else "transparent"
            ui.button(label, on_click=lambda r=route: ui.navigate.to(r)).props(
                "flat no-caps"
            ).style(f"color:#fff;background:{colour}")


def section(title: str, subtitle: str = "") -> None:
    ui.html(
        f'<h2 style="font-size:19px;font-weight:600;margin:28px 0 4px">{escape(title)}</h2>'
        + (f'<p class="dr-page-sub" style="margin-bottom:12px">{escape(subtitle)}</p>' if subtitle else "")
    )