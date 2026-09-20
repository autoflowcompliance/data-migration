"""Shared page scaffolding: navigation plus the content shell.

Split out of ``components.py`` so pages can import the shell without pulling
in the widget library, and so adding a route never means editing a page.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Sequence

from nicegui import ui

from app_files.interface.web import components as c
from app_files.interface.web.session import session

NAV = [
    ("Home", "/"),
    ("Upload", "/upload"),
    ("Templates", "/templates"),
    ("Batch", "/batch"),
    ("Results", "/results"),
    ("Branding", "/branding"),
    ("Settings", "/settings"),
    ("Verify", "/verify"),
]


@contextmanager
def page_shell(links: Sequence[tuple[str, str]] | None = None, active: str = "") -> Iterator[None]:
    """Wrap page content in the standard navigation and centred shell."""
    c.nav_bar(links or NAV, active=active)
    with ui.column().classes("dr-shell w-full gap-0"):
        yield
    _demo_footer()


def _demo_footer() -> None:
    """A quiet, always-visible mode indicator.

    The write-once conditions matter: the limits are read from disk when the
    page is built, so a user who installs a licence while the app is open sees
    the correct state the moment they navigate anywhere.
    """
    from app_files.licensing import current_mode

    licence, limits = current_mode()
    if limits.demo:
        with ui.row().classes("items-center gap-2 mt-6"):
            c.demo_badge("Demo mode")
            ui.label(
                "Up to 500 rows, 5 MB, CSV output only. Add a licence in Settings "
                "for the full tool."
            ).classes("text-xs text-gray-500")
    elif licence.email:
        ui.label(f"Licensed to {licence.email}").classes("text-xs text-gray-400 mt-6")
    session()  # touch the session so the store stays warm for this client