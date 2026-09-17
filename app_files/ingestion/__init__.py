"""Ingestion layer: read any supported file format into a DataFrame."""

from app_files.ingestion.base import Adapter, UnsupportedFormatError
from app_files.ingestion.registry import ADAPTERS, available_extensions, get_adapter, read_any

__all__ = [
    "ADAPTERS",
    "Adapter",
    "UnsupportedFormatError",
    "available_extensions",
    "get_adapter",
    "read_any",
]