"""Unit tests for the output writers: one input, four formats, identical data."""

from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from app_files.output import (
    FORMATS,
    normalise_format,
    output_filename,
    to_bytes,
    write_any,
)


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def test_all_four_formats_are_registered():
    assert set(FORMATS) == {"csv", "excel", "json", "sql"}


@pytest.mark.parametrize(
    "alias,expected",
    [("csv", "csv"), ("CSV", "csv"), ("xlsx", "excel"), ("xls", "excel"),
     ("excel", "excel"), ("json", "json"), ("sql", "sql"), ("insert", "sql")],
)
def test_format_aliases_are_normalised(alias: str, expected: str):
    assert normalise_format(alias) == expected


def test_unknown_format_is_rejected():
    with pytest.raises(ValueError):
        normalise_format("parquet")


@pytest.mark.parametrize(
    "fmt,expected", [("csv", ".csv"), ("excel", ".xlsx"), ("json", ".json"), ("sql", ".sql")]
)
def test_output_filename_uses_the_right_suffix(fmt: str, expected: str):
    assert output_filename("clean_data", fmt).endswith(expected)


def test_output_filename_replaces_a_wrong_suffix():
    assert output_filename("clean_data.csv", "excel") == "clean_data.xlsx"


@pytest.mark.parametrize("fmt", ["csv", "excel", "json", "sql"])
def test_each_format_writes_a_file(tmp_path: Path, clean_frame: pd.DataFrame, fmt: str):
    path = write_any(clean_frame, tmp_path / "out", fmt)
    assert path.exists()
    assert path.stat().st_size > 0


def test_csv_output_round_trips(tmp_path: Path, clean_frame: pd.DataFrame):
    path = write_any(clean_frame, tmp_path / "out", "csv")
    pd.testing.assert_frame_equal(_read_csv(path), clean_frame)


def test_excel_output_round_trips(tmp_path: Path, clean_frame: pd.DataFrame):
    path = write_any(clean_frame, tmp_path / "out", "excel")
    restored = pd.read_excel(path, dtype=str).fillna("")
    assert list(restored.columns) == list(clean_frame.columns)
    assert len(restored) == len(clean_frame)


def test_json_output_round_trips(tmp_path: Path, clean_frame: pd.DataFrame):
    path = write_any(clean_frame, tmp_path / "out", "json")
    restored = pd.DataFrame(json.loads(path.read_text()))
    assert list(restored.columns) == list(clean_frame.columns)
    assert len(restored) == len(clean_frame)


def test_sql_output_round_trips_through_sqlite(tmp_path: Path, clean_frame: pd.DataFrame):
    path = write_any(clean_frame, tmp_path / "out", "sql", table="contacts")
    connection = sqlite3.connect(":memory:")
    connection.executescript(path.read_text())
    restored = pd.read_sql("SELECT * FROM contacts", connection)
    assert list(restored.columns) == list(clean_frame.columns)
    assert len(restored) == len(clean_frame)


def test_sql_writer_preserves_leading_zeroes(tmp_path: Path):
    """Numeric affinity must not turn an account number 01234 into 1234."""
    frame = pd.DataFrame({"account": ["01234", "00567"]})
    path = write_any(frame, tmp_path / "out", "sql", table="accounts")
    connection = sqlite3.connect(":memory:")
    connection.executescript(path.read_text())
    restored = pd.read_sql("SELECT account FROM accounts", connection)
    assert restored["account"].tolist() == ["01234", "00567"]


def test_sql_writer_preserves_plus_prefix(tmp_path: Path):
    """E.164 phone numbers must survive SQL numeric affinity unchanged."""
    frame = pd.DataFrame({"phone": ["+14155552671", "+441632960961"], "amount": [10, 20]})
    path = write_any(frame, tmp_path / "out", "sql", table="phones")
    connection = sqlite3.connect(":memory:")
    connection.executescript(path.read_text())
    restored = pd.read_sql("SELECT phone, amount FROM phones ORDER BY amount", connection)
    assert restored["phone"].tolist() == ["+14155552671", "+441632960961"]
    # A genuinely numeric column is still numeric, so SUM works.
    assert recovered_amount_sum(connection, "phones") == 30


