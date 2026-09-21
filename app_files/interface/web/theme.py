"""Design tokens and the global stylesheet — the one visual language.

Every colour, font and spacing decision lives here. The widgets in
``components.py`` reference these names rather than literal hex values, so a
palette change reaches every page, the hosted demo and the packaged client
build at once.

Injected once per page via :func:`inject_theme`, which every route calls from
``page_shell``. A page that skips it renders unstyled NiceGUI defaults — the
reason the injection lives in the shared shell rather than in each route.
"""

from __future__ import annotations

# Palette. Names match the CSS custom properties below, so a value is written
# once and read as `theme.INK` in Python or `var(--ink)` in CSS.
INK = "#2B2420"
INK_SOFT = "#3A322B"
PAPER = "#F5F0E6"
SURFACE = "#FDFBF7"
SLATE = "#6B6255"
SLATE_LIGHT = "#9A9182"
LINE = "#E4DCC8"
AMBER = "#C97A2E"
AMBER_SOFT = "#F3E3D0"
TEAL = "#2C7A6B"
TEAL_SOFT = "#DCEAE7"
DANGER = "#B0473D"
DANGER_SOFT = "#F3DEDA"

# Threshold colours. Kept as aliases so a badge, a bar and a scorecard row
# cannot drift apart.
OK = TEAL
WARN = AMBER
BAD = DANGER

# Type stacks.
SERIF = "Fraunces, Georgia, serif"
SANS = "Inter, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

# 8px grid.
SPACE_UNIT = 8

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    "family=Fraunces:opsz,wght@9..144,400;9..144,600&"
    "family=Inter:wght@400;500;600;700&"
    'family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">'
    '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">'
)


def score_band(score: float) -> str:
    """Green at 90+, amber at 70-89, red below."""
    return "ok" if score >= 90 else "warn" if score >= 70 else "bad"


def score_colour(score: float) -> str:
    if score >= 90:
        return OK
    if score >= 70:
        return WARN
    return BAD


