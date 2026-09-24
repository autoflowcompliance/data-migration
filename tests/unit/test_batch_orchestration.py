"""Scheduling, dependency chains, retries and incremental processing (Layer 9)."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from app_files.batch import (
    CronSchedule,
    DependencyCycleError,
    IncrementalStore,
    JobNode,
    RetryPolicy,
    ScheduledJob,
    parse_schedule,
    record_fingerprint,
    resolve_order,
    run_chain,
    run_with_retry,
)

UTC = timezone.utc


class TestCronSchedule:
    def test_every_fifteen_minutes(self):
        schedule = CronSchedule("*/15 * * * *")
        assert schedule.matches(datetime(2026, 1, 1, 9, 15, tzinfo=UTC))
        assert not schedule.matches(datetime(2026, 1, 1, 9, 16, tzinfo=UTC))

    def test_a_wrong_field_count_is_rejected(self):
        with pytest.raises(ValueError, match="5 fields"):
            CronSchedule("0 9 * *")

    def test_next_after_returns_following_matches(self):
        schedule = CronSchedule("*/15 * * * *")
        start = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
        assert [d.strftime("%H:%M") for d in schedule.upcoming(3, start)] == [
            "09:15", "09:30", "09:45",
        ]

    def test_weekly_schedule_lands_on_monday(self):
        schedule = CronSchedule("0 2 * * 1")
        nxt = schedule.next_after(datetime(2026, 1, 1, tzinfo=UTC))
        assert nxt is not None
        assert nxt.weekday() == 0  # Monday
        assert (nxt.hour, nxt.minute) == (2, 0)

    def test_monthly_schedule(self):
        schedule = CronSchedule("0 0 1 * *")
        nxt = schedule.next_after(datetime(2026, 1, 15, tzinfo=UTC))
        assert nxt is not None and (nxt.month, nxt.day) == (2, 1)

    def test_range_and_list_fields(self):
        schedule = CronSchedule("0 9-17 * * *")
        assert schedule.matches(datetime(2026, 1, 1, 13, 0, tzinfo=UTC))
        assert not schedule.matches(datetime(2026, 1, 1, 18, 0, tzinfo=UTC))

    def test_parse_schedule_is_the_constructor(self):
        assert parse_schedule("* * * * *").matches(datetime(2026, 1, 1, 0, 0, tzinfo=UTC))

    def test_no_match_returns_none_within_the_window(self):
        # 30 February never happens.
        schedule = CronSchedule("0 0 30 2 *")
        assert schedule.next_after(datetime(2026, 1, 1, tzinfo=UTC), limit_days=365) is None


class TestScheduledJob:
    def test_first_check_is_due(self):
        job = ScheduledJob("nightly", CronSchedule("0 2 * * *"))
        assert job.is_due(datetime(2026, 1, 1, 2, 0, tzinfo=UTC))

    def test_not_due_twice_in_the_same_minute(self):
        job = ScheduledJob("nightly", CronSchedule("0 2 * * *"))
        moment = datetime(2026, 1, 1, 2, 0, tzinfo=UTC)
        job.mark_run(moment)
        assert not job.is_due(moment)

    def test_not_due_off_schedule(self):
        job = ScheduledJob("nightly", CronSchedule("0 2 * * *"))
        assert not job.is_due(datetime(2026, 1, 1, 3, 0, tzinfo=UTC))

    def test_next_run_is_in_the_future(self):
        job = ScheduledJob("nightly", CronSchedule("0 2 * * *"))
        nxt = job.next_run(datetime(2026, 1, 1, 5, 0, tzinfo=UTC))
        assert nxt is not None and nxt.day == 2


class TestDependencyChains:
    def test_topological_order(self):
        nodes = [JobNode("C", ["A", "B"]), JobNode("B", ["A"]), JobNode("A")]
        assert resolve_order(nodes) == ["A", "B", "C"]

    def test_unknown_dependency_is_rejected(self):
        with pytest.raises(ValueError, match="unknown jobs"):
            resolve_order([JobNode("A", ["ghost"])])

    def test_cycle_is_rejected(self):
        with pytest.raises(DependencyCycleError):
            resolve_order([JobNode("A", ["B"]), JobNode("B", ["A"])])

    def test_a_failed_upstream_halts_the_chain(self):
        nodes = [JobNode("A"), JobNode("B", ["A"]), JobNode("C", ["A", "B"])]
        outcome = run_chain(nodes, lambda name: name != "A")
        assert outcome.failed == ["A"]
        assert outcome.skipped == ["B", "C"]
        assert outcome.halted

    def test_a_raising_job_counts_as_failed(self):
        def explode(name):
            if name == "A":
                raise RuntimeError("boom")
            return True

        outcome = run_chain([JobNode("A"), JobNode("B", ["A"])], explode)
        assert outcome.failed == ["A"]
        assert outcome.skipped == ["B"]

    def test_all_success_runs_everything_in_order(self):
        nodes = [JobNode("A"), JobNode("B", ["A"]), JobNode("C", ["A", "B"])]
        outcome = run_chain(nodes, lambda name: True)
        assert outcome.order == ["A", "B", "C"]
        assert outcome.ran == ["A", "B", "C"]
        assert not outcome.halted

    def test_independent_branches_are_unaffected_by_a_failure(self):
        nodes = [JobNode("A"), JobNode("B", ["A"]), JobNode("D")]
        outcome = run_chain(nodes, lambda name: name != "A")
        assert outcome.skipped == ["B"]
        assert "D" in outcome.ran


class TestRetry:
    def _policy(self) -> RetryPolicy:
        return RetryPolicy(attempts=3, base_delay=1.0, factor=2.0, sleep=lambda _: None)

    def test_transient_failure_succeeds_on_retry(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 2:
                raise ValueError("transient")
            return "ok"

        outcome = run_with_retry(flaky, self._policy())
        assert outcome.succeeded
        assert outcome.attempts == 2
        assert outcome.result == "ok"

    def test_exhausted_retries_report_the_last_error(self):
        outcome = run_with_retry(
            lambda: (_ for _ in ()).throw(RuntimeError("dead")), self._policy()
        )
        assert not outcome.succeeded
        assert outcome.attempts == 3
        assert "dead" in (outcome.error or "")

    def test_backoff_is_exponential_and_capped(self):
        policy = RetryPolicy(base_delay=1.0, factor=2.0, max_delay=5.0, sleep=lambda _: None)
        assert policy.delay_for(1) == 0.0
        assert policy.delay_for(2) == 1.0
        assert policy.delay_for(3) == 2.0
        assert policy.delay_for(4) == 4.0
        assert policy.delay_for(5) == 5.0  # capped

    def test_the_first_attempt_has_no_delay(self):
        waits = []
        policy = RetryPolicy(attempts=1, sleep=waits.append)
        run_with_retry(lambda: "fine", policy)
        assert waits == []


class TestIncrementalStore:
    @pytest.fixture
    def store(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
        return IncrementalStore("source", path=tmp_path / "state.json")

    @staticmethod
    def frame(ids) -> pd.DataFrame:
        return pd.DataFrame({"id": ids, "value": [f"v{i}" for i in ids]})

    def test_first_run_returns_everything(self, store):
        assert len(store.new_records(self.frame([1, 2, 3]))) == 3

    def test_second_run_on_an_unchanged_file_returns_nothing(self, store):
        frame = self.frame([1, 2, 3])
        store.commit(frame)
        assert len(store.new_records(frame)) == 0

    def test_only_the_new_row_is_returned(self, store):
        store.commit(self.frame([1, 2, 3]))
        grown = self.frame([1, 2, 3, 4])
        fresh = store.new_records(grown)
        assert list(fresh["id"]) == [4]

    def test_commit_reports_the_total_known(self, store):
        assert store.commit(self.frame([1, 2])) == 2
        assert store.commit(self.frame([3])) == 3

    def test_state_persists_across_instances(self, store, tmp_path):
        store.commit(self.frame([1, 2]))
        reopened = IncrementalStore("source", path=tmp_path / "state.json")
        assert len(reopened.new_records(self.frame([1, 2]))) == 0

    def test_empty_frame_is_handled(self, store):
        assert len(store.new_records(pd.DataFrame({"id": [], "value": []}))) == 0

    def test_clear_forgets_everything(self, store):
        store.commit(self.frame([1, 2]))
        assert store.clear() == 2
        assert len(store.new_records(self.frame([1, 2]))) == 2

    def test_corrupt_state_does_not_raise(self, store):
        store.path.parent.mkdir(parents=True, exist_ok=True)
        store.path.write_text("{not json")
        assert len(store.new_records(self.frame([1]))) == 1

    def test_explicit_columns_limit_the_fingerprint(self):
        a = {"id": 1, "note": "x"}
        b = {"id": 1, "note": "y"}
        assert record_fingerprint(a, ["id"]) == record_fingerprint(b, ["id"])

    def test_different_values_fingerprint_differently(self):
        assert record_fingerprint({"id": 1}) != record_fingerprint({"id": 2})

    def test_blank_values_are_stable(self):
        assert record_fingerprint({"id": None}) == record_fingerprint({"id": ""})
