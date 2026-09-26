"""Interface-level failure paths: the CLI must not crash on bad options.

Each of these was a real crash: a provider option that did not apply reached a
constructor that did not accept it, and a single-poll watch looked like a
no-op because the settle window had not elapsed.
"""

from __future__ import annotations

import sqlite3

import pytest

from app_files.cli import main


@pytest.fixture()
def sqlite_db(tmp_path):
    path = tmp_path / "demo.db"
    conn = sqlite3.connect(path)
    conn.execute("create table contacts (firstname text, lastname text, email text)")
    conn.execute("insert into contacts values ('Ada', 'Lovelace', 'ada@example.com')")
    conn.commit()
    conn.close()
    return path


def test_pull_ignores_options_the_provider_does_not_use(tmp_path, capsys, sqlite_db):
    """``--path`` on a database used to raise TypeError from the constructor."""
    code = main(
        [
            "pull",
            "sqlite",
            "--url",
            f"sqlite:///{sqlite_db}",
            "--table",
            "contacts",
            "--path",
            "/tmp/whatever",
            "-c",
            "hubspot",
            "-o",
            str(tmp_path / "out"),
            "--dry-run",
        ]
    )
    captured = capsys.readouterr()

    assert code == 0
    assert "Traceback" not in captured.err
    assert "does not use --path" in captured.err
    assert "Pulled 1 rows" in captured.out


def test_pull_runs_the_pipeline_when_not_dry(tmp_path, capsys, sqlite_db):
    out = tmp_path / "out"
    code = main(
        [
            "pull",
            "sqlite",
            "--url",
            f"sqlite:///{sqlite_db}",
            "--table",
            "contacts",
            "-c",
            "hubspot",
            "-o",
            str(out),
        ]
    )
    captured = capsys.readouterr()

    assert code == 0
    assert (out / "clean_data.csv").is_file()
    assert "1 rows in, 1 out" in captured.out


def test_watch_once_then_once_again_processes_the_file(tmp_path, capsys, monkeypatch):
    """A single poll only marks the file seen; the next poll does the work.

    ``--once`` is documented as a cron tick, so this two-call sequence is the
    contract, not a bug: the first call cannot read a file it just saw for the
    first time, because the settle window has not elapsed.
    """
    inbox = tmp_path / "in"
    inbox.mkdir()
    out = tmp_path / "out"
    (inbox / "contacts.csv").write_text(
        "First Name,Last Name,Email\nAda,Lovelace,ada@example.com\n",
        encoding="utf-8",
    )
    argv = [
        "watch",
        "--in",
        str(inbox),
        "--template",
        "hubspot",
        "--out",
        str(out),
        "--once",
    ]

    assert main(argv) == 0
    assert not (out / "contacts").exists()

    # The settle window is measured in wall time; a real cron tick arrives
    # later, so emulate that rather than sleeping for it.
    from app_files.batch import watcher

    monkeypatch.setattr(
        watcher.WatchFolder, "ready", lambda self, now=None: list(inbox.glob("*.csv"))
    )
    assert main(argv) == 0
    assert (out / "contacts" / "clean_data.csv").is_file()


def test_watch_rejects_a_missing_folder(tmp_path, capsys):
    code = main(
        [
            "watch",
            "--in",
            str(tmp_path / "nope"),
            "--template",
            "hubspot",
            "--out",
            str(tmp_path / "out"),
            "--once",
        ]
    )
    assert code == 2
    assert "not found" in capsys.readouterr().err
