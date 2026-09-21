"""Reusable NiceGUI widgets.

Every page composes these rather than re-styling raw elements, so a change to
the visual language happens in one file. The specs implemented here — metric
card, step indicator, download card, score badge, empty state, unavailable note
— were designed against the tokens in :mod:`app_files.interface.web.theme`.

Widgets render through ``ui.html`` with escaped values rather than f-string
interpolation of user data, because a filename or a CRM name can contain
characters that would otherwise break the markup.
"""

from __future__ import annotations

from contextlib import contextmanager
from html import escape
from typing import Callable, Iterable, Sequence

import pandas as pd
from nicegui import ui

from app_files.interface.web import theme


# ---------------------------------------------------------------------------
# Page furniture
# ---------------------------------------------------------------------------
def page_header(title: str, subtitle: str = "") -> None:
    """Standard page title block."""
    ui.html(f'<h1 class="dr-page-title">{escape(title)}</h1>')
    if subtitle:
        ui.html(f'<p class="dr-page-sub">{escape(subtitle)}</p>')


def section(title: str, subtitle: str = "") -> None:
    ui.html(f'<h2 class="dr-section-title">{escape(title)}</h2>')
    if subtitle:
        ui.html(f'<p class="dr-page-sub" style="margin-bottom:12px">{escape(subtitle)}</p>')


def nav_bar(links: Sequence[tuple[str, str]], active: str = "") -> None:
    """Top navigation. Each entry is ``(label, route)``."""
    with ui.row().classes("dr-nav w-full items-center gap-1"):
        ui.html('<span class="dr-brand">DataReady</span>')
        for label, route in links:
            element = theme.button(label, on_click=lambda r=route: ui.navigate.to(r))
            element.classes("dr-nav-btn")
            if route == active:
                element.classes("dr-active")


# ---------------------------------------------------------------------------
# Spec'd components
# ---------------------------------------------------------------------------
def metric_card(value, label: str, colour: str | None = None) -> None:
    """One metric: mono value over an uppercase label."""
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
    """Colour-coded badge: teal at 90+, amber 70-89, danger below."""
    band = theme.score_band(score)
    ui.html(f'<span class="dr-badge {band}">{escape(f"{score}{suffix}")}</span>')


def demo_badge(text: str = "Demo mode") -> None:
    ui.html(f'<span class="dr-badge demo">{escape(text)}</span>')


def step_indicator(steps: Sequence[str], current: int) -> None:
    """Horizontal stepper. ``current`` is 0-indexed.

    A completed step is teal with a check, the current step amber, and every
    step still ahead is drawn in the line colour.
    """
    parts = []
    for index, label in enumerate(steps):
        if index < current:
            colour, marker, text = theme.TEAL, "✓", theme.SURFACE
        elif index == current:
            colour, marker, text = theme.AMBER, str(index + 1), theme.SURFACE
        else:
            colour, marker, text = theme.LINE, str(index + 1), theme.SLATE
        label_colour = theme.INK if index == current else theme.SLATE
        weight = "600" if index == current else "400"
        parts.append(
            '<div class="dr-step">'
            f'<div class="dr-step-dot" style="background:{colour};color:{text}">{marker}</div>'
            f'<span class="dr-step-label" style="color:{label_colour};font-weight:{weight}">'
            f"{escape(label)}</span></div>"
        )
        if index < len(steps) - 1:
            parts.append('<div class="dr-step-connector"></div>')
    ui.html(f'<div class="dr-steps">{"".join(parts)}</div>')


def icon(name: str) -> str:
    """Render an icon, accepting either an emoji or a Material icon name.

    Call sites predate the redesign and pass Material names such as
    ``table_view``; newer ones pass emoji. Detecting which is which here keeps
    both rendering correctly without touching every caller.
    """
    if name.isascii() and name.replace("_", "").isalnum() and name.islower():
        return f'<span class="material-icons" style="font-size:1.4rem">{escape(name)}</span>'
    return escape(name)


def download_card(
    label: str,
    icon_name: str,
    on_click: Callable[[], None],
    description: str = "",
) -> None:
    """A centred icon-and-label card with a download button beneath."""
    with ui.column().classes("w-full items-stretch gap-0"):
        ui.html(
            f'<div class="dr-download-card"><div class="dr-download-icon">'
            f'{icon(icon_name)}</div>'
            f'<div class="dr-download-label">{escape(label)}</div></div>'
        )
        if description:
            ui.label(description).classes("text-xs text-center mb-1").style(
                f"color:{theme.SLATE}"
            )
        theme.download_button(f"Download {label}", on_click=on_click).classes("w-full")


