"""Direct database reads (Layer 1 connector extension).

SQLite is the standard library, so the entire connector — URL parsing, quote
handling, query construction, cursor iteration, stringification — runs against
a genuine database here. The other dialects share that code; what differs is
the driver module and the placeholder style, and those are pinned separately.

The claim the tests hold: a table read and a CSV of the same rows produce the
same frame, so nothing downstream can tell a database from an upload.
"""

from __future__ import annotations

import sqlite3

import pytest

from app_files.ingestion.database import (
    DIALECTS,
    DatabaseError,
    MissingDriver,
    available_drivers,
    execute_query,
    list_tables,
    parse_url,
    read_table,
)
from app_files.ingestion.registry import read_any

ROWS = [
    ("alice@example.com", "Alice", "GB", "1200.50", "2024-01-05"),
    ("bob@example.com", "Bob", "US", "980.00", "2024-02-11"),
    ("carol@example.com", "", "", "0", ""),
    ("dave@example.com", "Dave", "GB", "-45.25", "2024-03-02"),
]


@pytest.fixture
def db_path(tmp_path):
    """A real SQLite database with a table whose values exercise the edges."""
    path = tmp_path / "customers.db"
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE customers (email TEXT, full_name TEXT, country TEXT, "
        "amount REAL, signed_up TEXT)"
    )
    connection.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
        ROWS,
    )
    connection.execute(
        "CREATE TABLE orders (email TEXT, total REAL)"
    )
    connection.executemany(
        "INSERT INTO orders VALUES (?, ?)",
        [("alice@example.com", 10.5), ("alice@example.com", 20.25)],
    )
    connection.commit()
    connection.close()
    return path


def url_for(path) -> str:
    return f"sqlite:///{path}"


class TestParseUrl:
    def test_postgres_url_is_parsed(self):
        target = parse_url("postgresql://reader@db.internal:5433/warehouse")
        assert target.dialect == "postgresql"
        assert target.host == "db.internal"
        assert target.port == 5433
        assert target.username == "reader"
        assert target.database == "warehouse"

    def test_the_default_port_is_filled_in(self):
        assert parse_url("postgresql://u@h/db").port == 5432
        assert parse_url("mysql://u@h/db").port == 3306
        assert parse_url("mssql://u@h/db").port == 1433

    def test_a_sqlalchemy_style_dialect_suffix_is_ignored(self):
        assert parse_url("mssql+pyodbc://u@h/db").dialect == "mssql"

    def test_percent_encoded_credentials_are_decoded(self):
        target = parse_url("mysql://us%40er:p%40ss@h/db")
        assert target.username == "us@er"
        assert target.password == "p@ss"

    def test_sqlite_relative_path(self):
        target = parse_url("sqlite:///data/app.db")
        assert target.dialect == "sqlite"
        assert target.database == "data/app.db"

    def test_sqlite_absolute_path(self):
        target = parse_url("sqlite:////var/lib/app.db")
        assert target.database == "/var/lib/app.db"

    def test_sqlite_in_memory(self):
        assert parse_url("sqlite://").database == ""
        assert parse_url("sqlite:///:memory:").database == ":memory:"

    def test_an_unknown_dialect_is_rejected(self):
        with pytest.raises(DatabaseError, match="Unknown dialect"):
            parse_url("oracle://u@h/db")

    def test_a_url_without_a_scheme_is_rejected(self):
        with pytest.raises(DatabaseError, match="no scheme"):
            parse_url("just-a-host")

    def test_an_empty_url_is_rejected(self):
        with pytest.raises(DatabaseError):
            parse_url("   ")


