"""Layer 8-11 tests: onboarding, collaboration, intelligence, distribution.

These cover the seams added by the market-widening layers and the repairs made
during verification. Nothing here reaches the network: the connectors take an
injected transport, the updater reads a manifest from disk, and the workspace
and wizard tests relocate ``AUTOFLOW_HOME`` to a temporary directory.
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import pandas as pd
import pytest

from app_files.collaboration.workspaces import (
    WorkspaceError,
    create_workspace,
    run_in_workspace,
    workspaces_dir,
)
from app_files.distribution.connectors import (
    ConnectorError,
    MissingCredentials,
    available_connectors,
    credential_report,
    get_connector,
)
from app_files.distribution.updater import (
    check_for_update,
    is_newer,
    manifest_payload,
    manifest_url,
    parse_version,
)


@pytest.fixture
def home(tmp_path, monkeypatch):
    """Relocate AUTOFLOW_HOME so nothing touches the repository."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    return tmp_path


# ------------------------------------------------------------------ updater E4
class _FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


def test_version_parsing_and_comparison():
    assert parse_version("v1.2.3") == (1, 2, 3)
    assert is_newer("1.2.0", "1.1.9") is True
    assert is_newer("1.0.0", "1.0.0") is False


def test_updater_unconfigured_is_honest(monkeypatch):
    """No URL means 'not configured', never a silent 'up to date'."""
    monkeypatch.delenv("AUTOFLOW_UPDATE_URL", raising=False)
    assert manifest_url() is None
    result = check_for_update()
    assert result.reachable is False
    assert result.update_available is False
    assert result.status == "CHECK FAILED"
    assert "configured" in result.error


