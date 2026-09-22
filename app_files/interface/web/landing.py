"""Serve the marketing landing page at ``/``.

The app itself lives at ``/demo``; ``/`` is the public landing page. It is a
standalone document — its own ``<head>``, its own stylesheet — and it must not
be wrapped in the app shell, so it is returned as raw HTML from a FastAPI route
rather than built as a NiceGUI element tree.

``ui.html`` is not an option here: the page carries a ``<script>`` block, which
``ui.html`` rejects outright ("HTML elements must not contain <script> tags"),
and an element tree would be injected into NiceGUI's own body instead of being
returned as a document with the page's ``<title>``.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import app

REPO_ROOT = Path(__file__).resolve().parents[3]
LANDING_FILE = REPO_ROOT / "site" / "index.html"

_registered: list[bool] = []


def register_landing_route() -> None:
    """Mount ``GET /``, at most once.

    Registration order matters. NiceGUI appends its own routes when ``ui.run``
    builds the app, and Starlette matches in registration order; a raw route
    added afterwards still wins here because nothing in this app registers a
    catch-all, but registering before ``ui.run`` is the arrangement that does
    not depend on that.
    """
    if _registered:
        return
    _registered.append(True)

    @app.get("/")
    def serve_landing():
        from fastapi import Response

        if not LANDING_FILE.is_file():
            return Response(
                "<!DOCTYPE html><html><head><title>DataFlow</title></head>"
                "<body><p>The landing page is missing from this build. "
                'The app itself is at <a href="/demo">/demo</a>.</p></body></html>',
                media_type="text/html",
                status_code=404,
            )
        return Response(
            LANDING_FILE.read_text(encoding="utf-8"), media_type="text/html"
        )
