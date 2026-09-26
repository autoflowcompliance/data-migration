"""Chunked ingestion for files too large to hold in memory.

The same contract as :mod:`app_files.ingestion.registry` — a DataFrame of
strings — but read in windows instead of all at once, so a two-gigabyte export
does not need two gigabytes of RAM. Downstream cleaning sees the same frame it
would have seen from a whole-file read, which is what keeps this an extension
of Layer 1 rather than a second ingestion path with its own behaviour.

What "identical" means here, precisely:

* the same columns, in the same order, as strings, with blanks not NaN;
* the same rows, in the same order, for well-formed input;
* the same encoding and separator decisions, with one documented difference —
  a streamed read decides the encoding from a bounded sample of the head rather
  than from the whole file. That is the only way to avoid reading the whole
  file to decide how to read the whole file, and it is what every streaming
  reader does. For a file whose encoding changes partway through, the chunked
  and whole reads can differ; such a file is already broken.

The memory ceiling is a *growth* ceiling, not an absolute one: it measures how
much the process grew while streaming, because an absolute figure would include
the interpreter and the caller's own data. ``growth_ceiling_bytes=256 MiB``
means "streaming this file must not add more than 256 MiB".
"""

from __future__ import annotations

import io
import os
import shutil
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app_files.ingestion.base import UnsupportedFormatError
from app_files.ingestion.csv_adapter import CSVAdapter, detect_encoding

#: A gigabyte is where chunking becomes the default rather than a choice.
DEFAULT_LARGE_BYTES = 1 << 30

#: Rows per window. Chosen so a wide row (say 1 KB) is ~50 MB of frame.
DEFAULT_CHUNK_ROWS = 50_000

#: How many bytes of the head to sample when detecting the encoding of a stream.
ENCODING_SAMPLE_BYTES = 1 << 20


class MemoryCeilingExceeded(RuntimeError):
    """The streamed read grew the process beyond the configured ceiling."""

    def __init__(self, growth: int, ceiling: int, window: int) -> None:
        self.growth = growth
        self.ceiling = ceiling
        self.window = window
        super().__init__(
            f"Streaming grew memory by {growth:,} bytes, over the "
            f"{ceiling:,}-byte ceiling, at window {window}. Lower chunk_rows "
            f"or raise growth_ceiling_bytes."
        )


def current_rss_bytes() -> int:
    """The process's current resident set size, in bytes, or 0 when unavailable.

    Reads ``/proc/self/statm`` on Linux, because ``ru_maxrss`` is a *high-water
    mark*: it only ever rises, so measuring growth against it reports zero once
    the process has already peaked, and a memory ceiling built on it would pass
    a test it should fail. macOS has no ``statm`` and reports bytes in
    ``ru_maxrss``, so the peak is the best available figure there.

    ``0`` means "unavailable", never "zero bytes used": a guard that invents a
    number can pass silently.
    """
    try:
        with open("/proc/self/statm", encoding="ascii") as handle:  # noqa: PTH123
            resident_pages = int(handle.read().split()[1])
        return resident_pages * os.sysconf("SC_PAGE_SIZE")
    except (OSError, IndexError, ValueError):
        pass
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (ImportError, ValueError, OSError):
        return 0
    return int(usage) * (1024 if os.name != "darwin" else 1)


@dataclass
class ChunkPlan:
    """What will be done with a source, and why."""

    total_bytes: int
    chunk_rows: int
    use_chunked: bool
    estimated_windows: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_bytes": self.total_bytes,
            "chunk_rows": self.chunk_rows,
            "use_chunked": self.use_chunked,
            "estimated_windows": self.estimated_windows,
        }


