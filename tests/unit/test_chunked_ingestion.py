"""Chunked ingestion for large files (Layer 1 extension).

The contract is that a streamed read and a whole-file read produce the same
DataFrame. That is tested directly, across chunk sizes smaller than a row's
worth of bytes, across the encodings and separators the frozen adapter knows,
and finally on a file large enough for the memory ceiling to mean something.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest

from app_files.ingestion import chunked_read, iter_chunks, read_any
from app_files.ingestion.chunked import (
    ChunkPlan,
    MemoryCeilingExceeded,
    current_rss_bytes,
    is_large,
    merge_outputs,
    plan_chunks,
    process_in_windows,
    read_large,
    write_in_windows,
)


def _write_csv(path, rows: int, *, header: str = "id,name,amount", sep: str = ",") -> None:
    if sep != ",":
        header = header.replace(",", sep)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(header + "\n")
        handle.writelines(sep.join([str(index), f"name{index}", f"{index}.50"]) + "\n" for index in range(rows))


class TestChunkedEqualsWholeRead:
    def test_a_small_sample_is_identical(self, contacts_csv):
        whole = read_any(contacts_csv)
        for chunk_rows in (1, 2, 3, 7, 1000):
            streamed = chunked_read(contacts_csv, chunk_rows=chunk_rows)
            assert streamed.equals(whole), chunk_rows

    def test_column_order_is_preserved(self, contacts_csv):
        whole = read_any(contacts_csv)
        streamed = chunked_read(contacts_csv, chunk_rows=2)
        assert list(streamed.columns) == list(whole.columns)

    def test_rows_are_in_the_same_order(self, tmp_path):
        path = tmp_path / "rows.csv"
        _write_csv(path, 250)
        whole = read_any(path)
        streamed = chunked_read(path, chunk_rows=7)
        assert whole["id"].tolist() == streamed["id"].tolist()

    def test_everything_is_a_string_with_no_nan(self, tmp_path):
        path = tmp_path / "blanks.csv"
        path.write_text("a,b,c\n1,,3\n,,\n", encoding="utf-8")
        streamed = chunked_read(path, chunk_rows=1)
        assert streamed.iloc[0]["b"] == ""
        assert streamed.iloc[1]["b"] == ""
        assert streamed["c"].map(type).eq(str).all()

    def test_blank_values_are_not_read_as_nan(self, tmp_path):
        path = tmp_path / "na.csv"
        path.write_text("a,b\nNA,\nNaN,x\n", encoding="utf-8")
        whole = read_any(path)
        streamed = chunked_read(path, chunk_rows=1)
        # The literal strings survive; only emptiness is blank.
        assert streamed["a"].tolist() == ["NA", "NaN"]
        assert streamed.equals(whole)

    def test_windows_never_exceed_the_requested_size(self, tmp_path):
        path = tmp_path / "many.csv"
        _write_csv(path, 100)
        sizes = [len(window) for window in iter_chunks(path, chunk_rows=9)]
        assert max(sizes) <= 9
        assert sum(sizes) == 100

    def test_a_single_row_file_streams_to_one_window(self, tmp_path):
        path = tmp_path / "one.csv"
        _write_csv(path, 1)
        windows = list(iter_chunks(path, chunk_rows=100))
        assert len(windows) == 1
        assert windows[0].equals(read_any(path))

    def test_an_empty_file_yields_no_windows(self, tmp_path):
        path = tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        assert list(iter_chunks(path)) == []
        assert chunked_read(path).empty

    def test_a_header_only_file_yields_one_empty_window(self, tmp_path):
        path = tmp_path / "header.csv"
        path.write_text("a,b\n", encoding="utf-8")
        windows = list(iter_chunks(path))
        assert len(windows) == 1 and windows[0].empty
        assert list(windows[0].columns) == ["a", "b"]

    def test_tab_separated_is_read_as_one_column_set(self, tmp_path):
        path = tmp_path / "x.tsv"
        _write_csv(path, 40, sep="\t")
        whole = read_any(path)
        streamed = chunked_read(path, chunk_rows=6)
        assert streamed.equals(whole)
        assert list(streamed.columns) == ["id", "name", "amount"]

    def test_an_explicit_separator_wins(self, tmp_path):
        path = tmp_path / "pipes.csv"
        _write_csv(path, 20, sep="|")
        streamed = chunked_read(path, chunk_rows=3, separator="|")
        assert list(streamed.columns) == ["id", "name", "amount"]
        assert len(streamed) == 20

    def test_utf8_bom_is_stripped_like_the_whole_read(self, tmp_path):
        path = tmp_path / "bom.csv"
        path.write_bytes("\ufeffa,b\n1,2\n".encode())
        assert list(chunked_read(path).columns) == list(read_any(path).columns) == ["a", "b"]

    def test_cp1252_bytes_decode_the_same(self, tmp_path):
        path = tmp_path / "accents.csv"
        path.write_bytes("name,city\nJosé,München\n".encode("cp1252"))
        whole = read_any(path)
        streamed = chunked_read(path)
        assert streamed.equals(whole)
        assert streamed.iloc[0]["city"] == "München"

    def test_ragged_rows_are_skipped_without_raising(self, tmp_path):
        path = tmp_path / "ragged.csv"
        path.write_text("a,b,c\n1,2,3\n4,5\n6,7,8\n", encoding="utf-8")
        whole = read_any(path)
        streamed = chunked_read(path, chunk_rows=1)
        assert streamed.equals(whole)

    def test_missing_file_raises_a_clear_error(self, tmp_path):
        from app_files.ingestion import UnsupportedFormatError

        with pytest.raises(UnsupportedFormatError):
            list(iter_chunks(tmp_path / "nope.csv"))

    def test_a_non_positive_chunk_size_is_rejected(self, tmp_path):
        path = tmp_path / "x.csv"
        _write_csv(path, 2)
        with pytest.raises(ValueError):
            list(iter_chunks(path, chunk_rows=0))


class TestMergeAndWindows:
    def test_merge_preserves_row_order_across_windows(self, tmp_path):
        path = tmp_path / "m.csv"
        _write_csv(path, 50)
        merged = merge_outputs(iter_chunks(path, chunk_rows=7))
        assert merged["id"].tolist() == [str(i) for i in range(50)]

    def test_merge_of_nothing_is_an_empty_frame(self):
        assert merge_outputs([]).empty

    def test_merge_ignores_empty_frames(self, tmp_path):
        path = tmp_path / "m.csv"
        _write_csv(path, 3)
        frames = [pd.DataFrame(), next(iter(iter_chunks(path))), pd.DataFrame()]
        assert len(merge_outputs(frames)) == 3

    def test_a_row_local_handler_matches_the_whole_file_result(self, tmp_path):
        """The nord pattern: a per-row transform that does not need context."""
        path = tmp_path / "h.csv"
        _write_csv(path, 30)
        whole = read_any(path)

        def upper_only_names(window):
            window["name"] = window["name"].str.upper()
            return window

        streamed = process_in_windows(path, upper_only_names, chunk_rows=4)
        expected = upper_only_names(whole.copy())
        assert streamed.equals(expected)

    def test_the_on_window_callback_reports_each_window(self, tmp_path):
        path = tmp_path / "h.csv"
        _write_csv(path, 30)
        seen: list[tuple[int, int]] = []
        process_in_windows(
            path, lambda window: window, chunk_rows=10, on_window=lambda i, n: seen.append((i, n))
        )
        assert seen == [(1, 10), (2, 10), (3, 10)]


class TestWriteInWindows:
    def test_streaming_to_disk_matches_the_whole_file_write(self, tmp_path):
        path = tmp_path / "w.csv"
        _write_csv(path, 60)
        out = tmp_path / "out.csv"
        rows = write_in_windows(path, lambda window: window, out, chunk_rows=7)
        assert rows == 60
        assert pd.read_csv(out, dtype=str, keep_default_na=False).equals(read_any(path))

    def test_a_row_local_filter_streams_the_survivors(self, tmp_path):
        path = tmp_path / "f.csv"
        _write_csv(path, 100)
        out = tmp_path / "kept.csv"

        def keep_even(window):
            return window[window["id"].astype(int) % 2 == 0]

        rows = write_in_windows(path, keep_even, out, chunk_rows=13)
        assert rows == 50
        result = pd.read_csv(out, dtype=str, keep_default_na=False)
        assert result["id"].tolist() == [str(i) for i in range(0, 100, 2)]

    def test_a_tsv_destination_is_written_with_tabs(self, tmp_path):
        path = tmp_path / "w.csv"
        _write_csv(path, 10)
        out = tmp_path / "out.tsv"
        write_in_windows(path, lambda window: window, out, chunk_rows=4, out_format="tsv")
        assert "\t" in out.read_text().splitlines()[0]

    def test_an_empty_source_still_produces_a_file(self, tmp_path):
        path = tmp_path / "e.csv"
        path.write_text("", encoding="utf-8")
        out = tmp_path / "out.csv"
        rows = write_in_windows(path, lambda window: window, out, chunk_rows=5)
        assert rows == 0 and out.exists()

    def test_an_unsupported_stream_format_is_refused(self, tmp_path):
        path = tmp_path / "w.csv"
        _write_csv(path, 2)
        with pytest.raises(ValueError):
            write_in_windows(path, lambda w: w, tmp_path / "o.xlsx", out_format="excel")


class TestPlanning:
    def test_a_small_file_is_not_streamed(self, tmp_path):
        path = tmp_path / "s.csv"
        _write_csv(path, 2)
        plan = plan_chunks(path, large_bytes=1 << 30)
        assert plan.use_chunked is False
        assert isinstance(plan, ChunkPlan)

    def test_a_file_over_the_threshold_is_streamed(self, tmp_path):
        path = tmp_path / "b.csv"
        _write_csv(path, 100)
        assert plan_chunks(path, large_bytes=10, chunk_rows=10).use_chunked is True

    def test_the_window_estimate_grows_with_the_file(self, tmp_path):
        small = tmp_path / "s.csv"
        large = tmp_path / "l.csv"
        _write_csv(small, 10)
        _write_csv(large, 10_000)
        assert (
            plan_chunks(large, chunk_rows=10, average_row_bytes=20).estimated_windows
            > plan_chunks(small, chunk_rows=10, average_row_bytes=20).estimated_windows
        )

    def test_the_plan_serialises(self, tmp_path):
        path = tmp_path / "p.csv"
        _write_csv(path, 5)
        assert set(plan_chunks(path).as_dict()) == {
            "total_bytes",
            "chunk_rows",
            "use_chunked",
            "estimated_windows",
        }

    def test_is_large_agrees_with_the_plan(self, tmp_path):
        path = tmp_path / "x.csv"
        _write_csv(path, 50)
        assert is_large(path, large_bytes=10) is True
        assert is_large(path, large_bytes=1 << 30) is False

    def test_is_large_is_false_for_a_missing_file(self, tmp_path):
        assert is_large(tmp_path / "nope.csv") is False

    def test_read_large_delegates_to_the_frozen_reader_for_small_files(self, contacts_csv):
        """A small file must go through the existing adapter, unchanged."""
        assert read_large(contacts_csv).equals(read_any(contacts_csv))

    def test_read_large_streams_when_the_threshold_is_crossed(self, contacts_csv):
        assert read_large(contacts_csv, large_bytes=1).equals(read_any(contacts_csv))


def _write_big_csv(target, megabytes: int) -> Path:
    size = megabytes * 1024 * 1024
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("id,name,amount,note\n")
        written = 0
        index = 0
        while written < size:
            line = f"{index},name{index},{(index % 1000)}.25,a moderately wide note field\n"
            handle.write(line)
            written += len(line)
            index += 1
    return target


#: Rewritten per module, not per test: writing even tens of MB five times over
#: dominates the runtime of the suite.
_BIG_CSV_CACHE: dict[str, Path] = {}


@pytest.fixture(scope="module")
def big_csv(tmp_path_factory) -> Path:
    """A wide CSV of a configurable size, written once per module."""
    megabytes = int(os.getenv("AUTOFLOW_LARGE_FIXTURE_MB", "48"))
    key = str(megabytes)
    if key not in _BIG_CSV_CACHE:
        target = tmp_path_factory.mktemp("large") / "big.csv"
        _BIG_CSV_CACHE[key] = _write_big_csv(target, megabytes)
    return _BIG_CSV_CACHE[key]


class TestMemoryCeiling:

    def test_a_large_file_streams_under_a_growth_ceiling(self, big_csv):
        """The point of the whole module: a big file must not add big memory."""
        if current_rss_bytes() == 0:
            pytest.skip("RSS unavailable on this platform")
        ceiling = int(os.getenv("AUTOFLOW_MEMORY_CEILING_MB", "96")) * 1024 * 1024
        baseline = current_rss_bytes()
        rows = write_in_windows(
            big_csv,
            lambda window: window,
            big_csv.parent / "streamed.out.csv",
            chunk_rows=20_000,
            growth_ceiling_bytes=ceiling,
        )
        growth = current_rss_bytes() - baseline
        assert rows > 100_000
        assert growth < ceiling

    def test_the_same_file_read_whole_costs_far_more(self, big_csv):
        """Evidence that the ceiling is a real constraint, not decoration."""
        if current_rss_bytes() == 0:
            pytest.skip("RSS unavailable on this platform")
        baseline = current_rss_bytes()
        frame = read_any(big_csv)
        whole_growth = current_rss_bytes() - baseline
        del frame

        baseline = current_rss_bytes()
        list(iter_chunks(big_csv, chunk_rows=20_000))
        streamed_growth = current_rss_bytes() - baseline

        assert whole_growth > streamed_growth

    def test_exceeding_the_ceiling_raises_with_a_useful_message(self, big_csv):
        if current_rss_bytes() == 0:
            pytest.skip("RSS unavailable on this platform")
        with pytest.raises(MemoryCeilingExceeded) as excinfo:
            process_in_windows(
                big_csv,
                lambda window: window,
                chunk_rows=200_000,
                growth_ceiling_bytes=1,
            )
        assert "ceiling" in str(excinfo.value)
        assert excinfo.value.ceiling == 1

    def test_the_ceiling_error_names_the_window(self, big_csv):
        if current_rss_bytes() == 0:
            pytest.skip("RSS unavailable on this platform")
        with pytest.raises(MemoryCeilingExceeded) as excinfo:
            process_in_windows(
                big_csv,
                lambda window: window,
                chunk_rows=50_000,
                growth_ceiling_bytes=1,
            )
        assert excinfo.value.window >= 1

    def test_chunking_bounds_the_frame_held_at_once(self, big_csv):
        window = next(iter(iter_chunks(big_csv, chunk_rows=1_000)))
        assert len(window) == 1_000
