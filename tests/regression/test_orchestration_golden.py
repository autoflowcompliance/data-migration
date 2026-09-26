"""Golden file for Layer 14 — a known job sequence produces a known transcript.

The input is a list of job specs (kind, priority, dependency, retry budget). The
expected file is the order they ran in and the state each finished in. If a
change alters priority ordering, dependency gating or retry behaviour, this
fails.

If it breaks, the change is guilty until proven innocent: revert it or fix the
bug. Do not regenerate the expected file to make the test green.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_files.orchestration import JobQueue, JobSpec, Priority, Worker
from app_files.orchestration.workers import HANDLERS

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "orchestration"


def _handlers():
    attempts: dict[str, int] = {}

    def ok(payload):
        return {"ok": True, "tag": payload.get("tag", "")}

    def fail_once(payload):
        tag = payload.get("tag", "")
        attempts[tag] = attempts.get(tag, 0) + 1
        if attempts[tag] == 1:
            raise RuntimeError("transient")
        return {"ok": True, "attempt": attempts[tag]}

    def always_fail(payload):
        raise RuntimeError("permanent")

    return {"ok": ok, "fail_once": fail_once, "always_fail": always_fail}


def test_orchestration_golden_transcript(tmp_path):
    spec = json.loads((GOLDEN / "jobs.json").read_text())
    expected = json.loads((GOLDEN / "expected_transcript.json").read_text())

    snapshot = dict(HANDLERS)
    HANDLERS.clear()
    HANDLERS.update(_handlers())
    try:
        queue = JobQueue(tmp_path / "jobs.jsonl")
        keys: dict[str, str] = {}
        for entry in spec["jobs"]:
            keys[entry["key"]] = queue.submit(
                JobSpec(
                    kind=entry["kind"],
                    payload={"tag": entry["key"]},
                    priority=Priority[entry.get("priority", "normal").upper()],
                    max_attempts=entry.get("max_attempts", 1),
                    depends_on=[keys[parent] for parent in entry.get("depends_on", [])],
                )
            ).id

        order: list[tuple[str, str]] = []
        while True:
            job = queue.claim("golden")
            if job is None:
                break
            outcome = Worker("golden", queue)._execute(job)
            order.append((job.spec.payload["tag"], outcome.value))

        produced = {
            "order": [{"job": key, "state": state} for key, state in order],
            "final": {key: queue.get(job_id).state.value for key, job_id in keys.items()},
        }
    finally:
        HANDLERS.clear()
        HANDLERS.update(snapshot)

    assert produced == expected
