"""Database and SFTP connectors feeding the real pipeline.

The unit tests prove the connector returns the right frame. This proves a run
triggered from a database produces the same output as the same rows uploaded as
a file — the "nothing downstream knows the difference" claim, asserted against
the real pipeline rather than a stub.
"""

from __future__ import annotations

import sqlite3

import pytest

from app_files.distribution.connectors import get_connector
from app_files.ingestion import read_any
from app_files.pipeline import run_pipeline

CUSTOMER_ROWS = [
    ("  alice@example.com ", "Alice", "GB", "1,200.50", "2024-01-05"),
    ("bob@example.com", "Bob  ", "US", "980", "2024-02-11"),
    ("carol@example.com", "", "", "0", ""),
    ("dave@example.com", "dave", "GB", "-45.25", "2024-03-02"),
    ("eve@example.com", "Eve", "gb", "1.000,00", "2024-03-09"),
]


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "crm.db"
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE contacts (email TEXT, first_name TEXT, country TEXT, "
        "amount TEXT, created TEXT)"
    )
    connection.executemany("INSERT INTO contacts VALUES (?, ?, ?, ?, ?)", CUSTOMER_ROWS)
    connection.commit()
    connection.close()
    return path


@pytest.fixture
def contacts_csv(tmp_path):
    """The same rows, as a file, with the same header names the table has."""
    path = tmp_path / "contacts.csv"
    import csv

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["email", "first_name", "country", "amount", "created"])
        writer.writerows(CUSTOMER_ROWS)
    return path


class TestDatabaseFeedsThePipeline:
    def test_a_table_run_matches_a_file_run(self, database, contacts_csv):
        """The spec's acceptance test: database output equals file output."""
        connector = get_connector("database", url=f"sqlite:///{database}", table="contacts")
        from_db = connector.fetch().as_frame()
        from_file = read_any(contacts_csv)
        assert from_db.equals(from_file)

    def test_the_pipeline_result_is_identical(self, database, contacts_csv):
        connector = get_connector("database", url=f"sqlite:///{database}", table="contacts")
        db_run = run_pipeline(connector.fetch().as_frame(), crm="hubspot")
        file_run = run_pipeline(read_any(contacts_csv), crm="hubspot")
        assert db_run.clean_frame.equals(file_run.clean_frame)
        assert db_run.summary() == file_run.summary()

    def test_a_query_run_matches_the_same_rows_as_a_file(self, database, contacts_csv):
        connector = get_connector("database", url=f"sqlite:///{database}")
        payload = connector.fetch(
            query="SELECT email, first_name, country, amount, created FROM contacts "
            "WHERE country LIKE 'g%' OR country LIKE 'G%'"
        )
        subset = payload.as_frame()
        file_run = run_pipeline(read_any(contacts_csv), crm="hubspot").clean_frame
        db_run = run_pipeline(subset, crm="hubspot").clean_frame
        # The same three GB rows, however they arrived.
        assert set(db_run["email"].str.lower()) <= set(file_run["email"].str.lower())
        assert len(db_run) == 3

    def test_a_where_clause_narrows_the_pipeline_input(self, database):
        from app_files.ingestion.database import read_table

        # SQLite's `=` is case-sensitive, so 'gb' (lowercase) is correctly not
        # matched. A query that wants both spellings says so, as it would in
        # any SQL client -- the connector does not silently widen the predicate.
        frame = read_table(f"sqlite:///{database}", "contacts", where="country = 'GB'")
        assert len(frame) == 2
        case_insensitive = read_table(
            f"sqlite:///{database}", "contacts", where="upper(country) = 'GB'"
        )
        assert len(case_insensitive) == 3

    def test_the_output_written_from_a_database_run_is_well_formed(self, database, tmp_path):
        connector = get_connector("database", url=f"sqlite:///{database}", table="contacts")
        result = run_pipeline(connector.fetch().as_frame(), crm="hubspot")
        out = tmp_path / "clean.csv"
        result.clean_frame.to_csv(out, index=False)
        assert out.exists() and len(read_any(out)) == len(result.clean_frame)


class TestSftpFeedsThePipeline:
    class FakeSFTP:
        def __init__(self, payload: bytes):
            self.payload = payload

        def open(self, path, mode="rb"):
            sftp = self

            class Handle:
                def __enter__(self_inner):
                    return self_inner

                def __exit__(self_inner, *args):
                    return False

                def read(self_inner):
                    return sftp.payload

            return Handle()

        def listdir_attr(self, path):
            return []

        def close(self):
            pass

    class FakeClient:
        def __init__(self, sftp):
            self._sftp = sftp

        def open_sftp(self):
            return self._sftp

    def test_a_file_pulled_over_sftp_runs_the_pipeline(self, contacts_csv, tmp_path):
        payload = contacts_csv.read_bytes()
        from app_files.distribution.connectors import SFTPConnector

        connector = SFTPConnector(
            host="files.example.com",
            path="/in/contacts.csv",
            client=self.FakeClient(self.FakeSFTP(payload)),
        )
        pulled = connector.fetch().as_frame()
        file_frame = read_any(contacts_csv)
        assert pulled.equals(file_frame)
        assert run_pipeline(pulled, crm="hubspot").clean_frame.equals(
            run_pipeline(file_frame, crm="hubspot").clean_frame
        )