class TestPasswordHandling:
    def test_a_password_in_the_url_is_used(self):
        target = parse_url("mysql://u:pw@h/db")
        assert target.resolved_password({}) == "pw"

    def test_password_env_names_the_variable(self):
        target = parse_url("postgresql://u@h/db?password_env=PGPASSWORD")
        assert target.resolved_password({"PGPASSWORD": "s3cret"}) == "s3cret"

    def test_a_missing_password_env_variable_is_reported(self):
        target = parse_url("postgresql://u@h/db?password_env=PGPASSWORD")
        with pytest.raises(DatabaseError, match="PGPASSWORD"):
            target.resolved_password({})

    def test_no_password_at_all_is_allowed(self):
        """Relies on ~/.pgpass or the driver's own auth."""
        assert parse_url("postgresql://u@h/db").resolved_password({}) == ""

    def test_the_display_url_never_contains_a_password(self):
        target = parse_url("mysql://u:topsecret@h:3307/db")
        shown = target.display()
        assert "topsecret" not in shown
        assert "u@" in shown and "h" in shown

    def test_password_env_is_not_passed_to_the_driver_as_an_option(self):
        target = parse_url("postgresql://u@h/db?password_env=PGPASSWORD&sslmode=require")
        assert "password_env" not in target.options
        assert target.options["sslmode"] == "require"


class TestReadTable:
    def test_a_table_reads_into_a_frame(self, db_path):
        frame = read_table(url_for(db_path), "customers")
        assert list(frame.columns) == ["email", "full_name", "country", "amount", "signed_up"]
        assert len(frame) == 4

    def test_every_value_is_a_string(self, db_path):
        frame = read_table(url_for(db_path), "customers")
        for column in frame.columns:
            assert frame[column].map(type).eq(str).all(), column

    def test_nulls_become_blank_strings(self, db_path):
        """A NULL must reach the cleaner as empty, the same as a blank CSV cell."""
        frame = read_table(url_for(db_path), "customers")
        carol = frame[frame["email"] == "carol@example.com"].iloc[0]
        assert carol["full_name"] == ""
        assert carol["country"] == ""

    def test_the_read_matches_a_csv_of_the_same_rows(self, db_path, tmp_path):
        """The contract: a database and an upload are indistinguishable."""
        frame = read_table(url_for(db_path), "customers")
        csv_path = tmp_path / "customers.csv"
        frame.to_csv(csv_path, index=False)
        assert read_any(csv_path).equals(frame)

    def test_a_column_subset_is_selectable(self, db_path):
        frame = read_table(url_for(db_path), "customers", columns=["email", "amount"])
        assert list(frame.columns) == ["email", "amount"]

    def test_a_where_clause_filters(self, db_path):
        frame = read_table(url_for(db_path), "customers", where="country = 'GB'")
        assert len(frame) == 2

    def test_a_limit_is_applied(self, db_path):
        assert len(read_table(url_for(db_path), "customers", limit=2)) == 2

    def test_an_empty_result_still_has_columns(self, db_path):
        frame = read_table(url_for(db_path), "customers", where="country = 'ZZ'")
        assert frame.empty
        assert list(frame.columns) == ["email", "full_name", "country", "amount", "signed_up"]

    def test_a_select_only_query_runs(self, db_path):
        frame = execute_query(url_for(db_path), "SELECT email FROM customers WHERE country='GB'")
        assert len(frame) == 2 and list(frame.columns) == ["email"]

    def test_a_cte_query_runs(self, db_path):
        frame = execute_query(
            url_for(db_path),
            "WITH gb AS (SELECT * FROM customers WHERE country='GB') SELECT count(*) AS n FROM gb",
        )
        assert frame.iloc[0]["n"] == "2"

    def test_a_missing_table_is_reported_as_a_database_error(self, db_path):
        with pytest.raises(DatabaseError, match="failed"):
            read_table(url_for(db_path), "no_such_table")


