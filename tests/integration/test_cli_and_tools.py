"""Tests for the CLI's batch subcommand and the fulfilment tools."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from app_files.cli import main
from tools.build_client_package import build
from tools.make_license import make_license


@pytest.fixture
def inbox(tmp_path, contacts_csv, bank_csv) -> Path:
    folder = tmp_path / "inbox"
    folder.mkdir()
    for source in (contacts_csv, bank_csv):
        (folder / source.name).write_bytes(source.read_bytes())
    return folder


# ------------------------------------------------------------------ CLI batch
def test_batch_cli_processes_a_folder(inbox, tmp_path, capsys):
    out = tmp_path / "outbox"
    exit_code = main(["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out)])
    assert exit_code == 0
    assert (out / "summary.csv").is_file()
    assert (out / "dashboard.html").is_file()
    printed = capsys.readouterr().out
    assert "2 of 2 file(s) processed" in printed


def test_batch_cli_prints_a_line_per_file(inbox, tmp_path, capsys):
    main(["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(tmp_path / "o")])
    printed = capsys.readouterr().out
    assert "messy_contacts.csv" in printed
    assert "bank_statement.csv" in printed


def test_batch_cli_reports_missing_input_folder(tmp_path, capsys):
    exit_code = main(
        ["batch", "--in", str(tmp_path / "nope"), "--template", "hubspot",
         "--out", str(tmp_path / "out")]
    )
    assert exit_code == 2
    assert "not found" in capsys.readouterr().err


def test_batch_cli_exits_non_zero_when_a_file_fails(inbox, tmp_path):
    (inbox / "broken.csv").write_text("", encoding="utf-8")
    exit_code = main(
        ["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(tmp_path / "out")]
    )
    assert exit_code == 1


def test_batch_cli_honours_the_format_flag(inbox, tmp_path):
    out = tmp_path / "out"
    main(
        ["batch", "--in", str(inbox), "--template", "hubspot", "--out", str(out),
         "--format", "json"]
    )
    assert (out / "messy_contacts" / "clean_data.json").is_file()


def test_single_file_cli_still_works(contacts_csv, tmp_path):
    """The flat-flag interface must survive the batch subcommand being added."""
    exit_code = main(["-i", str(contacts_csv), "-c", "hubspot", "-o", str(tmp_path / "out")])
    assert exit_code == 1  # the sample deliberately contains an invalid email
    assert (tmp_path / "out" / "clean_data.csv").is_file()


# --------------------------------------------------------------- make_license
def test_make_license_produces_a_verifiable_document():
    from app_files.licensing import verify_license

    data = make_license("buyer@acme.com", issued="2025-01-01")
    assert data["email"] == "buyer@acme.com"
    assert data["issued"] == "2025-01-01"
    assert verify_license(data).valid


def test_make_license_produces_a_distinct_signature_per_buyer():
    a = make_license("a@x.com", issued="2025-01-01")
    b = make_license("b@x.com", issued="2025-01-01")
    assert a["signature"] != b["signature"]


def test_make_license_tool_writes_a_file(tmp_path, capsys):
    from tools.make_license import main as license_main

    out = tmp_path / "license.json"
    assert license_main(["buyer@acme.com", "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["email"] == "buyer@acme.com"
    # The JSON goes to stdout so it can be pasted into an email.
    assert "signature" in capsys.readouterr().out


# ------------------------------------------------------- verify_install tool
def test_verify_install_tool_passes_on_this_checkout(monkeypatch, tmp_path):
    from tools.verify_install import main as verify_main

    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path / "home"))
    assert verify_main([]) == 0


def test_verify_install_tool_emits_json(monkeypatch, tmp_path, capsys):
    from tools.verify_install import main as verify_main

    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path / "home"))
    assert verify_main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert any(check["name"] == "Pipeline — clean, map, validate" for check in payload)


def test_verify_install_tool_fails_on_a_corrupt_licence(monkeypatch, tmp_path):
    from app_files.licensing import license_path
    from tools.verify_install import main as verify_main

    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path / "home"))
    path = license_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"email": "a@x.com", "issued": "2025-01-01",
                                "signature": "wrong"}), encoding="utf-8")
    assert verify_main([]) == 1


# ------------------------------------------------------- package builder
def test_build_creates_a_zip(tmp_path):
    zip_path = build(tmp_path / "dist", "DataFlow-Test")
    assert zip_path.is_file()
    assert zip_path.suffix == ".zip"


def test_package_contains_the_app_and_launchers(tmp_path):
    zip_path = build(tmp_path / "dist", "DataFlow-Test")
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    assert any(name.endswith("main.py") for name in names)
    assert any(name.endswith("start.bat") for name in names)
    assert any(name.endswith("start.sh") for name in names)
    assert any(name.endswith("start.command") for name in names)
    assert any("app_files/interface/web/main.py" in name for name in names)


def test_package_excludes_caches_and_compiled_files(tmp_path):
    zip_path = build(tmp_path / "dist", "DataFlow-Test")
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    assert not any("__pycache__" in name for name in names)
    assert not any(name.endswith(".pyc") for name in names)


def test_package_ships_the_client_readme(tmp_path):
    zip_path = build(tmp_path / "dist", "DataFlow-Test")
    with zipfile.ZipFile(zip_path) as archive:
        readme = archive.read("DataFlow-Test/README.md").decode("utf-8")
    assert "start.bat" in readme
    assert "Activate your licence" in readme


def test_package_carries_the_client_config_and_samples(tmp_path):
    zip_path = build(tmp_path / "dist", "DataFlow-Test")
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    assert any(name.endswith("configs/client.yaml") for name in names)
    assert any(name.endswith("configs/demo.yaml") for name in names)
    assert any("samples/messy_contacts.csv" in name for name in names)


def test_package_can_bundle_a_runtime(tmp_path):
    runtime = tmp_path / "portable_python"
    (runtime / "bin").mkdir(parents=True)
    (runtime / "bin" / "python3").write_text("#!/bin/sh\n", encoding="utf-8")
    zip_path = build(tmp_path / "dist", "DataFlow-Test", runtime=runtime)
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    assert any("runtime/python/bin/python3" in name for name in names)


def test_build_is_repeatable(tmp_path):
    """Rebuilding over an existing folder must not nest or duplicate."""
    first = build(tmp_path / "dist", "DataFlow-Test")
    second = build(tmp_path / "dist", "DataFlow-Test")
    with zipfile.ZipFile(second) as archive:
        names = archive.namelist()
    assert len(names) == len(set(names)), "no duplicate entries"
    assert not any("DataFlow-Test/DataFlow-Test/" in name for name in names)
    assert first == second