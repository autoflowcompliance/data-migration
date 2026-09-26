"""Cloud/SaaS licensing (Layer 11) and multi-brand profiles (Layer 10).

The two additions are linked by one idea: a hosted install serves many
customers, so it needs a license that counts seats and a brand per customer.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app_files.branding import (
    Branding,
    BrandProfileError,
    delete_profile,
    load_profiles,
    profile_names,
    resolve_profile,
    save_branding,
    save_profile,
)
from app_files.licensing import sign
from app_files.licensing.cloud import (
    CloudLicense,
    CloudLicenseError,
    CloudLicenseStore,
    Trial,
)


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOF_HOME", str(tmp_path))
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    monkeypatch.setenv("DATAREADY_HOME", str(tmp_path))
    return CloudLicenseStore(tmp_path / "cloud_license")


@pytest.fixture
def cloud(store):
    return CloudLicense(store)


def _activate(cloud, account="acme@example.com", seats=1, expires=""):
    return cloud.activate(
        account=account,
        issued="2026-01-01T00:00:00",
        signature=sign(account, "2026-01-01T00:00:00"),
        seats=seats,
        expires=expires,
    )


class TestActivation:
    def test_a_good_signature_activates(self, cloud):
        config = _activate(cloud)
        assert config.account == "acme@example.com"
        assert cloud.store.exists()

    def test_a_bad_signature_is_refused_and_writes_nothing(self, cloud):
        with pytest.raises(CloudLicenseError, match="signature"):
            cloud.activate(
                account="acme@example.com",
                issued="2026-01-01T00:00:00",
                signature="not-a-real-signature",
            )
        assert not cloud.store.exists()

    def test_without_a_license_is_not_active(self, cloud):
        assert cloud.is_active() is False

    def test_an_activated_license_is_active(self, cloud):
        _activate(cloud)
        assert cloud.is_active() is True

    def test_an_expired_license_is_not_active(self, cloud):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        _activate(cloud, expires=past)
        assert cloud.is_active() is False

    def test_status_reports_offline_with_no_config(self, cloud):
        assert cloud.status() == {"mode": "offline", "cloud": False}

    def test_metering_without_a_license_raises(self, cloud):
        with pytest.raises(CloudLicenseError, match="No cloud license"):
            cloud.record_run(rows=10)


class TestSeats:
    def test_exceeding_the_seat_count_is_refused(self, cloud):
        _activate(cloud, seats=2)
        cloud.add_seat("alice")
        cloud.add_seat("bob")
        with pytest.raises(CloudLicenseError, match="All 2 seat"):
            cloud.add_seat("carol")

    def test_a_released_seat_can_be_reused(self, cloud):
        _activate(cloud, seats=1)
        cloud.add_seat("alice")
        cloud.release_seat("alice")
        assert cloud.add_seat("carol").name == "carol"

    def test_the_same_person_cannot_hold_two_seats(self, cloud):
        _activate(cloud, seats=3)
        cloud.add_seat("alice")
        with pytest.raises(CloudLicenseError, match="already holds"):
            cloud.add_seat("alice")

    def test_releasing_an_unknown_seat_raises(self, cloud):
        _activate(cloud)
        with pytest.raises(CloudLicenseError, match="No active seat"):
            cloud.release_seat("nobody")

    def test_seat_limits_use_active_seats_not_total_history(self, cloud):
        _activate(cloud, seats=1)
        cloud.add_seat("alice")
        cloud.release_seat("alice")
        # History holds one inactive seat; the count that matters is active ones.
        assert cloud.status()["seats_used"] == []
        assert cloud.status()["seats_remaining"] == 1

    def test_a_seat_cannot_be_added_to_an_expired_subscription(self, cloud):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        _activate(cloud, expires=past)
        with pytest.raises(CloudLicenseError, match="expired"):
            cloud.add_seat("alice")


class TestMetering:
    def test_runs_and_rows_accumulate(self, cloud):
        _activate(cloud)
        cloud.record_run(rows=120)
        cloud.record_run(rows=80)
        usage = cloud.usage()
        assert usage["runs"] == 2
        assert usage["rows"] == 200

    def test_negative_rows_do_not_reduce_the_total(self, cloud):
        _activate(cloud)
        cloud.record_run(rows=-50)
        assert cloud.usage()["rows"] == 0

    def test_usage_records_the_billing_period(self, cloud):
        _activate(cloud)
        assert cloud.usage()["period_start"].startswith("20")


class TestTrials:
    def test_a_trial_expires_on_its_date(self, cloud):
        config = cloud.issue_trial("new@example.com", days=14)
        assert config.trial is not None
        assert config.trial.days_remaining() == 14
        assert cloud.is_active() is True

    def test_the_day_after_the_trial_it_is_inactive(self, cloud):
        config = cloud.issue_trial("new@example.com", days=14)
        day_after = datetime.strptime(config.trial.expires, "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        ) + timedelta(seconds=1)
        assert config.trial.is_expired(day_after) is True
        assert config.trial.days_remaining(day_after) == 0

    def test_a_trial_must_last_at_least_a_day(self, cloud):
        with pytest.raises(CloudLicenseError, match="at least one day"):
            cloud.issue_trial("new@example.com", days=0)

    def test_a_trial_shortened_at_issue_expires_earlier(self):
        short = Trial.issue("a@x.com", days=3)
        long = Trial.issue("b@x.com", days=30)
        assert short.expires < long.expires

    def test_conversion_keeps_the_history_and_changes_the_plan(self, cloud):
        cloud.issue_trial("new@example.com", days=14)
        converted = cloud.convert()
        assert converted.trial.converted is True
        assert converted.plan == "team"

    def test_converting_a_non_trial_raises(self, cloud):
        _activate(cloud)
        with pytest.raises(CloudLicenseError, match="not a trial"):
            cloud.convert()

    def test_status_reports_days_remaining_for_a_trial(self, cloud):
        cloud.issue_trial("new@example.com", days=14)
        assert cloud.status()["trial_days_remaining"] == 14


class TestBrandProfiles:
    def _profile(self, name, company):
        return Branding(company_name=company, contact_email=f"hi@{company.lower()}.com")

    def test_no_profiles_is_an_empty_set(self, tmp_path):
        assert load_profiles(tmp_path / "none.json") == {}
        assert profile_names(tmp_path / "none.json") == []

    def test_saving_then_loading_round_trips(self, tmp_path):
        path = tmp_path / "p.json"
        save_profile("acme", self._profile("acme", "Acme Corp"), path)
        save_profile("beta", self._profile("beta", "Beta Ltd"), path)
        profiles = load_profiles(path)
        assert set(profiles) == {"acme", "beta"}
        assert profiles["acme"].company_name == "Acme Corp"
        assert profile_names(path) == ["acme", "beta"]

    def test_saving_the_same_name_overwrites(self, tmp_path):
        path = tmp_path / "p.json"
        save_profile("acme", self._profile("acme", "Acme Corp"), path)
        save_profile("acme", self._profile("acme", "Acme Group"), path)
        assert load_profiles(path)["acme"].company_name == "Acme Group"

    def test_deleting_a_profile(self, tmp_path):
        path = tmp_path / "p.json"
        save_profile("acme", self._profile("acme", "Acme Corp"), path)
        assert delete_profile("acme", path) is True
        assert load_profiles(path) == {}
        assert delete_profile("acme", path) is False

    def test_resolving_an_unknown_profile_raises_rather_than_falling_back(
        self, tmp_path
    ):
        # Falling back would brand one client's report with another client's name.
        path = tmp_path / "p.json"
        save_profile("acme", self._profile("acme", "Acme Corp"), path)
        with pytest.raises(BrandProfileError, match="Available: acme"):
            resolve_profile("gamma", path=path)

    def test_resolving_a_known_profile(self, tmp_path):
        path = tmp_path / "p.json"
        save_profile("acme", self._profile("acme", "Acme Corp"), path)
        assert resolve_profile("acme", path=path).company_name == "Acme Corp"

    def test_default_resolves_to_the_single_brand_settings(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATAREADY_HOME", str(tmp_path))
        save_branding(Branding(company_name="The Install"))
        assert resolve_profile(None).company_name == "The Install"
        assert resolve_profile("default").company_name == "The Install"

    def test_default_is_the_single_brand_settings_even_with_profiles_saved(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("DATAREADY_HOME", str(tmp_path))
        save_branding(Branding(company_name="The Install"))
        save_profile("acme", Branding(company_name="Acme Corp"), tmp_path / "p.json")
        assert resolve_profile("default", path=tmp_path / "p.json").company_name == "The Install"

    def test_two_profiles_give_two_brands_from_one_install(self, tmp_path):
        path = tmp_path / "p.json"
        save_profile("acme", self._profile("acme", "Acme Corp"), path)
        save_profile("beta", self._profile("beta", "Beta Ltd"), path)
        assert resolve_profile("acme", path=path).company_name == "Acme Corp"
        assert resolve_profile("beta", path=path).company_name == "Beta Ltd"

    def test_an_unreadable_profiles_file_is_empty_not_fatal(self, tmp_path):
        path = tmp_path / "p.json"
        path.write_text("{not json")
        assert load_profiles(path) == {}

    def test_a_profile_may_be_a_path_to_a_branding_file(self, tmp_path):
        branding_file = tmp_path / "branding.json"
        branding_file.write_text('{"company_name": "Referenced Co"}')
        path = tmp_path / "p.json"
        path.write_text(f'{{"acme": "{branding_file}"}}')
        assert resolve_profile("acme", path=path).company_name == "Referenced Co"
