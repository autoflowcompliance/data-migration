"""Visual rule builder page — the new web UI (LAYER 7).

The implementation lives in :mod:`app_files.interface.web.rule_builder_view` so
the original CRM app (``app_files/app.py``) can render the identical builder
from its own ``pages/`` directory. This module is only the page shell.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app_files.interface.web.rule_builder_view import render

st.set_page_config(page_title="Rule builder", page_icon="✅", layout="wide")

render()