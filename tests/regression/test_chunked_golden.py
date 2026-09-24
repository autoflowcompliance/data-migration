"""Golden file for chunked ingestion (Layer 1).

A known messy CSV, read in windows of every size from one row up, must equal
the frozen whole-file read byte for byte. The input is deliberately hostile:
blanks, an embedded comma inside a quoted field, an escaped quote, non-ASCII
text, an apostrophe, and a field with surrounding whitespace that the adapter
strips.

Do not regenerate `expected.csv` to make the test green. If it disagrees with a
whole-file read, the streaming path is the guilty party.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.ingestion import chunked_read, read_any

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "chunked"


@pytest.mark.parametrize("chunk_rows", [1, 2, 3, 5, 11])
def test_every_window_size_matches_the_whole_read(chunk_rows):
    produced = chunked_read(GOLDEN / "input.csv", chunk_rows=chunk_rows)
    expected = read_any(GOLDEN / "expected.csv")
    assert produced.equals(expected)


def test_the_whole_read_matches_the_frozen_adapter():
    """The windowed read must agree with the unchanged whole-file adapter."""
    assert read_any(GOLDEN / "input.csv").equals(read_any(GOLDEN / "expected.csv"))
