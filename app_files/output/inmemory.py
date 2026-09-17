"""Build an output payload in memory, for download buttons.

The web UI needs the same bytes a file writer would produce, without touching
the filesystem. Rather than duplicate format knowledge in the UI, that logic
lives here and is covered by tests.
"""

from __future__ import annotations

import io
import json
from typing import NamedTuple

import pandas as pd

from app_files.output.excel_writer import write as write_excel
from app_files.output.formats import normalise_format

MIME_TYPES = {
    "csv": "text/csv",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "json": "application/json",
    "sql": "application/sql",
}

EXTENSIONS = {"csv": ".csv", "excel": ".xlsx", "json": ".json", "sql": ".sql"}


class Payload(NamedTuple):
    data: bytes
    filename: str
    mime: str


def to_bytes(df: pd.DataFrame, output_format: str = "csv", stem: str = "clean_data") -> Payload:
    """Render ``df`` in the requested format entirely in memory.

    Returns the bytes, a suggested filename and the MIME type, ready to hand to
    a download button.
    """
    canonical = normalise_format(output_format)
    filename = f"{stem}{EXTENSIONS[canonical]}"
    mime = MIME_TYPES[canonical]

    if canonical == "csv":
        data = df.to_csv(index=False).encode("utf-8")
    elif canonical == "json":
        data = json.dumps(
            json.loads(df.to_json(orient="records")), indent=2, ensure_ascii=False
        ).encode("utf-8")
    elif canonical == "sql":
        from app_files.output.sql_writer import render_sql

        data = render_sql(df, table="clean_data").encode("utf-8")
    else:  # excel
        buffer = io.BytesIO()
        write_excel(df, buffer)
        data = buffer.getvalue()
    return Payload(data, filename, mime)