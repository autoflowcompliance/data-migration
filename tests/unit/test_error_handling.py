"""Malformed and hostile input must produce readable errors, not stack traces.

The UI is expected to catch exceptions and show a short message, so every case
here asserts *which* error is raised rather than merely that something blew up.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.ingestion import UnsupportedFormatError, get_adapter, read_any
from app_files.output import normalise_format
from app_files.pipeline import run_pipeline
from app_files.rules import RuleConfigError, load_rules, run_rules
from app_files.services.bank_reconciliation.reconciler import run_reconciliation


# ------------------------------------------------------------------ ingestion
def test_empty_file_yields_an_empty_frame(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")
    frame = read_any(path)
    assert frame.empty


def test_binary_garbage_with_a_csv_extension_does_not_crash(tmp_path):
    path = tmp_path / "garbage.csv"
    path.write_bytes(b"\x00\x01\x02\xff\xfe" * 100)
    # Either it raises a clear ingest error or it returns a frame; it must not
    # raise a bare UnicodeDecodeError/OSError.
    try:
        read_any(path)
    except UnsupportedFormatError:
        pass


def test_unknown_extension_names_the_supported_set():
    with pytest.raises(UnsupportedFormatError) as caught:
        get_adapter("data.parquet")
    assert "csv" in str(caught.value).lower()


def test_pdf_without_pdfplumber_is_a_clear_error(tmp_path, monkeypatch):
    """A missing optional dependency must not surface as an ImportError."""
    path = tmp_path / "statement.pdf"
    path.write_bytes(b"%PDF-1.4\nnot really a pdf\n")

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pdfplumber":
            raise ImportError("No module named 'pdfplumber'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(UnsupportedFormatError) as caught:
        read_any(path)
    assert "pdfplumber" in str(caught.value)


# ---------------------------------------------------------------------- rules
def test_bad_yaml_shapes_raise_rule_config_error():
    with pytest.raises(RuleConfigError):
        load_rules({"rules": "nope"})
    with pytest.raises(RuleConfigError):
        load_rules({"rules": [42]})
    with pytest.raises(RuleConfigError):
        load_rules({"rules": [{"field": "x", "type": "range", "min": "abc"}]})
    with pytest.raises(RuleConfigError):
        load_rules({"rules": [{"field": "x", "type": "length", "exactly": "abc"}]})


def test_rules_on_an_empty_frame_do_not_crash():
    result = run_rules(pd.DataFrame(), load_rules({"rules": [{"field": "a", "type": "required"}]}))
    assert result.total_failures == 0


def test_mixed_types_in_a_rule_column_do_not_crash():
    """A text value in a numeric column is a rule failure, not a TypeError."""
    frame = pd.DataFrame({"amount": [10, "not-a-number", None]})
    result = run_rules(
        frame, load_rules({"rules": [{"field": "amount", "type": "range", "min": 0}]})
    )
    assert isinstance(result.total_failures, int)


# ------------------------------------------------------------------- pipeline
def test_pipeline_reports_a_frame_with_no_usable_columns():
    """Unrecognised headers are reported as issues, not raised as an exception."""
    result = run_pipeline(pd.DataFrame({"unrelated": ["x"]}), crm="hubspot")
    assert len(result.clean_frame) == 1
    # The mapped output has no usable values, so the quality score is 0.
    assert result.summary()["quality_score"] == 0.0


def test_pipeline_raises_a_clear_error_for_an_unknown_config():
    with pytest.raises(Exception) as caught:
        run_pipeline(pd.DataFrame({"Email Address": ["a@x.com"]}), crm="does_not_exist")
    assert "does_not_exist" in str(caught.value)


def test_pipeline_handles_a_single_row():
    frame = pd.DataFrame({"Email Address": ["a@x.com"], "Last Name": ["Smith"]})
    result = run_pipeline(frame, crm="hubspot")
    assert len(result.clean_frame) == 1


# -------------------------------------------------------------------- outputs
def test_unknown_output_format_is_a_value_error():
    with pytest.raises(ValueError):
        normalise_format("docx")


# ------------------------------------------------------------ reconciliation
def test_reconciliation_reports_missing_columns_by_name(bank_csv, ledger_csv):
    with pytest.raises(KeyError) as caught:
        run_reconciliation(
            bank_csv.read_bytes(), ledger_csv.read_bytes(),
            "Date", "Amount", "Date", "NotAColumn", 2,
        )
    assert "NotAColumn" in str(caught.value)


def test_reconciliation_reports_an_empty_file_clearly(bank_csv):
    from app_files.services.bank_reconciliation.reconciler import UnreadableStatementError

    with pytest.raises(UnreadableStatementError) as caught:
        run_reconciliation(
            bank_csv.read_bytes(), b"", "Date", "Amount", "Date", "Amount", 2,
        )
    assert "ledger" in str(caught.value)
    assert "empty" in str(caught.value).lower()


def test_reconciliation_reports_a_headerless_file_clearly(bank_csv):
    from app_files.services.bank_reconciliation.reconciler import UnreadableStatementError

    with pytest.raises(UnreadableStatementError) as caught:
        run_reconciliation(
            bank_csv.read_bytes(), b"\n\n", "Date", "Amount", "Date", "Amount", 2,
        )
    assert "ledger" in str(caught.value)


def test_reconciliation_survives_a_header_only_ledger(bank_csv):
    result = run_reconciliation(
        bank_csv.read_bytes(), b"Date,Amount\n", "Date", "Amount", "Date", "Amount", 2
    )
    assert result["summary"]["matched"] == 0
    assert result["summary"]["missing_from_books"] == 7
    assert result["summary"]["recorded_but_never_cleared"] == 0


def test_reconciliation_handles_mixed_date_formats():
    bank = b"Date,Amount\n2024-01-03,100\n01/04/2024,50\n"
    ledger = b"Date,Amount\n2024-01-03,100\n"
    result = run_reconciliation(bank, ledger, "Date", "Amount", "Date", "Amount", 2)
    # The ISO row matches; the ambiguous one is left for a human rather than
    # guessed at, and neither case raises.
    assert result["summary"]["matched"] == 1
    assert result["summary"]["missing_from_books"] == 1