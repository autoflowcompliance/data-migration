import pandas as pd

from data_migration_tool.cleaners import CleaningConfig, clean_data


def sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "First Name": [" John ", "Jane", "Jane"],
            "Email Address": ["JOHN@Email.com", "jane@x.com", "jane@x.com"],
            "Phone 1": ["(555) 123-4567", "555.987.6543", "555.987.6543"],
            "Created Date": ["12/31/24", "2024-11-05", "2024-11-05"],
            "SKU": ["4.05E+14", "1", "1"],
        }
    )


def test_clean_data_standardizes_and_deduplicates():
    result = clean_data(sample())
    frame = result.frame
    assert len(frame) == 2
    assert result.duplicates_removed == 1
    assert frame.loc[0, "First Name"] == "John"
    assert frame.loc[0, "Email Address"] == "john@email.com"
    assert frame.loc[0, "Phone 1"] == "+15551234567"
    assert frame.loc[0, "Created Date"] == "2024-12-31"
    assert frame.loc[0, "SKU"] == "405000000000000"


def test_column_roles_are_detected_without_hardcoding():
    result = clean_data(sample())
    assert result.column_roles["Email Address"] == "email"
    assert result.column_roles["Phone 1"] == "phone"
    assert result.column_roles["Created Date"] == "date"
    assert result.column_roles["SKU"] == "identifier"


def test_cleaning_log_records_actions():
    log = clean_data(sample()).actions_frame()
    assert set(log.columns) == {"column", "action", "records", "detail"}
    assert "standardized_phone" in set(log["action"])


def test_missing_values_can_be_filled_automatically():
    frame = pd.DataFrame({"City": ["Boston", "", "Boston"]})
    result = clean_data(
        frame, CleaningConfig(missing_value_strategy="auto", remove_duplicates=False)
    )
    assert list(result.frame["City"]) == ["Boston", "Boston", "Boston"]


def test_day_first_date_parsing():
    frame = pd.DataFrame({"Date": ["04/03/2026", "31/12/2024"]})
    result = clean_data(
        frame, CleaningConfig(standardize_dates=True, date_first=True, remove_duplicates=False)
    )
    # With day_first=True, 04/03/2026 should be April 3rd (2026-03-04)
    assert result.frame.loc[0, "Date"] == "2026-03-04"
    assert result.frame.loc[1, "Date"] == "2024-12-31"
