"""Layer 19 end to end: the drift gate in front of the real pipeline.

The unit tests prove the verdicts. These prove the wiring: a run goes through
the actual CLI, a changed source stops it, and state lands under AUTOFLOW_HOME
rather than in the repository.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.cli import main

HEADER = "Email Address,First Name,Last Name,Phone\n"


@pytest.fixture
def home(tmp_path, monkeypatch):
    """Every drift artifact must resolve under AUTOFLOW_HOME."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "state"))
    return tmp_path


def write_csv(path: Path, rows: str) -> Path:
    path.write_text(HEADER + rows, encoding="utf-8")
    return path


class TestDriftCli:
    def test_a_first_run_proceeds_and_records(self, home, tmp_path, capsys):
        source = write_csv(tmp_path / "contacts.csv", "a@x.com,Ada,Lovelace,1\n")
        code = main(["drift", "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "o")])
        assert code == 0
        out = tmp_path / "o" / "clean_data.csv"
        assert out.exists()
        assert pd.read_csv(out).shape[0] == 1

    def test_an_unchanged_second_run_proceeds(self, home, tmp_path):
        source = write_csv(tmp_path / "contacts.csv", "a@x.com,Ada,Lovelace,1\n")
        args = ["drift", "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "o")]
        assert main(args) == 0
        assert main(args) == 0

    def test_a_blocking_change_stops_the_run(self, home, tmp_path, capsys):
        source = write_csv(tmp_path / "contacts.csv", "a@x.com,Ada,Lovelace,1\n")
        main(["drift", "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "o")])
        # Drop the email column entirely: a required mapping is lost.
        dropped = tmp_path / "contacts.csv"
        dropped.write_text("First Name,Last Name,Phone\nAda,Lovelace,1\n", encoding="utf-8")
        code = main(["drift", "-i", str(dropped), "-c", "hubspot", "-o", str(tmp_path / "o2")])
        assert code == 1
        assert not (tmp_path / "o2" / "clean_data.csv").exists()
        assert "stopped" in capsys.readouterr().err

    def test_accept_records_the_approved_change(self, home, tmp_path):
        source = write_csv(tmp_path / "contacts.csv", "a@x.com,Ada,Lovelace,1\n")
        main(["drift", "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "o")])
        dropped = tmp_path / "contacts.csv"
        dropped.write_text("First Name,Last Name,Phone\nAda,Lovelace,1\n", encoding="utf-8")
        accepted = ["drift", "-i", str(dropped), "-c", "hubspot",
                    "-o", str(tmp_path / "o3"), "--accept"]
        assert main(accepted) == 0
        # Once accepted, the same shape runs without --accept.
        assert main(["drift", "-i", str(dropped), "-c", "hubspot",
                     "-o", str(tmp_path / "o4")]) == 0

    def test_an_added_column_warns_but_runs(self, home, tmp_path, capsys):
        source = write_csv(tmp_path / "contacts.csv", "a@x.com,Ada,Lovelace,1\n")
        main(["drift", "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "o")])
        grown = tmp_path / "contacts.csv"
        grown.write_text(
            HEADER + "a@x.com,Ada,Lovelace,1,Something Extra\n", encoding="utf-8"
        )
        code = main(["drift", "-i", str(grown), "-c", "hubspot", "-o", str(tmp_path / "o5")])
        assert code == 0
        assert "Warning" in capsys.readouterr().out

    def test_state_honours_autoflow_home(self, home, tmp_path):
        source = write_csv(tmp_path / "contacts.csv", "a@x.com,Ada,Lovelace,1\n")
        main(["drift", "-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "o")])
        assert (tmp_path / "state" / "mapping" / "schemas.json").exists()
        # Nothing should have been written into the repository working tree.
        assert not (Path.cwd() / ".autoflow").exists()
