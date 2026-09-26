"""Layer 14 was library-only: no operator command reached the job queue.

These tests drive ``python -m app_files.cli jobs`` — submit, list, and run —
through the real process entry point, against the real JSONL queue under
``AUTOFLOW_HOME``. The built-in ``batch`` handler is what makes a submitted job
actually do something without the operator writing Python.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.cli import main


@pytest.fixture
def home(tmp_path, monkeypatch):
    state = tmp_path / "state"
    monkeypatch.setenv("AUTOFLOW_HOME", str(state))
    return state


@pytest.fixture
def inbox(tmp_path):
    folder = tmp_path / "inbox"
    folder.mkdir()
    (folder / "contacts.csv").write_text(
        "Email Address,First Name,Last Name\n"
        "john@acme.com,John,Smith\n"
        "jane@acme.com,Jane,Doe\n",
        encoding="utf-8",
    )
    return folder


class TestSubmit:
    def test_a_batch_job_is_queued(self, home, inbox, tmp_path, capsys):
        code = main([
            "jobs", "submit", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(tmp_path / "out"),
        ])
        assert code == 0
        assert "Submitted job" in capsys.readouterr().out
        assert home.exists()

    def test_the_job_is_listed(self, home, inbox, tmp_path, capsys):
        main([
            "jobs", "submit", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(tmp_path / "out"),
        ])
        main(["jobs", "list"])
        listing = capsys.readouterr().out
        assert "batch" in listing
        assert "queued" in listing

    def test_priority_is_recorded(self, home, inbox, tmp_path, capsys):
        main([
            "jobs", "submit", "--input-dir", str(inbox), "--template", "hubspot",
            "--out", str(tmp_path / "out"), "--priority", "high",
        ])
        main(["jobs", "list"])
        assert "high" in capsys.readouterr().out

    def test_missing_batch_arguments_are_refused(self, home, tmp_path, capsys):
        code = main(["jobs", "submit", "--template", "hubspot"])
        assert code == 2
        assert "needs" in capsys.readouterr().err

    def test_an_unknown_kind_is_refused(self, home, inbox, tmp_path, capsys):
        code = main([
            "jobs", "submit", "--kind", "sparkle", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(tmp_path / "out"),
        ])
        assert code == 2
        assert "No built-in handler" in capsys.readouterr().err

    def test_a_dependency_is_recorded_and_run_in_order(self, home, inbox, tmp_path, capsys):
        out = tmp_path / "out"
        main([
            "jobs", "submit", "--input-dir", str(inbox), "--template", "hubspot",
            "--out", str(out),
        ])
        first = capsys.readouterr().out.split()[2]
        main([
            "jobs", "submit", "--input-dir", str(inbox), "--template", "hubspot",
            "--out", str(out / "second"), "--depends-on", first,
        ])
        code = main(["jobs", "run", "--workers", "1"])
        assert code == 0
        capsys.readouterr()
        main(["jobs", "list"])
        assert capsys.readouterr().out.count("succeeded") == 2


class TestRun:
    def test_the_batch_output_is_produced(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main([
            "jobs", "submit", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(out),
        ])
        code = main(["jobs", "run", "--workers", "1"])
        assert code == 0
        assert (out / "contacts" / "clean_data.csv").is_file()
        assert (out / "summary.csv").is_file()

    def test_the_run_is_summarised(self, home, inbox, tmp_path, capsys):
        main([
            "jobs", "submit", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(tmp_path / "out"),
        ])
        capsys.readouterr()
        main(["jobs", "run", "--workers", "2"])
        assert "succeeded" in capsys.readouterr().out

    def test_running_an_empty_queue_does_nothing(self, home, capsys):
        assert main(["jobs", "run"]) == 0

    def test_a_failed_job_exits_non_zero(self, home, inbox, tmp_path, capsys):
        from app_files.orchestration import JobQueue, JobSpec
        from app_files.orchestration.queue import Priority

        # No handler is registered for this kind, so the worker must fail it.
        JobQueue().submit(JobSpec("ghost", {"x": 1}, priority=Priority.NORMAL))
        capsys.readouterr()
        code = main(["jobs", "run"])
        assert code == 1
        assert "failed" in capsys.readouterr().out

    def test_the_queue_survives_a_missing_queue_file(self, home, capsys):
        assert main(["jobs", "list"]) == 0


class TestDurableState:
    def test_the_queue_log_lives_under_autoflow_home(self, home, inbox, tmp_path):
        main([
            "jobs", "submit", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(tmp_path / "out"),
        ])
        assert (home / "queue" / "jobs.jsonl").is_file()

    def test_a_job_claimed_by_one_worker_is_not_run_twice(self, home, inbox, tmp_path):
        out = tmp_path / "out"
        main([
            "jobs", "submit", "--input-dir", str(inbox),
            "--template", "hubspot", "--out", str(out),
        ])
        main(["jobs", "run", "--workers", "1"])
        # A second drain finds nothing to do.
        assert main(["jobs", "run", "--workers", "1"]) == 0
        assert pd.read_csv(out / "summary.csv")["rows_in"].sum() == 2
