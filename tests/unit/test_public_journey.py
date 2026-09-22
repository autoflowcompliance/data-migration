"""The public journey: landing at ``/``, app at ``/demo``, purchase at ``/buy``.

These guard the shape of the URL space itself. The failure they catch is a
visitor who reaches ``/`` expecting the product and finds either a 404 or the
app shell wearing a marketing URL, the quieter one where the landing page's
CTAs point at a domain that was never deployed, and the footer's Privacy and
Terms links pointing at pages that were never written.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
from pathlib import Path

import pytest
from nicegui import app
from nicegui.testing.general import nicegui_reset_globals, prepare_simulation

from app_files.interface.web import landing
from app_files.interface.web.routes import (
    batch, branding, buy, home, results, settings, templates, upload, verify,
)

SITE_DIR = Path(__file__).resolve().parents[2] / "site"
SITE_INDEX = SITE_DIR / "index.html"

APP_ROUTE_MODULES = (batch, branding, buy, home, results, settings, templates, upload, verify)

ROUTES = "app_files.interface.web.routes"

PUBLIC_PAGES = ("/", "/privacy.html", "/terms.html")


@pytest.fixture
def mounted_public_paths(monkeypatch):
    """The public document routes actually present on the FastAPI app."""
    monkeypatch.setattr(landing, "_registered", [])
    with nicegui_reset_globals():
        prepare_simulation()
        landing.register_landing_route()
        return [getattr(route, "path", None) for route in app.routes]


@pytest.fixture
def registered_routes():
    """The paths the app actually registers, in a fresh NiceGUI runtime."""
    for name in list(sys.modules):
        if name.startswith(ROUTES):
            del sys.modules[name]

    os.environ["NICEGUI_USER_SIMULATION"] = "true"
    try:
        with nicegui_reset_globals():
            prepare_simulation()
            importlib.import_module(ROUTES)
            return [getattr(route, "path", None) for route in app.routes]
    finally:
        os.environ.pop("NICEGUI_USER_SIMULATION", None)


def test_the_app_home_is_the_demo_route(registered_routes):
    """``/`` belongs to the landing page; the app home moved to ``/demo``."""
    assert "/demo" in registered_routes


def test_no_app_route_claims_the_root_path(registered_routes):
    """``/`` is served by the raw landing route, never by a NiceGUI page."""
    assert "/" not in registered_routes


def test_the_nicegui_pages_still_all_register(registered_routes):
    for path in ("/demo", "/upload", "/templates", "/batch", "/results",
                 "/branding", "/settings", "/verify", "/buy", "/buy/confirmed"):
        assert path in registered_routes, f"{path} is no longer registered"


def test_the_landing_file_is_the_one_committed_in_the_repo():
    assert landing.LANDING_FILE == SITE_INDEX
    assert landing.LANDING_FILE.is_file()


def test_every_nav_home_entry_points_at_the_demo_route():
    """A leftover ``/`` here sends an app user back out to the marketing page."""
    for module in APP_ROUTE_MODULES:
        for label, route in getattr(module, "NAV", []):
            if label == "Home":
                assert route == "/demo", f"{module.__name__} Home points at {route!r}"


def test_the_landing_page_hero_cta_points_at_the_demo_route():
    html = SITE_INDEX.read_text()
    hero = re.search(r'<a\s+href="([^"]+)"[^>]*>\s*Try the demo\s*</a>', html)
    assert hero, "the landing page has no 'Try the demo' CTA"
    assert hero.group(1) == "/demo", f"the demo CTA points at {hero.group(1)!r}"


def test_the_landing_page_has_no_undeployed_demo_domain():
    assert "demo.dataflow.io" not in SITE_INDEX.read_text()


def test_the_landing_page_is_a_standalone_document():
    """It is served raw, so it must carry its own head and title."""
    html = SITE_INDEX.read_text()
    assert "<!DOCTYPE html>" in html
    assert "<title>DataFlow" in html
    assert "<style>" in html


# ------------------------------------------------------------ privacy & terms
# The footer has always linked these; before they existed the landing page
# advertised a privacy policy and terms of sale that 404'd.

def test_every_public_page_maps_to_a_file_that_exists():
    for route, file in landing.PUBLIC_PAGES.items():
        assert file.is_file(), f"{route} points at the missing file {file}"
        assert file.parent == SITE_DIR


def test_all_three_public_pages_are_mounted(mounted_public_paths):
    for route in PUBLIC_PAGES:
        assert route in mounted_public_paths, f"{route} is not mounted"


def test_the_public_routes_are_mounted_once(mounted_public_paths):
    """Registering twice would shadow the first mount with an identical one."""
    for route in PUBLIC_PAGES:
        assert mounted_public_paths.count(route) == 1, f"{route} mounted more than once"


def test_the_footer_links_point_at_served_pages():
    """The landing footer must not link a document that is not mounted."""
    html = SITE_INDEX.read_text()
    for route in ("/privacy.html", "/terms.html"):
        assert f'href="{route}"' in html, f"the footer does not link {route}"
        assert route in landing.PUBLIC_PAGES, f"{route} is linked but not served"


@pytest.mark.parametrize("name", ["privacy.html", "terms.html"])
def test_each_public_page_is_a_standalone_document(name):
    html = (SITE_DIR / name).read_text()
    assert "<!DOCTYPE html>" in html
    assert "<title>" in html
    assert "<style>" in html


def test_the_public_pages_carry_the_warm_editorial_tokens():
    """Same palette as the landing page, not a different-looking microsite."""
    landing_html = SITE_INDEX.read_text()
    for name in ("privacy.html", "terms.html"):
        html = (SITE_DIR / name).read_text()
        for token in ("--ink: #2B2420", "--paper: #F5F0E6", "--amber: #C97A2E",
                      "--teal: #2C7A6B", "--line: #E4DCC8"):
            assert token in landing_html, f"the landing page no longer defines {token}"
            assert token in html, f"{name} is missing the {token} token"


def test_the_privacy_page_states_the_retention_position():
    """The claims a privacy policy is actually read for."""
    html = (SITE_DIR / "privacy.html").read_text()
    for claim in ("What we collect: Nothing", "processed in memory",
                  "Nothing is written to disk", "We do not track you across the web",
                  "We do not sell data", "autoflowcompliance@outlook.com"):
        assert claim in html, f"the privacy page does not state {claim!r}"


def test_the_terms_page_states_the_commercial_terms():
    html = (SITE_DIR / "terms.html").read_text()
    for term in ("perpetual, non-exclusive, non-transferable", "$2,000", "one-time",
                 "No subscription", "within 24 hours", "30 days of email support",
                 "lifetime of the current major version", "refund the purchase in full",
                 "provided as-is", "autoflowcompliance@outlook.com"):
        assert term in html, f"the terms page does not state {term!r}"
