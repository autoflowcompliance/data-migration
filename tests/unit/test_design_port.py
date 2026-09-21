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
