"""Output writers: same clean data, several formats.

``write_any`` writes to disk; ``to_bytes`` renders the same content in memory
for download buttons.
"""

from app_files.output import csv_writer, excel_writer, json_writer, sql_writer
from app_files.output.csv_writer import write as write_csv
from app_files.output.excel_writer import write as write_excel
from app_files.output.formats import (
    FORMATS,
    Format,
    normalise_format,
    output_filename,
    write_any,
)
from app_files.output.inmemory import Payload, to_bytes
from app_files.output.json_writer import write as write_json
from app_files.output.sql_writer import write as write_sql

__all__ = [
    "FORMATS",
    "Format",
    "Payload",
    "csv_writer",
    "excel_writer",
    "json_writer",
    "normalise_format",
    "output_filename",
    "sql_writer",
    "to_bytes",
    "write_any",
    "write_csv",
    "write_excel",
    "write_json",
    "write_sql",
]