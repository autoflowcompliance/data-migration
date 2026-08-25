"""Netlify Function handler for the AutoFlow data migration tool.

This is the entry point for Netlify Functions.
"""
import sys
from pathlib import Path

# Add parent directory to path to import the main app
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from mangum import Mangum
from app import app

# ASGI to Lambda adapter
handler = Mangum(app)