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
  background: var(--ink); border-bottom: 4px solid var(--amber);
  padding: 12px 24px; display: flex; align-items: center; gap: 4px;
  flex-wrap: wrap;
}}
.dr-nav .dr-brand {{
  font-family: var(--serif); color: var(--surface); font-weight: 600;
  font-size: 19px; margin-right: 20px; letter-spacing: .01em;
}}
/* The optional side panel some layouts use: surface on paper, ruled on the
   right. Present so a route can adopt it without inventing its own colours. */
.dr-sidebar {{
  background: var(--surface); border-right: 1px solid var(--line);
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
/* A calm informational strip, for things that are not warnings. */
.dr-note-info {{ background: var(--teal-soft); border-color: var(--teal); }}
/* The demo banner: a standing state, so it is quiet rather than alarming. */
.dr-note-demo {{
  background: var(--amber-soft); border-color: var(--amber);
  justify-content: space-between; flex-wrap: wrap; margin-top: 18px;
}}
.dr-buy {{
  color: var(--ink); font-weight: 600; text-decoration: none;
  border-bottom: 2px solid var(--amber); white-space: nowrap;
}}
.dr-buy:hover {{ color: var(--amber); }}

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
  background: var(--surface); border: 1.5px dashed var(--slate-light) !important;
  border-radius: 8px; padding: 8px;
}}
.dr-dropzone:hover {{ border-color: var(--amber) !important; }}
/* Quasar's uploader paints its own grey card and blue "add" strip; strip both
   so the dashed surface shows through. */
.dr-dropzone .q-uploader__header {{
  background: transparent !important; color: var(--ink) !important;
  border: none !important; height: auto !important; min-height: 0 !important;
  padding: 8px !important;
}}
.dr-dropzone .q-uploader__list {{ background: var(--surface) !important; }}
/* The heading ("Drop a file here or click to choose") sits at ink weight 500
   so it reads as the page's instruction rather than as a grey hint, and the
   file-size line ("0.0B / 0.00%") at slate so it stays subordinate to it. */
.dr-dropzone .q-uploader__header-content {{ color: var(--ink) !important; font-weight: 500 !important; }}
.dr-dropzone .q-uploader__title {{ color: var(--ink) !important; font-weight: 500 !important; }}
.dr-dropzone .q-uploader__subtitle,
.dr-dropzone .q-item__label--caption {{ color: var(--slate) !important; }}
.dr-dropzone .q-btn {{ color: var(--amber) !important; }}

/* ---- Quasar controls, re-skinned so nothing renders in default styling ----
   Everything below exists because NiceGUI ships Quasar defaults (indigo
   accents, grey borders, blue focus rings) that would otherwise ignore the
   palette. Each rule maps one Quasar class onto a design token. */

/* Text, number and textarea fields. Outlined by default, ink focus. */
.dr-field .q-field__control,
.q-field--outlined .q-field__control {{
  background: var(--surface) !important;
  border-radius: 6px !important;
}}
.dr-field .q-field__control:before,
.q-field--outlined .q-field__control:before {{ border-color: var(--line) !important; }}
.dr-field .q-field__control:hover:before,
.q-field--outlined .q-field__control:hover:before {{ border-color: var(--slate-light) !important; }}
.dr-field .q-field--focused .q-field__control:after,
.q-field--outlined.q-field--focused .q-field__control:after {{
  border-color: var(--amber) !important;
}}
.dr-field .q-field__label,
.q-field__label {{ color: var(--slate) !important; }}
.q-field__native, .q-field__input {{ color: var(--ink) !important; }}
.q-field__marginal {{ color: var(--slate) !important; }}
.q-placeholder {{ color: var(--slate-light) !important; }}
.q-field__bottom {{ color: var(--slate) !important; }}

