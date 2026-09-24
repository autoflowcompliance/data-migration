"""Multi-brand profiles, custom domain, and the client portal."""

from __future__ import annotations

import pytest

from app_files.branding import (
    BrandProfile,
    Branding,
    PortalEntry,
    ProfileError,
    ProfileSet,
    apply_profile_to_report,
    build_portal,
    load_profiles,
    portal_entries_from_directory,
    save_profiles,
)
from app_files.branding.profiles import profiles_path


def _profile(slug, name, colour="#C97A2E", domain=""):
    return BrandProfile(
        slug=slug,
        branding=Branding(company_name=name, accent_color=colour),
        domain=domain,
    )


def test_a_bare_install_presents_one_default_profile(tmp_path):
    profiles = load_profiles(tmp_path / "none.json")
    assert list(profiles.profiles) == ["default"]
    assert profiles.active == "default"


def test_profiles_round_trip(tmp_path):
    path = tmp_path / "profiles.json"
    profile_set = ProfileSet()
    profile_set.add(_profile("acme", "ACME Ltd", "#112233", "acme.example.com"))
    profile_set.add(_profile("globex", "Globex"))
    profile_set.active = "globex"
    save_profiles(profile_set, path)

    reloaded = load_profiles(path)
    assert set(reloaded.profiles) == {"acme", "globex"}
    assert reloaded.active == "globex"
    assert reloaded.get("acme").branding.company_name == "ACME Ltd"
    assert reloaded.get("acme").domain == "acme.example.com"


def test_get_with_no_slug_returns_the_active_profile(tmp_path):
    profile_set = ProfileSet()
    profile_set.add(_profile("a", "A"))
    profile_set.add(_profile("b", "B"))
    profile_set.active = "b"
    assert profile_set.get().slug == "b"


def test_unknown_profile_lists_the_known_ones(tmp_path):
    profile_set = ProfileSet()
    profile_set.add(_profile("acme", "ACME Ltd"))
    with pytest.raises(ProfileError, match="acme"):
        profile_set.get("nope")


def test_malformed_profile_file_is_a_clear_error(tmp_path):
    path = tmp_path / "profiles.json"
    path.write_text("{not json")
    with pytest.raises(ProfileError, match="Could not read"):
        load_profiles(path)


def test_first_profile_becomes_active(tmp_path):
    profile_set = ProfileSet()
    profile_set.add(_profile("first", "First"))
    profile_set.add(_profile("second", "Second"))
    assert profile_set.active == "first"


def test_a_report_is_reskinned_with_the_profile(tmp_path):
    profile_set = ProfileSet()
    profile_set.add(_profile("acme", "ACME Ltd", "#112233"))
    html = "<html><head></head><body>{{BRAND_NAME}}</body></html>"
    branded = apply_profile_to_report(html, profile_set.get("acme"))
    assert "ACME Ltd" in branded


# ------------------------------------------------------------------- portal
def test_portal_lists_deliverables_with_branding(tmp_path):
    entries = [
        PortalEntry(filename="clean_data.csv", label="Clean Data", size_bytes=120),
        PortalEntry(filename="qa_report.html", label="QA Report"),
    ]
    html = build_portal(_profile("acme", "ACME Ltd", "#112233"), entries)
    assert "ACME Ltd" in html
    assert "Clean Data" in html
    assert "clean_data.csv" in html
    assert "#112233" in html


def test_portal_shows_the_client_domain_when_set(tmp_path):
    profile = _profile("acme", "ACME Ltd", domain="data.acme.example.com")
    html = build_portal(profile, [])
    assert "data.acme.example.com" in html


def test_portal_escapes_filenames_and_labels():
    entries = [PortalEntry(filename="a&b.csv", label="A <b>report</b>")]
    html = build_portal(_profile("x", "X"), entries)
    assert "a&amp;b.csv" in html
    assert "&lt;b&gt;" in html
    assert "<b>report</b>" not in html


def test_portal_entries_skip_signatures_and_manifest(tmp_path):
    (tmp_path / "clean_data.csv").write_text("x" * 10)
    (tmp_path / "clean_data.csv.sig").write_text("{}")
    (tmp_path / "manifest.json").write_text("{}")
    entries = portal_entries_from_directory(tmp_path)
    assert [e.filename for e in entries] == ["clean_data.csv"]
    assert entries[0].size_bytes == 10
    assert entries[0].delivered_at


def test_profiles_path_honours_dataready_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path))
    assert profiles_path().parent == tmp_path