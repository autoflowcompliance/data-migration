"""Watch folders: process a file the moment it lands (Layer 9 / Layer 1).

The two ways a watcher causes damage are reading a file that is still being
written, and reprocessing the whole folder on every poll. Both are tested with
a fake clock rather than real sleeps.
"""

from __future__ import annotations

import os

import pytest

from app_files.batch import WatchFolder, is_deliverable, watch_once, watch_state_path


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


@pytest.fixture
def inbox(tmp_path, contacts_csv):
    folder = tmp_path / "inbox"
    folder.mkdir()
    (folder / "contacts.csv").write_bytes(contacts_csv.read_bytes())
    return folder


class TestDeliverableFilter:
    def test_a_supported_file_is_deliverable(self, tmp_path):
        path = tmp_path / "a.csv"
        path.write_text("a\n1\n")
        assert is_deliverable(path) is True

    @pytest.mark.parametrize(
        "name", ["a.csv.part", "a.csv.tmp", "big.csv.crdownload", "a.csv.download"]
    )
    def test_in_progress_suffixes_are_not_deliverable(self, tmp_path, name):
        path = tmp_path / name
        path.write_text("x")
        assert is_deliverable(path) is False

    def test_office_lock_files_are_not_deliverable(self, tmp_path):
        path = tmp_path / "~$book.xlsx"
        path.write_text("x")
        assert is_deliverable(path) is False

    def test_an_unsupported_extension_is_not_deliverable(self, tmp_path):
        path = tmp_path / "notes.md"
        path.write_text("x")
        assert is_deliverable(path) is False

    def test_a_directory_is_not_deliverable(self, tmp_path):
        folder = tmp_path / "a.csv"
        folder.mkdir()
        assert is_deliverable(folder) is False


class TestSettling:
    def test_a_file_seen_once_is_not_ready_yet(self, inbox, tmp_path, home):
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=2.0)
        assert watcher.ready(now=100.0) == []

    def test_a_file_steady_for_the_settle_window_is_ready(self, inbox, tmp_path, home):
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=2.0)
        watcher.ready(now=100.0)
        assert [p.name for p in watcher.ready(now=102.5)] == ["contacts.csv"]

    def test_a_growing_file_restarts_its_window(self, inbox, tmp_path, home):
        """A file that is still being written must never be read."""
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=2.0)
        watcher.ready(now=100.0)
        with (inbox / "contacts.csv").open("a", encoding="utf-8") as handle:
            handle.write("still,arriving\n1,2\n")
        assert watcher.ready(now=103.0) == []
        assert [p.name for p in watcher.ready(now=105.5)] == ["contacts.csv"]

    def test_a_missing_folder_yields_nothing(self, tmp_path, home):
        watcher = WatchFolder(tmp_path / "nope", "hubspot", tmp_path / "out")
        assert watcher.candidates() == []
        assert watcher.ready(now=1.0) == []


