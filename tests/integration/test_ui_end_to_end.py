"""End-to-end tests that drive the real NiceGUI app.

``test_web_interface.py`` exercises the ``state`` helpers that the pages
delegate to. These tests go further: they render the pages in a live NiceGUI
runtime, click the controls, and assert on what reaches the screen. That is the
only way to catch a page that imports cleanly and then 500s the moment a user
opens it.

NiceGUI's ``user`` fixture runs ``main.py`` once per process, and the harness
drops the routes it registered between tests — so only the first test gets
working pages. The ``app_user`` fixture below boots the app the same way the
library does, but registers the pages explicitly: it imports the route package
*after* the reset, which re-runs the ``@ui.page`` decorators for every test.

It builds the simulation by hand rather than calling the library's
``user_simulation`` because that helper runs its setup and the app's entry
point in one step, leaving no point at which to re-import the routes.
"""

from __future__ import annotations

import importlib
import os
import re
import sys

import httpx
import pytest
from nicegui import core, ui
from nicegui.testing import User
from nicegui.testing.general import nicegui_reset_globals, prepare_simulation

ROUTES = "app_files.interface.web.routes"


@pytest.fixture
async def app_user():
    """A simulated browser on the real app, with the pages freshly registered."""
    for name in list(sys.modules):
        if name.startswith(ROUTES):
            del sys.modules[name]

    # Marks this as a simulated run, so ``ui.run`` wires up the in-process
    # server the simulated user talks to instead of a real socket.
    os.environ["NICEGUI_USER_SIMULATION"] = "true"
    try:
        with nicegui_reset_globals():
            prepare_simulation()
            ui.run(storage_secret="test secret", reload=False, show=False)
            # After the reset: importing the package runs the page decorators.
            importlib.import_module(ROUTES)
            async with core.app.router.lifespan_context(core.app):
                transport = httpx.ASGITransport(core.app)
                async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                    yield User(client)
    finally:
        os.environ.pop("NICEGUI_USER_SIMULATION", None)


@pytest.fixture
async def raw_http():
    """A plain HTTP client on the same in-process app.

    Separate from ``app_user`` because the simulated ``User`` only sees
    elements that arrive over the websocket. The design tokens travel in the
    initial HTML response's ``<head>``, so verifying them needs a real GET.
    """
    for name in list(sys.modules):
        if name.startswith(ROUTES):
            del sys.modules[name]

    os.environ["NICEGUI_USER_SIMULATION"] = "true"
    try:
        with nicegui_reset_globals():
            prepare_simulation()
            ui.run(storage_secret="test secret", reload=False, show=False)
            importlib.import_module(ROUTES)
            async with core.app.router.lifespan_context(core.app):
                transport = httpx.ASGITransport(core.app)
                async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                    yield client
    finally:
        os.environ.pop("NICEGUI_USER_SIMULATION", None)


async def test_every_route_renders_the_app_shell(app_user):
    for path in ["/demo", "/upload", "/results", "/templates", "/settings",
                 "/batch", "/branding", "/verify"]:
        await app_user.open(path)
        assert app_user.find("DataFlow").elements, f"{path} did not render the shell"


async def test_the_served_html_carries_the_design_tokens(raw_http):
    """The tokens must be in the *response body*, not just in the source.

    A previous port added every component rule yet the deployed page still
    rendered Quasar blue, because nothing asserted on the bytes a browser
    actually receives. This checks the served HTML for the palette and the
    Quasar brand override, on every route.
    """
    for path in ["/demo", "/upload", "/results", "/templates", "/settings",
                 "/batch", "/branding", "/verify"]:
        response = await raw_http.get(path)
        assert response.status_code == 200, f"{path} returned {response.status_code}"
        html = response.text
        for needle in (
            "DataFlow",
            "--ink: #2B2420",
            "--paper: #F5F0E6",
            "--amber: #C97A2E",
            "--teal: #2C7A6B",
            "Fraunces",
            "--q-primary: #2B2420",
        ):
            assert needle in html, f"{needle!r} missing from the served {path}"
        assert "DataReady" not in html, f"the old product name is still served on {path}"


async def test_the_nav_bar_carries_the_spec_classes(raw_http):
    """The bar and its buttons must reach the browser with the spec's classes."""
    html = (await raw_http.get("/demo")).text
    for class_name in ("nav-bar", "nav-btn", "logo"):
        assert class_name in html, f"the served nav bar is missing .{class_name} class"


