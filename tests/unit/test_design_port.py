"""The design port: every token, and every Quasar control, carries the palette.

``theme.py`` and ``components.py`` are the design source of truth. These tests
exist because the failure mode is silent: a route that reaches for a raw
``ui.input`` or leaves a default Quasar colour in place renders a component
that is *wrong* without raising anything, and only a human looking at the page
would notice. Pinning the tokens and the set of overrides here means that a
regression shows up as a failed test instead.
"""

from __future__ import annotations

import pytest

from app_files.interface.web import components as c
from app_files.interface.web import theme

# The palette, stated once. If a token changes it must change here too, which
# is the point — these are the values the design was signed off against.
EXPECTED_TOKENS = {
    "--ink": "#2B2420",
    "--ink-soft": "#3A322B",
    "--paper": "#F5F0E6",
    "--surface": "#FDFBF7",
    "--slate": "#6B6255",
    "--slate-light": "#9A9182",
    "--line": "#E4DCC8",
    "--amber": "#C97A2E",
    "--amber-soft": "#F3E3D0",
    "--teal": "#2C7A6B",
}


# ------------------------------------------------------------------- tokens
@pytest.mark.parametrize("token,value", EXPECTED_TOKENS.items())
def test_every_design_token_is_in_the_stylesheet(token, value):
    assert f"{token}: {value}" in theme.STYLESHEET


def test_the_module_constants_match_the_tokens():
    """The Python side and the CSS side must not drift apart."""
    assert theme.INK == EXPECTED_TOKENS["--ink"]
    assert theme.PAPER == EXPECTED_TOKENS["--paper"]
    assert theme.SURFACE == EXPECTED_TOKENS["--surface"]
    assert theme.AMBER == EXPECTED_TOKENS["--amber"]
    assert theme.TEAL == EXPECTED_TOKENS["--teal"]


def test_no_default_quasar_indigo_survives():
    """NiceGUI's stock accent is indigo; it must never appear in the palette."""
    lowered = theme.STYLESHEET.lower()
    for stranded in ("#1976d2", "#5898d4", "#2196f3", "#027be3"):
        assert stranded not in lowered


# ---------------------------------------------------------- component rules
@pytest.mark.parametrize(
    "rule",
    [
        ".dr-nav",       # the top bar
        ".dr-card",      # metric cards
        ".dr-empty",     # empty states
        ".dr-note",      # notices
        ".dr-dropzone",  # the uploader
        ".dr-field",     # text inputs
        ".dr-tabs",      # the tab strip
        ".dr-expansion", # collapsible panels
        ".dr-radio",     # the job-type chooser
        ".dr-sidebar",   # side panel
    ],
)
def test_each_in_house_component_class_is_defined(rule):
    assert rule in theme.STYLESHEET


@pytest.mark.parametrize(
    "quasar_class",
    [
        ".q-field__control",
        ".q-menu",
        ".q-checkbox",
        ".q-toggle",
        ".q-radio",
        ".q-slider",
        ".q-tab",
        ".q-expansion-item",
        ".q-table",
        ".q-separator",
        ".q-card",
        ".q-notification",
        ".q-tooltip",
        ".q-drawer",
        ".q-dialog",
    ],
)
def test_each_quasar_control_is_reskinned(quasar_class):
    """A control with no override renders in Quasar's defaults.

    This is the list of controls the app actually uses; adding a new widget to
    a route means adding its class here and a rule to the stylesheet.
    """
    assert quasar_class in theme.STYLESHEET


# ------------------------------------------------------------- colour roles
def test_score_colour_uses_the_palette_bands():
    assert theme.score_colour(95) == theme.TEAL
    assert theme.score_colour(80) == theme.AMBER
    assert theme.score_colour(40) == theme.DANGER


def test_ok_warn_bad_are_aliases_of_the_palette():
    assert theme.OK == theme.TEAL
    assert theme.WARN == theme.AMBER
    assert theme.BAD == theme.DANGER


# ------------------------------------------------------------ form helpers
def test_form_helpers_exist_for_every_control_the_routes_need():
    """Routes call these rather than raw NiceGUI widgets, so the class sticks."""
    for name in ("field", "number_field", "textarea", "select", "tabs", "expansion"):
        assert callable(getattr(c, name)), f"components.{name} is missing"


