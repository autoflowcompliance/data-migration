"""A watcher on a real inbox, with the real pipeline.

Unit tests use a fake clock. This drops real sample files into a real folder
and proves the output is the same bytes a batch run produces — the whole point
of the watcher being a trigger and not a second pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.batch import WatchFolder, run_batch

SAMPLES = Path(__file__).resolve().parents[2] / "app_files" / "samples"


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


def _drop(folder: Path, *names: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        (folder / name).write_bytes((SAMPLES / name).read_bytes())


class TestWatchOnRealSamples:
    def test_a_csv_landing_produces_a_real_migration(self, tmp_path, home):
        inbox = tmp_path / "inbox"
        _drop(inbox, "messy_contacts.csv")
        out = tmp_path / "out"

        watcher = WatchFolder(inbox, "hubspot", out, settle_seconds=1.0)
        watcher.ready(now=0.0)
        outcomes = watcher.process_ready(now=10.0)

        assert [o.file for o in outcomes] == ["messy_contacts.csv"]
        assert outcomes[0].ok
        assert outcomes[0].item.rows_out > 0
        assert (out / "messy_contacts" / "clean_data.csv").exists()
        assert (out / "messy_contacts" / "qa_report.html").exists()

    def test_output_matches_a_batch_run_byte_for_byte(self, tmp_path, home):
        inbox = tmp_path / "inbox"
        _drop(inbox, "messy_contacts.csv")
        watched_out = tmp_path / "watched"
        batch_out = tmp_path / "batch"

        run_batch(inbox, template="hubspot", output_dir=batch_out)
        watcher = WatchFolder(inbox, "hubspot", watched_out, settle_seconds=1.0)
        watcher.ready(now=0.0)
        watcher.process_ready(now=10.0)

        for name in ("clean_data.csv", "issues.csv", "mapping_log.csv"):
            assert (watched_out / "messy_contacts" / name).read_bytes() == (
                batch_out / "messy_contacts" / name
            ).read_bytes(), name

    def test_an_excel_drop_is_handled_too(self, tmp_path, home):
        inbox = tmp_path / "inbox"
        _drop(inbox, "messy_contacts.xlsx")
        out = tmp_path / "out"

        watcher = WatchFolder(inbox, "hubspot", out, settle_seconds=1.0)
        watcher.ready(now=0.0)
        outcomes = watcher.process_ready(now=10.0)
        assert [o.file for o in outcomes] == ["messy_contacts.xlsx"]
        assert outcomes[0].ok

    def test_a_part_file_beside_the_real_one_is_ignored(self, tmp_path, home):
        inbox = tmp_path / "inbox"
        _drop(inbox, "messy_contacts.csv")
        (inbox / "next_batch.csv.part").write_text("half,a,file\n")
        out = tmp_path / "out"

        watcher = WatchFolder(inbox, "hubspot", out, settle_seconds=1.0)
        watcher.ready(now=0.0)
        outcomes = watcher.process_ready(now=10.0)
        assert [o.file for o in outcomes] == ["messy_contacts.csv"]

    def test_two_files_landing_together_are_both_processed(self, tmp_path, home):
        inbox = tmp_path / "inbox"
        _drop(inbox, "messy_contacts.csv", "messy_contacts.xlsx")
        out = tmp_path / "out"

        watcher = WatchFolder(inbox, "hubspot", out, settle_seconds=1.0)
        watcher.ready(now=0.0)
        outcomes = watcher.process_ready(now=10.0)
        assert sorted(o.file for o in outcomes) == [
            "messy_contacts.csv",
            "messy_contacts.xlsx",
        ]
        assert all(o.ok for o in outcomes)

    def test_the_summary_of_the_whole_cycle_is_reproducible(self, tmp_path, home):
        """Two identical drops in two folders give identical outcomes."""
        results = []
        for index in (1, 2):
            inbox = tmp_path / f"inbox{index}"
            _drop(inbox, "messy_contacts.csv", "messy_contacts.xlsx")
            watcher = WatchFolder(inbox, "hubspot", tmp_path / f"out{index}",
                                  settle_seconds=1.0)
            watcher.ready(now=0.0)
            outcomes = watcher.process_ready(now=10.0)
            results.append([(o.file, o.item.rows_out, o.item.score) for o in outcomes])
        assert results[0] == results[1]
