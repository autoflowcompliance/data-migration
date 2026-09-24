"""The public Python SDK."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app_files.sdk import Client, Migration, SDKError

REPO_ROOT = Path(__file__).resolve().parents[2]
MESSY = REPO_ROOT / "app_files" / "samples" / "messy_contacts.csv"


def test_a_run_returns_the_clean_frame():
    run = Migration.from_file(MESSY, crm="hubspot").execute()
    assert len(run.clean_frame) == 6
    assert run.valid is False  # the sample has known issues
    assert run.summary()["rows_in"] == 7


def test_the_sdk_attaches_every_artifact():
    run = Migration.from_file(MESSY, crm="hubspot", lineage=True).execute()
    assert not run.qa_report_html == ""
    assert list(run.issues().columns) == ["row", "field", "check", "severity", "message"]
    assert len(run.mapping_log()) > 0
    assert len(run.cleaning_log()) > 0
    assert len(run.lineage_log()) > 0


def test_lineage_is_off_unless_asked_for():
    run = Migration.from_file(MESSY, crm="hubspot").execute()
    assert run.lineage_log().empty


def test_execute_does_not_write_anything(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Migration.from_file(MESSY, crm="hubspot").execute()
    assert list(tmp_path.iterdir()) == []


def test_run_and_write_writes_deliverables(tmp_path):
    run = Migration.from_file(MESSY, crm="hubspot", lineage=True).run_and_write(tmp_path)
    for name in ("clean_data", "qa_report", "mapping_log", "cleaning_log", "issues", "lineage_report"):
        assert name in run.written
        assert run.written[name].exists()
    assert (tmp_path / "clean_data.csv").exists()


def test_output_format_is_honoured(tmp_path):
    run = Migration.from_file(MESSY, crm="hubspot", output_format="json").run_and_write(tmp_path)
    assert run.written["clean_data"].suffix == ".json"


def test_the_sdk_accepts_a_frame_directly():
    frame = pd.DataFrame({"First Name": ["Ann"], "Last Name": ["Lee"], "Email Address": ["a@x.com"]})
    run = Migration(frame, crm="hubspot").execute()
    assert run.clean_frame["email"].tolist() == ["a@x.com"]


def test_a_missing_file_is_a_clear_error(tmp_path):
    with pytest.raises(SDKError, match="No such file"):
        Migration.from_file(tmp_path / "nope.csv", crm="hubspot")


def test_a_missing_crm_is_a_clear_error():
    with pytest.raises(SDKError, match="target config"):
        Migration(pd.DataFrame({"a": [1]}), crm="")


def test_dry_run_reports_a_plan_without_writing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plan = Migration.from_file(MESSY, crm="hubspot").dry_run()
    assert plan["dry_run"] is True
    assert plan["rows_in"] == 7
    assert list(tmp_path.iterdir()) == []


def test_privacy_report_names_the_personal_columns():
    report = Migration.from_file(MESSY, crm="hubspot").privacy_report()
    assert "email" in report["by_class"]


def test_as_dict_is_json_shaped():
    run = Migration.from_file(MESSY, crm="hubspot").execute()
    body = run.as_dict()
    assert body["summary"]["rows_in"] == 7
    assert body["valid"] is False


def test_a_client_holds_defaults():
    client = Client(crm="hubspot", lineage=True)
    run = client.migrate(MESSY)
    assert len(run.lineage_log()) > 0


def test_a_client_processes_several_files():
    client = Client(crm="hubspot")
    runs = client.migrate_many([MESSY, MESSY])
    assert [r.summary()["rows_in"] for r in runs] == [7, 7]


def test_a_client_accepts_a_frame():
    client = Client(crm="hubspot")
    run = client.migrate(pd.DataFrame({"Email Address": ["a@x.com"]}))
    assert run.clean_frame["email"].tolist() == ["a@x.com"]