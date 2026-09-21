"""Unit tests for the branding layer: settings persistence and report injection."""

from __future__ import annotations

import base64
import json

import pandas as pd
import pytest

from app_files.branding import (
    Branding,
    branding_path,
    inject_branding,
    inject_branding_into_bytes,
    inject_demo_watermark,
    load_branding,
    logo_data_uri,
    normalise_colour,
    save_branding,
)
from app_files.pipeline import run_pipeline


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


@pytest.fixture
def report_html(contacts_frame) -> str:
    """A real report, produced by the frozen reporter.

    Using the actual reporter output rather than a hand-written snippet is the
    point: the shipped report has no ``{{BRAND_*}}`` placeholders, and this
    fixture is what proves branding still applies to it.
    """
    return run_pipeline(contacts_frame, crm="hubspot").qa_report_html


@pytest.fixture
def png_bytes() -> bytes:
    # 1x1 transparent PNG.
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )


# ------------------------------------------------------------------- settings
def test_defaults_are_loaded_when_no_file_exists():
    branding = load_branding()
    assert branding.company_name == "DataFlow"
    assert branding.logo_path is None
    assert branding.accent_color == "#C97A2E"
    assert branding.show_powered_by is True


def test_save_then_load_round_trips():
    saved = Branding(
        company_name="Acme Data Co",
        contact_email="hi@acme.com",
        website="https://acme.com",
        accent_color="#FF0000",
        show_powered_by=False,
    )
    path = save_branding(saved)
    assert path == branding_path()
    loaded = load_branding()
    assert loaded.company_name == "Acme Data Co"
    assert loaded.contact_email == "hi@acme.com"
    assert loaded.show_powered_by is False


def test_save_branding_accepts_a_dict():
    save_branding({"company_name": "From Dict"})
    assert load_branding().company_name == "From Dict"


def test_partial_file_merges_over_defaults():
    path = branding_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"company_name": "Partial"}), encoding="utf-8")
    branding = load_branding()
    assert branding.company_name == "Partial"
    assert branding.accent_color == "#C97A2E"  # untouched default


def test_unknown_keys_are_ignored():
    path = branding_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"company_name": "X", "future_key": "whatever"}), encoding="utf-8"
    )
    assert load_branding().company_name == "X"


def test_corrupt_branding_file_falls_back_to_defaults():
    path = branding_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    assert load_branding().company_name == "DataFlow"


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("#c97a2e", "#C97A2E"),
        ("c97a2e", "#C97A2E"),
        ("#FF0000", "#FF0000"),
        ("", "#C97A2E"),
        ("nonsense", "#C97A2E"),
        ("#GGGGGG", "#C97A2E"),
        ("#12345", "#C97A2E"),
    ],
)
def test_normalise_colour(given, expected):
    assert normalise_colour(given) == expected


# -------------------------------------------------------------------- logos
def test_logo_data_uri_is_empty_without_a_path():
    assert logo_data_uri(None) == ""
    assert logo_data_uri("") == ""


def test_logo_data_uri_is_empty_for_a_missing_file():
    assert logo_data_uri("/nonexistent/logo.png") == ""


def test_logo_data_uri_inlines_the_bytes(tmp_path, png_bytes):
    path = tmp_path / "logo.png"
    path.write_bytes(png_bytes)
    uri = logo_data_uri(path)
    assert uri.startswith("data:image/png;base64,")
    assert base64.b64decode(uri.split(",", 1)[1]) == png_bytes


def test_logo_data_uri_picks_the_mime_from_the_suffix(tmp_path, png_bytes):
    path = tmp_path / "logo.svg"
    path.write_bytes(png_bytes)
    assert logo_data_uri(path).startswith("data:image/svg+xml;base64,")


# ----------------------------------------------------------------- injection
def test_branding_changes_a_real_report(report_html):
    """The shipped reporter has no placeholders, so this is the important case."""
    branded = inject_branding(report_html, Branding(company_name="Acme Data Co"))
    assert branded != report_html
    assert "Acme Data Co" in branded


def test_masthead_goes_above_the_report_title(report_html):
    branded = inject_branding(report_html, Branding(company_name="Acme Data Co"))
    assert branded.index("Acme Data Co") < branded.index("<h1")


def test_accent_colour_is_applied(report_html):
    branded = inject_branding(report_html, Branding(accent_color="#FF0000"))
    assert "#FF0000" in branded


def test_footer_is_present_by_default(report_html):
    assert "Powered by DataFlow" in inject_branding(report_html, Branding())


def test_footer_is_suppressed_when_disabled(report_html):
    branded = inject_branding(report_html, Branding(show_powered_by=False))
    assert "Powered by DataFlow" not in branded


def test_contact_details_appear_when_set(report_html):
    branded = inject_branding(
        report_html, Branding(contact_email="hi@acme.com", website="https://acme.com")
    )
    assert "hi@acme.com" in branded
    assert "https://acme.com" in branded


def test_logo_is_embedded_as_a_data_uri(report_html, tmp_path, png_bytes):
    logo = tmp_path / "logo.png"
    logo.write_bytes(png_bytes)
    branded = inject_branding(report_html, Branding(logo_path=str(logo)))
    assert "data:image/png;base64," in branded


def test_placeholders_are_substituted_when_a_template_opts_in():
    template = (
        "<html><body><h1>{{BRAND_NAME}}</h1>"
        "<p>{{BRAND_EMAIL}}</p>{{POWERED_BY}}</body></html>"
    )
    branded = inject_branding(
        template, Branding(company_name="Acme", contact_email="hi@acme.com")
    )
    assert "Acme" in branded
    assert "hi@acme.com" in branded
    assert "{{BRAND_NAME}}" not in branded
    assert "Powered by DataFlow" in branded


def test_company_name_is_html_escaped(report_html):
    branded = inject_branding(report_html, Branding(company_name="<script>x</script>"))
    assert "<script>x</script>" not in branded
    assert "&lt;script&gt;" in branded


def test_inject_into_bytes_round_trips():
    html = "<html><body><h1>Report</h1></body></html>"
    data = inject_branding_into_bytes(html.encode("utf-8"), Branding(company_name="Acme"))
    assert b"Acme" in data


def test_loading_branding_from_disk_when_omitted():
    save_branding(Branding(company_name="From Disk"))
    assert "From Disk" in inject_branding(
        "<html><body><h1>R</h1></body></html>"
    )


# ---------------------------------------------------------------- watermark
def test_watermark_marks_the_report_as_a_demo(report_html):
    marked = inject_demo_watermark(report_html)
    assert "DEMO" in marked
    assert marked.endswith("</html>")


def test_watermark_includes_the_reason_when_given(report_html):
    marked = inject_demo_watermark(report_html, "first 500 rows only")
    assert "first 500 rows only" in marked


def test_watermark_is_inserted_before_the_closing_body(report_html):
    marked = inject_demo_watermark(report_html)
    assert marked.index("DEMO") < marked.index("</body>")


def test_watermark_handles_html_without_a_body_tag():
    assert "DEMO" in inject_demo_watermark("<div>bare</div>")