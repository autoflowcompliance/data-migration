"""The ``quality`` command surfaces the Layer 5 trend store.

The trend store was written by ``--record-quality`` and read only from Python;
``render_trend_html`` — the dashboard half of the spec item — had no caller.
These tests drive the command end to end against a real store.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app_files.cli import main


@pytest.fixture(autouse=True)
def _isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path / "home"))


def _record(tmp_path: Path, rows: str, times: int = 1) -> Path:
    source = tmp_path / "contacts.csv"
    source.write_text(rows, encoding="utf-8")
    for _ in range(times):
        # A run with validation errors still records its score, and the exit
        # code reflects those errors, so accept either outcome.
        main(
            [
                "-i", str(source),
                "-c", "hubspot",
                "-o", str(tmp_path / "out"),
                "--record-quality",
            ]
        )
    return source


def test_quality_with_no_history_says_so(tmp_path, capsys):
    code = main(["quality"])
    assert code == 0
    assert "No quality history recorded yet" in capsys.readouterr().out


def test_quality_lists_recorded_sources(tmp_path, capsys):
    _record(tmp_path, "Email,Name\na@b.com,Alice\nc@d.com,Bob\n", times=2)
    code = main(["quality"])
    assert code == 0
    out = capsys.readouterr().out
    assert "contacts" in out
    assert "2 run(s)" in out


def test_quality_writes_a_trend_dashboard(tmp_path, capsys):
    _record(tmp_path, "Email,Name\na@b.com,Alice\nc@d.com,Bob\n", times=3)
    report = tmp_path / "reports" / "trend.html"
    code = main(["quality", "contacts.csv", "--html", str(report)])
    assert code == 0
    assert report.exists()
    html = report.read_text(encoding="utf-8")
    assert "contacts" in html and "<table>" in html
    assert "3 runs" in html
    captured = capsys.readouterr().out
    assert "3 run(s)" in captured


def test_quality_outdir_names_the_file_after_the_source(tmp_path):
    _record(tmp_path, "Email,Name\na@b.com,Alice\nc@d.com,Bob\n")
    outdir = tmp_path / "outdir"
    code = main(["quality", "contacts.csv", "-o", str(outdir)])
    assert code == 0
    assert (outdir / "contacts_quality_trend.html").exists()


def test_quality_for_an_unknown_source_exits_non_zero(tmp_path, capsys):
    _record(tmp_path, "Email,Name\na@b.com,Alice\n", times=1)
    code = main(["quality", "never_seen.csv"])
    assert code == 1
    assert "No recorded runs" in capsys.readouterr().err


def test_a_degrading_source_shows_a_decline(tmp_path, capsys):
    # First run is clean; the later runs each drop a value, so the history
    # should read as declining rather than stable.
    source = tmp_path / "contacts.csv"
    for rows in (
        "Email,Name\na@b.com,Alice\nc@d.com,Bob\ne@f.com,Carol\n",
        "Email,Name\na@b.com,\nc@d.com,\n,\n",
        "Email,Name\n,,\n,,\n,,\n",
    ):
        source.write_text(rows, encoding="utf-8")
        # A degraded file fails validation, so the exit code is non-zero; the
        # score is still recorded, which is what the trend reads.
        main(["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out"),
              "--record-quality"])
    code = main(["quality", "contacts.csv", "--html", str(tmp_path / "t.html")])
    assert code == 0
    html = (tmp_path / "t.html").read_text(encoding="utf-8")
    assert "declining" in html or "improving" in html
