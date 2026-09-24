"""Output writers: same clean data, several formats.

``write_any`` writes to disk; ``to_bytes`` renders the same content in memory
for download buttons.
"""

from app_files.output import csv_writer, excel_writer, json_writer, sql_writer
from app_files.output.csv_writer import write as write_csv
from app_files.output.destinations import (
    DeliveryReceipt,
    EmailDestination,
    FileDestination,
    GoogleSheetsDestination,
    S3Destination,
    SFTPDestination,
    push,
    push_file,
)
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
from app_files.output.signed import (
    SignatureBundle,
    SignatureError,
    SignatureManifest,
    read_manifest,
    sign_bytes,
    sign_directory,
    sign_file,
    verify_file,
    verify_or_raise,
    write_manifest,
)
from app_files.output.sql_writer import write as write_sql
from app_files.output.webhooks import (
    EVENTS,
    DeliveryResult,
    Webhook,
    WebhookDispatcher,
    WebhookPayload,
    notify_completion,
)

__all__ = [
    "EVENTS",
    "FORMATS",
    "DeliveryReceipt",
    "DeliveryResult",
    "EmailDestination",
    "FileDestination",
    "Format",
    "GoogleSheetsDestination",
    "Payload",
    "S3Destination",
    "SFTPDestination",
    "SignatureBundle",
    "SignatureError",
    "SignatureManifest",
    "Webhook",
    "WebhookDispatcher",
    "WebhookPayload",
    "csv_writer",
    "excel_writer",
    "json_writer",
    "normalise_format",
    "notify_completion",
    "output_filename",
    "push",
    "push_file",
    "read_manifest",
    "sign_bytes",
    "sign_directory",
    "sign_file",
    "sql_writer",
    "to_bytes",
    "verify_file",
    "verify_or_raise",
    "write_any",
    "write_csv",
    "write_excel",
    "write_json",
    "write_manifest",
    "write_sql",
]