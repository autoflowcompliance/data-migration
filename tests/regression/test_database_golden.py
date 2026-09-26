"""Golden file for the database connector (Layer 1).

A real committed SQLite database and the exact frame it must produce. No mock:
`crm.db` is a genuine SQLite file, and `expected.csv` is what the frozen
pipeline's input must look like whether those rows arrived as a file or as a
table read.

Do not regenerate `expected.csv` to make the test green. If it disagrees with a
table read, the read path is the guilty party.
"""

from __future__ import annotations

from pathlib import Path

from app_files.distribution.connectors import get_connector
from app_files.ingestion import read_any
from app_files.ingestion.database import read_table

GOLDEN = Path(__file__).resolve().parent / "golden_files" / "database"


def url() -> str:
    return f"sqlite:///{GOLDEN / 'crm.db'}"


def test_a_table_read_matches_the_golden_file():
    produced = read_table(url(), "contacts")
    expected = read_any(GOLDEN / "expected.csv")
    assert produced.equals(expected)


def test_a_connector_pull_matches_the_golden_file():
    payload = get_connector("database", url=url(), table="contacts").fetch()
    assert payload.as_frame().equals(read_any(GOLDEN / "expected.csv"))


def test_a_where_clause_matches_the_expected_subset():
    produced = read_table(url(), "contacts", where="country = 'GB'")
    assert produced["email"].tolist() == [
        "alice@example.com",
        "dave@example.com",
    ]


def test_the_pipeline_run_matches_a_file_run():
    """The whole point: same rows, same output, either way they arrived."""
    from app_files.pipeline import run_pipeline

    expected = read_any(GOLDEN / "expected.csv")
    from_db = read_table(url(), "contacts")
    assert run_pipeline(from_db, crm="hubspot").clean_frame.equals(
        run_pipeline(expected, crm="hubspot").clean_frame
    )


def test_the_golden_database_still_has_the_schema_it_claims():
    from app_files.ingestion.database import parse_url

    target = parse_url(url())
    assert target.dialect == "sqlite"
    assert read_table(url(), "contacts").shape == (5, 7)
