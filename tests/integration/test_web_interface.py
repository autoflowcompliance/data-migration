"""Integration tests for the NiceGUI interface layer.

The pages themselves are thin and NiceGUI-specific, so these tests exercise the
UI-independent logic they delegate to (``state``), plus the kinds of runs a user
actually performs: a licensed full run and a watermarked demo run.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app_files.interface.web import state
from app_files.licensing import Limits, resolve_limits


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


@pytest.fixture
def demo() -> Limits:
    return resolve_limits(False)


@pytest.fixture
def full() -> Limits:
    return resolve_limits(True)


# ------------------------------------------------------------------ discovery
def test_templates_on_disk_lists_the_shipped_configs():
    templates = state.templates_on_disk()
    assert "hubspot" in templates
    assert "bank_reconciliation" in templates


def test_upload_routing_accepts_the_legacy_and_tsv_extensions():
    """The extensions added to ingestion must be offered to the user.

    ``read_upload`` rejects anything outside ``available_extensions()``, so a
    working adapter for ``.xls`` or ``.tsv`` is invisible unless the extension
    list grows with it.
    """
    from app_files.ingestion import available_extensions

    assert {".xls", ".tsv"} <= set(available_extensions())
    # And the UI's own pre-check agrees, so an upload is not rejected up front.
    frame = state.read_upload(b"name\tcity\nJohn\tBoston\n", "contacts.tsv")
    assert frame.iloc[0]["city"] == "Boston"


def test_read_upload_decodes_a_cp1252_upload(isolated_home):
    """An accented Windows-1252 CSV survives the whole upload path."""
    frame = state.read_upload("name,note\nJosé,café naïve\n".encode("cp1252"), "contacts.csv")
    assert frame["name"].tolist() == ["José"]
    assert frame["note"].tolist() == ["café naïve"]


def test_available_samples_only_lists_files_that_exist():
    samples = state.available_samples()
    assert samples
    for entry in samples:
        assert state.sample_path(entry["file"]).is_file()


def test_every_sample_declares_a_real_template():
    templates = set(state.templates_on_disk())
    for entry in state.available_samples():
        assert entry["template"] in templates


def test_sample_path_accepts_a_key_or_a_filename():
    assert state.sample_path("messy_contacts").name == "messy_contacts.csv"
    assert state.sample_path("messy_contacts.csv").name == "messy_contacts.csv"


def test_load_sample_reads_a_frame():
    frame = state.load_sample("messy_contacts.csv")
    assert not frame.empty


# -------------------------------------------------------------------- formats
def test_demo_offers_only_csv(demo):
    assert state.allowed_formats(demo) == ["csv"]


def test_full_mode_offers_every_format(full):
    assert state.allowed_formats(full) == ["csv", "excel", "json", "sql"]


def test_format_choices_are_display_labels(full):
    assert state.format_choices(full) == ["Csv", "Excel", "Json", "Sql"]


# ------------------------------------------------------------------ ingest
def test_read_upload_rejects_an_unsupported_extension():
    with pytest.raises(ValueError, match="not a supported file type"):
        state.read_upload(b"anything", "photo.png")


def test_read_upload_accepts_a_supported_file(contacts_csv):
    frame = state.read_upload(contacts_csv.read_bytes(), contacts_csv.name)
    assert not frame.empty


# -------------------------------------------------------------- demo vs full
def test_demo_run_is_watermarked(demo, contacts_csv):
    outcome = state.run_migration(
        state.read_upload(contacts_csv.read_bytes(), contacts_csv.name),
        source_name=contacts_csv.name,
        template="hubspot",
        limits=demo,
    )
    assert "DEMO" in outcome.qa_report_html


def test_full_run_is_not_watermarked(full, contacts_csv):
    outcome = state.run_migration(
        state.read_upload(contacts_csv.read_bytes(), contacts_csv.name),
        source_name=contacts_csv.name,
        template="hubspot",
        limits=full,
    )
    assert "DEMO" not in outcome.qa_report_html


def test_demo_run_enforces_the_row_limit(full, contacts_csv):
    """A frame larger than the demo cap is trimmed, and the note says so."""
    large = pd.concat([state.load_sample("messy_contacts.csv")] * 200, ignore_index=True)
    outcome = state.run_migration(
        large, source_name="big.csv", template="hubspot", limits=resolve_limits(False)
    )
    assert outcome.row_limit.truncated
    assert len(outcome.pipeline.clean_frame) <= 500
    assert any("500" in note for note in outcome.notes)


def test_full_run_does_not_truncate(full):
    large = pd.concat([state.load_sample("messy_contacts.csv")] * 200, ignore_index=True)
    outcome = state.run_migration(
        large, source_name="big.csv", template="hubspot", limits=full
    )
    assert not outcome.row_limit.truncated


def test_demo_run_does_not_track_lineage(demo, contacts_csv):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=demo,
    )
    assert outcome.pipeline.lineage_log().empty


def test_full_run_tracks_lineage(full):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=full,
    )
    assert not outcome.pipeline.lineage_log().empty


# ------------------------------------------------------------------- branding
def test_demo_run_ignores_custom_branding(demo):
    from app_files.branding import Branding

    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=demo,
        branding=Branding(company_name="Should Not Appear"),
    )
    assert "Should Not Appear" not in outcome.qa_report_html


def test_full_run_applies_custom_branding(full):
    from app_files.branding import Branding

    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=full,
        branding=Branding(company_name="Acme Data Co"),
    )
    assert "Acme Data Co" in outcome.qa_report_html


def test_no_placeholder_ever_leaks_into_a_finished_report(demo):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=demo,
    )
    assert "{{BRAND" not in outcome.qa_report_html
    assert "{{POWERED_BY}}" not in outcome.qa_report_html


# ---------------------------------------------------------------- report body
def test_outcome_exposes_a_score_and_summary(demo):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=demo,
    )
    assert 0 <= outcome.score <= 100
    assert outcome.summary["rows_in"] > 0


def test_outcome_issues_include_rule_failures(full):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=full,
    )
    assert not outcome.issues.empty


def test_base_report_is_unpolluted_by_the_scorecard(contacts_frame):
    """The frozen reporter's own output must stay scorecard-free.

    The scorecard is injected afterwards; this is the guard that the core
    reporter was not modified to produce it.
    """
    from app_files.pipeline import run_pipeline

    html = run_pipeline(contacts_frame, crm="hubspot").qa_report_html
    assert "Quality scorecard" not in html


# ------------------------------------------------------------- report serving
def test_a_run_publishes_its_report_and_is_fetchable_over_http(demo):
    """A report must be reachable by token, not carried over the WebSocket."""
    from app_files.interface.web import session as session_store

    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="messy_contacts.csv",
        template="hubspot",
        limits=demo,
    )

    assert outcome.report_token
    assert session_store.get_report(outcome.report_token) == outcome.qa_report_html


def test_the_report_route_serves_the_report_and_404s_unknown_tokens():
    """The route is what an iframe hits, so it has to answer both cases."""
    from fastapi.testclient import TestClient
    from nicegui import app

    from app_files.interface.web import reports
    from app_files.interface.web import session as session_store

    # Importing the package registers the page routes; the report route is
    # mounted explicitly, and twice to prove re-registration is a no-op.
    import app_files.interface.web.main  # noqa: F401  (page routes)

    reports.register_report_route()
    reports.register_report_route()

    token = session_store.publish_report("<html>hello</html>")
    client = TestClient(app)

    response = client.get(reports.report_url(token))
    assert response.status_code == 200
    assert "hello" in response.text

    missing = client.get(reports.report_url("not-a-real-token"))
    assert missing.status_code == 404
    assert "no longer available" in missing.text