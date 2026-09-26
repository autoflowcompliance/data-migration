"""Layer 14 end to end: the queue drives a real batch run.

The queue is a trigger and a bookkeeper. This proves the trigger fires: a job
whose payload names a folder runs the actual batch pipeline, and the output the
pipeline has always produced is the output the job reports.
"""

from __future__ import annotations

import shutil

import pytest

from app_files.batch import run_batch
from app_files.orchestration import (
    JobQueue,
    JobSpec,
    JobState,
    Priority,
    ResourceLimits,
    Worker,
    register_handler,
    run_workers,
)
from app_files.orchestration.workers import HANDLERS


@pytest.fixture(autouse=True)
def _clean_handlers():
    snapshot = dict(HANDLERS)
    yield
    HANDLERS.clear()
    HANDLERS.update(snapshot)


@pytest.fixture
def queue(tmp_path):
    return JobQueue(tmp_path / "jobs.jsonl")


def _register_batch():
    def run_batch_job(payload):
        result = run_batch(
            input_dir=payload["input_dir"],
            template=payload.get("template", "hubspot"),
            output_dir=payload["output_dir"],
            write_summary_files=False,
        )
        return {
            "files": len(result.items),
            "succeeded": sum(1 for item in result.items if item.ok),
        }

    register_handler("batch", run_batch_job)


class TestQueueDrivesThePipeline:
    def test_a_batch_job_runs_and_reports_its_counts(self, tmp_path, contacts_csv):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")
        _register_batch()

        queue = JobQueue(tmp_path / "jobs.jsonl")
        job = queue.submit(
            JobSpec(
                kind="batch",
                payload={
                    "input_dir": str(input_dir),
                    "output_dir": str(tmp_path / "out"),
                },
            )
        )
        Worker("w", queue).run()

        stored = queue.get(job.id)
        assert stored.state is JobState.SUCCEEDED
        assert stored.result["files"] == 1
        assert stored.result["succeeded"] == 1

    def test_the_batch_output_matches_a_direct_run(self, tmp_path, contacts_csv):
        """The queue must not change what the pipeline produces."""
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")

        direct = run_batch(
            input_dir=input_dir,
            template="hubspot",
            output_dir=tmp_path / "direct",
            write_summary_files=False,
        )
        _register_batch()
        queue = JobQueue(tmp_path / "jobs.jsonl")
        queue.submit(
            JobSpec(
                kind="batch",
                payload={
                    "input_dir": str(input_dir),
                    "output_dir": str(tmp_path / "queued"),
                },
            )
        )
        Worker("w", queue).run()

        direct_csv = (tmp_path / "direct" / "contacts" / "clean_data.csv").read_text()
        queued_csv = (tmp_path / "queued" / "contacts" / "clean_data.csv").read_text()
        assert queued_csv == direct_csv
        assert len(direct.items) == 1

    def test_a_failing_batch_job_does_not_stop_the_queue(self, tmp_path, contacts_csv):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")
        _register_batch()

        def bad_batch(payload):
            raise RuntimeError("disk full")

        register_handler("bad_batch", bad_batch)
        queue = JobQueue(tmp_path / "jobs.jsonl")
        bad = queue.submit(JobSpec(kind="bad_batch"))
        good = queue.submit(
            JobSpec(
                kind="batch",
                payload={"input_dir": str(input_dir), "output_dir": str(tmp_path / "out")},
            )
        )
        report = Worker("w", queue).run()
        assert report.succeeded == 1
        assert report.failed == 1
        assert queue.get(bad.id).state is JobState.FAILED
        assert queue.get(good.id).state is JobState.SUCCEEDED

    def test_two_workers_drain_two_batch_jobs_without_double_running(self, tmp_path, contacts_csv):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        shutil.copy(contacts_csv, input_dir / "contacts.csv")
        runs = {"n": 0}

        def counted_batch(payload):
            runs["n"] += 1
            result = run_batch(
                input_dir=payload["input_dir"],
                template="hubspot",
                output_dir=payload["output_dir"],
                write_summary_files=False,
            )
            return {"files": len(result.items), "runs": runs["n"]}

        register_handler("counted", counted_batch)
        queue = JobQueue(tmp_path / "jobs.jsonl")
        for index in range(4):
            queue.submit(
                JobSpec(
                    kind="counted",
                    payload={
                        "input_dir": str(input_dir),
                        "output_dir": str(tmp_path / f"out{index}"),
                    },
                )
            )
        reports = run_workers(queue, count=2, threads=True)
        assert sum(report.processed for report in reports) == 4
        assert runs["n"] == 4
        assert queue.counts()["succeeded"] == 4


class TestQueuePriorityEndToEnd:
    def test_priority_lanes_drain_in_order(self, queue):
        _register_batch()
        order: list[str] = []

        def recording(payload):
            order.append(payload["tag"])
            return {}

        register_handler("recording", recording)
        queue.submit(JobSpec(kind="recording", payload={"tag": "low"}, priority=Priority.LOW))
        queue.submit(JobSpec(kind="recording", payload={"tag": "high"}, priority=Priority.HIGH))
        queue.submit(JobSpec(kind="recording", payload={"tag": "normal"}))
        Worker("w", queue).run()
        assert order == ["high", "normal", "low"]

    def test_a_resource_limit_stops_a_runaway_job(self, queue):
        def hog(payload):
            return {"blob": bytearray(60 * 1024 * 1024)}

        register_handler("hog", hog)
        job = queue.submit(
            JobSpec(kind="hog", limits=ResourceLimits(max_memory_mb=1.0))
        )
        Worker("w", queue).run()
        stored = queue.get(job.id)
        assert stored.state is JobState.FAILED
        assert "memory" in stored.error.lower()