def empty_state(
    icon_name: str,
    title: str,
    message: str,
    action_label: str | None = None,
    on_action: Callable[[], None] | None = None,
) -> None:
    """A pleasant empty state, optionally with a call to action."""
    with ui.column().classes("dr-empty w-full items-center"):
        ui.html(f'<div style="font-size:2.2rem">{icon(icon_name)}</div>')
        ui.html(f'<div class="dr-empty-title">{escape(title)}</div>')
        ui.html(f'<p class="dr-empty-msg">{escape(message)}</p>')
        if action_label and on_action:
            theme.button(action_label, on_click=on_action)


def unavailable_note(feature_name: str) -> None:
    """Shown when a backend call is missing, instead of crashing the page.

    Same visual language as :func:`empty_state` but distinct enough to signal
    "not wired up" rather than "no data yet".
    """
    ui.html(
        '<div class="dr-note"><span>🔧</span><div>'
        f"<b>{escape(feature_name)}</b> isn't wired up in this build yet — "
        "the rest of DataReady works normally.</div></div>"
    )


# ---------------------------------------------------------------------------
# Form controls, pre-skinned
# ---------------------------------------------------------------------------
# Every input in the app goes through these so Quasar's stock outlines and
# indigo focus colour never appear. The heavy lifting is in the stylesheet; the
# helpers exist so a call site cannot forget the class.
def field(label: str = "", **kwargs):
    """An outlined text field in the house style."""
    return ui.input(label, **kwargs).classes("dr-field w-full").props("outlined dense")


def number_field(label: str = "", **kwargs):
    return ui.number(label, **kwargs).classes("dr-field w-full").props("outlined dense")


def textarea(label: str = "", **kwargs):
    return ui.textarea(label, **kwargs).classes("dr-field w-full").props("outlined")


def select(options, label: str = "", **kwargs):
    return ui.select(options, label=label, **kwargs).classes("dr-field").props(
        "outlined dense"
    )


@contextmanager
def tabs(names: Sequence[str]):
    """A tab strip in the house style, yielding ``(strip, panels)``.

    Usage::

        with c.tabs(["One", "Two"]) as (strip, (first, second)):
            with ui.tab_panels(strip, value=first): ...

    The panels are plain ``ui.tab`` elements and the caller builds the panel
    container, because only the caller knows what goes in each one.
    """
    with ui.tabs().classes("dr-tabs w-full") as strip:
        panels = [ui.tab(name) for name in names]
    yield strip, panels


def expansion(title: str, **kwargs):
    return ui.expansion(title, **kwargs).classes("dr-expansion w-full")


# ---------------------------------------------------------------------------
# Notices and demo messaging
# ---------------------------------------------------------------------------
def info_note(text: str) -> None:
    """A calm informational strip — teal, not the amber of a warning."""
    ui.html(f'<div class="dr-note dr-note-info">{escape(text)}</div>')


def demo_banner(runs: int) -> None:
    """The persistent demo strip.

    Says what the demo actually is: a run allowance, with everything else
    switched on. The old wording listed caps that no longer exist (rows, file
    size, CSV-only), which made the product look smaller than it is — the
    opposite of what a demo is for.

    ``runs`` comes from the resolved limits rather than being hard-coded here,
    so lowering ``DEMO_RUNS_PER_SESSION`` changes the banner too.
    """
    ui.html(
        '<div class="dr-note dr-note-demo">'
        f"<b>Demo mode</b> — {runs} runs per session. Everything else works. "
        "The licensed version has no limit.</div>"
    )


def runs_exhausted_note(purchase_url: str, runs: int) -> None:
    """Shown when the run allowance is spent, with the way to remove it."""
    ui.html(
        '<div class="dr-note dr-note-demo" style="align-items:center">'
        f"<span>You've used your {runs} free demo runs. "
        "The licensed version has no limit.</span>"
        f'<a class="dr-buy" href="{escape(purchase_url)}" target="_blank" '
        'rel="noopener">Get a licence →</a></div>'
    )


def report_embed(token: str, height: str = "75vh") -> None:
    """Embed a published report by token.

    An iframe, not ``ui.html``: a report runs to hundreds of kilobytes, which
    exceeds the WebSocket message limit and drops the connection. Fetching it
    over HTTP keeps the socket alive.
    """
    from app_files.interface.web.reports import report_url

    ui.element("iframe").props(f'src="{report_url(token)}"').classes(
        "w-full border rounded-lg"
    ).style(f"height:{height};background:var(--surface);border-color:var(--line)")


# ---------------------------------------------------------------------------
# Data display
# ---------------------------------------------------------------------------
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
            f'<div class="dr-scorecard-value">{escape(str(score))}</div></div>'
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