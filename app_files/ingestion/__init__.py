"""Ingestion layer: read any supported file format into a DataFrame."""

from app_files.ingestion.base import Adapter, UnsupportedFormatError
from app_files.ingestion.chunked import (
    ChunkPlan,
    MemoryCeilingExceeded,
    chunked_read,
    current_rss_bytes,
    is_large,
    iter_chunks,
    merge_outputs,
    plan_chunks,
    process_in_windows,
    read_large,
    write_in_windows,
)
from app_files.ingestion.registry import ADAPTERS, available_extensions, get_adapter, read_any

__all__ = [
    "ADAPTERS",
    "Adapter",
    "ChunkPlan",
    "MemoryCeilingExceeded",
    "UnsupportedFormatError",
    "chunked_read",
    "current_rss_bytes",
    "available_extensions",
    "get_adapter",
    "is_large",
    "iter_chunks",
    "merge_outputs",
    "plan_chunks",
    "process_in_windows",
    "read_any",
    "read_large",
    "write_in_windows",
]