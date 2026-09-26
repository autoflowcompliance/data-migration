"""The CI workflow that runs the suite on every push.

A green badge is a claim, and the failure this guards against is a workflow that
runs *something* other than the suite the README documents — a narrower test
path, a different interpreter, or a step that passes without running tests. The
file is read as text, so the test cannot drift from what GitHub actually runs.
"""

from __future__ import annotations

from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "tests.yml"


def _workflow() -> str:
    assert WORKFLOW.is_file(), f"the CI workflow is missing: {WORKFLOW}"
    return WORKFLOW.read_text()


def test_the_workflow_runs_on_push_and_pull_request():
    body = _workflow()
    assert "push:" in body, "CI does not run on push"
    assert "pull_request:" in body, "CI does not run on pull requests"


def test_the_workflow_runs_the_documented_suite():
    # The same command the README tells a buyer to run. A narrower path would
    # make the badge green while the suite a buyer runs is red.
    assert "python -m pytest -q" in _workflow()


def test_the_workflow_installs_from_the_requirements_file():
    assert "pip install -r requirements.txt" in _workflow()


def test_the_workflow_tests_the_interpreter_the_image_ships():
    """python:3.10-slim is what the deployed app runs, so a break there breaks
    production even if a newer interpreter is green."""
    assert '"3.10"' in _workflow(), "CI does not test the deployed interpreter"


def test_the_workflow_keeps_state_out_of_the_checkout():
    """Runtime state resolves under AUTOFLOW_HOME. A job that let it land in the
    repo would pass while littering the tree the portability tests guard."""
    assert "AUTOFLOW_HOME" in _workflow()


def test_the_workflow_declares_read_only_permissions():
    body = _workflow()
    assert "permissions:" in body
    assert "contents: read" in body


def test_the_workflow_runs_the_live_database_test_against_a_real_server():
    """The SQLite connector tests need no server, so they cannot catch a broken
    PostgreSQL path. The job starts a real server and points the live test at
    it; without this the test silently skips and the path stays unproven."""
    body = _workflow()
    assert "postgres:16-alpine" in body, "no real PostgreSQL server is started"
    assert "test_postgres_live.py" in body, "the live test is never run"
    assert "DATAREADY_TEST_POSTGRES_URL" in body, "the live test is not pointed at the server"
