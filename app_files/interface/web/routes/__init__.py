"""NiceGUI route modules. Importing this package registers every ``@ui.page`` route.

Kept out of a ``pages`` folder: that name is reserved for multipage app
entries, and nothing here should be auto-discovered as a page. Importing this
package is what registers each route, so it must stay an explicit import.
"""

from app_files.interface.web.routes import (  # noqa: F401
    batch,
    branding,
    home,
    results,
    settings,
    templates,
    upload,
    verify,
)

__all__ = [
    "batch",
    "branding",
    "home",
    "results",
    "settings",
    "templates",
    "upload",
    "verify",
]