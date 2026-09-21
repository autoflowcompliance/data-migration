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


async def test_every_route_renders_the_app_shell(app_user):
    for path in ["/", "/upload", "/results", "/templates", "/settings",
                 "/batch", "/branding", "/verify"]:
        await app_user.open(path)
        assert app_user.find("DataReady").elements, f"{path} did not render the shell"


async def test_a_crm_sample_run_reaches_the_results_page(app_user):
    await app_user.open("/upload")
    app_user.find("Try it with sample data").click()

    await app_user.should_see("Clean data")
    await app_user.should_see("Issues")
    assert app_user.find("Quality score").elements


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
