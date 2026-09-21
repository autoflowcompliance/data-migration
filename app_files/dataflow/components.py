"""Reusable DataFlow UI components. All rendering via st.html — never
st.markdown(unsafe_allow_html=True), which does not reliably render <style>
blocks and has been a confirmed bug in this codebase before.

Text that reaches the markup is escaped: these components are handed
filenames, field names and quality values that come from the uploaded file,
and an unescaped ``<`` in any of them would inject markup into the page.
"""

from __future__ import annotations

from html import escape

import streamlit as st


def metric_card(value, label: str) -> None:
    st.html(
        f"""
        <div style="background:var(--surface); border:1px solid var(--line); border-radius:8px;
                    padding:18px 20px; text-align:left;">
            <div style="font-family:'IBM Plex Mono', monospace; font-size:1.7rem; font-weight:600;
                        color:var(--ink);">{escape(str(value))}</div>
            <div style="font-size:.76rem; color:var(--slate); text-transform:uppercase;
                        letter-spacing:.04em; margin-top:4px;">{escape(str(label))}</div>
        </div>
        """
    )


def step_indicator(steps: list[str], current: int) -> None:
    """A horizontal stepper. current is 0-indexed.

    ``current`` may be ``-1`` (nothing started yet), in which case no step is
    marked active or done.
    """
    parts = []
    for i, label in enumerate(steps):
        if i < current:
            color, marker = "var(--teal)", "✓"
        elif i == current:
            color, marker = "var(--amber)", str(i + 1)
        else:
            color, marker = "var(--line)", str(i + 1)
        text_color = "var(--surface)" if i <= current else "var(--slate)"
        active = i == current
        parts.append(
            f'<div style="display:flex; align-items:center; gap:8px;">'
            f'<div style="width:26px; height:26px; border-radius:50%; background:{color}; '
            f'color:{text_color}; display:flex; align-items:center; justify-content:center; '
            f'font-size:.8rem; font-weight:600;">{marker}</div>'
            f'<span style="font-size:.9rem; color:{"var(--ink)" if active else "var(--slate)"}; '
            f'font-weight:{"600" if active else "400"};">{escape(label)}</span></div>'
        )
        if i < len(steps) - 1:
            parts.append('<div style="flex:1; height:1px; background:var(--line); min-width:24px;"></div>')
    st.html(f'<div style="display:flex; align-items:center; gap:10px; margin:12px 0 24px;">{"".join(parts)}</div>')


def download_card(label: str, icon: str, data, file_name: str, mime: str) -> None:
    st.html(
        f"""
        <div style="background:var(--surface); border:1px solid var(--line); border-radius:8px;
                    padding:16px; text-align:center; margin-bottom:8px;">
            <div style="font-size:1.4rem;">{escape(icon)}</div>
            <div style="font-size:.88rem; font-weight:600; color:var(--ink); margin-top:6px;">{escape(label)}</div>
        </div>
        """
    )
    st.download_button(f"Download {label}", data=data, file_name=file_name, mime=mime, use_container_width=True)


def score_badge(score: float) -> str:
    color = "var(--ok)" if score >= 90 else "var(--warn)" if score >= 70 else "var(--bad)"
    return f'<span style="color:{color}; font-weight:600;">{score}%</span>'


def empty_state(icon: str, title: str, message: str) -> None:
    st.html(
        f"""
        <div style="text-align:center; padding:48px 24px; background:var(--surface);
                    border:1px dashed var(--line); border-radius:10px;">
            <div style="font-size:2.2rem;">{escape(icon)}</div>
            <div style="font-family:'Fraunces', serif; font-size:1.1rem; font-weight:600;
                        color:var(--ink); margin-top:10px;">{escape(title)}</div>
            <div style="color:var(--slate); font-size:.9rem; margin-top:6px; max-width:40ch;
                        margin-left:auto; margin-right:auto;">{escape(message)}</div>
        </div>
        """
    )


def unavailable_note(feature_name: str) -> None:
    """Shown when a defensively-wrapped backend call isn't available, instead
    of crashing the page. Same visual language as empty_state but distinct
    enough to signal 'not wired up' rather than 'no data yet'."""
    st.html(
        f"""
        <div style="display:flex; gap:10px; background:var(--amber-soft); border:1px solid var(--amber);
                    border-radius:6px; padding:12px 16px; font-size:.88rem; color:var(--ink-soft);">
            <span>🔧</span>
            <div><b>{escape(feature_name)}</b> isn't wired up in this build yet — the rest of DataFlow works normally.</div>
        </div>
        """
    )