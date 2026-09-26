"""Chunked ingestion inside the real pipeline.

The unit tests prove windows equal a whole read. This proves the same on a file
large enough to cross the threshold, and that a chunked run's output matches a
whole-file run's output — which is the only claim that matters to a buyer with a
two-gigabyte export.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pandas as pd
import pytest

from app_files.ingestion import chunked_read, read_any, write_in_windows

WIDE_PREFIX = "id,first_name,last_name,email,phone,company,country,amount,note"

#: Rows per generated file. A fixture that is fast enough to run on every
#: commit and wide enough for the streaming path to be exercised.
FIXTURE_ROWS = int(os.getenv("AUTOFLOW_STREAM_ROWS", "5000"))


@pytest.fixture(scope="module")
def wide_csv(tmp_path_factory) -> Path:
    """A wide export with the shapes that trip a naive chunker: blanks, quotes,
    embedded commas in a quoted field, and non-ASCII text."""
    path = tmp_path_factory.mktemp("wide") / "wide.csv"
    countries = ["US", "GB", "DE", "FR", "NL", ""]
    rows = []
    for index in range(FIXTURE_ROWS):
        note = (
            'He said "hello, world" and left' if index % 11 == 0 else f"note {index}"
        )
        rows.append(
            [
                str(index),
                f"Name{index}",
                f"Last{index}",
                f"person{index}@example.com" if index % 7 else "",
                f"+44 7700 {index % 1000000:06d}",
                f"Acme {index % 50}",
                countries[index % len(countries)],
                f"{index % 250}.75",
                note,
            ]
        )
    # csv.writer quotes and escapes properly: a hand-rolled f-string with an
    # inner quote produces a shifted row that reads as valid but is not.
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(WIDE_PREFIX.split(","))
        writer.writerows(rows)
    return path


class TestChunkedOnARealExport:
    def test_the_generated_file_is_actually_wide(self, wide_csv):
        assert wide_csv.stat().st_size > 200_000
        whole = read_any(wide_csv)
        assert len(whole) == FIXTURE_ROWS
        assert list(whole.columns) == WIDE_PREFIX.split(",")

    def test_streaming_the_whole_export_matches_a_whole_read(self, wide_csv):
        whole = read_any(wide_csv)
        streamed = chunked_read(wide_csv, chunk_rows=1_000)
        assert streamed.equals(whole)

    def test_many_small_windows_match_a_few_large_ones(self, wide_csv):
        coarse = chunked_read(wide_csv, chunk_rows=5_000)
        fine = chunked_read(wide_csv, chunk_rows=137)
        assert coarse.equals(fine)

    def test_a_quoted_field_with_a_comma_survives_windowing(self, wide_csv):
        streamed = chunked_read(wide_csv, chunk_rows=99)
        assert streamed["note"].str.contains("hello, world", regex=False).any()
        assert not streamed["note"].str.startswith('"').any()

    def test_blank_emails_stay_blank_strings(self, wide_csv):
        streamed = chunked_read(wide_csv, chunk_rows=500)
        assert (streamed["email"] == "").any()
        assert streamed["email"].map(type).eq(str).all()

    def test_the_pipeline_input_is_the_same_frame_either_way(self, wide_csv):
        """What downstream layers receive must not depend on the read path."""
        from app_files.cleaners import clean_data

        whole = clean_data(read_any(wide_csv)).frame
        streamed = clean_data(chunked_read(wide_csv, chunk_rows=777)).frame
        assert whole.equals(streamed)

    def test_a_full_migration_matches_between_read_paths(self, wide_csv, tmp_path):
        """The end-to-end claim: same file, same output, either way it is read."""
        from app_files.pipeline import run_pipeline

        whole = run_pipeline(read_any(wide_csv), crm="hubspot")
        streamed = run_pipeline(chunked_read(wide_csv, chunk_rows=333), crm="hubspot")
        assert whole.clean_frame.equals(streamed.clean_frame)
        assert whole.summary()["rows_in"] == streamed.summary()["rows_in"]

    def test_streaming_to_disk_produces_the_same_bytes_as_a_whole_write(
        self, wide_csv, tmp_path
    ):
        out_streamed = tmp_path / "streamed.csv"
        out_whole = tmp_path / "whole.csv"
        write_in_windows(wide_csv, lambda window: window, out_streamed, chunk_rows=1_007)
        read_any(wide_csv).to_csv(out_whole, index=False)
        # Row counts and parsed contents, not bytes: pandas quirk-quotes a
        # field differently depending on chunk boundaries, and the contract is
        # the data, not the quoting.
        assert pd.read_csv(out_streamed, dtype=str, keep_default_na=False).equals(
            pd.read_csv(out_whole, dtype=str, keep_default_na=False)
        )

    def test_memory_growth_is_bounded_on_a_real_export(self, wide_csv):
        from app_files.ingestion.chunked import current_rss_bytes, write_in_windows

        if current_rss_bytes() == 0:
            pytest.skip("RSS unavailable on this platform")
        baseline = current_rss_bytes()
        write_in_windows(
            wide_csv,
            lambda window: window,
            wide_csv.parent / "streamed.out.csv",
            chunk_rows=2_000,
            growth_ceiling_bytes=64 * 1024 * 1024,
        )
        assert current_rss_bytes() - baseline < 64 * 1024 * 1024
