"""Serve the public marketing pages: ``/``, ``/privacy.html``, ``/terms.html``.

The app itself lives at ``/demo``; everything under ``site/`` is a standalone
document — its own ``<head>``, its own stylesheet — and must not be wrapped in
the app shell, so these are returned as raw HTML from FastAPI routes rather
than built as NiceGUI element trees.

``ui.html`` is not an option here: the landing page carries a ``<script>``
block, which ``ui.html`` rejects outright ("HTML elements must not contain
<script> tags"), and an element tree would be injected into NiceGUI's own body
instead of being returned as a document with the page's ``<title>``.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import app

REPO_ROOT = Path(__file__).resolve().parents[3]
SITE_DIR = REPO_ROOT / "site"

LANDING_FILE = SITE_DIR / "index.html"

# Public document routes. Every entry is a file under ``site/`` served verbatim
# at the given path, so adding a page is one line here and one file there.
PUBLIC_PAGES: dict[str, Path] = {
    "/": SITE_DIR / "index.html",
    "/privacy.html": SITE_DIR / "privacy.html",
    "/terms.html": SITE_DIR / "terms.html",
}

_registered: list[bool] = []


def register_landing_route() -> None:
    """Mount the public document routes, at most once.

    Registration order matters. NiceGUI appends its own routes when ``ui.run``
    builds the app, and Starlette matches in registration order; a raw route
    added afterwards still wins here because nothing in this app registers a
    catch-all, but registering before ``ui.run`` is the arrangement that does
    not depend on that.
    """
    if _registered:
        return
    _registered.append(True)

    for route, file in PUBLIC_PAGES.items():
        app.get(route)(_make_page_handler(file))


def _make_page_handler(file: Path):
    """Build the handler for one page.

    A factory rather than a loop-body closure with a default argument: FastAPI
    inspects the handler's signature and would read a ``file: Path = ...``
    parameter as a query string, and a plain loop closure would capture the
    loop variable, leaving every route serving whichever page registered last.
    """

    def serve_page():
        from fastapi import Response

        if not file.is_file():
            return Response(
                "<!DOCTYPE html><html><head><title>DataFlow</title></head>"
                f"<body><p>{file.name} is missing from this build. "
                'The app itself is at <a href="/demo">/demo</a>.</p></body></html>',
                media_type="text/html",
                status_code=404,
            )
        return Response(file.read_text(encoding="utf-8"), media_type="text/html")

    return serve_page
