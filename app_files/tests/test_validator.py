import pandas as pd

from data_migration_tool.mappers import load_mapping_config
from data_migration_tool.validators import validate_data

CONFIG = load_mapping_config("hubspot")


def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "firstname": ["John", "Jane", ""],
            "lastname": ["Smith", "Doe", "Brown"],
            "email": ["john@email.com", "bad-email", "john@email.com"],
            "phone": ["+15551234567", "555-000", ""],
            "createdate": ["2024-12-31", "31/12/2024", ""],
        }
    )


def test_validation_flags_each_issue_type():
    report = validate_data(frame(), CONFIG)
    kinds = {(issue.check, issue.field) for issue in report.issues}
    assert ("completeness", "firstname") in kinds
    assert ("validity", "email") in kinds
    assert ("uniqueness", "email") in kinds
    assert ("validity", "phone") in kinds
    assert ("consistency", "createdate") in kinds
    assert not report.valid


def test_quality_score_is_100_for_clean_data():
    clean = pd.DataFrame(
        {
            "firstname": ["John"],
            "lastname": ["Smith"],
            "email": ["john@email.com"],
            "phone": ["+14155552671"],
        }
    )
    report = validate_data(clean, CONFIG)
    assert report.valid
    assert report.quality_score == 100.0
    assert report.total_records == 1


def test_issue_rows_point_at_spreadsheet_rows():
    report = validate_data(frame(), CONFIG)
    assert min(report.flagged_rows) >= 2
