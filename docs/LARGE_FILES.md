# Large files

Read a file that does not fit in memory, without reading it all at once.

```python
from app_files.ingestion import read_large, write_in_windows, plan_chunks

plan = plan_chunks("export_2024.csv")        # what will be done, and why
frame = read_large("export_2024.csv")        # streams if large, whole if not

# Stream a row-local transform straight to disk, never accumulating output.
write_in_windows(
    "export_2024.csv",
    lambda window: window[window["country"] == "GB"],
    "uk_only.csv",
    chunk_rows=50_000,
    growth_ceiling_bytes=256 * 1024 * 1024,
)
```

## The contract

A windowed read produces the same DataFrame as the frozen whole-file adapter:

- the same columns, in the same order, as strings, with blanks not NaN;
- the same rows, in the same order, for well-formed input;
- the same encoding and separator decisions.

One documented difference: a streamed read decides the encoding from a bounded
sample of the head rather than from the whole file. Reading the whole file to
decide how to read the whole file defeats the purpose, and every streaming
reader samples. For a file whose encoding changes partway through, the two
reads can differ — such a file is already broken.

Equivalence is pinned by `tests/regression/test_chunked_golden.py` across
window sizes of 1, 2, 3, 5 and 11 rows, over an input containing blanks, an
embedded comma inside a quoted field, an escaped quote, non-ASCII text and a
padded field.

## The threshold

`read_large` streams a file at or over `DEFAULT_LARGE_BYTES` (1 GiB) and
delegates to the existing adapter below it, so a small file's read is unchanged
byte for byte. `plan_chunks` reports the decision and a rough window count
before you commit to a run.

## What can be streamed

`process_in_windows` and `write_in_windows` take a handler applied to each
window. The handler must be **row-local**: masking, normalisation, a filter,
per-row rules. A handler that needs global context — a dedupe across the whole
file, a percentile — is not safe here and will produce different output from a
whole-file run. That is a real limitation, stated rather than hidden; those
operations need a materialising merge.

`write_in_windows` streams `csv` and `tsv` only. Other formats need a
materialising merge first, and the function says so instead of silently
buffering the whole result.

## The memory ceiling

`growth_ceiling_bytes` measures *growth* of the process's resident set since
the call began, checked after every window. A growth figure, not an absolute
one: an absolute number would include the interpreter and the caller's own
data, and would mean different things in different programs.

```python
from app_files.ingestion import MemoryCeilingExceeded

try:
    write_in_windows(src, handler, out, growth_ceiling_bytes=256 << 20)
except MemoryCeilingExceeded as exc:
    print(exc.growth, exc.ceiling, exc.window)
```

On Linux the figure comes from `/proc/self/statm`. It deliberately does **not**
use `resource.getrusage().ru_maxrss`, which is a high-water mark that only
rises: a ceiling built on it reports zero growth once the process has peaked,
so it would pass a check it should fail. Where the figure is unavailable,
`current_rss_bytes()` returns `0` and callers skip the check rather than
inventing a number.

## Measured

A 278 MB, 3,000,000-row CSV, filtered to disk in 50,000-row windows:

| Read path | RSS growth |
|---|---|
| `write_in_windows` (streamed) | 29.7 MB |
| `read_any` (whole file) | 681.2 MB |

Streaming was 23x gentler on memory. Run it yourself with
`tests/unit/test_chunked_ingestion.py`, which asserts both that streaming stays
under a ceiling and that a whole read of the same file costs more — the second
claim is what stops the first from being decoration.
