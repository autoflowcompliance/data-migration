"""Layer 14 — a durable job queue, workers, and resource limits."""

from __future__ import annotations

import json
import threading
import time

import pytest

from app_files.orchestration import (
    JobQueue,
    JobSpec,
    JobState,
    LimitBreach,
    Priority,
    ResourceBudget,
    ResourceLimits,
    ResourceUsage,
    Worker,
    check_budget,
    measure,
    register_handler,
    registered_kinds,
    run_workers,
)


@pytest.fixture(autouse=True)
def _clean_handlers():
    from app_files.orchestration.workers import HANDLERS

    snapshot = dict(HANDLERS)
    yield
    HANDLERS.clear()
    HANDLERS.update(snapshot)


@pytest.fixture
def queue(tmp_path):
    return JobQueue(tmp_path / "jobs.jsonl")


def _spec(kind="noop", **kwargs):
    return JobSpec(kind=kind, **kwargs)


# --------------------------------------------------------------------- queue
class TestJobQueue:
    def test_a_submitted_job_is_queued(self, queue):
        job = queue.submit(_spec())
        assert queue.get(job.id).state is JobState.QUEUED
        assert queue.counts()["queued"] == 1

    def test_state_survives_a_reopen(self, queue):
        job = queue.submit(_spec())
        reopened = JobQueue(queue.path)
        assert reopened.get(job.id) is not None

    def test_succeeding_a_job_records_a_result(self, queue):
        job = queue.submit(_spec())
        queue.claim("w")
        queue.succeed(job.id, {"rows": 12})
        stored = queue.get(job.id)
        assert stored.state is JobState.SUCCEEDED
        assert stored.result["rows"] == 12

    def test_failing_a_job_records_the_error(self, queue):
        job = queue.submit(_spec())
        queue.claim("w")
        queue.fail(job.id, "boom")
        stored = queue.get(job.id)
        assert stored.state is JobState.FAILED
        assert stored.error == "boom"

    def test_claim_returns_none_on_an_empty_queue(self, queue):
        assert queue.claim("w") is None

    def test_claim_marks_the_job_running_and_counts_the_attempt(self, queue):
        queue.submit(_spec())
        claimed = queue.claim("worker-a")
        assert claimed.state is JobState.RUNNING
        assert claimed.attempts == 1
        assert claimed.worker == "worker-a"

    def test_a_claimed_job_is_not_claimed_twice(self, queue):
        queue.submit(_spec())
        first = queue.claim("a")
        assert first is not None
        assert queue.claim("b") is None

    def test_priority_order_is_high_first(self, queue):
        low = queue.submit(_spec(priority=Priority.LOW))
        high = queue.submit(_spec(priority=Priority.HIGH))
        normal = queue.submit(_spec(priority=Priority.NORMAL))
        order = [queue.claim("w").id for _ in range(3)]
        assert order == [high.id, normal.id, low.id]

    def test_within_a_lane_the_oldest_wins(self, queue):
        first = queue.submit(_spec())
        time.sleep(0.01)
        second = queue.submit(_spec())
        assert queue.claim("w").id == first.id
        assert queue.claim("w").id == second.id

    def test_a_dependency_blocks_a_job_until_its_parent_succeeds(self, queue):
        parent = queue.submit(_spec())
        child = queue.submit(_spec(depends_on=[parent.id]))
        assert queue.claim("w").id == parent.id
        assert queue.claim("w") is None  # child still blocked
        queue.succeed(parent.id)
        assert queue.claim("w").id == child.id

    def test_a_dependency_on_an_unknown_job_is_refused(self, queue):
        with pytest.raises(ValueError, match="unknown job"):
            queue.submit(_spec(depends_on=["ghost"]))

    def test_cancel_removes_a_queued_job(self, queue):
        job = queue.submit(_spec())
        queue.cancel(job.id)
        assert queue.get(job.id).state is JobState.CANCELLED
        assert queue.claim("w") is None

    def test_a_running_job_cannot_be_cancelled(self, queue):
        job = queue.submit(_spec())
        queue.claim("w")
        with pytest.raises(ValueError, match="only queued"):
            queue.cancel(job.id)

    def test_requeue_returns_a_failed_job_to_the_queue(self, queue):
        job = queue.submit(_spec())
        queue.claim("w")
        queue.fail(job.id, "transient")
        queue.requeue(job.id)
        stored = queue.get(job.id)
        assert stored.state is JobState.QUEUED
        assert stored.error is None

    def test_a_stale_running_job_is_recovered(self, queue):
        job = queue.submit(_spec())
        queue.claim("dead-worker")
        # Age the job past the deadline.
        records = queue._lines()
        records[-1]["started_at"] = time.time() - 7200
        queue.path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
        recovered = queue.requeue_stale(older_than_seconds=3600)
        assert recovered == [job.id]
        assert queue.get(job.id).state is JobState.QUEUED

    def test_a_torn_final_line_does_not_lose_the_queue(self, queue):
        job = queue.submit(_spec())
        with open(queue.path, "a", encoding="utf-8") as handle:
            handle.write('{"id": "partial", "spec":')  # crash mid-append
        assert queue.get(job.id) is not None

    def test_the_lock_is_released_after_a_write(self, queue):
        queue.submit(_spec())
        assert not queue.lock_path.exists()

    def test_a_stuck_lock_times_out_with_a_clear_message(self, tmp_path):
        stuck = JobQueue(tmp_path / "jobs.jsonl", lock_timeout=0.05)
        stuck.lock_path.parent.mkdir(parents=True, exist_ok=True)
        stuck.lock_path.write_text("99999")
        with pytest.raises(TimeoutError, match="Could not lock"):
            stuck.submit(_spec())

    def test_render_summarises_the_queue(self, queue):
        queue.submit(_spec())
        assert "queued" in queue.render()

    def test_render_handles_an_empty_queue(self, queue):
        assert "empty" in queue.render()


