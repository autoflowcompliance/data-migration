"""Failure paths a buyer tries before buying: each must fail cleanly.

A migration tool that crashes on a malformed config, or worse, reports a
perfect score for a config that maps nothing, is worse than one that refuses.
These pin the exit code and the plain-language message for each.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app_files.cli import main


def _run(argv: list[str], capsys) -> tuple[int, str, str]:
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_malformed_yaml_fails_with_a_message_not_a_traceback(tmp_path, capsys):
    config = tmp_path / "bad.yaml"
    config.write_text(
        'crm: Broken\nversion: "1.0"\nfields:\n  - name: a\n   aliases: ["A"]\n',
        encoding="utf-8",
    )
    source = tmp_path / "in.csv"
    source.write_text("A\nx\n", encoding="utf-8")

    code, out, err = _run(
        ["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")], capsys
    )

    assert code == 2
    assert "Invalid mapping config" in err
    assert "Traceback" not in err
    assert not (tmp_path / "out" / "clean_data.csv").exists()


def test_config_with_no_fields_is_rejected_not_reported_as_perfect(tmp_path, capsys):
    config = tmp_path / "no_fields.yaml"
    config.write_text('crm: NoFields\nversion: "1.0"\n', encoding="utf-8")
    source = tmp_path / "in.csv"
    source.write_text("A\nx\n", encoding="utf-8")

    code, out, err = _run(
        ["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")], capsys
    )

    assert code == 2
    assert "declares no 'fields'" in err
    assert "100" not in out


def test_non_mapping_yaml_is_rejected(tmp_path, capsys):
    config = tmp_path / "list.yaml"
    config.write_text("- just\n- a\n- list\n", encoding="utf-8")
    source = tmp_path / "in.csv"
    source.write_text("A\nx\n", encoding="utf-8")

    code, out, err = _run(
        ["-i", str(source), "-c", str(config), "-o", str(tmp_path / "out")], capsys
    )

    assert code == 2
    assert "expected a YAML mapping" in err


def test_empty_file_fails_with_its_name(tmp_path, capsys):
    source = tmp_path / "empty.csv"
    source.write_text("", encoding="utf-8")

    code, out, err = _run(
        ["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out")], capsys
    )

    assert code == 2
    assert "is empty" in err
    assert "Traceback" not in err


def test_blank_file_fails_the_same_way(tmp_path, capsys):
    source = tmp_path / "blank.csv"
    source.write_text("\n\n", encoding="utf-8")

    code, out, err = _run(
        ["-i", str(source), "-c", "hubspot", "-o", str(tmp_path / "out")], capsys
    )

    assert code == 2
    assert "is empty" in err


def test_dead_notification_endpoint_does_not_fail_the_run(tmp_path, capsys):
    """Delivery is best-effort: a dead hook must not lose the deliverables."""
    config = tmp_path / "notify.yaml"
    config.write_text(
        'crm: Contacts\nfields:\n  - name: a\n    aliases: ["A"]\n'
        "notifications:\n"
        "  channels:\n    - type: webhook\n      url: http://127.0.0.1:9/dead\n"
        "  webhooks:\n    - url: http://127.0.0.1:9/dead\n",
        encoding="utf-8",
    )
    source = tmp_path / "in.csv"
    source.write_text("A\nx\n", encoding="utf-8")
    out = tmp_path / "out"

    code, stdout, err = _run(
        ["-i", str(source), "-c", str(config), "-o", str(out), "--notify"], capsys
    )

    assert (out / "clean_data.csv").is_file()
    assert (out / "qa_report.html").is_file()
    assert "delivery failure" in stdout
    assert code != 2


def test_unparseable_dates_are_reported_not_raised(tmp_path, capsys):
    config = tmp_path / "dates.yaml"
    config.write_text(
        'crm: Dates\nfields:\n  - name: name\n    aliases: ["Name"]\n'
        '  - name: date\n    transform: date_iso\n    aliases: ["Date"]\n',
        encoding="utf-8",
    )
    source = tmp_path / "in.csv"
    source.write_text("Name,Date\nA,not-a-date\nB,13/45/2026\n", encoding="utf-8")
    out = tmp_path / "out"

    code, stdout, err = _run(
        ["-i", str(source), "-c", str(config), "-o", str(out)], capsys
    )

    assert "Traceback" not in err
    issues = (out / "issues.csv").read_text(encoding="utf-8")
    assert "not-a-date" in issues
    assert "13/45/2026" in issues


def test_missing_required_source_column_is_an_error_not_a_crash(tmp_path, capsys):
    source = tmp_path / "in.csv"
    source.write_text("First Name\nOnlyFirst\n", encoding="utf-8")
    out = tmp_path / "out"

    code, stdout, err = _run(
        ["-i", str(source), "-c", "hubspot", "-o", str(out)], capsys
    )

    assert "Traceback" not in err
    issues = (out / "issues.csv").read_text(encoding="utf-8")
    assert "lastname" in issues
    assert code == 1


def test_unknown_config_name_says_what_is_known(tmp_path, capsys):
    source = tmp_path / "in.csv"
    source.write_text("A\nx\n", encoding="utf-8")

    code, out, err = _run(
        ["-i", str(source), "-c", "not_a_crm", "-o", str(tmp_path / "out")], capsys
    )

    assert code != 0
    assert "hubspot" in err
