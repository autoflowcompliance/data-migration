"""Golden file for the watcher (Layer 9 trigger, Layer 1 drop-in).

A file dropped into a watched folder must produce the *same* output as the
batch command. The golden pins the clean CSV and the outcome summary so an
accidental change to how the settle window picks files up — say, reading a
partly-written file — shows up here as different bytes.

Do not regenerate the expected file to make the test green.
"""

from __future__ import annotations

from pathlib import Path

from app_files.batch import WatchFolder

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "watcher"
SAMPLES = Path(__file__).resolve().parents[2] / "app_files" / "samples"


def _watch_a_drop(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "home"))
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "messy_contacts.csv").write_bytes(
        (SAMPLES / "messy_contacts.csv").read_bytes()
    )
    watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
    watcher.ready(now=0.0)
    return watcher.process_ready(now=10.0)


def test_watcher_golden_clean_data(tmp_path, monkeypatch):
    outcomes = _watch_a_drop(tmp_path, monkeypatch)
    assert len(outcomes) == 1
    produced = (tmp_path / "out" / "messy_contacts" / "clean_data.csv").read_bytes()
    assert produced == (GOLDEN / "clean_data.csv").read_bytes()


def test_watcher_golden_outcome(tmp_path, monkeypatch):
    outcome = _watch_a_drop(tmp_path, monkeypatch)[0]
    produced = (
        f"file={outcome.file}\n"
        f"rows_out={outcome.item.rows_out}\n"
        f"score={outcome.item.score}\n"
    )
    assert produced == (GOLDEN / "outcome.txt").read_text()