def plan_chunks(
    source: str | Path,
    *,
    large_bytes: int = DEFAULT_LARGE_BYTES,
    chunk_rows: int = DEFAULT_CHUNK_ROWS,
    average_row_bytes: int = 200,
) -> ChunkPlan:
    """Decide whether ``source`` is big enough to stream.

    The window estimate is deliberately rough — it exists to report "about 400
    windows" before a run, not to size anything. ``average_row_bytes`` is only a
    divisor here.
    """
    path = Path(source)
    total = path.stat().st_size if path.exists() else 0
    windows = max(1, total // max(1, chunk_rows * max(1, average_row_bytes)))
    return ChunkPlan(
        total_bytes=total,
        chunk_rows=chunk_rows,
        use_chunked=total >= large_bytes,
        estimated_windows=windows,
    )


def _sample_encoding(path: Path) -> str:
    """Detect the encoding from a bounded head of raw bytes."""
    with open(path, "rb") as handle:  # noqa: PTH123 - binary sample
        head = handle.read(ENCODING_SAMPLE_BYTES)
    if not head:
        return "utf-8-sig"
    return detect_encoding(head)


def _open_text(path: Path, encoding: str) -> io.TextIOWrapper:
    """An unbuffered-as-possible TextIOBase for ``pandas`` to iterate.

    ``newline=""`` leaves embedded carriage returns to pandas' parser rather
    than letting Python's universal-newline mode rewrite them mid-field.
    """
    return open(path, encoding=encoding, newline="")  # noqa: SIM115 - closed by caller


def _separator_for(path: Path, extension: str | None) -> str:
    suffix = (extension or path.suffix).lower()
    return "\t" if suffix == ".tsv" else ","


def iter_chunks(
    source: str | Path,
    *,
    chunk_rows: int = DEFAULT_CHUNK_ROWS,
    extension: str | None = None,
    encoding: str | None = None,
    separator: str | None = None,
    skip_bad_lines: bool = True,
    max_windows: int | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield the file in windows of at most ``chunk_rows`` rows.

    Only the current window is in memory at once. Each window is stringified
    the same way the whole-file adapter does it, so a caller cannot tell the
    windows apart from one whole read.
    """
    path = Path(source)
    if not path.is_file():
        raise UnsupportedFormatError(f"Not a file: {path}")
    if chunk_rows <= 0:
        raise ValueError("chunk_rows must be positive")
    if path.stat().st_size == 0:
        # The whole-file adapter returns an empty frame for blank input; a
        # streamed read must not instead raise EmptyDataError.
        return

    adapter = CSVAdapter()
    chosen = encoding or _sample_encoding(path)

    sep = separator or _separator_for(path, extension)
    with _open_text(path, chosen) as handle:
        windows = 0
        try:
            reader = pd.read_csv(
                handle,
                dtype=str,
                keep_default_na=False,
                sep=sep,
                chunksize=chunk_rows,
            )
        except (UnicodeDecodeError, pd.errors.ParserError):
            handle.seek(0)
            reader = pd.read_csv(
                handle,
                dtype=str,
                keep_default_na=False,
                sep=sep,
                chunksize=chunk_rows,
                engine="python",
                on_bad_lines="skip" if skip_bad_lines else "error",
            )
        for window in reader:
            yield adapter._stringify(window)
            windows += 1
            if max_windows is not None and windows >= max_windows:
                return


def chunked_read(
    source: str | Path, *, chunk_rows: int = DEFAULT_CHUNK_ROWS, **kwargs: Any
) -> pd.DataFrame:
    """The whole file, assembled from windows.

    Exists to prove the windows are correct, and for callers whose output is
    genuinely small even when the input is not (a filtered extract, an
    aggregate). Not a way to read a huge file into memory on purpose.
    """
    parts = list(iter_chunks(source, chunk_rows=chunk_rows, **kwargs))
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def merge_outputs(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate window results, preserving column order and row order."""
    parts = [frame for frame in frames if frame is not None and not frame.empty]
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def process_in_windows(
    source: str | Path,
    handler: Callable[[pd.DataFrame], pd.DataFrame],
    *,
    chunk_rows: int = DEFAULT_CHUNK_ROWS,
    growth_ceiling_bytes: int | None = None,
    on_window: Callable[[int, int], None] | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Apply ``handler`` to each window and merge the results.

    This is how a transform that is row-local — dedupe within a window,
    masking, normalisation — runs on a file that does not fit. A handler that
    needs global context is not safe here and will produce different output
    from a whole-file run; that is the caller's decision to make, and the
    docstring says so rather than pretending otherwise.

    ``growth_ceiling_bytes`` measures the growth of the process's resident set
    since the call began, checked after every window.
    """
    baseline = current_rss_bytes()
    results: list[pd.DataFrame] = []
    for index, window in enumerate(
        iter_chunks(source, chunk_rows=chunk_rows, **kwargs), start=1
    ):
        results.append(handler(window))
        if on_window is not None:
            on_window(index, len(window))
        if growth_ceiling_bytes:
            growth = current_rss_bytes() - baseline
            if growth > growth_ceiling_bytes:
                raise MemoryCeilingExceeded(growth, growth_ceiling_bytes, index)
    return merge_outputs(results)


def write_in_windows(
    source: str | Path,
    handler: Callable[[pd.DataFrame], pd.DataFrame],
    out_path: str | Path,
    *,
    chunk_rows: int = DEFAULT_CHUNK_ROWS,
    out_format: str = "csv",
    growth_ceiling_bytes: int | None = None,
    **kwargs: Any,
) -> int:
    """Stream ``source`` to ``out_path``, writing each window as it is handled.

    The point is that output does not accumulate either: a filter over a 2 GB
    file whose result is 50 MB must not hold 2 GB of intermediate frames. The
    first window writes the header, later windows append, and the rows written
    are returned.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out_format not in ("csv", "tsv"):
        raise ValueError(
            f"write_in_windows streams csv/tsv only; '{out_format}' must be "
            f"written after a materialising merge."
        )
    sep = "\t" if out_format == "tsv" else ","
    baseline = current_rss_bytes()
    written = 0
    first = True
    for index, window in enumerate(
        iter_chunks(source, chunk_rows=chunk_rows, **kwargs), start=1
    ):
        produced = handler(window)
        written += len(produced)
        produced.to_csv(out, mode="w" if first else "a", header=first, index=False, sep=sep)
        first = False
        if growth_ceiling_bytes:
            growth = current_rss_bytes() - baseline
            if growth > growth_ceiling_bytes:
                raise MemoryCeilingExceeded(growth, growth_ceiling_bytes, index)
    if first:
        # No windows at all: still produce a valid, empty file with a header
        # only when we know one, which for a headerless source we do not.
        out.write_text("", encoding="utf-8")
    return written


def is_large(source: str | Path, large_bytes: int = DEFAULT_LARGE_BYTES) -> bool:
    """Whether ``source`` crosses the chunking threshold."""
    try:
        return Path(source).stat().st_size >= large_bytes
    except OSError:
        return False


def read_large(
    source: str | Path,
    *,
    large_bytes: int = DEFAULT_LARGE_BYTES,
    chunk_rows: int = DEFAULT_CHUNK_ROWS,
    **kwargs: Any,
) -> pd.DataFrame:
    """Read ``source``, streaming it when it is large and whole otherwise.

    The whole-file branch delegates to the existing adapter, so a small file's
    read is unchanged, byte for byte, from the frozen layer.
    """
    path = Path(source)
    if is_large(path, large_bytes):
        return chunked_read(path, chunk_rows=chunk_rows, **kwargs)
    from app_files.ingestion.registry import read_any

    return read_any(path)


def free_space_bytes(path: str | Path) -> int:
    """Free space at ``path``, used before streaming a file to disk."""
    return shutil.disk_usage(str(Path(path).resolve().parent)).free


__all__ = [
    "DEFAULT_CHUNK_ROWS",
    "DEFAULT_LARGE_BYTES",
    "ENCODING_SAMPLE_BYTES",
    "ChunkPlan",
    "MemoryCeilingExceeded",
    "chunked_read",
    "current_rss_bytes",
    "free_space_bytes",
    "is_large",
    "iter_chunks",
    "merge_outputs",
    "plan_chunks",
    "process_in_windows",
    "read_large",
    "write_in_windows",
]