class TestQueueUnderConcurrency:
    def test_two_threads_never_claim_the_same_job(self, queue):
        for _ in range(20):
            queue.submit(_spec())
        claimed: list[str] = []
        lock = threading.Lock()

        def worker():
            while True:
                job = queue.claim("t")
                if job is None:
                    return
                with lock:
                    claimed.append(job.id)
                queue.succeed(job.id)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(claimed) == 20
        assert len(set(claimed)) == 20


# ------------------------------------------------------------------- limits
class TestResourceLimits:
    def test_an_unbounded_limit_admits_everything(self):
        assert check_budget(ResourceLimits(), ResourceUsage(peak_memory_mb=1e9)) is None

    def test_a_memory_breach_is_reported(self):
        message = check_budget(
            ResourceLimits(max_memory_mb=10.0), ResourceUsage(peak_memory_mb=11.0)
        )
        assert message and "memory" in message.lower()

    def test_a_runtime_breach_is_reported(self):
        message = check_budget(
            ResourceLimits(max_runtime_seconds=1.0), ResourceUsage(wall_seconds=2.0)
        )
        assert message and "runtime" in message.lower()

    def test_a_cpu_breach_is_reported(self):
        message = check_budget(
            ResourceLimits(max_cpu_seconds=1.0), ResourceUsage(cpu_seconds=2.0)
        )
        assert message and "cpu" in message.lower()

    def test_within_budget_returns_no_message(self):
        limits = ResourceLimits(max_memory_mb=100.0, max_runtime_seconds=10.0)
        assert check_budget(limits, ResourceUsage(peak_memory_mb=5, wall_seconds=1)) is None

    def test_the_first_exceeded_limit_is_the_one_reported(self):
        limits = ResourceLimits(max_memory_mb=1.0, max_runtime_seconds=1.0)
        usage = ResourceUsage(peak_memory_mb=2.0, wall_seconds=2.0)
        assert "memory" in check_budget(limits, usage).lower()

    def test_a_budget_tracks_wall_time(self):
        budget = ResourceBudget()
        time.sleep(0.02)
        assert budget.usage().wall_seconds > 0

    def test_require_within_raises_on_breach(self):
        limits = ResourceLimits(max_runtime_seconds=0.0)
        budget = ResourceBudget(limits=limits)
        time.sleep(0.01)
        with pytest.raises(LimitBreach):
            budget.require_within()

    def test_measure_runs_the_function_and_reports_usage(self):
        result, usage = measure(lambda: 42)
        assert result == 42
        assert usage.wall_seconds >= 0

    def test_measure_raises_on_a_breach(self):
        with pytest.raises(LimitBreach):
            measure(lambda: time.sleep(0.02), limits=ResourceLimits(max_runtime_seconds=0.001))

    def test_an_unaffordable_declared_memory_is_refused(self):
        from app_files.orchestration.limits import affordable

        assert affordable(ResourceLimits(max_memory_mb=100.0), available_mb=50.0) is False

    def test_an_affordable_declared_memory_is_admitted(self):
        from app_files.orchestration.limits import affordable

        assert affordable(ResourceLimits(max_memory_mb=10.0), available_mb=50.0) is True

    def test_no_declared_limit_is_always_affordable(self):
        from app_files.orchestration.limits import affordable

        assert affordable(ResourceLimits(), available_mb=0.0) is True

    def test_limits_round_trip_through_config(self):
        limits = ResourceLimits(max_memory_mb=64, max_runtime_seconds=30)
        spec = JobSpec.from_dict({"kind": "x", "limits": limits.as_dict()})
        assert spec.limits.max_memory_mb == 64
        assert spec.limits.max_runtime_seconds == 30

    def test_current_memory_is_reported_where_the_platform_allows(self):
        from app_files.orchestration.limits import current_memory_mb

        assert current_memory_mb() > 0

    def test_a_job_that_allocates_past_its_budget_fails(self, queue):
        def hog(payload):
            return {"blob": bytearray(40 * 1024 * 1024)}

        register_handler("hog", hog)
        job = queue.submit(_spec(kind="hog", limits=ResourceLimits(max_memory_mb=1.0)))
        Worker("w", queue).run()
        assert queue.get(job.id).state is JobState.FAILED
        assert "memory" in queue.get(job.id).error.lower()

    def test_the_memory_limit_holds_with_a_warm_allocator_arena(self, queue):
        """The bug this pins: RSS growth is blind to arena reuse.

        Allocating and freeing the same size first leaves the pages resident, so
        a subsequent allocation of that size does not raise RSS at all -- and a
        limit read from RSS alone then misses it entirely. Reproduced reliably:
        60 of 60 warm-arena allocations slipped past a 1 MB limit. This is why
        the measurement is not RSS growth alone.
        """
        import gc

        def hog(payload):
            return {"blob": bytearray(40 * 1024 * 1024)}

        register_handler("hog", hog)
        # Warm the arena with allocations of the same size, then free them. RSS
        # after this is already ~40 MB, so the job's own allocation adds none.
        for _ in range(4):
            bytearray(40 * 1024 * 1024)
        gc.collect()

        for _ in range(5):
            job = queue.submit(_spec(kind="hog", limits=ResourceLimits(max_memory_mb=1.0)))
            Worker("w", queue).run()
            assert queue.get(job.id).state is JobState.FAILED, "warm arena slipped past the limit"
            assert "memory" in queue.get(job.id).error.lower()

    def test_memory_growth_is_measured_by_allocation_not_resident_pages(self):
        """A budget's usage must see an allocation the OS never re-faulted."""
        import gc

        bytearray(40 * 1024 * 1024)
        gc.collect()
        budget = ResourceBudget(limits=ResourceLimits(max_memory_mb=1.0))
        try:
            bytearray(40 * 1024 * 1024)
            assert budget.usage().peak_memory_mb > 1.0
            assert budget.breach() is not None
        finally:
            # Release the tracer. Leaving a budget's own tracing running would
            # tax every later test in the session with tracemalloc's overhead.
            budget.stop()


