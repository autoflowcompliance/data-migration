"""Schedules, triggers, dependency chains and retry policy.

The clock is injected everywhere, so a nightly schedule and a backoff series are
tested by construction rather than by sleeping.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app_files.orchestration.pipeline import (
    CronExpression,
    DependencyError,
    EventTrigger,
    JobGraph,
    RetryPolicy,
    ScheduleError,
    events_that_fire,
    next_run,
)


# ------------------------------------------------------------------ schedules
def test_nightly_at_two_fires_at_two():
    after = datetime(2026, 3, 1, 3, 0, tzinfo=timezone.utc)
    fire = next_run("0 2 * * *", after=after)
    assert (fire.hour, fire.minute) == (2, 0)
    assert fire.day == 2  # next day, since 2am already passed


def test_weekday_only_schedule_skips_the_weekend():
    saturday = datetime(2026, 3, 7, 12, 0, tzinfo=timezone.utc)  # a Saturday
    fire = next_run("0 9 * * 1-5", after=saturday)
    assert fire.weekday() < 5  # Monday
    assert (fire.hour, fire.minute) == (9, 0)


def test_step_and_list_fields():
    every_fifteen = CronExpression.parse("*/15 * * * *")
    assert every_fifteen.minute == frozenset({0, 15, 30, 45})
    listed = CronExpression.parse("0 0,12 * * *")
    assert listed.hour == frozenset({0, 12})


def test_invalid_expressions_are_rejected():
    for bad in ["0 2 * *", "0 25 * * *", "0 2 32 * *", "not a cron", "*/0 * * * *"]:
        with pytest.raises(ScheduleError):
            CronExpression.parse(bad)


def test_matches_uses_sunday_zero_weekday():
    cron = CronExpression.parse("0 0 * * 0")  # Sundays
    sunday = datetime(2026, 3, 8, 0, 0, tzinfo=timezone.utc)
    assert sunday.weekday() == 6  # Python: Sunday = 6
    assert cron.matches(sunday) is True


# ------------------------------------------------------------------- triggers
def test_file_trigger_fires_on_a_matching_upload():
    trigger = EventTrigger(job="nightly_clean", source="file", suffix=".csv")
    assert trigger.matches({"source": "file", "detail": "s3://bucket/new.csv"}) is True
    assert trigger.matches({"source": "file", "detail": "s3://bucket/new.xlsx"}) is False
    assert trigger.matches({"source": "webhook", "detail": "new.csv"}) is False


def test_job_trigger_fires_on_upstream_completion():
    trigger = EventTrigger(job="load", source="job", contains="extract:done")
    assert trigger.matches({"source": "job", "detail": "extract:done"}) is True


def test_events_that_fire_returns_all_matching_jobs():
    triggers = [
        EventTrigger(job="a", source="file", suffix=".csv"),
        EventTrigger(job="b", source="file", contains="new"),
        EventTrigger(job="c", source="webhook"),
    ]
    fired = events_that_fire(triggers, {"source": "file", "detail": "/inbox/new.csv"})
    assert fired == ["a", "b"]


# --------------------------------------------------------- dependency chains
def test_ready_respects_dependencies():
    graph = JobGraph().add("extract").add("clean", ["extract"]).add("load", ["clean"])
    assert graph.ready({}) == ["extract"]
    assert graph.ready({"extract": "running"}) == []
    assert graph.ready({"extract": "succeeded"}) == ["clean"]


def test_a_failed_dependency_blocks_the_dependent_job():
    graph = JobGraph().add("extract").add("clean", ["extract"])
    # clean must not run when extract failed.
    assert graph.ready({"extract": "failed"}) == []


def test_run_order_is_topological():
    graph = JobGraph().add("load", ["clean"]).add("clean", ["extract"]).add("extract")
    assert graph.run_order() == ["extract", "clean", "load"]


def test_cycle_is_detected():
    graph = JobGraph().add("a", ["b"]).add("b", ["a"])
    assert graph.detect_cycle() is not None
    with pytest.raises(DependencyError):
        graph.run_order()


def test_unknown_dependency_is_rejected():
    graph = JobGraph().add("a", ["ghost"])
    with pytest.raises(DependencyError):
        graph.detect_cycle()


# ---------------------------------------------------------------------- retry
def test_backoff_grows_and_caps():
    policy = RetryPolicy(base_delay=1, multiplier=2, max_delay=10, max_attempts=6)
    assert [policy.delay_for(n) for n in range(1, 6)] == [1, 2, 4, 8, 10]


def test_retry_stops_after_max_attempts_and_reraises():
    policy = RetryPolicy(max_attempts=3, base_delay=0)
    calls = {"n": 0}

    def always_fails():
        calls["n"] += 1
        raise RuntimeError("transient")

    with pytest.raises(RuntimeError):
        policy.run(always_fails, sleep=lambda _: None)
    assert calls["n"] == 3


def test_retry_succeeds_on_a_later_attempt():
    policy = RetryPolicy(max_attempts=4, base_delay=0)
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient")
        return "ok"

    waited = []
    result, used, delays = policy.run(flaky, sleep=waited.append)
    assert result == "ok"
    assert used == 3
    assert len(delays) == 2  # two waits before the third, successful attempt


def test_a_successful_first_attempt_waits_nothing():
    policy = RetryPolicy(base_delay=0)
    result, used, delays = policy.run(lambda: 42, sleep=lambda _: None)
    assert (result, used, delays) == (42, 1, [])