/* Select menus and their popups. */
.q-menu {{
  background: var(--surface) !important; border: 1px solid var(--line) !important;
  border-radius: 6px !important; box-shadow: 0 8px 24px rgba(43, 36, 32, .12) !important;
}}
.q-item {{ color: var(--ink) !important; }}
.q-item.q-manual-focusable--focused, .q-item--active {{
  background: var(--amber-soft) !important; color: var(--ink) !important;
}}
.q-item__label {{ color: inherit !important; }}

/* Checkbox and switch. */
.q-checkbox__inner--truthy .q-checkbox__bg,
.q-checkbox__inner--indet .q-checkbox__bg {{ background: var(--ink) !important; }}
.q-checkbox__inner .q-checkbox__bg {{ border-color: var(--line) !important; }}
.q-checkbox__label, .q-toggle__label {{ color: var(--ink) !important; }}
.q-toggle__inner--truthy .q-toggle__track {{ background: var(--teal) !important; }}
.q-toggle__inner--truthy .q-toggle__thumb {{ color: var(--teal) !important; }}

/* Radio and slider. */
.q-radio__inner--truthy .q-radio__bg {{ color: var(--teal) !important; }}
.q-radio__label {{ color: var(--ink) !important; }}
/* The job-type chooser reads as a pair of options, not a bare radio group. */
.dr-radio .q-radio {{ padding: 8px 14px; border: 1px solid var(--line);
  border-radius: 6px; background: var(--surface); }}
.dr-radio .q-radio + .q-radio {{ margin-left: 10px; }}
.q-slider__track {{ color: var(--line) !important; }}
.q-slider__selection {{ color: var(--amber) !important; }}
.q-slider__thumb {{ color: var(--amber) !important; }}

/* Tabs. */
.dr-tabs .q-tab {{ color: var(--slate) !important; text-transform: none !important; }}
.dr-tabs .q-tab--active {{ color: var(--ink) !important; font-weight: 600 !important; }}
.dr-tabs .q-tab__indicator {{ background: var(--amber) !important; height: 3px !important; }}
.dr-tabs .q-tabs__content {{ border-bottom: 1px solid var(--line) !important; }}

/* Expansion panels. */
.dr-expansion .q-expansion-item__container {{
  border: 1px solid var(--line) !important; border-radius: 8px !important;
  background: var(--surface) !important;
}}
.dr-expansion .q-item__label {{ color: var(--ink) !important; font-weight: 600 !important; }}
.dr-expansion .q-expansion-item__toggle-icon {{ color: var(--slate) !important; }}
.dr-expansion .q-expansion-item__content {{ color: var(--slate) !important; }}

/* Tables inherit the palette rather than NiceGUI's grey. */
.q-table__container {{ background: var(--surface) !important; border: 1px solid var(--line) !important; }}
.q-table th {{
  background: var(--paper) !important; color: var(--ink) !important;
  font-weight: 600 !important; text-transform: none !important;
}}
.q-table td {{ color: var(--ink-soft) !important; }}
.q-table tbody tr:hover {{ background: var(--amber-soft) !important; }}
.q-table__bottom {{ color: var(--slate) !important; border-top: 1px solid var(--line) !important; }}

/* Separator, cards and images. */
.q-separator {{ background: var(--line) !important; }}
.q-card {{
  background: var(--surface) !important; border: 1px solid var(--line) !important;
  border-radius: 8px !important; box-shadow: none !important;
}}
.q-img__content > div {{ background: transparent !important; color: var(--ink) !important; }}

/* Notifications (toasts) carry the palette instead of Quasar's stock colours. */
.q-notification {{
  background: var(--surface) !important; color: var(--ink) !important;
  border-left: 4px solid var(--line) !important; border-radius: 6px !important;
  box-shadow: 0 8px 24px rgba(43, 36, 32, .16) !important; font-family: var(--sans);
}}
.q-notification--positive {{ border-left-color: var(--teal) !important; }}
.q-notification--negative {{ border-left-color: var(--danger) !important; }}
.q-notification--warning {{ border-left-color: var(--amber) !important; }}
.q-notification--info {{ border-left-color: var(--slate-light) !important; }}

