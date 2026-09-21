"""DataFlow — the current web UI (Streamlit).

A sibling of the NiceGUI interface under ``app_files/interface/web``. The two
share the frozen core and the licensing decisions, but not their theme or
widgets, so either can be run or removed without touching the other.

Run it with ``python -m streamlit run app_files/dataflow/app.py``, or
``python main.py`` (which is what Docker and Render use).
"""

from __future__ import annotations

__all__ = ["components", "state", "theme"]