STYLESHEET = f"""
:root {{
  --ink: {INK};
  --ink-soft: {INK_SOFT};
  --paper: {PAPER};
  --surface: {SURFACE};
  --slate: {SLATE};
  --slate-light: {SLATE_LIGHT};
  --line: {LINE};
  --amber: {AMBER};
  --amber-soft: {AMBER_SOFT};
  --teal: {TEAL};
  --teal-soft: {TEAL_SOFT};
  --danger: {DANGER};
  --danger-soft: {DANGER_SOFT};
  --ok: {OK};
  --warn: {WARN};
  --bad: {BAD};
  --serif: {SERIF};
  --sans: {SANS};
  --mono: {MONO};
  --unit: {SPACE_UNIT}px;
}}

body, .nicegui-content, .q-page {{
  font-family: var(--sans);
  color: var(--ink);
  background: var(--paper);
}}

h1, h2, h3, h4, .dr-title {{
  font-family: var(--serif);
  color: var(--ink);
  font-weight: 600;
}}

/* NiceGUI pads its content container by default; the shell owns spacing. */
.nicegui-content {{ padding: 0 !important; }}

.dr-shell {{ max-width: 1080px; margin: 0 auto; padding: 1.8rem 24px 48px; }}

.dr-page-title {{
  font-family: var(--serif); font-size: 30px; font-weight: 600;
  color: var(--ink); margin: 0 0 4px;
}}
.dr-page-sub {{ color: var(--slate); font-size: 15px; margin: 0 0 28px; }}
.dr-section-title {{
  font-family: var(--serif); font-size: 19px; font-weight: 600;
  margin: 28px 0 4px;
}}

/* Nav — a paper-on-ink bar, not the old indigo. */
.dr-nav {{
  background: var(--ink); border-bottom: 8px solid var(--amber);
  padding: 12px 24px; display: flex; align-items: center; gap: 4px;
  flex-wrap: wrap;
}}
.dr-nav .dr-brand {{
  font-family: var(--serif); color: var(--surface); font-weight: 600;
  font-size: 19px; margin-right: 20px; letter-spacing: .01em;
}}

/* Cards and metrics. */
.dr-cards {{ display: flex; flex-wrap: wrap; gap: 14px; }}
.dr-card {{
  background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
  padding: 18px 20px; text-align: left; flex: 1 1 150px;
}}
.dr-card .dr-value {{
  font-family: var(--mono); font-size: 1.7rem; font-weight: 600;
  color: var(--ink); line-height: 1.2;
}}
.dr-card .dr-label {{
  color: var(--slate); font-size: .76rem; text-transform: uppercase;
  letter-spacing: .04em; margin-top: 4px;
}}

/* Steps. */
.dr-steps {{ display: flex; align-items: center; gap: 10px; margin: 12px 0 24px; }}
.dr-step {{ display: flex; align-items: center; gap: 8px; }}
.dr-step-dot {{
  width: 26px; height: 26px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; font-size: .8rem; font-weight: 600;
}}
.dr-step-label {{ font-size: .9rem; }}
.dr-step-connector {{ flex: 1; height: 1px; background: var(--line); min-width: 24px; }}

/* Badges. */
.dr-badge {{
  display: inline-block; border-radius: 6px; padding: 2px 10px;
  font-family: var(--mono); font-size: .8rem; font-weight: 600;
}}
.dr-badge.ok {{ background: var(--teal-soft); color: var(--teal); }}
.dr-badge.warn {{ background: var(--amber-soft); color: var(--amber); }}
.dr-badge.bad {{ background: var(--danger-soft); color: var(--danger); }}
.dr-badge.demo {{ background: var(--amber-soft); color: var(--ink-soft); }}

/* Scorecard bars. */
.dr-track {{ background: var(--line); border-radius: 5px; height: 12px; overflow: hidden; }}
.dr-fill {{ height: 100%; border-radius: 5px; }}
.dr-scorecard-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.dr-scorecard-name {{ flex: 0 0 130px; font-size: 13px; color: var(--slate); }}
.dr-scorecard-value {{
  flex: 0 0 46px; text-align: right; font-family: var(--mono);
  font-size: 13px; font-weight: 500;
}}

/* Checklist. */
.dr-checklist {{ list-style: none; padding: 0; margin: 0; }}
.dr-checklist li {{
  padding: 6px 0; font-size: 14px; color: var(--slate);
  display: flex; align-items: center; gap: 8px;
}}
.dr-checklist li.done {{ color: var(--teal); }}
.dr-checklist li.active {{ color: var(--ink); font-weight: 600; }}

/* Empty state and unavailable note. */
.dr-empty {{
  text-align: center; padding: 48px 24px; background: var(--surface);
  border: 1px dashed var(--line); border-radius: 10px;
}}
.dr-empty .dr-empty-title {{
  font-family: var(--serif); font-size: 1.1rem; font-weight: 600;
  color: var(--ink); margin: 10px 0 6px;
}}
.dr-empty .dr-empty-msg {{
  color: var(--slate); font-size: .9rem; margin: 0 auto; max-width: 40ch;
}}
.dr-note {{
  display: flex; gap: 10px; background: var(--amber-soft);
  border: 1px solid var(--amber); border-radius: 6px; padding: 12px 16px;
  font-size: .88rem; color: var(--ink-soft);
}}

/* Download card. */
.dr-download-card {{
  background: var(--surface); border: 1px solid var(--line); border-radius: 8px;
  padding: 16px; text-align: center; margin-bottom: 8px;
}}
.dr-download-icon {{ font-size: 1.4rem; }}
.dr-download-label {{
  font-size: .88rem; font-weight: 600; color: var(--ink); margin-top: 6px;
}}

.dr-hero {{ padding: 40px 0; }}
.dr-hero h1 {{ font-size: 44px; line-height: 1.12; margin: 0 0 12px; }}
.dr-hero p {{ font-size: 17px; color: var(--slate); margin: 0 0 24px; }}
.dr-feature-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}}
.dr-trust {{
  background: var(--teal-soft); border: 1px solid var(--teal); color: var(--ink-soft);
  border-radius: 10px; padding: 16px; margin-top: 24px; font-size: 14px;
}}

/* Buttons — primary is ink, hover amber. Download is surface, hover teal. */
.dr-btn.q-btn {{
  background: var(--ink) !important; color: var(--surface) !important;
  border: none !important; border-radius: 6px !important;
  font-weight: 600 !important; padding: .55rem 1.4rem !important;
  text-transform: none !important;
}}
.dr-btn.q-btn:hover {{ background: var(--amber) !important; color: var(--ink) !important; }}

.dr-btn-download.q-btn {{
  background: var(--surface) !important; color: var(--ink) !important;
  border: 1px solid var(--line) !important; border-radius: 6px !important;
  font-weight: 600 !important; text-transform: none !important;
}}
.dr-btn-download.q-btn:hover {{
  border-color: var(--teal) !important; color: var(--teal) !important;
}}

/* Nav links: surface text, amber when active. */
.dr-nav-btn.q-btn {{ color: var(--surface) !important; text-transform: none !important; }}
.dr-nav-btn.dr-active.q-btn {{ color: var(--amber) !important; font-weight: 600 !important; }}

/* Drop zone. */
.dr-dropzone {{
  background: var(--surface); border: 1.5px dashed var(--slate-light);
  border-radius: 8px; padding: 32px;
}}
.dr-dropzone:hover {{ border-color: var(--amber); }}

/* Tables inherit the palette rather than NiceGUI's grey. */
.q-table__container {{ background: var(--surface); border: 1px solid var(--line); }}
"""


def inject_theme() -> None:
    """Add the fonts and the stylesheet to the page being built.

    Called once from ``layout.page_shell``, so every route is styled whether or
    not its author remembered to ask.
    """
    from nicegui import ui

    ui.add_head_html(FONT_LINK)
    ui.add_head_html(f"<style>{STYLESHEET}</style>")


def button(label: str = "", **kwargs):
    """A primary button in the house style."""
    from nicegui import ui

    return ui.button(label, **kwargs).classes("dr-btn").props("unelevated no-caps")


def download_button(label: str = "", **kwargs):
    """A download button in the house style."""
    from nicegui import ui

    return ui.button(label, **kwargs).classes("dr-btn-download").props("unelevated no-caps")
