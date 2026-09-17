"""Registry: pick the right adapter for a file and read it.

Detection is by file extension. ``read_any`` accepts a path, an open file
object (Streamlit's ``UploadedFile`` behaves like one) or raw bytes; when raw
bytes are passed the caller must supply ``filename=`` so the extension is known.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

from app_files.ingestion.base import Adapter, UnsupportedFormatError
from app_files.ingestion.csv_adapter import CSVAdapter
from app_files.ingestion.excel_adapter import ExcelAdapter
from app_files.ingestion.json_adapter import JSONAdapter
from app_files.ingestion.pdf_adapter import PDFAdapter

ADAPTERS: tuple[Adapter, ...] = (
    CSVAdapter(),
    ExcelAdapter(),
    JSONAdapter(),
    PDFAdapter(),
)

_EXTENSION_INDEX: dict[str, Adapter] = {
    extension: adapter for adapter in ADAPTERS for extension in adapter.extensions
}


def available_extensions() -> list[str]:
    return sorted(_EXTENSION_INDEX)


def get_adapter(source: str | Path) -> Adapter:
    """Return the adapter registered for ``source``'s extension."""
    extension = Path(str(source)).suffix.lower()
    try:
        return _EXTENSION_INDEX[extension]
    except KeyError:
        raise UnsupportedFormatError(
            f"No reader for '{extension or 'unknown'}'. Supported: "
            f"{', '.join(available_extensions())}"
        ) from None


def read_any(
    source: str | Path | BinaryIO | bytes, filename: str | None = None
) -> pd.DataFrame:
    """Read ``source`` with the adapter matching its extension.

    Args:
        source: path, file object, or raw bytes.
        filename: required when ``source`` is raw bytes, so the format is known.
    """
    if isinstance(source, (str, Path)):
        return get_adapter(source).read(source)
    if isinstance(source, bytes):
        if not filename:
            raise UnsupportedFormatError(
                "filename= is required when passing raw bytes so the format can be detected."
            )
        return get_adapter(filename).read(source)
    # File-like object: prefer its name, fall back to a 'type' attribute.
    name = filename or getattr(source, "name", None) or getattr(source, "type", None)
    if not name:
        raise UnsupportedFormatError(
            "Cannot detect the file format from this object. Pass filename= explicitly."
        )
    return get_adapter(str(name)).read(source)