"""Unit tests for the per-session store.

The store exists because a NiceGUI page is rebuilt per request and cannot
receive the run outcome as an argument. The subtle part is the key: pages are
built *before* the WebSocket handshake, so neither ``client.tab_id`` nor
``client.id`` is usable. These tests pin the behaviour that keeps a run
attached to the browser across the navigation to the results page.
"""

from __future__ import annotations

import pytest

from app_files.interface.web import session as session_store


@pytest.fixture(autouse=True)
def clean_store():
    session_store.reset_all()
    yield
    session_store.reset_all()


# ------------------------------------------------------------------- keying
def test_current_key_falls_back_without_a_request_context():
    """Helpers must be usable from plain code, which is what tests rely on."""
    assert session_store.current_key() == "__global__"


def test_session_data_is_addressed_by_an_explicit_key():
    first = session_store.session("browser-a")
    first.template = "salesforce"

    assert session_store.session("browser-a").template == "salesforce"
    assert session_store.session("browser-b").template == "hubspot"


def test_outcome_round_trips_under_an_explicit_key():
    sentinel = object()
    session_store.set_outcome(sentinel, key="browser-a")

    assert session_store.get_outcome(key="browser-a") is sentinel
    assert session_store.get_outcome(key="browser-b") is None


def test_clear_drops_only_the_named_session():
    session_store.set_outcome("a", key="browser-a")
    session_store.set_outcome("b", key="browser-b")

    session_store.clear(key="browser-a")

    assert session_store.get_outcome(key="browser-a") is None
    assert session_store.get_outcome(key="browser-b") == "b"


def test_the_store_stays_bounded():
    """Old sessions are dropped rather than growing the process forever."""
    for index in range(session_store.MAX_SESSIONS + 10):
        session_store.session(f"s{index}")

    assert len(session_store._sessions) == session_store.MAX_SESSIONS
    # The newest survive; the oldest are evicted.
    assert "s0" not in session_store._sessions
    assert f"s{session_store.MAX_SESSIONS + 9}" in session_store._sessions


# --------------------------------------------------------------- report tokens
def test_publish_report_returns_a_token_that_serves_the_html():
    token = session_store.publish_report("<html>report</html>")

    assert token
    assert session_store.get_report(token) == "<html>report</html>"


def test_each_publish_gets_a_fresh_token():
    first = session_store.publish_report("one")
    second = session_store.publish_report("two")

    assert first != second
    assert session_store.get_report(first) == "one"
    assert session_store.get_report(second) == "two"


def test_unknown_report_token_is_none():
    assert session_store.get_report("nope") is None


def test_reports_are_bounded_and_evict_the_oldest():
    first = session_store.publish_report("oldest")
    for index in range(session_store.MAX_REPORTS):
        session_store.publish_report(f"r{index}")

    assert len(session_store._reports) == session_store.MAX_REPORTS
    assert session_store.get_report(first) is None


# ------------------------------------------------------- demo run allowance
def test_runs_start_at_zero_and_count_up():
    assert session_store.runs_used("browser-a") == 0

    session_store.register_run("browser-a")
    session_store.register_run("browser-a")

    assert session_store.runs_used("browser-a") == 2


def test_runs_remaining_subtracts_from_the_allowance():
    assert session_store.runs_remaining(3, "browser-a") == 3
    session_store.register_run("browser-a")
    assert session_store.runs_remaining(3, "browser-a") == 2


def test_runs_remaining_never_goes_negative():
    for _ in range(5):
        session_store.register_run("browser-a")
    assert session_store.runs_remaining(3, "browser-a") == 0


def test_no_allowance_means_no_count():
    """A licensed install has an unlimited allowance, reported as ``None``."""
    session_store.register_run("browser-a")
    assert session_store.runs_remaining(None, "browser-a") is None


def test_the_count_is_per_session():
    session_store.register_run("browser-a")
    session_store.register_run("browser-a")
    session_store.register_run("browser-b")

    assert session_store.runs_used("browser-a") == 2
    assert session_store.runs_used("browser-b") == 1


def test_reset_runs_clears_only_the_counter():
    session_store.register_run("browser-a")
    session_store.session("browser-a").template = "salesforce"

    session_store.reset_runs("browser-a")

    assert session_store.runs_used("browser-a") == 0
    assert session_store.session("browser-a").template == "salesforce"