/* Dialogs, drawers and tooltips. */
.q-dialog .q-card {{ background: var(--surface) !important; padding: 4px; }}
.q-tooltip {{
  background: var(--ink) !important; color: var(--surface) !important;
  font-family: var(--sans); font-size: 12px;
}}
.q-drawer {{ background: var(--surface) !important; }}
.q-drawer .q-item {{ color: var(--ink) !important; }}

/* Scrollbars, so a long issue table does not break the palette. */
* {{ scrollbar-color: var(--line) transparent; }}

/* ---------------------------------------------------------------- *
 * Quasar brand colours.
 *
 * This is the load-bearing block. Quasar ships a stock blue primary colour
 * and derives a great many of its own colours from it — progress bars,
 * spinners, tab ink, ``.text-primary``/``.bg-primary``, the
 * uploader's add button, focus rings. Overriding individual components (as
 * everything above does) leaves whichever ones nobody listed still blue, which
 * is exactly why the deployed app kept rendering blue controls no matter how
 * many component rules were added.
 *
 * Quasar reads its palette from these custom properties, so setting them once
 * here re-points *every* primary-derived colour at the Warm Editorial ink, and
 * any component we have not explicitly styled inherits the palette instead of
 * Quasar's default.
 * ---------------------------------------------------------------- */
:root, body.body--light, .q-app {{
  --q-primary: {INK} !important;
  --q-secondary: {SLATE} !important;
  --q-accent: {AMBER} !important;
  --q-dark: {INK} !important;
  --q-positive: {TEAL} !important;
  --q-negative: {DANGER} !important;
  --q-info: {SLATE} !important;
  --q-warning: {AMBER} !important;
}}

/* ---------------------------------------------------------------- *
 * The design spec's own rules, verbatim.
 *
 * The components emit the spec's class names (``nav-bar``, ``logo``,
 * ``nav-btn``, ``active``, ``download-btn``) alongside the ``dr-*`` ones, so
 * these rules apply exactly as written in the brief.
 * ---------------------------------------------------------------- */

/* Primary buttons — every q-btn that is not a download or nav button. */
.q-btn.bg-primary,
.q-btn[color="primary"],
.q-btn:not(.download-btn):not(.nav-btn) {{
  background: var(--ink) !important;
  color: var(--surface) !important;
  border: none !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  padding: 0.55rem 1.4rem !important;
  transition: background 0.15s ease;
  text-transform: none !important;
}}
.q-btn.bg-primary:hover,
.q-btn[color="primary"]:hover,
.q-btn:not(.download-btn):not(.nav-btn):hover {{
  background: var(--amber) !important;
  color: var(--ink) !important;
}}

/* Download buttons. */
.q-btn.download-btn {{
  background: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  text-transform: none !important;
}}
.q-btn.download-btn:hover {{
  border-color: var(--teal) !important;
  color: var(--teal) !important;
}}

/* Nav bar. */
.nav-bar {{
  background: var(--ink) !important;
  border-bottom: 4px solid var(--amber) !important;
  padding: 12px 24px;
}}
.nav-bar .logo {{
  font-family: var(--serif);
  color: var(--surface);
  font-weight: 600;
  font-size: 1.4rem;
}}
.q-btn.nav-btn {{
  background: transparent !important;
  color: var(--slate-light) !important;
  border: none !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  padding: 0.5rem 1.2rem !important;
  text-transform: none !important;
}}
.q-btn.nav-btn:hover {{
  background: var(--surface) !important;
  color: var(--ink) !important;
}}
.q-btn.nav-btn.active {{
  background: var(--amber) !important;
  color: var(--ink) !important;
}}

/* File upload drop zone. */
.q-uploader {{
  background: var(--surface) !important;
  border: 1.5px dashed var(--slate-light) !important;
  border-radius: 8px !important;
}}
.q-uploader:hover {{ border-color: var(--amber) !important; }}

