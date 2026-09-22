"""The public journey: landing at ``/``, app at ``/demo``, purchase at ``/buy``.

These guard the shape of the URL space itself. The failure they catch is a
visitor who reaches ``/`` expecting the product and finds either a 404 or the
app shell wearing a marketing URL, and the quieter one where the landing page's
CTAs point at a domain that was never deployed.
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

SITE_INDEX = Path(__file__).resolve().parents[2] / "site" / "index.html"

APP_ROUTE_MODULES = (batch, branding, buy, home, results, settings, templates, upload, verify)

ROUTES = "app_files.interface.web.routes"


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
