"""Design tokens and the global stylesheet.

One palette, one spacing scale, injected once per page. Keeping the colours
here means the score badges, the scorecard bars and the dashboard all agree on
what "good" and "bad" look like.
"""

from __future__ import annotations

PRIMARY = "#4F46E5"
PRIMARY_DARK = "#4338CA"
SIDEBAR = "#111827"
INK = "#111827"
MUTED = "#6B7280"
LINE = "#E5E7EB"
BACKGROUND = "#F9FAFB"
OK = "#047857"
WARN = "#D97706"
BAD = "#DC2626"

# 8px grid.
SPACE_UNIT = 8


def score_colour(score: float) -> str:
    """Green at 90+, amber at 70-89, red below."""
    if score >= 90:
        return OK
    if score >= 70:
        return WARN
    return BAD


def score_band(score: float) -> str:
    return "ok" if score >= 90 else "warn" if score >= 70 else "bad"


STYLESHEET = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --dr-primary: {PRIMARY};
  --dr-primary-dark: {PRIMARY_DARK};
  --dr-sidebar: {SIDEBAR};
  --dr-ink: {INK};
  --dr-muted: {MUTED};
  --dr-line: {LINE};
  --dr-bg: {BACKGROUND};
  --dr-ok: {OK};
  --dr-warn: {WARN};
  --dr-bad: {BAD};
  --dr-unit: {SPACE_UNIT}px;
}}

body, .nicegui-content {{
  font-family: Inter, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--dr-ink);
  background: var(--dr-bg);
}}

.dr-shell {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px; }}
.dr-page-title {{ font-size: 28px; font-weight: 700; margin: 0 0 4px; }}
.dr-page-sub {{ color: var(--dr-muted); font-size: 14px; margin: 0 0 24px; }}

.dr-card {{
  background: #fff; border: 1px solid var(--dr-line); border-radius: 10px;
  padding: 16px; flex: 1 1 150px;
}}
.dr-card .dr-value {{ font-size: 24px; font-weight: 600; line-height: 1.2; }}
.dr-card .dr-label {{
  color: var(--dr-muted); font-size: 12px; text-transform: uppercase;
  letter-spacing: .04em;
}}
.dr-cards {{ display: flex; flex-wrap: wrap; gap: 14px; }}

.dr-badge {{
  display: inline-block; border-radius: 9999px; padding: 2px 10px;
  font-size: 12px; font-weight: 600;
}}
.dr-badge.ok {{ background: #D1FAE5; color: var(--dr-ok); }}
.dr-badge.warn {{ background: #FEF3C7; color: #92400E; }}
.dr-badge.bad {{ background: #FEE2E2; color: var(--dr-bad); }}
.dr-badge.demo {{ background: #EDE9FE; color: #5B21B6; }}

.dr-track {{ background: #F3F4F6; border-radius: 5px; height: 12px; overflow: hidden; }}
.dr-fill {{ height: 100%; border-radius: 5px; }}
.dr-scorecard-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.dr-scorecard-name {{ flex: 0 0 130px; font-size: 13px; color: var(--dr-muted); }}
.dr-scorecard-value {{ flex: 0 0 46px; text-align: right; font-size: 13px; font-weight: 600; }}

.dr-checklist {{ list-style: none; padding: 0; margin: 0; }}
.dr-checklist li {{
  padding: 6px 0; font-size: 14px; color: var(--dr-muted);
  display: flex; align-items: center; gap: 8px;
}}
.dr-checklist li.done {{ color: var(--dr-ok); }}
.dr-checklist li.active {{ color: var(--dr-ink); font-weight: 600; }}

.dr-empty {{
  text-align: center; padding: 48px 24px; color: var(--dr-muted);
  border: 1px dashed var(--dr-line); border-radius: 10px; background: #fff;
}}
.dr-empty .dr-empty-title {{ font-size: 17px; font-weight: 600; color: var(--dr-ink); margin: 8px 0 4px; }}
.dr-download {{
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  background: #fff; border: 1px solid var(--dr-line); border-radius: 10px;
  padding: 12px 16px; margin-bottom: 10px;
}}
.dr-download .dr-download-label {{ font-weight: 500; font-size: 15px; }}
.dr-hero {{ padding: 40px 0; }}
.dr-hero h1 {{ font-size: 40px; line-height: 1.15; margin: 0 0 12px; font-weight: 700; }}
.dr-hero p {{ font-size: 17px; color: var(--dr-muted); margin: 0 0 24px; }}
.dr-feature-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }}
.dr-trust {{ background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46;
             border-radius: 10px; padding: 16px; margin-top: 24px; font-size: 14px; }}

.nicegui-content {{ padding: 0 !important; }}
"""


def inject_theme() -> None:
    """Add the stylesheet to the page being built. Called at the top of every page."""
    from nicegui import ui

    ui.add_css(STYLESHEET)