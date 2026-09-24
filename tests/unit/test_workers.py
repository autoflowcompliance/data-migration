"""Distributed workers, leases, and resource limits."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app_files.orchestration import (
    JobQueue,
    LeaseError,
    ResourceLimitExceeded,
    ResourceLimits,
    Worker,
    WorkerPool,
    run_pool,
)


@pytest.fixture
def pool():
    queue = JobQueue(capacity=20)
    workers = [Worker(name="w1", capacity=2), Worker(name="w2", capacity=2)]
    return WorkerPool(queue, workers, lease_seconds=60)


def test_a_worker_leases_a_job(pool):
    pool.queue.submit({"n": 1})
    lease = pool.lease_next("w1")
    assert lease.job_id == "job-1"
    assert lease.worker == "w1"
    assert not lease.expired()


def test_leasing_from_an_unknown_worker_is_an_error(pool):
    with pytest.raises(LeaseError, match="Unknown worker"):
        pool.lease_next("ghost")


def test_a_worker_at_capacity_gets_nothing(pool):
    for _ in range(4):
        pool.queue.submit()
    pool.lease_next("w1")
    pool.lease_next("w1")
    assert pool.lease_next("w1") is None


def test_two_workers_take_different_jobs(pool):
    pool.queue.submit({"n": 1})
    pool.queue.submit({"n": 2})
    first = pool.lease_next("w1")
    second = pool.lease_next("w2")
    assert first.job_id != second.job_id


def test_releasing_a_job_marks_it_done(pool):
    pool.queue.submit()
    lease = pool.lease_next("w1")
    pool.release(lease.job_id, succeeded=True)
    assert pool.queue.counts()["done"] == 1
    assert pool.workers["w1"].completed == 1
    assert pool.workers["w1"].active == []


def test_releasing_a_failed_job_records_the_error(pool):
    pool.queue.submit()
    lease = pool.lease_next("w1")
    job = pool.release(lease.job_id, succeeded=False, error="boom")
    assert job.status == "failed"
    assert job.error == "boom"
    assert pool.workers["w1"].failed == 1


def test_an_expired_lease_goes_back_to_the_queue(pool):
    pool.queue.submit()
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    pool.lease_next("w1", now=start)
    # Another worker arrives after the lease expired.
    later = start + timedelta(seconds=120)
    reclaimed = pool._reclaim_expired(later)
    assert reclaimed == ["job-1"]
    assert pool.queue._jobs["job-1"].status == "queued"


def test_a_renewed_lease_does_not_expire(pool):
    pool.queue.submit()
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    lease = pool.lease_next("w1", now=start)
    pool.renew(lease.job_id, now=start + timedelta(seconds=30))
    assert not lease.expired(start + timedelta(seconds=80))


def test_renewing_a_job_without_a_lease_is_an_error(pool):
    with pytest.raises(LeaseError, match="No active lease"):
        pool.renew("job-1")


def test_releasing_a_job_without_a_lease_is_an_error(pool):
    with pytest.raises(LeaseError, match="No active lease"):
        pool.release("job-1", succeeded=True)


def test_run_pool_drains_across_workers(pool):
    for n in range(4):
        pool.queue.submit({"n": n})
    handled = run_pool(pool, ["w1", "w2"], lambda job: None)
    assert handled == {"done": 4, "failed": 0}
    assert pool.queue.counts()["done"] == 4


def test_run_pool_records_a_handler_failure(pool):
    pool.queue.submit({"n": 1})

    def handler(job):
        raise RuntimeError("poison")

    handled = run_pool(pool, ["w1"], handler)
    assert handled == {"done": 0, "failed": 1}
    assert pool.queue.counts()["failed"] == 1


def test_add_worker_extends_the_pool(pool):
    worker = pool.add_worker("w3", capacity=1)
    assert worker.name == "w3"
    assert "w3" in pool.counts()["workers"]


def test_counts_summarise_the_fleet(pool):
    pool.queue.submit()
    pool.lease_next("w1")
    counts = pool.counts()
    assert counts["active_leases"] == 1
    assert counts["queue"]["running"] == 1


def test_lease_seconds_must_be_positive():
    with pytest.raises(ValueError):
        WorkerPool(JobQueue(), lease_seconds=0)


# ---------------------------------------------------------- resource limits
def test_a_job_within_limits_passes():
    ResourceLimits(max_rows=100, max_bytes=1000, max_minutes=10).check(
        rows=50, bytes_=500, minutes=1
    )


def test_too_many_rows_is_refused_with_the_numbers():
    with pytest.raises(ResourceLimitExceeded, match="rows of 200 exceeds"):
        ResourceLimits(max_rows=100).check(rows=200)


def test_too_many_bytes_is_refused():
    with pytest.raises(ResourceLimitExceeded, match="bytes"):
        ResourceLimits(max_bytes=10).check(bytes_=11)


def test_too_many_minutes_is_refused():
    with pytest.raises(ResourceLimitExceeded, match="minutes"):
        ResourceLimits(max_minutes=1).check(minutes=2)


def test_a_pool_exposes_its_limits(pool):
    pool.limits = ResourceLimits(max_rows=5)
    with pytest.raises(ResourceLimitExceeded):
        pool.check_resources(rows=6)


def test_limits_serialise():
    assert ResourceLimits().as_dict() == {
        "max_rows": 1_000_000,
        "max_bytes": 512 * 1024 * 1024,
        "max_minutes": 30.0,
    }