async def test_the_served_html_carries_no_stock_quasar_blue(raw_http):
    """The stock Quasar blue must not reach the browser by any route.

    Two independent leaks put it there once: the bg-primary utility Quasar
    attaches to any button given a color prop, and the default brand config
    serialised into window.vue_config. Both are visible in the served HTML,
    so both are checked here rather than trusting the screenshot.
    """
    for path in ["/demo", "/upload", "/settings", "/branding"]:
        html = (await raw_http.get(path)).text
        for stock in ("#5898d4", "#26a69a", "#9c27b0"):
            assert stock not in html, f"stock Quasar colour {stock} is served on {path}"
        # A button carrying color="primary" makes Quasar attach the layered
        # bg-primary utility, which outranks the stylesheet. Quasar's own
        # loading-bar config legitimately names "primary", so match a button's
        # own props rather than the bare string.
        for props in re.findall(r'"tag":"q-btn","class":\[[^\]]*\],"props":\{[^}]*\}', html):
            assert '"color":"primary"' not in props, (
                f"a button on {path} still asks Quasar for its primary colour"
            )


async def test_a_crm_sample_run_reaches_the_results_page(app_user):
    await app_user.open("/upload")
    app_user.find("Try it with sample data").click()

    await app_user.should_see("Clean data")
    await app_user.should_see("Issues")
    assert app_user.find("Quality score").elements


async def test_the_run_counter_is_absent_on_a_fresh_visit(app_user):
    """A first-time visitor must not be greeted with a limit.

    The counter used to render "3 of 3 demo runs left" before anything had been
    run, which announces a restriction rather than showing the product.
    """
    await app_user.open("/upload")
    app_user.find("Upload your file")
    await app_user.should_not_see("demo runs left")
    await app_user.should_not_see("used your")


async def test_the_sample_path_never_raises_the_counter(app_user):
    """The sample consumes no run, so it must not surface an allowance either.

    Clicking the sample button is the guided tour; a visitor who only clicks it
    has spent nothing, and a "3 of 3 left" banner here was pure noise.
    """
    await app_user.open("/upload")
    app_user.find("Try it with sample data").click()
    await app_user.should_see("Clean data")

    await app_user.should_not_see("demo runs left")


async def test_a_reconciliation_sample_run_reaches_the_dashboard(app_user):
    """The sample must follow the job type, not the config selector.

    Following the selector alone ran a CRM migration on this tab and answered
    with mapping output in place of the reconciliation dashboard.
    """
    await app_user.open("/upload")
    app_user.find("Bank reconciliation").click()
    await app_user.should_see("Bank statement")
    app_user.find("Try it with sample data").click()

    await app_user.should_see("Matched")
    assert app_user.find("Missing from books").elements


async def test_the_buy_form_submits_and_shows_a_unique_reference(app_user):
    """A filled-in form must reach the confirmation page with its own code.

    The buyer used to be sent to a page quoting the same static reference as
    every other buyer, which made the incoming payment unreconcilable.
    """
    from app_files.interface.web.routes.buy import buy_reference

    await app_user.open("/buy")
    await app_user.should_see("Get your data cleaned")
    app_user.find("Name *").type("Jane Doe")
    app_user.find("Email *").type("jane@example.com")
    app_user.find("Request an invoice").click()

    await app_user.should_see("Thanks, Jane Doe.")
    # The page must quote this buyer's own code, not the shared fallback.
    expected = buy_reference("jane@example.com")
    await app_user.should_see(expected)
    assert expected != "DF-2026-001"


async def test_a_name_with_an_ampersand_survives_the_redirect(app_user):
    """The regression: an unencoded name truncated at the ``&``.

    ``/buy/confirmed?name=A&b`` arrives as ``name=A``, so the buyer's own name
    was cut in half on the page thanking them by name.
    """
    await app_user.open("/buy")
    app_user.find("Name *").type("Smith & Wesson")
    app_user.find("Email *").type("smith@example.com")
    app_user.find("Request an invoice").click()

    await app_user.should_see("Thanks, Smith & Wesson.")


async def test_the_buy_form_rejects_a_missing_name_or_email(app_user):
    await app_user.open("/buy")
    app_user.find("Email *").type("jane@example.com")
    app_user.find("Request an invoice").click()

    await app_user.should_see("Name and email are required.")


async def test_both_purchase_pages_load_the_theme_and_a_way_back(raw_http):
    """The pages must not be orphans: styled like the app, and escapable.

    A purchase page that renders in bare NiceGUI defaults looks like a
    phishing page, which is the last impression a buyer should get.
    """
    for path in ["/buy", "/buy/confirmed"]:
        response = await raw_http.get(path)
        assert response.status_code == 200, f"{path} returned {response.status_code}"
        html = response.text
        for needle in ("DataFlow", "Fraunces", "--ink: #2B2420", "Back to DataFlow"):
            assert needle in html, f"{needle!r} missing from the served {path}"


async def test_the_confirmation_page_quotes_the_reference_from_the_url(raw_http):
    response = await raw_http.get("/buy/confirmed?name=Jane&ref=DF-ABC123")
    assert response.status_code == 200
    assert "DF-ABC123" in response.text
