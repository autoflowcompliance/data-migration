"""NiceGUI route modules. Importing this package registers every ``@ui.page`` route.

Deliberately not named ``pages``: Streamlit auto-discovers a ``pages/`` folder
next to its entrypoint as multipage app entries, so keeping these here stops
``streamlit run app_files/interface/web/app.py`` from trying to execute NiceGUI
route modules as Streamlit pages.
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