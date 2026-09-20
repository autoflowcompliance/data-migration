"""Page modules. Importing this package registers every ``@ui.page`` route."""

from app_files.interface.web.pages import (  # noqa: F401
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