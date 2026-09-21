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


def test_bytes_upload_honours_the_filename_extension(tmp_path: Path):
    """A `.tsv` arriving as bytes must be tab-split, not read as one column.

    The backend receives uploads as ``read_any(data, filename=...)``. Adapters
    cannot see a suffix on raw bytes, so the registry has to pass the declared
    extension down or a tab-separated upload parses as a single column.
    """
    payload = b"name\tcity\nJohn\tBoston\n"
    frame = read_any(payload, filename="contacts.tsv")
    assert list(frame.columns) == ["name", "city"]
    assert frame.iloc[0]["city"] == "Boston"


def test_legacy_xls_reads_via_bytes_and_path(tmp_path: Path):
    """A real BIFF `.xls` reads the same whether given as a path or upload bytes.

    openpyxl cannot open the legacy container, so this only works if the
    registry forwards ``.xls`` to the adapter's xlrd branch.
    """
    pytest.importorskip("xlrd")
    xlwt = pytest.importorskip("xlwt")

    path = tmp_path / "legacy.xls"
    book = xlwt.Workbook()
    sheet = book.add_sheet("Sheet1")
    for column, header in enumerate(["First Name", "Last Name", "Email Address"]):
        sheet.write(0, column, header)
    for row, values in enumerate(
        [["John", "Smith", "john@email.com"], ["Jane", "Doe", "jane@doe.com"]], start=1
    ):
        for column, value in enumerate(values):
            sheet.write(row, column, value)
    book.save(str(path))

    from_path = read_any(path)
    from_bytes = read_any(path.read_bytes(), filename="legacy.xls")

    assert list(from_path.columns) == ["First Name", "Last Name", "Email Address"]
    assert from_path.iloc[0]["Email Address"] == "john@email.com"
    pd.testing.assert_frame_equal(from_path, from_bytes)


def test_cp1252_bytes_are_not_misdecoded(tmp_path: Path):
    """A small Windows-1252 export must keep its accents.

    chardet reports these bytes as a legacy Mac or Central-European codepage at
    ~0.02 confidence, which silently turns ``José`` into ``Josť``.
    """
    path = tmp_path / "cp1252.csv"
    path.write_bytes("name,note\nJosé,café résumé naïve\nZürich,Straße\n".encode("cp1252"))

    frame = read_any(path)
    assert frame["name"].tolist() == ["José", "Zürich"]
    assert frame["note"].iloc[0] == "café résumé naïve"


def test_cyrillic_bytes_are_still_detected(tmp_path: Path):
    """The cp1252 default must not swallow a genuine non-Latin encoding."""
    path = tmp_path / "cp1251.csv"
    path.write_bytes("name,city\nПётр,Москва\nИван,Тверь\n".encode("cp1251"))

    frame = read_any(path)
    assert frame["name"].tolist() == ["Пётр", "Иван"]


def test_utf8_wins_over_everything(tmp_path: Path):
    """UTF-8 is verified by decoding, so accents and non-Latin text both survive."""
    path = tmp_path / "utf8.csv"
    path.write_text("name,city\nJosé,Привет\n", encoding="utf-8")
    frame = read_any(path)
    assert frame["name"].tolist() == ["José"]
    assert frame["city"].tolist() == ["Привет"]