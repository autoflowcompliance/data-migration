"""Rule builder page for the original CRM app.

``app_files/pages/`` is Streamlit's auto-discovered multipage directory for
``streamlit run app_files/app.py``. Each page script runs independently, so
setting page config here affects only this page.

The builder itself lives in :mod:`app_files.interface.web.rule_builder_view`,
shared with the new web UI, so the two apps cannot drift apart.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app_files.interface.web.rule_builder_view import render

st.set_page_config(page_title="Rule builder", page_icon="✅", layout="wide")

render()