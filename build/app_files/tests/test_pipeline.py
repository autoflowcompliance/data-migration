from pathlib import Path

import pandas as pd

from data_migration_tool.cli import main
from data_migration_tool.pipeline import run_pipeline

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "messy_contacts.csv"


def test_pipeline_produces_import_ready_output():
    source = pd.read_csv(SAMPLE, dtype=str, keep_default_na=False)
    result = run_pipeline(source, crm="hubspot", source_filename=SAMPLE.name)

    assert list(result.clean_frame.columns) == [f.name for f in result.mapping_config.fields]
    assert result.summary()["duplicates_removed"] == 1
    assert result.clean_frame.iloc[0]["phone"] == "+15551234567"
    assert result.clean_frame.iloc[0]["createdate"] == "2024-12-31"
    assert "<h1>Data Migration QA Report</h1>" in result.qa_report_html
    assert any(issue.field == "email" for issue in result.validation.errors)


def test_cli_writes_all_deliverables(tmp_path):
    exit_code = main(["-i", str(SAMPLE), "-c", "hubspot", "-o", str(tmp_path)])
    written = {path.name for path in tmp_path.iterdir()}
    assert written == {
        "clean_data.csv",
        "mapping_log.csv",
        "cleaning_log.csv",
        "issues.csv",
        "qa_report.html",
    }
    assert exit_code == 1  # the sample intentionally contains an invalid email