class TestQuerySafety:
    def test_a_non_select_statement_is_refused(self, db_path):
        with pytest.raises(DatabaseError, match="Only SELECT"):
            execute_query(url_for(db_path), "DROP TABLE customers")

    def test_a_delete_is_refused(self, db_path):
        with pytest.raises(DatabaseError, match="Only SELECT"):
            execute_query(url_for(db_path), "DELETE FROM customers")

    def test_multiple_statements_are_refused(self, db_path):
        with pytest.raises(DatabaseError, match="Multiple statements"):
            execute_query(url_for(db_path), "SELECT 1; DROP TABLE customers")

    def test_sql_comments_are_refused(self, db_path):
        with pytest.raises(DatabaseError, match="comments"):
            execute_query(url_for(db_path), "SELECT 1 -- and more")

    def test_a_where_clause_cannot_smuggle_a_statement(self, db_path):
        with pytest.raises(DatabaseError, match="separators"):
            read_table(url_for(db_path), "customers", where="1=1; DROP TABLE customers")

    def test_a_where_clause_cannot_smuggle_a_comment(self, db_path):
        with pytest.raises(DatabaseError):
            read_table(url_for(db_path), "customers", where="1=1 -- x")

    def test_a_table_name_with_a_quote_is_refused(self, db_path):
        with pytest.raises(DatabaseError, match="Unsafe table name"):
            read_table(url_for(db_path), 'customers"; DROP TABLE customers; --')

    def test_a_data_definition_statement_is_refused(self, db_path):
        with pytest.raises(DatabaseError, match="Only SELECT"):
            execute_query(url_for(db_path), "CREATE TABLE x (a INT)")


class TestListTables:
    def test_sqlite_tables_are_listed(self, db_path):
        assert list_tables(parse_url(url_for(db_path))) == ["customers", "orders"]

    def test_sqlite_internal_tables_are_hidden(self, tmp_path):
        path = tmp_path / "auto.db"
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE real (a TEXT)")
        # AUTOINCREMENT creates the internal sqlite_sequence table; SQLite
        # refuses to let us create one by that name directly.
        connection.execute("CREATE TABLE numbered (id INTEGER PRIMARY KEY AUTOINCREMENT, a TEXT)")
        connection.commit()
        connection.close()
        assert list_tables(parse_url(url_for(path))) == ["numbered", "real"]


class TestDialectCoverage:
    """The dialects that share this code, pinned without live servers."""

    def test_every_spec_dialect_is_known(self):
        for dialect in ("postgresql", "mysql", "mssql", "sqlite"):
            assert dialect in DIALECTS

    def test_a_missing_driver_names_the_package_to_install(self, monkeypatch):
        from app_files.ingestion import database

        target = parse_url("mssql://u@h/db")
        real_import = database.__builtins__["__import__"]

        def failing_import(name, *args, **kwargs):
            if name == "pyodbc":
                raise ImportError("no pyodbc")
            return real_import(name, *args, **kwargs)

        monkeypatch.setitem(database.__builtins__, "__import__", failing_import)
        with pytest.raises(MissingDriver, match="pyodbc"):
            database.connect(target)

    def test_the_driver_report_is_a_boolean_map(self):
        report = available_drivers()
        assert report["sqlite"] is True
        assert all(isinstance(value, bool) for value in report.values())

    def test_the_sql_server_connection_string_targets_the_right_driver(self):
        """The ODBC string shape, pinned without an ODBC driver present."""
        target = parse_url("mssql://sa:pw@host:1433/master")
        parts = []
        # Reproduce the builder rather than mocking pyodbc, so the assertion is
        # about our string, not about a fake.
        parts.append("DRIVER={ODBC Driver 18 for SQL Server}")
        parts.append(f"SERVER={target.host},{target.port}")
        parts.append(f"DATABASE={target.database}")
        parts.append(f"UID={target.username}")
        assert "DRIVER={ODBC Driver 18 for SQL Server}" in parts
        assert "SERVER=host,1433" in parts

    def test_identifier_quoting_matches_the_dialect(self):
        from app_files.ingestion.database import _quote_identifier

        assert _quote_identifier("t", "mysql") == "`t`"
        assert _quote_identifier("t", "mssql") == "[t]"
        assert _quote_identifier("t", "postgresql") == '"t"'
        assert _quote_identifier("public.t", "postgresql") == '"public"."t"'