# ------------------------------------------------------------------ workers
class TestWorkers:
    def test_a_worker_runs_a_job_to_success(self, queue):
        register_handler("noop", lambda payload: {"echo": payload.get("n")})
        queue.submit(_spec(payload={"n": 7}))
        report = Worker("w", queue).run()
        assert report.succeeded == 1
        assert next(iter(queue.jobs().values())).result["echo"] == 7

    def test_an_unserialisable_result_fails_cleanly(self, queue):
        """A handler may return bytes; the durable log holds JSON.

        Before this was guarded, the json.dumps inside the queue raised out of
        the worker, the job stayed RUNNING forever, and the failure surfaced as
        a bare TypeError rather than anything a user could act on.
        """
        register_handler("bytes_result", lambda payload: {"blob": b"\x00binary"})
        job = queue.submit(_spec(kind="bytes_result"))
        report = Worker("w", queue).run()
        assert report.failed == 1
        stored = queue.get(job.id)
        assert stored.state is JobState.FAILED
        assert "could not be stored" in stored.error

    def test_a_handler_failure_marks_the_job_failed(self, queue):
        register_handler("boom", lambda payload: (_ for _ in ()).throw(RuntimeError("nope")))
        job = queue.submit(_spec(kind="boom"))
        Worker("w", queue).run()
        assert queue.get(job.id).state is JobState.FAILED
        assert "nope" in queue.get(job.id).error

    def test_an_unknown_kind_fails_only_that_job(self, queue):
        register_handler("noop", lambda payload: {})
        bad = queue.submit(_spec(kind="missing"))
        good = queue.submit(_spec(kind="noop"))
        report = Worker("w", queue).run()
        assert report.succeeded == 1
        assert report.failed == 1
        assert queue.get(bad.id).state is JobState.FAILED
        assert queue.get(good.id).state is JobState.SUCCEEDED

    def test_a_transient_failure_retries_when_configured(self, queue):
        attempts = {"n": 0}

        def flaky(payload):
            attempts["n"] += 1
            if attempts["n"] == 1:
                raise RuntimeError("transient")
            return {"attempt": attempts["n"]}

        register_handler("flaky", flaky)
        job = queue.submit(_spec(kind="flaky", max_attempts=2))
        report = Worker("w", queue).run()
        assert report.succeeded == 1
        assert report.requeued == 1
        assert queue.get(job.id).result["attempt"] == 2

    def test_retries_are_capped_at_max_attempts(self, queue):
        register_handler("always", lambda payload: (_ for _ in ()).throw(RuntimeError("x")))
        job = queue.submit(_spec(kind="always", max_attempts=2))
        Worker("w", queue).run()
        assert queue.get(job.id).state is JobState.FAILED
        assert queue.get(job.id).attempts == 2

    def test_a_job_over_its_memory_budget_is_refused_before_it_runs(self, queue):
        ran = {"n": 0}

        def big(payload):
            ran["n"] += 1
            return {}

        register_handler("big", big)
        job = queue.submit(_spec(kind="big", limits=ResourceLimits(max_memory_mb=99999)))
        Worker("w", queue, available_mb=64.0).run()
        assert ran["n"] == 0
        assert queue.get(job.id).state is JobState.FAILED
        assert "available" in queue.get(job.id).error

    def test_a_job_within_its_budget_runs(self, queue):
        register_handler("small", lambda payload: {})
        queue.submit(_spec(kind="small", limits=ResourceLimits(max_memory_mb=10.0)))
        report = Worker("w", queue, available_mb=1024.0).run()
        assert report.succeeded == 1

    def test_a_runtime_breach_fails_the_job(self, queue):
        register_handler("slow", lambda payload: time.sleep(0.05) or {})
        job = queue.submit(_spec(kind="slow", limits=ResourceLimits(max_runtime_seconds=0.001)))
        Worker("w", queue).run()
        assert queue.get(job.id).state is JobState.FAILED
        assert "limit" in queue.get(job.id).error.lower()

    def test_the_report_records_the_usage(self, queue):
        register_handler("noop", lambda payload: {})
        queue.submit(_spec())
        Worker("w", queue).run()
        assert "usage" in next(iter(queue.jobs().values())).result

    def test_run_once_processes_exactly_one_job(self, queue):
        register_handler("noop", lambda payload: {})
        queue.submit(_spec())
        queue.submit(_spec())
        assert Worker("w", queue).run_once() is not None
        assert queue.counts()["succeeded"] == 1
        assert queue.counts()["queued"] == 1

    def test_max_jobs_caps_a_run(self, queue):
        register_handler("noop", lambda payload: {})
        for _ in range(5):
            queue.submit(_spec())
        report = Worker("w", queue).run(max_jobs=2)
        assert report.processed == 2
        assert queue.counts()["queued"] == 3