class TestProcessingOnce:
    def _settle(self, watcher):
        watcher.ready(now=0.0)
        return watcher.process_ready(now=10.0)

    def test_a_new_file_is_processed_and_written(self, inbox, tmp_path, home):
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        outcomes = self._settle(watcher)
        assert [o.file for o in outcomes] == ["contacts.csv"]
        assert outcomes[0].ok is True
        assert (tmp_path / "out" / "contacts" / "clean_data.csv").exists()

    def test_an_untouched_file_is_not_processed_twice(self, inbox, tmp_path, home):
        """Delivery folders are not emptied, so a second poll must be a no-op."""
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        self._settle(watcher)
        assert watcher.ready(now=10.0) == []
        assert watcher.process_ready(now=20.0) == []

    def test_a_changed_file_is_processed_again(self, inbox, tmp_path, home):
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        self._settle(watcher)
        with (inbox / "contacts.csv").open("a", encoding="utf-8") as handle:
            handle.write("new,row,added,here,now\n1,2,3,4,5\n")
        watcher.ready(now=30.0)
        assert [o.file for o in watcher.process_ready(now=40.0)] == ["contacts.csv"]

    def test_a_failed_file_is_not_retried_forever(self, inbox, tmp_path, home):
        """A file the pipeline rejects is marked, not looped on."""
        bad = inbox / "empty.csv"
        bad.write_text("", encoding="utf-8")
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        outcomes = self._settle(watcher)
        failed = [o for o in outcomes if o.file == "empty.csv"]
        assert failed and failed[0].ok is False
        assert watcher.ready(now=10.0) == []

    def test_state_survives_a_new_watcher_instance(self, inbox, tmp_path, home):
        first = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        self._settle(first)
        second = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        assert second.ready(now=0.0) == []

    def test_the_state_file_lives_under_autoflow_home(self, inbox, tmp_path, home):
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        self._settle(watcher)
        assert watcher.state_path == watch_state_path()
        assert str(watcher.state_path).startswith(str(home))
        assert watcher.state_path.exists()

    def test_a_corrupt_state_file_is_not_read_as_everything_is_new(
        self, inbox, tmp_path, home
    ):
        """Unknown is not 'new': reprocessing an inbox double-delivers."""
        path = watch_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json", encoding="utf-8")
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        assert watcher.state.load() == {}
        # The file is genuinely unseen, so it does process once, then stops.
        self._settle(watcher)
        assert watcher.ready(now=10.0) == []


class TestRunLoop:
    def test_run_with_iterations_uses_the_injected_clock(self, inbox, tmp_path, home):
        ticks = iter([0.0, 10.0])
        sleeps: list[float] = []
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        outcomes = watcher.run(
            iterations=2,
            poll_interval=1.0,
            sleep=sleeps.append,
            clock=lambda: next(ticks),
        )
        assert [o.file for o in outcomes] == ["contacts.csv"]
        assert sleeps == [1.0]

    def test_watch_once_processes_nothing_before_settling(self, inbox, tmp_path, home):
        assert watch_once(inbox, "hubspot", tmp_path / "out") == []

    def test_output_is_identical_to_a_batch_run(self, inbox, tmp_path, home):
        """The watcher is a trigger, not a second pipeline."""
        from app_files.batch import run_batch

        watched_out = tmp_path / "watched"
        batch_out = tmp_path / "batch"
        run_batch(inbox, template="hubspot", output_dir=batch_out)

        watcher = WatchFolder(inbox, "hubspot", watched_out, settle_seconds=1.0)
        watcher.ready(now=0.0)
        watcher.process_ready(now=10.0)

        watched = (watched_out / "contacts" / "clean_data.csv").read_bytes()
        batch = (batch_out / "contacts" / "clean_data.csv").read_bytes()
        assert watched == batch


class TestOutcomeShape:
    def test_outcome_reports_rows_and_score(self, inbox, tmp_path, home):
        watcher = WatchFolder(inbox, "hubspot", tmp_path / "out", settle_seconds=1.0)
        watcher.ready(now=0.0)
        outcome = watcher.process_ready(now=10.0)[0]
        data = outcome.as_dict()
        assert data["rows_out"] > 0
        assert data["score"] is not None

    def test_a_missing_outcome_has_zero_rows(self):
        from app_files.batch import WatchOutcome

        data = WatchOutcome(file="x.csv", status="skipped", reason="not ready").as_dict()
        assert data["rows_out"] == 0
        assert data["score"] is None


def test_state_path_is_not_inside_the_package(monkeypatch, tmp_path):
    """An installed client has read-only program files."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    assert "app_files" not in str(watch_state_path())


def test_default_state_path_without_a_home(monkeypatch):
    monkeypatch.delenv("AUTOFLOW_HOME", raising=False)
    assert str(watch_state_path()).startswith(str(os.path.expanduser("~")))
