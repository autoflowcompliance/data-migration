# Watch folders

Process a file the moment it lands in a folder, instead of waiting for someone
to run the batch command.

```bash
python -m app_files.cli watch --in inbox --template hubspot --out out
```

Or from Python:

```python
from app_files.batch import WatchFolder

folder = WatchFolder("inbox", "hubspot", "out", settle_seconds=2)
folder.run(poll_interval=5)          # until interrupted
folder.process_ready()               # one poll
```

## The settle window

A file is only read once its size and mtime have held steady for
`settle_seconds`. Without this, an export that lands in several writes is read
at the first write: the file is truncated, but it is a valid CSV with a valid
header, so the pipeline happily produces a plausible, wrong migration. There is
no error to notice, which is exactly why the check exists.

A file that grows restarts its window from the new size. A file that has not
been touched for the settle window is ready.

## Running from cron

`--once` polls once and exits:

```cron
* * * * * cd /srv/dataflow && python -m app_files.cli watch \
    --in /srv/inbox --template hubspot --out /srv/out --once --settle 30
```

This works because the settle observation is written to disk, not held in
memory. The first invocation observes the file and exits; a later invocation —
a separate process — sees the same size and mtime, the settle window has
passed, and the file is processed. An in-memory window would make the cron path
never process anything, because every run would be seeing the file for the
first time.

The same file, once processed, is recorded and is not processed again. If it
changes (a new export overwrites it), the record no longer matches and the file
is treated as new.

## What is ignored

- In-progress names: `.part`, `.partial`, `.tmp`, `.crdownload`, `.download`,
  `.filepart`.
- Editor lock files: `~$…` and `.~…` (Word and Excel write one beside the real
  file).
- Extensions the ingestion layer does not support.
- Subdirectories. Only direct children of the watched folder are considered.

## State

State lives in `$AUTOFLOW_HOME/watch_state.json` (default `~/.autoflow/`):

```json
{
  "/srv/inbox": {
    "seen": {"…/contacts.csv": {"first_seen": 1.7e9, "size": 812, "mtime": 1.7e9}},
    "handled": {"…/contacts.csv": {"size": 812, "mtime": 1.7e9}}
  }
}
```

Runtime state, deliberately not inside the package: an installed client has
read-only program files, and a watcher that can only remember what it has seen
by writing into its own package would reprocess the inbox forever.

A corrupt or unreadable state file is treated as "unknown", never as
"everything is new" — reprocessing an inbox on a corrupt byte would
double-deliver.

## Output

Identical to a batch run, byte for byte. The watcher is a trigger for
`app_files.batch.runner.process_one`, not a second pipeline. Per-file output
goes to `<out>/<stem>/`, the same layout batch uses.
