"""Abstract adapter contract shared by every ingestion format.

Adapters are deliberately dumb: they take a path (or raw bytes) and return a
DataFrame of strings, with no cleaning or type coercion. Cleaning stays in
``app_files.cleaners`` so that every format reaches the cleaner in the same
shape — that is what makes "a PDF and a CSV of the same data produce identical
output" achievable.
"""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd


class UnsupportedFormatError(ValueError):
    """Raised when no adapter can handle the given file."""


class Adapter(ABC):
    """Read a single file format into a DataFrame.

    Subclasses implement :meth:`read`. ``extensions`` lists the lowercase file
    suffixes (including the dot) the adapter claims.
    """

    extensions: tuple[str, ...] = ()
    name: str = "adapter"

    @abstractmethod
    def read(
        self, source: str | Path | BinaryIO | bytes, extension: str | None = None
    ) -> pd.DataFrame:
        """Return the file contents as a DataFrame.

        Implementations must return ``dtype=str``-like frames (all values
        stringified) so downstream cleaning behaves identically per format.

        ``extension`` is the caller-declared suffix (e.g. from an upload's
        ``filename=``). It matters only for formats that share one adapter and
        branch on the suffix; see :meth:`_extension_of`.
        """

    # -- helpers shared by concrete adapters -----------------------------

    @staticmethod
    def _as_bytes(source: str | Path | BinaryIO | bytes) -> bytes:
        """Normalise any supported input into raw bytes."""
        if isinstance(source, bytes):
            return source
        if isinstance(source, (str, Path)):
            return Path(source).read_bytes()
        if hasattr(source, "read"):
            data = source.read()
            return data.encode("utf-8") if isinstance(data, str) else data
        raise UnsupportedFormatError(f"Cannot read from {type(source).__name__}")

    @staticmethod
    def _stringify(frame: pd.DataFrame) -> pd.DataFrame:
        """Force every column to blank-free strings for uniform cleaning."""
        frame = frame.copy()
        frame.columns = [str(column).strip() for column in frame.columns]
        for column in frame.columns:
            frame[column] = frame[column].map(
                lambda value: "" if value is None or value is pd.NaT else str(value).strip()
            )
        return frame

    @staticmethod
    def _extension_of(source: str | Path | BinaryIO | bytes, declared: str | None = None) -> str:
        """The suffix to dispatch on: the caller's declaration wins, else the path.

        Raw bytes carry no suffix, so an upload that arrives as
        ``read_any(data, filename="x.xls")`` must pass the name down or the
        adapter cannot tell ``.xls`` from ``.xlsx``, or ``.tsv`` from ``.csv``.
        """
        if declared:
            return declared if declared.startswith(".") else f".{declared}"
        return Path(str(source)).suffix.lower() if isinstance(source, (str, Path)) else ""
