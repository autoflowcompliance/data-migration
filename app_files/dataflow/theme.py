"""Shared visual theme for DataFlow.

Uses st.html(), never st.markdown(unsafe_allow_html=True) — the latter runs
content through Streamlit's markdown parser, which does not reliably render
<style> blocks and can cause raw CSS to display as literal visible text.
This has been a confirmed, repeated bug in this exact codebase; st.html()
injects raw HTML/CSS directly with no markdown parsing. Requires
Streamlit >= 1.31.

A self-contained copy rather than a shared module: the NiceGUI web interface
must stay runnable from the same checkout, so neither UI imports the other's
theme.
"""

from __future__ import annotations

import streamlit as st

TOKENS = """
:root{
    --ink:#2B2420; --ink-soft:#3A322B; --paper:#F5F0E6; --surface:#FDFBF7;
    --slate:#6B6255; --slate-light:#9A9182; --line:#E4DCC8;
    --amber:#C97A2E; --amber-soft:#F3E3D0;
    --teal:#2C7A6B; --teal-soft:#DCEAE7;
    --danger:#B0473D; --danger-soft:#F3DEDA;
    --ok:#2C7A6B; --warn:#C97A2E; --bad:#B0473D;
}
"""


def inject_theme() -> None:
    st.html(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
        <style>
        {TOKENS}
        html, body, [class*="css"] {{ font-family:'Inter', -apple-system, sans-serif; }}
        .stApp {{ background:var(--paper); }}
        #MainMenu, footer, header[data-testid="stHeader"] {{ background:transparent; }}
        .block-container {{ padding-top:1.8rem; max-width:1080px; }}
        h1, h2, h3, h4 {{ color:var(--ink) !important; font-weight:600 !important; }}

        section[data-testid="stSidebar"] {{ background:var(--surface) !important; border-right:1px solid var(--line); }}
        section[data-testid="stSidebar"] * {{ color:var(--ink) !important; }}

        .stButton > button {{
            background:var(--ink) !important; color:var(--surface) !important; border:none !important;
            border-radius:6px !important; font-weight:600 !important; padding:.55rem 1.4rem !important;
            transition:background .15s ease;
        }}
        .stButton > button:hover {{ background:var(--amber) !important; color:var(--ink) !important; }}

        .stDownloadButton > button {{
            background:var(--surface) !important; color:var(--ink) !important;
            border:1px solid var(--line) !important; border-radius:6px !important; font-weight:600 !important;
        }}
        .stDownloadButton > button:hover {{ border-color:var(--teal) !important; color:var(--teal) !important; }}

        [data-testid="stFileUploaderDropzone"] {{
            background:var(--surface) !important; border:1.5px dashed var(--slate-light) !important;
            border-radius:8px !important;
        }}
        [data-testid="stFileUploaderDropzone"]:hover {{ border-color:var(--amber) !important; }}
        </style>
        """
    )