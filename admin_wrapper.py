"""Admin Dashboard - Private Client Delivery System

Personal backend for processing paid client files locally.
Run on your own machine only — never deploy this publicly.

Usage: streamlit run admin_wrapper.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add the repository root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import and run the actual admin app
from data_migration_tool.admin import *