class TestWorkerPool:
    def test_sequential_workers_drain_the_queue(self, queue):
        register_handler("noop", lambda payload: {})
        for _ in range(9):
            queue.submit(_spec())
        reports = run_workers(queue, count=3)
        assert sum(report.processed for report in reports) == 9
        assert queue.counts()["succeeded"] == 9

    def test_concurrent_workers_do_not_double_process(self, queue):
        register_handler("noop", lambda payload: {"worker": 1})
        for _ in range(50):
            queue.submit(_spec())
        reports = run_workers(queue, count=4, threads=True)
        assert sum(report.processed for report in reports) == 50
        assert queue.counts()["succeeded"] == 50

    def test_throughput_does_not_depend_on_worker_count_for_correctness(self, queue):
        register_handler("noop", lambda payload: {})
        for _ in range(20):
            queue.submit(_spec())
        run_workers(queue, count=1)
        assert queue.counts()["succeeded"] == 20

    def test_registered_kinds_are_listed(self):
        register_handler("noop", lambda payload: {})
        assert "noop" in registered_kinds()

    def test_registering_a_duplicate_kind_is_refused(self):
        register_handler("noop", lambda payload: {})
        with pytest.raises(ValueError, match="already exists"):
            register_handler("noop", lambda payload: {})

    def test_an_unknown_kind_names_the_known_ones(self):
        register_handler("noop", lambda payload: {})
        from app_files.orchestration.workers import get_handler

        with pytest.raises(ValueError, match="noop"):
            get_handler("nope")
