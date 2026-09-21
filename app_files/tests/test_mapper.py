import pandas as pd
import pytest

from app_files.mappers import available_crms, load_mapping_config, map_data


@pytest.fixture()
def source() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "First Name": ["John"],
            "Last Name": ["Smith"],
            "Phone 1": ["555-123-4567"],
            "Email Address": ["JOHN@Email.com"],
            "Company": ["Acme Inc"],
            "Internal Notes": ["ignore me"],
        }
    )


def test_all_shipped_configs_load():
    assert {"hubspot", "salesforce", "pipedrive"} <= set(available_crms())
    for crm in available_crms():
        assert load_mapping_config(crm).fields


def test_hubspot_mapping_matches_template(source):
    result = map_data(source, load_mapping_config("hubspot"))
    row = result.frame.iloc[0]
    assert row["firstname"] == "John"
    assert row["lastname"] == "Smith"
    assert row["email"] == "john@email.com"
    assert row["phone"] == "+15551234567"
    assert row["company"] == "Acme Inc"
    assert row["lifecyclestage"] == "lead"


def test_unmapped_source_columns_are_reported(source):
    result = map_data(source, load_mapping_config("hubspot"))
    assert "Internal Notes" in result.unmapped_sources
    log = result.mapping_log()
    assert (log["source_column"] == "Internal Notes").any()
    assert log.loc[log["target_field"] == "email", "source_column"].iloc[0] == "Email Address"


def test_pipedrive_combines_name_columns(source):
    result = map_data(source, load_mapping_config("pipedrive"))
    assert result.frame.iloc[0]["Name"] == "John Smith"


def test_unknown_crm_raises():
    with pytest.raises(FileNotFoundError):
        load_mapping_config("zoho-does-not-exist")


def test_exact_match_beats_an_earlier_fields_near_miss():
    """A column must go to the field that names it best, not the field listed first.

    HubSpot's `state` (aliases include `County`) fuzzy-matches a `Country`
    column at 0.923, clearing the 0.82 threshold. Mapping fields in config
    order let `state` claim it, which both filled `state` with country values
    and left `country` — an exact 1.0 match — with nothing.
    """
    frame = pd.DataFrame(
        {
            "First Name": ["John"],
            "Last Name": ["Smith"],
            "City": ["Boston"],
            "Country": ["USA"],
        }
    )
    result = map_data(frame, load_mapping_config("hubspot"))
    assert result.frame.iloc[0]["country"] == "USA"
    assert result.frame.iloc[0]["state"] is None
    assert "Country" not in result.unmapped_sources


def test_auto_mapping_never_assigns_one_column_twice():
    """Each source column feeds at most one target field."""
    frame = pd.DataFrame({"First Name": ["John"], "Company": ["Acme"]})
    result = map_data(frame, load_mapping_config("hubspot"))
    origins = [
        entry["source_column"]
        for entry in result.mappings
        if entry["match"] == "auto"
    ]
    assert len(origins) == len(set(origins))
