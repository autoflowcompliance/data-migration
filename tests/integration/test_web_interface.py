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
def test_demo_offers_every_format(demo):
    """The demo is a sales tool: it must not hide a format the buyer is sold."""
    assert state.allowed_formats(demo) == ["csv", "excel", "json", "sql"]


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


def test_demo_run_does_not_truncate(contacts_csv):
    """No row cap in the demo any more, so the whole file is processed."""
    large = pd.concat([state.load_sample("messy_contacts.csv")] * 200, ignore_index=True)
    outcome = state.run_migration(
        large, source_name="big.csv", template="hubspot", limits=resolve_limits(False)
    )
    assert not outcome.row_limit.truncated
    assert not any("rows" in note for note in outcome.notes)


def test_full_run_does_not_truncate(full):
    large = pd.concat([state.load_sample("messy_contacts.csv")] * 200, ignore_index=True)
    outcome = state.run_migration(
        large, source_name="big.csv", template="hubspot", limits=full
    )
    assert not outcome.row_limit.truncated


def test_demo_run_tracks_lineage(demo, contacts_csv):
    """Lineage is a headline feature; the demo shows it off like the rest."""
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=demo,
    )
    assert not outcome.pipeline.lineage_log().empty
    assert outcome.lineage_report_html


def test_full_run_tracks_lineage(full):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=full,
    )
    assert not outcome.pipeline.lineage_log().empty


# ------------------------------------------------------------------- branding
def test_demo_run_applies_custom_branding(demo):
    """Branding is part of the product, so the demo honours it too."""
    from app_files.branding import Branding

    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="x.csv",
        template="hubspot",
        limits=demo,
        branding=Branding(company_name="Acme Data Co"),
    )
    assert "Acme Data Co" in outcome.qa_report_html


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


# ------------------------------------------------- new run outputs surfaced
def test_a_run_carries_the_diff_and_lineage_reports(demo):
    """Both were computed by the backend but never reached the results page."""
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="messy_contacts.csv",
        template="hubspot",
        limits=demo,
    )
    assert outcome.diff_report_html
    assert outcome.lineage_report_html
    # Both reports wear the house palette, not the old grey.
    assert "#F5F0E6" in outcome.diff_report_html
    assert "#F5F0E6" in outcome.lineage_report_html


def test_the_issues_frame_merges_validation_and_rule_failures(demo):
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="messy_contacts.csv",
        template="hubspot",
        limits=demo,
    )
    issues = outcome.issues
    assert not issues.empty
    assert {"row", "field", "severity", "message"} <= set(issues.columns)
    if outcome.rules is not None and outcome.rules.total_failures:
        # Rule failures carry a `check` column that validation issues do not,
        # so its presence proves the two sources were actually merged.
        assert "check" in issues.columns


def test_rules_are_actually_run_not_just_loaded(demo):
    """The trap: a config whose rules never run reports a perfect score.

    ``run_pipeline`` validates the mapped frame only; rules are run separately.
    A regression that drops that call would leave ``quality_score: 100`` and
    zero issues, which reads as "your data is fine".
    """
    outcome = state.run_migration(
        state.load_sample("messy_contacts.csv"),
        source_name="messy_contacts.csv",
        template="hubspot",
        limits=demo,
    )
    assert outcome.rules is not None
    assert outcome.rules.rules_run > 0


# ---------------------------------------------------- reconciliation path
def test_reconciliation_run_produces_a_dashboard(demo):
    outcome = state.run_reconciliation_migration(
        state.load_sample("bank_statement.csv"),
        state.load_sample("ledger.csv"),
        source_name="bank_statement.csv",
        limits=demo,
    )
    assert outcome.reconciliation is not None
    # Reconciliation is not a mapping job, so there is no pipeline behind it —
    # and the results page must still be able to read it.
    assert outcome.pipeline is None
    assert outcome.summary == {}
    assert outcome.issues.empty
    summary = outcome.reconciliation.summary
    assert summary.bank_transactions > 0
    assert summary.matched > 0
    assert summary.match_rate > 0


def test_reconciliation_dashboard_report_wears_the_palette(demo):
    from app_files.utilities.reconciliation_dashboard import render_dashboard_html

    outcome = state.run_reconciliation_migration(
        state.load_sample("bank_statement.csv"),
        state.load_sample("ledger.csv"),
        source_name="bank_statement.csv",
        limits=demo,
    )
    html = render_dashboard_html(outcome.reconciliation)
    assert "#F5F0E6" in html
    assert "#FDFBF7" in html
    # The old green/red defaults are gone.
    assert "#059669" not in html
    assert "#dc2626" not in html


def test_reconciliation_rejects_a_frame_without_the_named_columns(demo):
    """The four column names are required; a missing one must be explained."""
    frame = pd.DataFrame({"When": ["2025-01-01"], "Value": ["1.00"]})
    with pytest.raises(ValueError, match="bank statement has no"):
        state.run_reconciliation_migration(
            frame, state.load_sample("ledger.csv"),
            source_name="bank.csv", limits=demo,
        )