def test_updater_reads_local_manifest(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOFLOW_UPDATE_URL", raising=False)
    manifest = tmp_path / "latest.json"
    manifest.write_text(manifest_payload("2.0.0", download_url="https://host/app.exe"))
    result = check_for_update(url=str(manifest), current="1.0.0")
    assert result.reachable is True
    assert result.update_available is True
    assert result.latest == "2.0.0"
    assert result.status == "UPDATE AVAILABLE"


def test_updater_file_url_and_missing_manifest(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOFLOW_UPDATE_URL", raising=False)
    manifest = tmp_path / "latest.json"
    manifest.write_text(manifest_payload("0.9.0", download_url="https://host/app.exe"))
    up_to_date = check_for_update(url=f"file://{manifest}", current="1.0.0")
    assert up_to_date.update_available is False
    assert up_to_date.status == "UP TO DATE"

    missing = check_for_update(url=str(tmp_path / "nope.json"))
    assert missing.reachable is False
    assert "no manifest" in missing.error


def test_updater_rejects_unreachable_host_and_bad_json(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOFLOW_UPDATE_URL", raising=False)

    def boom(method, url, **kwargs):
        raise ConnectionError("offline")

    failed = check_for_update(transport=boom, url="https://updates.example.invalid/latest.json")
    assert failed.reachable is False
    assert "offline" in failed.error

    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    assert check_for_update(url=str(bad)).reachable is False


def test_updater_parses_injected_transport():
    """The HTTP path is parsed correctly without a real request."""
    result = check_for_update(
        transport=lambda method, url, **kw: _FakeResponse(
            {"version": "3.1.0", "download_url": "https://host/app.exe", "notes": "faster"}
        ),
        url="https://updates.example.test/latest.json",
        current="3.0.0",
    )
    assert result.reachable is True
    assert result.update_available is True
    assert result.download_url == "https://host/app.exe"


def test_manifest_url_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTOFLOW_UPDATE_URL", str(tmp_path / "m.json"))
    assert manifest_url().endswith("m.json")


# ------------------------------------------------------------ connectors E1
class _Response:
    def __init__(self, payload=None, body=b"", status=200, content_type="text/csv", headers=None):
        self._payload = payload
        self.content = body
        self.status_code = status
        self.headers = {"Content-Type": content_type}
        if headers:
            self.headers.update(headers)

    def json(self):
        return self._payload


def test_connectors_are_registered():
    # Catalogue, cloud storage, and SaaS destinations/sources.
    assert set(available_connectors()) == {
        "s3",
        "gcs",
        "azure_blob",
        "google_sheets",
        "google_drive",
        "dropbox",
        "onedrive",
        "hubspot",
        "salesforce",
        "slack",
        "sftp",
    }


def test_dropbox_fetch_builds_authenticated_request():
    seen = {}

    def transport(method, url, **kwargs):
        seen["method"] = method
        seen["url"] = url
        seen["headers"] = kwargs.get("headers", {})
        return _Response(body=b"email\nada@example.com\n")

    connector = get_connector(
        "dropbox",
        path="/Clients/Acme/contacts.csv",
        transport=transport,
        environ={"DROPBOX_ACCESS_TOKEN": "tok"},
    )
    fetched = connector.fetch()
    assert fetched.data.startswith(b"email")
    assert seen["headers"]["Authorization"] == "Bearer tok"
    assert "Dropbox-API-Arg" in seen["headers"]
    assert seen["url"].endswith("/files/download")


def test_google_sheets_converts_values_to_csv():
    connector = get_connector(
        "google_sheets",
        spreadsheet_id="abc",
        sheet_name="Sheet1",
        transport=lambda *a, **k: _Response(payload={"values": [["email", "phone"], ["a@b.c", "123"]]}),
        environ={"GOOGLE_ACCESS_TOKEN": "tok"},
    )
    fetched = connector.fetch()
    assert fetched.name == "Sheet1.csv"
    assert fetched.data.decode().splitlines()[0] == "email,phone"
    assert fetched.as_frame().shape == (1, 2)


def test_onedrive_follows_redirect():
    calls = []

    def transport(method, url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            return _Response(status=302, headers={"Location": "https://signed.example/file"})
        return _Response(body=b"email\na@b.c\n")

    connector = get_connector(
        "onedrive",
        item_path="Clients/Acme/contacts.csv",
        transport=transport,
        environ={"MS_GRAPH_ACCESS_TOKEN": "tok"},
    )
    fetched = connector.fetch()
    assert fetched.data.startswith(b"email")
    assert calls[-1] == "https://signed.example/file"


def test_missing_credentials_are_named():
    connector = get_connector("dropbox", path="/a.csv", environ={})
    status = connector.check_credentials()
    assert status["ready"] is False
    assert status["missing"] == ["DROPBOX_ACCESS_TOKEN"]
    with pytest.raises(MissingCredentials):
        connector.fetch()


def test_credential_report_covers_every_provider():
    report = credential_report(environ={})
    assert len(report) == len(available_connectors())
    assert all(entry["ready"] is False for entry in report)


def test_unknown_provider_rejected():
    with pytest.raises(ConnectorError):
        get_connector("box", environ={})


def test_s3_uses_injected_client():
    class Client:
        def get_object(self, Bucket, Key):
            return {"Body": io.BytesIO(b"email\na@b.c\n"), "ContentType": "text/csv"}

    connector = get_connector("s3", bucket="b", key="contacts.csv", client=Client(), environ={})
    fetched = connector.fetch()
    assert fetched.location == "s3://b/contacts.csv"
    assert fetched.data.startswith(b"email")


# ------------------------------------------------- cloud storage & SaaS D
def test_gcs_fetch_builds_authenticated_request():
    seen = {}

    def transport(method, url, **kwargs):
        seen["url"] = url
        seen["headers"] = kwargs.get("headers", {})
        return _Response(body=b"email\na@b.c\n", headers={"Content-Type": "text/csv"})

    connector = get_connector(
        "gcs",
        bucket="my-bucket",
        key="clients/acme/contacts.csv",
        transport=transport,
        environ={"GOOGLE_ACCESS_TOKEN": "tok"},
    )
    fetched = connector.fetch()
    assert fetched.location == "gs://my-bucket/clients/acme/contacts.csv"
    assert seen["headers"]["Authorization"] == "Bearer tok"
    # The object key is percent-encoded into the path.
    assert "clients%2Facme%2Fcontacts.csv" in seen["url"]


def test_gcs_lists_objects():
    connector = get_connector(
        "gcs",
        bucket="b",
        transport=lambda *a, **k: _Response(
            payload={"items": [{"name": "a.csv", "size": "12"}]}
        ),
        environ={"GOOGLE_ACCESS_TOKEN": "tok"},
    )
    listing = connector.list_files()
    assert listing.names() == ["a.csv"]


def test_azure_blob_shared_key_headers_are_signed():
    seen = {}

    def transport(method, url, **kwargs):
        seen["url"] = url
        seen["headers"] = kwargs.get("headers", {})
        return _Response(body=b"email\na@b.c\n")

    connector = get_connector(
        "azure_blob",
        container="crm",
        blob="acme.csv",
        account="myacct",
        transport=transport,
        environ={"AZURE_STORAGE_KEY": base64.b64encode(b"secret-key").decode()},
    )
    fetched = connector.fetch()
    assert fetched.location == "azure://myacct/crm/acme.csv"
    assert seen["headers"]["Authorization"].startswith("SharedKey myacct:")
    assert seen["headers"]["x-ms-version"] == "2021-08-06"
    assert seen["url"].startswith("https://myacct.blob.core.windows.net/crm/acme.csv")


def test_azure_blob_accepts_a_bearer_token():
    seen = {}
    connector = get_connector(
        "azure_blob",
        container="c",
        blob="b.csv",
        account="acct",
        transport=lambda m, u, **k: (seen.update(k.get("headers", {})) or _Response(body=b"x\n")),
        environ={"AZURE_STORAGE_TOKEN": "tok"},
    )
    connector.fetch()
    assert seen["Authorization"] == "Bearer tok"


def test_azure_blob_missing_key_is_named():
    connector = get_connector("azure_blob", container="c", blob="b.csv", account="a", environ={})
    with pytest.raises(MissingCredentials):
        connector.fetch()


def test_hubspot_fetch_converts_records_to_csv():
    payload = {
        "results": [
            {"id": "1", "properties": {"email": "ann@x.com", "firstname": "Ann"}},
            {"id": "2", "properties": {"email": "bob@x.com", "firstname": "Bob"}},
        ]
    }
    connector = get_connector(
        "hubspot",
        transport=lambda *a, **k: _Response(payload=payload),
        environ={"HUBSPOT_TOKEN": "tok"},
    )
    fetched = connector.fetch()
    assert fetched.name == "hubspot_contacts.csv"
    frame = fetched.as_frame()
    assert frame["email"].tolist() == ["ann@x.com", "bob@x.com"]


def test_salesforce_fetch_returns_query_records():
    payload = {
        "records": [
            {"attributes": {"type": "Contact"}, "Id": "003", "Email": "a@b.c"},
        ]
    }
    connector = get_connector(
        "salesforce",
        instance_url="https://myorg.my.salesforce.com",
        query="SELECT Id, Email FROM Contact",
        transport=lambda *a, **k: _Response(payload=payload),
        environ={"SALESFORCE_TOKEN": "tok"},
    )
    fetched = connector.fetch()
    frame = fetched.as_frame()
    assert list(frame.columns) == ["Id", "Email"]  # attributes dropped
    assert frame["Email"].tolist() == ["a@b.c"]


def test_salesforce_needs_an_instance_url():
    connector = get_connector(
        "salesforce",
        query="SELECT Id FROM Contact",
        transport=lambda *a, **k: _Response(payload={}),
        environ={"SALESFORCE_TOKEN": "tok"},
    )
    with pytest.raises(MissingCredentials):
        connector.fetch()


def test_slack_send_posts_to_the_webhook():
    seen = {}
    connector = get_connector(
        "slack",
        webhook_url="https://hooks.slack.com/services/x",
        transport=lambda m, u, **k: (seen.update({"url": u, "json": k.get("json")}) or _Response(body=b"ok")),
        environ={},
    )
    result = connector.send("Cleaned 1,204 rows")
    assert result["delivered"] is True
    assert seen["json"]["text"] == "Cleaned 1,204 rows"


def test_slack_without_a_webhook_reports_missing_credentials():
    connector = get_connector("slack", environ={})
    with pytest.raises(MissingCredentials):
        connector.send("hi")


# ---------------------------------------------------------- workspaces C3/F9
def test_workspace_dir_follows_autoflow_home(home):
    assert workspaces_dir() == home / "workspaces"


def test_workspace_run_keeps_input_and_isolates_clients(home, samples_dir):
    alpha = create_workspace("Alpha_Client")
    beta = create_workspace("Beta_Client")
    run_in_workspace("Alpha_Client", samples_dir / "messy_contacts.csv")
    run_in_workspace("Beta_Client", samples_dir / "employee_records.csv")

    assert "samples/messy_contacts.csv" in alpha.tree()
    assert "samples/employee_records.csv" in beta.tree()
    assert not any("Beta" in path for path in alpha.tree())
    assert not any("Alpha" in path for path in beta.tree())
    assert alpha.samples()[0].name == "messy_contacts.csv"


def test_workspace_audit_trail_is_per_client(home, samples_dir):
    run_in_workspace("Alpha_Client", samples_dir / "messy_contacts.csv")
    alpha = create_workspace("Alpha_Client")
    history = alpha.run_history()
    assert len(history) == 1
    assert history[0]["client"] == "Alpha_Client"
    assert history[0]["output_hash"]


def test_workspace_refuses_escaping_paths(home):
    workspace = create_workspace("Alpha_Client")
    with pytest.raises(WorkspaceError):
        workspace.resolve_path("..", "Beta_Client", "output")
    with pytest.raises(WorkspaceError):
        create_workspace("../evil")


def test_workspace_writes_lineage_when_requested(home, samples_dir):
    run_in_workspace("Alpha_Client", samples_dir / "messy_contacts.csv", lineage=True)
    alpha = create_workspace("Alpha_Client")
    assert any(name.endswith("_lineage.csv") for name in alpha.tree())


# ------------------------------------------------------- hosted audit service C2
def test_orders_storage_honours_autoflow_home(home):
    from app_files.distribution import hosted_audit as hosted

    assert str(hosted.orders_path()).startswith(str(home))
    assert str(hosted.orders_dir()).startswith(str(home))


def test_stub_order_runs_audit_end_to_end(home, samples_dir):
    from app_files.distribution import hosted_audit as hosted

    data = (samples_dir / "messy_contacts.csv").read_bytes()
    order = hosted.Order.create("messy_contacts.csv", len(data))
    result = hosted.process_order(order, data, provider=hosted.get_payment_provider("stub"))

    assert result["order"]["status"] == "paid"
    assert result["summary"]["rows"] == 7
    report = Path(result["report_path"])
    assert report.exists()
    assert str(report).startswith(str(home))
    assert len(hosted.read_orders()) == 1


def test_stripe_without_key_names_the_variable(home):
    from app_files.distribution import hosted_audit as hosted

    order = hosted.Order.create("x.csv", 10)
    with pytest.raises(hosted.MissingCredentials) as excinfo:
        hosted.get_payment_provider("stripe").begin(order)
    assert "STRIPE_API_KEY" in str(excinfo.value)


def test_pricing_tiers_and_payment_status(home, monkeypatch):
    from app_files.distribution import hosted_audit as hosted

    assert hosted.pricing_for(1_000)["price"] == 99
    assert hosted.pricing_for(20 * 1024 * 1024)["price"] == 249
    assert hosted.pricing_for(200 * 1024 * 1024)["price"] == 499
    assert hosted.pricing_for(10**10)["max_bytes"] is None

    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    status = hosted.payment_is_wired()
    assert status["live_payments"] is False
    assert "STRIPE_API_KEY" in status["blocker"]


# ------------------------------------------------------ collaboration C1/C2/C4
def test_shareable_report_is_self_contained(samples_dir):
    import re

    from app_files.collaboration.shareable_report import Provenance, render_shareable_report
    from app_files.ingestion import read_any
    from app_files.pipeline import run_pipeline

    frame = read_any(str(samples_dir / "messy_contacts.csv"))
    result = run_pipeline(frame, crm="hubspot", source_filename="messy_contacts.csv")
    summary = result.summary()
    html = render_shareable_report(
        title="Messy contacts",
        provenance=Provenance(
            source_filename="messy_contacts.csv",
            rows_in=summary["rows_in"],
            rows_out=summary["rows_out"],
            quality_score=summary["quality_score"],
        ),
        qa_report_html=result.qa_report_html,
    )

    assert html.lstrip().startswith("<!DOCTYPE")
    assert re.findall(r'(?:src|href)\s*=\s*["\']https?://', html) == []
    for forbidden in ("<script", "fonts.googleapis", "unpkg", "jsdelivr", "@import"):
        assert forbidden not in html.lower()


def test_contract_passes_compliant_and_flags_violations():
    import pandas as pd

    from app_files.collaboration.contracts import check_contract, load_contract

    contract = load_contract("hubspot_contacts")
    compliant = pd.DataFrame(
        {"email": ["a@b.com", "c@d.com"], "lastname": ["Smith", "Jones"], "country": ["USA", "UK"]}
    )
    violating = pd.DataFrame(
        {
            "email": ["a@b.com", "bad-email", "a@b.com"],
            "lastname": ["Smith", "", "Jones"],
            "country": ["USA", "Mars", "UK"],
        }
    )
    assert check_contract(compliant, contract).passed is True
    failures = check_contract(violating, contract).failures
    checks = {(f.field, f.check) for f in failures}
    assert ("email", "format:email") in checks
    assert ("email", "unique") in checks
    assert ("lastname", "required") in checks
    assert ("country", "allowed") in checks


def test_comparison_report_counts_and_highlights(samples_dir):
    from app_files.collaboration.comparison import (
        build_comparison,
        changed_cell_count,
        render_comparison_html,
    )
    from app_files.ingestion import read_any
    from app_files.lineage import LineageTracker
    from app_files.pipeline import run_pipeline

    frame = read_any(str(samples_dir / "messy_contacts.csv"))
    tracker = LineageTracker()
    result = run_pipeline(frame, crm="hubspot", lineage_tracker=tracker)
    comparison = build_comparison(frame, tracker, result.clean_frame)

    assert comparison.summary()["rows_in"] == 7
    assert comparison.summary()["rows_out"] == 6
    assert changed_cell_count(comparison) > 0
    html = render_comparison_html(comparison)
    assert "changed" in html and "removed" in html


# ------------------------------------------------------------ intelligence D2-D4
def test_anomaly_detection_flags_a_spike(home):
    import pandas as pd

    from app_files.intelligence.anomaly import clear_baselines, detect

    baseline_frame = pd.DataFrame(
        {"email": ["a@b.com", "c@d.com", "e@f.com", "g@h.com"], "phone": ["1", "2", "3", "4"]}
    )
    assert detect(baseline_frame, name="contacts", quality_score=95.0).is_baseline_run is True

    spiked = baseline_frame.copy()
    spiked.loc[0:1, "email"] = ""
    report = detect(spiked, name="contacts", quality_score=70.0)

    assert report.is_baseline_run is False
    kinds = {a.kind for a in report.anomalies}
    assert "null_spike" in kinds
    assert "quality_drop" in kinds
    clear_baselines()


def test_suggestions_are_derived_from_the_frame():
    import pandas as pd

    from app_files.intelligence.suggestions import suggestion_texts

    sparse = pd.DataFrame({"email": ["a@b.com", "", "", "d@e.com"], "phone": ["", "", "", ""]})
    dense = pd.DataFrame(
        {
            "email": ["a@b.com", "c@d.com", "e@f.com", "g@h.com"],
            "phone": ["1", "2", "3", "4"],
        }
    )
    sparse_text = suggestion_texts(sparse, top_n=3)
    dense_text = suggestion_texts(dense, top_n=3)
    assert sparse_text != dense_text
    assert any("phone" in line for line in sparse_text)


def test_natural_language_query_filters_invalid_rows():
    import pandas as pd

    from app_files.intelligence.nl_query import query

    frame = pd.DataFrame(
        {"email": ["a@b.com", "bad-email", "e@f.com", "also bad"], "age": ["30", "x", "45", ""]}
    )
    result = query("show me rows where the email is invalid", frame)
    assert result.understood is True
    assert result.matched == 2
    assert result.total == 4

    numeric = query("show me rows where age is greater than 40", frame)
    assert numeric.understood is True
    assert numeric.matched == 1