/* Cards. */
.q-card, .card {{
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
}}

/* Form fields. */
.q-field__control {{
  background: var(--surface) !important;
  border-radius: 6px !important;
}}
.q-field--outlined .q-field__control:before {{ border-color: var(--line) !important; }}
.q-field--focused .q-field__control:after {{ border-color: var(--teal) !important; }}

/* Tabs. */
.q-tab--active .q-tab__label {{
  color: var(--ink) !important;
  font-weight: 600 !important;
}}
.q-tab__indicator {{ background: var(--amber) !important; }}

/* Headings, spelled out for Quasar's own heading utility classes. */
h1, h2, h3, h4, .text-h1, .text-h2, .text-h3, .text-h4 {{
  font-family: var(--serif) !important;
  font-weight: 600 !important;
  color: var(--ink) !important;
}}

/* The spec's drawer rule, in addition to the dr-sidebar one above. */
.q-drawer, .q-drawer__content {{
  background: var(--surface) !important;
  border-right: 1px solid var(--line) !important;
}}
.q-drawer .q-item, .q-drawer .q-item__label {{ color: var(--ink) !important; }}

/* Catch-all: anything still carrying Quasar's primary colour as a utility. */
.text-primary {{ color: var(--ink) !important; }}
.bg-primary {{ background: var(--ink) !important; }}
.text-secondary {{ color: var(--slate) !important; }}
.q-linear-progress__model, .q-linear-progress__track {{ color: var(--amber) !important; }}
.q-spinner {{ color: var(--amber) !important; }}
"""


def apply_quasar_brand() -> None:
    """Point Quasar's own JS-level theme at the Warm Editorial palette.

    The stylesheet sets the ``--q-*`` custom properties, which covers anything
    Quasar styles from CSS. This covers the rest: Quasar also serialises a
    brand config that components resolving a colour in JavaScript read, and
    that config defaults to Quasar's stock blue. Called on every page build so
    no entry point — including a test harness calling ``ui.run`` directly —
    can serve the stock palette.
    """
    from nicegui import app

    app.colors(
        primary=INK,
        secondary=SLATE,
        accent=AMBER,
        dark=INK,
        positive=TEAL,
        negative=DANGER,
        info=SLATE,
        warning=AMBER,
    )


def inject_theme() -> None:
    """Add the fonts and the stylesheet to the page being built.

    Called once from ``layout.page_shell``, so every route is styled whether or
    not its author remembered to ask.
    """
    from nicegui import ui

    apply_quasar_brand()
    ui.add_head_html(FONT_LINK)
    ui.add_head_html(f"<style>{STYLESHEET}</style>")


def button(label: str = "", **kwargs):
    """A primary button in the house style.

    The spec's ``.q-btn:not(.download-btn):not(.nav-btn)`` rule styles this by
    default, so it needs no marker class of its own — only the two exclusions
    to opt *out* of.

    ``color=None`` is deliberate. NiceGUI defaults a button to Quasar's
    ``primary`` colour, which makes Quasar apply its ``bg-primary`` and
    ``text-white`` utilities. Those live in Quasar's ``quasar_importants``
    cascade layer, and CSS reverses layer precedence for ``!important``
    declarations — so a layered ``!important`` utility beats our unlayered
    ``!important`` rule no matter how specific it is. Leaving the prop off
    removes the competing declarations entirely and lets the stylesheet win.
    """
    from nicegui import ui

    kwargs.setdefault("color", None)
    return ui.button(label, **kwargs).props("unelevated no-caps")


def download_button(label: str = "", **kwargs):
    """A download button in the house style, matched by ``.download-btn``.

    ``color=None`` for the same reason as :func:`button`: a Quasar colour prop
    would attach a layered ``!important`` utility that outranks this rule.
    """
    from nicegui import ui

    kwargs.setdefault("color", None)
    return ui.button(label, **kwargs).classes("download-btn").props("unelevated no-caps")