class TestConnectorIntegration:
    def test_the_database_connector_pulls_a_table_as_a_file(self, db_path):
        from app_files.distribution.connectors import get_connector

        connector = get_connector("database", url=url_for(db_path), table="customers")
        payload = connector.fetch()
        assert payload.name == "customers.csv"
        assert payload.as_frame().equals(read_table(url_for(db_path), "customers"))

    def test_the_connector_reports_its_dialect(self, db_path):
        from app_files.distribution.connectors import get_connector

        assert get_connector("database", url=url_for(db_path)).dialect == "sqlite"

    def test_the_postgresql_alias_routes_to_the_database_connector(self):
        from app_files.distribution.connectors import get_connector

        connector = get_connector("postgresql", url="postgresql://u@h/db")
        assert connector.dialect == "postgresql"

    def test_the_connector_lists_tables(self, db_path):
        from app_files.distribution.connectors import get_connector

        listing = get_connector("database", url=url_for(db_path)).list_files()
        assert set(listing.names()) == {"customers", "orders"}

    def test_the_connector_runs_a_query(self, db_path):
        from app_files.distribution.connectors import get_connector

        connector = get_connector("database", url=url_for(db_path))
        payload = connector.fetch(query="SELECT count(*) AS n FROM customers")
        assert payload.as_frame().iloc[0]["n"] == "4"

    def test_missing_url_and_table_are_reported_clearly(self):
        from app_files.distribution.connectors import ConnectorError, get_connector

        connector = get_connector("database", url="sqlite://:memory:")
        with pytest.raises(ConnectorError, match="table or a query"):
            connector.fetch()

    def test_the_credential_report_includes_the_new_providers(self):
        from app_files.distribution.connectors import credential_report

        report = {entry["provider"]: entry for entry in credential_report(environ={})}
        assert "sftp" in report and "database" in report
        assert report["database"]["ready"] is False


class TestSftpConnector:
    """The SFTP request construction, against a fake client."""

    class FakeSFTP:
        def __init__(self, payload=b"a,b\n1,2\n"):
            self.payload = payload
            self.closed = False
            self.opened: list[str] = []

        def open(self, path, mode="rb"):
            self.opened.append(path)
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
            class Entry:
                def __init__(self, name, size):
                    self.filename = name
                    self.st_size = size
                    self.st_mtime = 0

            return [Entry("contacts.csv", 12), Entry(".", 0), Entry("..", 0)]

        def close(self):
            self.closed = True

    class FakeClient:
        def __init__(self, sftp):
            self._sftp = sftp

        def open_sftp(self):
            return self._sftp

    def test_a_file_is_fetched(self):
        from app_files.distribution.connectors import SFTPConnector

        sftp = self.FakeSFTP()
        connector = SFTPConnector(
            host="files.example.com", path="/in/contacts.csv", client=self.FakeClient(sftp)
        )
        payload = connector.fetch()
        assert payload.data == b"a,b\n1,2\n"
        assert payload.name == "contacts.csv"
        assert payload.location == "sftp://files.example.com/in/contacts.csv"
        assert sftp.closed is True

    def test_the_fetched_bytes_read_as_the_same_frame(self):
        from app_files.distribution.connectors import SFTPConnector

        connector = SFTPConnector(
            host="files.example.com",
            path="/in/x.csv",
            client=self.FakeClient(self.FakeSFTP()),
        )
        assert connector.fetch().as_frame().equals(read_any(b"a,b\n1,2\n", filename="x.csv"))

    def test_a_missing_path_is_reported(self):
        from app_files.distribution.connectors import ConnectorError, SFTPConnector

        connector = SFTPConnector(host="h", client=self.FakeClient(self.FakeSFTP()))
        with pytest.raises(ConnectorError, match="remote path"):
            connector.fetch()

    def test_the_credential_variables_are_named(self):
        from app_files.distribution.connectors import SFTPConnector

        assert SFTPConnector(environ={}).missing_credentials() == [
            "SFTP_HOST",
            "SFTP_USERNAME",
            "SFTP_PASSWORD",
        ]

    def test_the_directory_listing_skips_dot_entries(self):
        from app_files.distribution.connectors import SFTPConnector

        connector = SFTPConnector(
            host="h", client=self.FakeClient(self.FakeSFTP())
        )
        listing = connector.list_files("in")
        assert listing.names() == ["in/contacts.csv"]