def recovered_amount_sum(connection: sqlite3.Connection, table: str) -> float:
    return float(pd.read_sql(f"SELECT SUM(amount) AS total FROM {table}", connection)["total"][0])


def test_all_four_outputs_contain_identical_data(tmp_path: Path, clean_frame: pd.DataFrame):
    """The acceptance criterion: one input, four formats, same content."""
    csv_frame = _read_csv(write_any(clean_frame, tmp_path / "c", "csv"))

    excel_frame = pd.read_excel(
        write_any(clean_frame, tmp_path / "e", "excel"), dtype=str
    ).fillna("")

    json_frame = pd.DataFrame(
        json.loads(write_any(clean_frame, tmp_path / "j", "json").read_text())
    )

    sql_path = write_any(clean_frame, tmp_path / "s", "sql", table="contacts")
    connection = sqlite3.connect(":memory:")
    connection.executescript(sql_path.read_text())
    sql_frame = pd.read_sql("SELECT * FROM contacts", connection).astype(str)

    expected = clean_frame.reset_index(drop=True)
    for name, frame in (
        ("csv", csv_frame), ("excel", excel_frame), ("json", json_frame), ("sql", sql_frame)
    ):
        frame = frame.reset_index(drop=True)
        assert list(frame.columns) == list(expected.columns), name
        assert frame.to_dict("records") == expected.to_dict("records"), name


def test_sql_writer_escapes_quotes_safely(tmp_path: Path):
    tricky = pd.DataFrame({"name": ["O'Brien", "quote \" inside"], "amount": ["10", "20"]})
    path = write_any(tricky, tmp_path / "out", "sql", table="names")
    connection = sqlite3.connect(":memory:")
    connection.executescript(path.read_text())
    restored = pd.read_sql("SELECT name FROM names ORDER BY amount", connection)
    assert restored["name"].tolist() == ["O'Brien", 'quote " inside']


def test_sql_injection_attempt_is_stored_as_a_literal(tmp_path: Path):
    attack = pd.DataFrame({"name": ["'; DROP TABLE names; --"]})
    path = write_any(attack, tmp_path / "out", "sql", table="names")
    connection = sqlite3.connect(":memory:")
    connection.executescript(path.read_text())
    restored = pd.read_sql("SELECT name FROM names", connection)
    # The table still exists and holds the literal text.
    assert restored["name"].tolist() == ["'; DROP TABLE names; --"]


def test_write_any_corrects_a_mismatched_suffix(tmp_path: Path, clean_frame: pd.DataFrame):
    path = write_any(clean_frame, tmp_path / "out.csv", "json")
    assert path.suffix == ".json"
    assert path.exists()


@pytest.mark.parametrize("fmt", ["csv", "excel", "json", "sql"])
def test_in_memory_payload_has_bytes_name_and_mime(clean_frame: pd.DataFrame, fmt: str):
    payload = to_bytes(clean_frame, fmt, stem="demo")
    assert payload.data
    assert payload.filename == f"demo{FORMATS[fmt].extension}"
    assert payload.mime


def test_in_memory_payloads_are_readable_files(clean_frame: pd.DataFrame):
    """The download bytes must be genuine files, not just non-empty."""
    csv_frame = pd.read_csv(io.BytesIO(to_bytes(clean_frame, "csv").data), dtype=str)

    excel_bytes = to_bytes(clean_frame, "excel").data
    assert excel_bytes[:2] == b"PK"  # xlsx is a zip container
    excel_frame = pd.read_excel(io.BytesIO(excel_bytes), dtype=str).fillna("")

    json_frame = pd.DataFrame(json.loads(to_bytes(clean_frame, "json").data))

    sql_bytes = to_bytes(clean_frame, "sql").data
    connection = sqlite3.connect(":memory:")
    connection.executescript(sql_bytes.decode())
    sql_frame = pd.read_sql("SELECT * FROM clean_data", connection).astype(str)

    expected = clean_frame.reset_index(drop=True)
    for name, frame in (
        ("csv", csv_frame), ("excel", excel_frame),
        ("json", json_frame), ("sql", sql_frame),
    ):
        frame = frame.reset_index(drop=True)
        assert frame.to_dict("records") == expected.to_dict("records"), name