def test_notice_helpers_exist_for_the_demo_states():
    for name in ("info_note", "demo_banner", "runs_exhausted_note", "report_embed"):
        assert callable(getattr(c, name)), f"components.{name} is missing"


# ------------------------------------------------ Quasar brand colour override
def test_quasar_brand_colours_are_repointed_at_the_palette():
    """Quasar derives most of its own colours from ``--q-primary``.

    Without this the components styled individually look right while
    everything else — progress bars, spinners, spinners, ``.text-primary`` —
    renders in Quasar's stock blue. That is the bug that reached the deployed
    site, so the override is pinned here rather than trusted.
    """
    sheet = theme.STYLESHEET
    assert "--q-primary:" in sheet
    assert f"--q-primary: {theme.INK}" in sheet
    assert f"--q-positive: {theme.TEAL}" in sheet
    assert f"--q-accent: {theme.AMBER}" in sheet


# ------------------------------------------------------- spec class coverage
@pytest.mark.parametrize(
    "spec_class",
    [".nav-bar", ".nav-btn", ".download-btn", ".q-btn.nav-btn.active"],
)
def test_the_specs_class_names_are_styled(spec_class):
    """The brief styles these exact selectors, so they must exist verbatim."""
    assert spec_class in theme.STYLESHEET


def test_nav_bar_emits_the_spec_class_names():
    """A nav bar rendered with only ``dr-*`` classes would not match the spec.

    Asserted against the source because the classes are applied at build time;
    ``nav_bar`` needs a running NiceGUI context to call.
    """
    import inspect

    source = inspect.getsource(c.nav_bar)
    for name in ("nav-bar", "logo", "nav-btn", "active"):
        assert name in source, f"nav_bar does not emit the spec class {name!r}"
    assert "DataFlow" in source


def test_the_step_indicator_is_actually_used_by_a_route():
    """A spec'd component nobody calls is a component that does not ship.

    ``step_indicator`` was defined but no route rendered it, so the teal/amber/
    line stepper never appeared in the browser. This pins the wiring.
    """
    import inspect

    from app_files.interface.web.routes import upload

    assert upload.WORKFLOW_STEPS == ["Upload", "Configure", "Process", "Review"]
    source = inspect.getsource(upload)
    assert "step_indicator" in source, "the upload route no longer renders the stepper"


def test_brand_buttons_do_not_ask_for_a_quasar_colour():
    """A Quasar ``color`` prop defeats the stylesheet, so the helpers must not set one.

    NiceGUI defaults a button to Quasar's ``primary`` colour, which makes
    Quasar apply its ``bg-primary``/``text-white`` utilities. Those live in
    Quasar's ``quasar_importants`` cascade layer and CSS *reverses* layer
    precedence for ``!important`` declarations, so the layered utility wins
    over our unlayered ``!important`` rule regardless of specificity. The
    visible symptom was a nav button whose ``.active`` amber background never
    painted. Asserting on the component's props catches a regression without a
    browser.
    """
    import inspect

    for helper in (theme.button, theme.download_button):
        source = inspect.getsource(helper)
        assert 'kwargs.setdefault("color", None)' in source, (
            f"{helper.__name__} lets Quasar's colour prop win over the stylesheet"
        )


def test_quasar_brand_config_is_repointed_at_the_palette():
    """Quasar's JS-level brand colours must match the CSS variables.

    ``theme.STYLESHEET`` sets the ``--q-*`` custom properties, but Quasar also
    serialises a brand config that JavaScript-side styling reads. Leaving it
    alone served the stock blue (``#5898d4``) in ``window.vue_config`` even
    though the CSS was warm.
    """
    import inspect

    source = inspect.getsource(theme.apply_quasar_brand)
    for token in ("primary=INK", "accent=AMBER", "positive=TEAL", "negative=DANGER"):
        assert token in source, f"the Quasar brand config is not set from {token}"
    assert "app.colors(" in source

    # It has to run on every page build, not only from the launcher, or a route
    # rendered by another entry point serves the stock palette.
    assert "apply_quasar_brand()" in inspect.getsource(theme.inject_theme)
