"""Unit tests for the ingestion adapters and the format registry."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest

from app_files.ingestion import (
    UnsupportedFormatError,
    available_extensions,
    get_adapter,
    read_any,
)


def test_registry_lists_expected_extensions():
    extensions = set(available_extensions())
    assert {".csv", ".xlsx", ".json", ".pdf"} <= extensions


def test_registry_picks_adapter_by_extension():
    assert type(get_adapter("data.csv")).__name__ == "CSVAdapter"
    assert type(get_adapter("data.xlsx")).__name__ == "ExcelAdapter"
    assert type(get_adapter("data.json")).__name__ == "JSONAdapter"
    assert type(get_adapter("data.pdf")).__name__ == "PDFAdapter"


def test_registry_rejects_unknown_extension():
    with pytest.raises(UnsupportedFormatError):
        get_adapter("data.parquet")


def test_csv_adapter_reads_sample(contacts_csv: Path):
    frame = read_any(contacts_csv)
    assert isinstance(frame, pd.DataFrame)
    assert len(frame) > 0
    assert "First Name" in frame.columns


def test_csv_adapter_reports_bytes_without_filename():
    with pytest.raises(UnsupportedFormatError):
        read_any(b"a,b\n1,2\n")


def test_csv_adapter_accepts_bytes_with_filename(contacts_csv: Path):
    from_bytes = read_any(contacts_csv.read_bytes(), filename="messy_contacts.csv")
    from_path = read_any(contacts_csv)
    pd.testing.assert_frame_equal(from_bytes, from_path)


def test_json_adapter_flattens_nested(contacts_json: Path):
    frame = read_any(contacts_json)
    assert len(frame) > 0
    # Nested {"address": {"city": ...}} becomes a dotted column.
    assert any("." in column for column in frame.columns)


def test_pdf_adapter_reads_table(bank_pdf: Path):
    frame = read_any(bank_pdf)
    assert len(frame) == 7
    lowered = {str(column).strip().lower() for column in frame.columns}
    assert {"date", "description", "amount"} <= lowered


def test_excel_adapter_round_trip(clean_frame: pd.DataFrame):
    from app_files.output.excel_writer import write as write_excel

    buffer = io.BytesIO()
    write_excel(clean_frame, buffer)
    buffer.seek(0)
    frame = read_any(buffer.getvalue(), filename="contacts.xlsx")
    assert len(frame) == 3
    assert "firstname" in frame.columns


def test_excel_adapter_reads_sample_workbook(contacts_xlsx: Path, contacts_csv: Path):
    """A real .xlsx on disk, not just a written-and-read round trip."""
    from_xlsx = read_any(contacts_xlsx)
    from_csv = read_any(contacts_csv)
    assert len(from_xlsx) == len(from_csv) == 7
    assert set(from_csv.columns) <= set(from_xlsx.columns)


def test_adapters_agree_across_formats(
    bank_csv: Path, bank_pdf: Path
):
    """The CSVs and the PDF of the same statement produce the same rows."""
    from_csv = read_any(bank_csv)
    from_pdf = read_any(bank_pdf)
    assert len(from_csv) == len(from_pdf) == 7

    csv_amounts = sorted(from_csv["Amount"].astype(str).str.replace("(", "-", regex=False).str.replace(")", "", regex=False).astype(float))
    pdf_amounts = sorted(from_pdf["Amount"].astype(str).str.replace("(", "-", regex=False).str.replace(")", "", regex=False).astype(float))
    assert csv_amounts == pytest.approx(pdf_amounts)