def test_headers_are_preserved_in_every_format(tmp_path: Path, clean_frame: pd.DataFrame):
    for fmt in ("csv", "excel", "json", "sql"):
        if fmt == "excel":
            frame = pd.read_excel(
                write_any(clean_frame, tmp_path / f"o_{fmt}", fmt), dtype=str
            ).fillna("")
        elif fmt == "json":
            frame = pd.DataFrame(
                json.loads(write_any(clean_frame, tmp_path / f"o_{fmt}", fmt).read_text())
            )
        elif fmt == "sql":
            path = write_any(clean_frame, tmp_path / f"o_{fmt}", fmt, table="t")
            connection = sqlite3.connect(":memory:")
            connection.executescript(path.read_text())
            frame = pd.read_sql("SELECT * FROM t", connection)
        else:
            frame = _read_csv(write_any(clean_frame, tmp_path / f"o_{fmt}", fmt))
        assert list(frame.columns) == list(clean_frame.columns), fmt


# --------------------------------------------------- SQL column type selection
@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 2, 3], "NUMERIC"),
        ([1.5, 2.5], "NUMERIC"),
        (["1", "2", "-3.5"], "NUMERIC"),
        # Text must never be declared NUMERIC. A word has no '+' and no leading
        # zero, so a check that only looks for those would call "John" numeric
        # and hand the values to SQL's numeric affinity.
        (["John", "Jane"], "TEXT"),
        (["john@email.com", "jane@example.com"], "TEXT"),
        (["Boston", "Austin"], "TEXT"),
        (["+14155552671", "+15559876543"], "TEXT"),
        (["01234", "56789"], "TEXT"),
        (["2024-12-31", "2024-11-05"], "TEXT"),
        (["1", "abc"], "TEXT"),
        (["", None], "TEXT"),
        (["1,234"], "TEXT"),
    ],
)
def test_sql_column_type_selection(values, expected):
    from app_files.output.sql_writer import _column_type

    assert _column_type(pd.Series(values)) == expected


def test_sql_text_columns_are_not_declared_numeric(tmp_path: Path):
    """String columns must be TEXT so their values survive SQL round-tripping."""
    frame = pd.DataFrame(
        {
            "firstname": ["John", "Jane"],
            "email": ["john@email.com", "jane@example.com"],
            "state": ["MA", "TX"],
            "amount": [10.5, -3.25],
        }
    )
    path = write_any(frame, tmp_path / "typed", "sql", table="t")
    script = path.read_text()

    for column in ("firstname", "email", "state"):
        assert f'"{column}" TEXT' in script, f"{column} should be TEXT:\n{script[:400]}"
    assert '"amount" NUMERIC' in script

    connection = sqlite3.connect(":memory:")
    connection.executescript(script)
    restored = pd.read_sql("SELECT * FROM t", connection)
    assert restored["firstname"].tolist() == ["John", "Jane"]
    assert restored["email"].tolist() == ["john@email.com", "jane@example.com"]
    assert restored["amount"].tolist() == [10.5, -3.25]


def test_sql_text_column_round_trips_values_that_look_numeric(tmp_path: Path):
    """A column holding both words and digits stays TEXT throughout."""
    frame = pd.DataFrame({"code": ["A1", "12", "0034"]})
    path = write_any(frame, tmp_path / "codes", "sql", table="t")
    assert '"code" TEXT' in path.read_text()

    connection = sqlite3.connect(":memory:")
    connection.executescript(path.read_text())
    restored = pd.read_sql("SELECT code FROM t", connection)
    assert sorted(restored["code"].tolist()) == sorted(["A1", "12", "0034"])