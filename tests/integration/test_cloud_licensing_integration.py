"""Cloud licensing and brand profiles through the real report path.

The point of these tests is that the additions are inert until asked for: a run
with no profile renders the install's own brand, and a run with a profile
renders that client's brand, from the same code path.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app_files.branding import Branding, profiles_path, save_branding, save_profile
from app_files.interface.web.state import run_migration
from app_files.licensing import FULL_LIMITS, resolve_limits, sign
from app_files.licensing.cloud import CloudLicense, CloudLicenseError, CloudLicenseStore
from app_files.tenancy import TenantRegistry


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture
def source(contacts_csv):
    from app_files.ingestion import read_any

    return read_any(contacts_csv)


class TestBrandProfileThroughTheReport:
    def test_a_profile_brands_a_run(self, home, source):
        save_profile("acme", Branding(company_name="Acme Corp"), profiles_path())

        outcome = run_migration(
            source,
            source_name="contacts.csv",
            template="hubspot",
            limits=resolve_limits(True),
            brand_profile="acme",
        )
        assert "Acme Corp" in outcome.qa_report_html
        assert "{{BRAND_COMPANY}}" not in outcome.qa_report_html

    def test_two_profiles_brand_the_same_file_two_ways(self, home, source):
        save_profile("acme", Branding(company_name="Acme Corp"), profiles_path())
        save_profile("beta", Branding(company_name="Beta Ltd"), profiles_path())

        first = run_migration(
            source, source_name="c.csv", template="hubspot",
            limits=resolve_limits(True), brand_profile="acme",
        )
        second = run_migration(
            source, source_name="c.csv", template="hubspot",
            limits=resolve_limits(True), brand_profile="beta",
        )
        assert "Acme Corp" in first.qa_report_html and "Beta Ltd" not in first.qa_report_html
        assert "Beta Ltd" in second.qa_report_html and "Acme Corp" not in second.qa_report_html

    def test_no_profile_uses_the_install_brand(self, home, source):
        save_branding(Branding(company_name="The Install"))
        outcome = run_migration(
            source, source_name="c.csv", template="hubspot",
            limits=resolve_limits(True),
        )
        assert "The Install" in outcome.qa_report_html

    def test_an_explicit_branding_beats_a_profile(self, home, source):
        save_profile("acme", Branding(company_name="Acme Corp"), profiles_path())
        outcome = run_migration(
            source, source_name="c.csv", template="hubspot",
            limits=resolve_limits(True),
            branding=Branding(company_name="Explicit Co"),
            brand_profile="acme",
        )
        assert "Explicit Co" in outcome.qa_report_html

    def test_an_unknown_profile_fails_the_run_rather_than_misbranding(self, home, source):
        from app_files.branding import BrandProfileError

        with pytest.raises(BrandProfileError):
            run_migration(
                source, source_name="c.csv", template="hubspot",
                limits=resolve_limits(True), brand_profile="ghost",
            )


class TestCloudLicenseWithTenants:
    def test_each_tenant_meters_its_own_runs(self, home):
        store_a = CloudLicenseStore(home / "a")
        store_b = CloudLicenseStore(home / "b")
        licence_a = CloudLicense(store_a)
        licence_b = CloudLicense(store_b)

        issued = "2026-01-01T00:00:00"
        licence_a.activate("a@example.com", issued, sign("a@example.com", issued), seats=1)
        licence_b.activate("b@example.com", issued, sign("b@example.com", issued), seats=1)

        licence_a.record_run(rows=100)
        licence_a.record_run(rows=50)
        licence_b.record_run(rows=10)

        assert licence_a.usage()["rows"] == 150
        assert licence_b.usage()["rows"] == 10

    def test_an_expiring_subscription_stops_new_seats(self, home):
        store = CloudLicenseStore(home / "cloud")
        licence = CloudLicense(store)
        soon = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")
        issued = "2026-01-01T00:00:00"
        licence.activate("acme@example.com", issued, sign("acme@example.com", issued),
                         seats=1, expires=soon)
        assert licence.is_active() is True
        licence.add_seat("alice")

        expired = CloudLicense(CloudLicenseStore(home / "cloud"))
        record = expired.store.load()
        record.expires = (
            datetime.now(timezone.utc) - timedelta(seconds=1)
        ).strftime("%Y-%m-%dT%H:%M:%S")
        expired.store.save(record)
        assert expired.is_active() is False
        with pytest.raises(CloudLicenseError, match="expired"):
            expired.add_seat("bob")


class TestTenancyAndFullLimitsAreIndependent:
    def test_a_licensed_install_still_resolves_full_limits(self, home):
        assert resolve_limits(True).demo is False
        assert resolve_limits(True).watermark is False
        assert FULL_LIMITS["output_formats"] == ["csv", "excel", "json", "sql"]

    def test_a_tenant_does_not_change_the_limits(self, home):
        before = resolve_limits(True).as_dict()
        TenantRegistry().create("Acme", tenant_id="acme")
        assert resolve_limits(True).as_dict() == before
