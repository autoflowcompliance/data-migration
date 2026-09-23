"""The scheduled job that keeps the hosted demo awake.

Render's free tier suspends the service after ~15 minutes idle, so the next
visitor pays a cold start. The workflow in ``.github/workflows/keep-alive.yml``
pings it on a schedule to prevent that.

The failure this guards against is quiet in both directions: a schedule that
sits outside the idle window does nothing, and a URL that has drifted from the
deployed host pings a 404 forever while the job reports success. Everything is
read from the YAML file as text, so the test needs no YAML parser and cannot
drift from what GitHub actually runs.
"""

from __future__ import annotations

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "keep-alive.yml"

DEPLOYED_DEMO = "dataflow-awxm.onrender.com"


def _workflow() -> str:
    assert WORKFLOW.is_file(), f"the keep-alive workflow is missing: {WORKFLOW}"
    return WORKFLOW.read_text()


def test_the_workflow_runs_on_a_schedule():
    assert "schedule:" in _workflow()
    assert re.search(r"cron:\s*['\"]", _workflow()), "no cron expression"


def test_the_ping_lands_inside_renders_idle_window():
    """Render suspends at ~15 idle minutes, so the gap must stay under that.

    Pinned rather than free-form: a cron someone slows to '*/30' looks harmless
    and silently stops keeping the service warm.
    """
    cron = re.search(r"cron:\s*['\"]([^'\"]+)['\"]", _workflow())
    assert cron, "no cron expression"
    step = cron.group(1).split()[0]

    minutes = re.fullmatch(r"\*/(\d+)", step)
    assert minutes, (
        f"the schedule step {step!r} is not a fixed-interval form; an hourly job "
        f"cannot keep a 15-minute idle window warm"
    )
    interval = int(minutes.group(1))
    assert 1 <= interval < 15, (
        f"the ping runs every {interval} minutes, which leaves a gap at or past "
        f"Render's 15-minute idle window"
    )


def test_the_ping_targets_the_deployed_demo_host():
    body = _workflow()
    assert DEPLOYED_DEMO in body, (
        f"the workflow does not ping {DEPLOYED_DEMO}; a stale host 404s forever "
        f"while the job reports success"
    )


def test_the_ping_fails_the_job_on_a_bad_response():
    """Without --fail curl exits 0 on a 503, so the job goes green while the
    demo is down — exactly the case the job exists to surface."""
    assert "--fail" in _workflow()


def test_the_ping_waits_out_a_cold_start():
    """A cold start is the case this job is for; a short timeout would report a
    failure for a service that was merely waking up."""
    body = _workflow()
    timeout = re.search(r"--max-time\s+(\d+)", body)
    assert timeout, "the ping has no explicit --max-time"
    assert int(timeout.group(1)) >= 60, (
        "the ping gives up before a cold start can finish"
    )
