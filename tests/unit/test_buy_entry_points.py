"""Every "Buy" entry point must reach the purchase flow.

The failure this guards against is quiet: a demo banner whose link points at
an external checkout that was never set up, or a landing page whose CTA scrolls
to a pricing section instead of starting a purchase. Nothing 500s, and the
only symptom is a visitor who never becomes a buyer.
"""

from __future__ import annotations

import re
from pathlib import Path

from app_files.interface.web import components as c
from app_files.interface.web import layout
from app_files.interface.web.routes import buy as buy_route
from app_files.settings import DEFAULT_PURCHASE_URL, purchase_url

SITE_INDEX = Path(__file__).resolve().parents[2] / "site" / "index.html"


def test_the_default_purchase_url_is_the_apps_own_buy_route():
    assert DEFAULT_PURCHASE_URL == "/buy"
    assert purchase_url() == "/buy"


def test_an_env_override_still_wins():
    """A deployment selling through a hosted checkout must keep working."""
    override = {"DATAREADY_PURCHASE_URL": "https://buy.example.com/checkout"}
    assert purchase_url(override) == "https://buy.example.com/checkout"


def test_the_nav_carries_a_buy_link_between_settings_and_verify():
    nav = buy_route.BUY_NAV
    labels = [label for label, _ in nav]
    assert ("Buy", "/buy") in nav
    assert labels.index("Buy") == labels.index("Settings") + 1
    assert labels.index("Buy") == labels.index("Verify") - 1


def test_every_route_nav_offers_the_buy_route():
    """A missing entry makes the purchase page unreachable from that screen."""
    from app_files.interface.web.routes import (
        batch, branding, home, results, settings, templates, upload, verify,
    )

    for module in (batch, branding, home, results, settings, templates, upload, verify):
        assert ("Buy", "/buy") in module.NAV, f"{module.__name__} nav has no Buy entry"


def test_the_demo_banner_links_to_the_purchase_flow():
    html = _rendered(c.demo_banner, 3, "/buy")
    assert 'href="/buy"' in html


def test_the_exhausted_runs_note_links_to_the_purchase_flow():
    html = _rendered(c.runs_exhausted_note, "/buy", 3)
    assert 'href="/buy"' in html


def test_an_internal_buy_link_does_not_force_a_new_tab():
    """``/buy`` is in the app; opening it in a tab loses the demo session."""
    html = _rendered(c.runs_exhausted_note, "/buy", 3)
    assert 'target="_blank"' not in html


def test_an_external_checkout_still_opens_in_a_new_tab():
    html = _rendered(c.runs_exhausted_note, "https://buy.example.com", 3)
    assert 'target="_blank"' in html
    assert 'rel="noopener"' in html


def test_the_demo_footer_passes_the_resolved_purchase_url(monkeypatch):
    """The banner used to hardcode its destination, ignoring the setting."""
    seen = {}

    def spy(runs, url="/buy"):
        seen["url"] = url

    monkeypatch.setattr(c, "demo_banner", spy)
    monkeypatch.setattr(layout.c, "demo_banner", spy)
    layout._demo_footer()
    assert seen["url"] == purchase_url()


def test_the_landing_page_buy_ctas_point_at_the_buy_route():
    html = SITE_INDEX.read_text()
    hrefs = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]*[Bb]uy[^<]*)</a>', html)
    assert len(hrefs) >= 2, f"expected at least 2 Buy CTAs, found {hrefs}"
    for href, text in hrefs:
        assert href == "/buy", f"CTA {text!r} points at {href!r}"


def test_the_landing_page_has_no_stale_checkout_links():
    html = SITE_INDEX.read_text()
    assert "buy.stripe.com" not in html
    assert "dataflow.app/pricing" not in html


# ------------------------------------------------- the counter's visibility
# The demo counter is useful only once something has been spent. On a fresh
# visit it announces a limit instead of showing the product, so these pin when
# it is allowed to render at all.
def test_the_counter_is_silent_before_any_run():
    from app_files.interface.web import session as session_store
    from app_files.interface.web.routes import upload as upload_route

    session_store.reset_all()
    captured = _capture(upload_route._run_allowance_note, 3, "/buy")
    assert captured == [], "the counter rendered before a run was consumed"
    session_store.reset_all()


def test_the_counter_appears_once_a_run_is_spent():
    from app_files.interface.web import session as session_store
    from app_files.interface.web.routes import upload as upload_route

    session_store.reset_all()
    session_store.register_run()
    html = "".join(_capture(upload_route._run_allowance_note, 3, "/buy"))
    assert "2 of 3 demo runs left" in html, html
    session_store.reset_all()


def test_the_counter_switches_to_the_exhausted_message_at_the_limit():
    from app_files.interface.web import session as session_store
    from app_files.interface.web.routes import upload as upload_route

    session_store.reset_all()
    for _ in range(3):
        session_store.register_run()
    html = "".join(_capture(upload_route._run_allowance_note, 3, "/buy"))
    assert "used your 3 free demo runs" in html
    assert 'href="/buy"' in html
    session_store.reset_all()


def test_the_sample_path_never_consumes_a_run():
    """The sample must not spend an allowance, so it cannot raise the counter.

    Read from the source because the path is a closure inside the page body and
    is not callable in isolation; the two facts are one behaviour, not two.
    """
    from pathlib import Path as _Path

    from app_files.interface.web.routes import upload as upload_route

    source = _Path(upload_route.__file__).read_text()
    sample = source.split("async def load_sample")[1].split("job_type = ui.radio")[0]
    assert "register_run" not in sample, "the sample path consumes a demo run"
    assert "claim_run" not in sample, "the sample path claims a demo run"


def _capture(func, *args):
    """Whatever ``func`` renders, as a list of markup strings.

    Like ``_rendered`` but tolerates a function that legitimately renders
    nothing, which is the behaviour under test for the pre-run counter.
    """
    captured = []

    class _Ui:
        @staticmethod
        def html(markup: str) -> None:
            captured.append(markup)

    original = c.ui
    c.ui = _Ui
    try:
        func(*args)
    finally:
        c.ui = original
    return captured


def _rendered(func, *args) -> str:
    """The HTML ``func`` passes to ``ui.html``, without a running NiceGUI app.

    Fails loudly when ``func`` renders nothing, for the callers that expect a
    note to be on screen. Use ``_capture`` directly to assert on silence.
    """
    captured = _capture(func, *args)
    assert captured, f"{func.__name__} rendered nothing"
    return "".join(captured)
