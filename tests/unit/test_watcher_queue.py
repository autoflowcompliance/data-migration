"""Watch folders, incremental processing, and the job queue."""

from __future__ import annotations

import pytest

from app_files.orchestration import (
    IncrementalState,
    JobQueue,
    QueueFullError,
    incremental_work_list,
    mark_processed,
    poll_watch_folder,
    scan_watched_directory,
)
from app_files.orchestration.watcher import load_watch_state, save_watch_state


@pytest.fixture
def watch_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "home"))
    folder = tmp_path / "inbox"
    folder.mkdir()
    return folder


def _write(folder, name, text="a,b\n1,2\n"):
    target = folder / name
    target.write_text(text)
    return target


# ------------------------------------------------------------ watch folders
def test_first_scan_sees_every_file_as_new(watch_env):
    _write(watch_env, "a.csv")
    _write(watch_env, "b.csv")
    new, changed, removed = scan_watched_directory(watch_env)
    assert {f.path.split("/")[-1] for f in new} == {"a.csv", "b.csv"}
    assert changed == []
    assert removed == []


def test_an_unchanged_file_is_not_seen_again(watch_env):
    _write(watch_env, "a.csv")
    new, _, _ = scan_watched_directory(watch_env)
    known = {entry.path: entry for entry in new}
    new2, changed, removed = scan_watched_directory(watch_env, known=known)
    assert new2 == [] and changed == [] and removed == []


def test_an_edited_file_is_seen_as_changed(watch_env):
    target = _write(watch_env, "a.csv", "a,b\n1,2\n")
    new, _, _ = scan_watched_directory(watch_env)
    known = {entry.path: entry for entry in new}
    target.write_text("a,b\n1,2\n3,4\n")  # grows, so size differs
    new2, changed, _ = scan_watched_directory(watch_env, known=known)
    assert new2 == []
    assert [f.path.split("/")[-1] for f in changed] == ["a.csv"]


def test_a_deleted_file_is_reported_as_removed(watch_env):
    target = _write(watch_env, "a.csv")
    new, _, _ = scan_watched_directory(watch_env)
    known = {entry.path: entry for entry in new}
    target.unlink()
    _, _, removed = scan_watched_directory(watch_env, known=known)
    assert [f.path.split("/")[-1] for f in removed] == ["a.csv"]


def test_non_matching_extensions_are_ignored(watch_env):
    _write(watch_env, "notes.txt")
    _write(watch_env, "a.csv")
    new, _, _ = scan_watched_directory(watch_env)
    assert [f.path.split("/")[-1] for f in new] == ["a.csv"]


def test_poll_remembers_state_across_calls(watch_env):
    _write(watch_env, "a.csv")
    first = poll_watch_folder(watch_env)
    assert first["pending"] == 1
    second = poll_watch_folder(watch_env)
    assert second["pending"] == 0


def test_poll_picks_up_a_file_added_later(watch_env):
    _write(watch_env, "a.csv")
    poll_watch_folder(watch_env)
    _write(watch_env, "b.csv")
    result = poll_watch_folder(watch_env)
    assert [f["path"].split("/")[-1] for f in result["new"]] == ["b.csv"]


def test_scanning_a_missing_directory_raises(watch_env):
    with pytest.raises(NotADirectoryError):
        scan_watched_directory(watch_env / "nope")


def test_corrupt_watch_state_is_ignored(watch_env):
    _write(watch_env, "a.csv")
    from app_files.orchestration.watcher import watch_state_path

    state = watch_state_path()
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text("{not json")
    assert load_watch_state() == {}


# ------------------------------------------------------- incremental processing
def test_work_list_skips_already_processed_items():
    state = IncrementalState(processed=["a.csv", "b.csv"])
    assert incremental_work_list(["a.csv", "b.csv", "c.csv"], state) == ["c.csv"]


def test_watermark_makes_a_newer_item_pending_again():
    state = IncrementalState(processed=["b.csv"])
    # The watermark is where the last run got to; anything after it is pending.
    assert incremental_work_list(["b.csv", "c.csv"], state, watermark="b.csv") == ["c.csv"]


def test_mark_processed_is_sorted_and_deduplicated():
    state = IncrementalState(processed=["b.csv"])
    updated = mark_processed(state, ["a.csv", "b.csv", "a.csv"])
    assert updated.processed == ["a.csv", "b.csv"]
    assert updated.last_run


def test_state_round_trips_through_a_file(tmp_path):
    from app_files.orchestration import load_incremental_state, save_incremental_state

    path = tmp_path / "state.json"
    save_incremental_state(mark_processed(IncrementalState(), ["a.csv"]), "job", path=path)
    reloaded = load_incremental_state("job", path=path)
    assert reloaded.processed == ["a.csv"]


def test_a_missing_incremental_state_is_empty(tmp_path):
    from app_files.orchestration import load_incremental_state

    state = load_incremental_state("none", path=tmp_path / "nothing.json")
    assert state.processed == []
    assert state.last_run == ""


# ---------------------------------------------------------------- job queue
def test_queue_runs_jobs_in_order():
    queue = JobQueue(capacity=10)
    queue.submit({"n": 1})
    queue.submit({"n": 2})
    order = []
    queue.drain(lambda job: order.append(job.payload["n"]))
    assert order == [1, 2]


def test_queue_reports_when_full():
    queue = JobQueue(capacity=2)
    queue.submit()
    queue.submit()
    with pytest.raises(QueueFullError, match="full"):
        queue.submit()


def test_a_failed_job_does_not_stop_the_drain():
    queue = JobQueue(capacity=10)
    queue.submit({"n": 1})
    queue.submit({"n": 2})

    def worker(job):
        if job.payload["n"] == 1:
            raise ValueError("boom")
        return "ok"

    handled = queue.drain(worker)
    assert handled == {"done": 1, "failed": 1}
    assert queue.counts()["failed"] == 1
    assert queue.counts()["done"] == 1


def test_a_failed_job_can_be_retried():
    queue = JobQueue(capacity=10)
    job = queue.submit()
    queue.drain(lambda _: (_ for _ in ()).throw(RuntimeError("nope")))
    assert queue._jobs[job.id].status == "failed"
    queue.retry(job.id)
    assert queue._jobs[job.id].status == "queued"
    queue.drain(lambda _: "ok")
    assert queue.counts()["done"] == 1


def test_retrying_a_job_that_did_not_fail_is_an_error():
    queue = JobQueue(capacity=10)
    job = queue.submit()
    with pytest.raises(ValueError, match="not failed"):
        queue.retry(job.id)


def test_duplicate_job_ids_are_rejected():
    queue = JobQueue(capacity=10)
    queue.submit(job_id="fixed")
    with pytest.raises(ValueError, match="already exists"):
        queue.submit(job_id="fixed")


def test_drain_respects_max_jobs():
    queue = JobQueue(capacity=10)
    for n in range(5):
        queue.submit({"n": n})
    handled = queue.drain(lambda job: None, max_jobs=2)
    assert handled["done"] == 2
    assert queue.counts()["queued"] == 3


def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        JobQueue(capacity=0)


def test_attempts_are_counted():
    queue = JobQueue(capacity=10)
    job = queue.submit()
    queue.next_job()
    assert queue._jobs[job.id].attempts == 1


def test_unknown_job_completion_is_an_error():
    queue = JobQueue(capacity=10)
    with pytest.raises(KeyError):
        queue.complete("nope")