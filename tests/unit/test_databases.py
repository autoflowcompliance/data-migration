"""Database connectors, tested where it is honest to test them.

SQLite is exercised end to end: a real database file is created, rows are
inserted, and they are read back through the same ``read_query``/``read_table``
path every other provider uses. That is a genuine SQL engine, not a stand-in.

The server-based providers (PostgreSQL, MySQL, SQL Server, Snowflake) cannot be
reached offline, so what is tested is everything this repository is responsible
for: the DSN it builds, the statement it issues, the row-to-DataFrame
conversion, and the refusals. The vendor's server and driver are out of scope
and are not pretended otherwise.
"""

from __future__ import annotations

import sqlite3

import pytest

from app_files.distribution.databases import (
    DATABASES,
    DatabaseError,
    MissingDatabaseCredentials,
    ReadOnlyViolation,
    available_databases,
    database_credential_report,
    get_database,
    is_read_only,
    read_database,
)


# --------------------------------------------------------------- read-only SQL
@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1",
        "select * from contacts",
        "  SELECT * FROM t",
        "-- a comment\nSELECT * FROM t",
        "/* block */ SELECT * FROM t",
        "WITH x AS (SELECT 1) SELECT * FROM x",
        "SHOW TABLES",
    ],
)
def test_read_statements_are_allowed(sql):
    assert is_read_only(sql) is True


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE contacts",
        "DELETE FROM contacts",
        "INSERT INTO t VALUES (1)",
        "UPDATE t SET a = 1",
        "TRUNCATE t",
        "SELECT 1; DROP TABLE t",  # multi-statement smuggling
        "-- c\nDROP TABLE t",
        "",
        "   ",
    ],
)
def test_write_and_smuggling_statements_are_refused(sql):
    assert is_read_only(sql) is False


def test_read_query_refuses_a_write(tmp_path):
    connector = get_database("sqlite", database=str(tmp_path / "x.db"))
    with pytest.raises(ReadOnlyViolation):
        connector.read_query("DROP TABLE contacts")
    with pytest.raises(ReadOnlyViolation):
        connector.read_query("SELECT 1; DROP TABLE contacts")


# ------------------------------------------------------------------- SQLite E2E
def _make_sqlite(path):
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE contacts (firstname TEXT, email TEXT, amount REAL)"
    )
    connection.executemany(
        "INSERT INTO contacts VALUES (?, ?, ?)",
        [("Ann", "ann@x.com", 10.5), ("Bob", "bob@x.com", 20.0), ("Cara", "", 0.0)],
    )
    connection.commit()
    connection.close()


def test_sqlite_reads_a_real_table(tmp_path):
    path = tmp_path / "real.db"
    _make_sqlite(path)

    frame = read_database("sqlite", table="contacts", database=str(path))
    assert list(frame.columns) == ["firstname", "email", "amount"]
    assert len(frame) == 3
    assert frame["firstname"].tolist() == ["Ann", "Bob", "Cara"]


def test_sqlite_read_query_with_columns_and_limit(tmp_path):
    path = tmp_path / "real.db"
    _make_sqlite(path)
    connector = get_database("sqlite", database=str(path))

    frame = connector.read_table("contacts", columns=["email"], limit=2)
    assert list(frame.columns) == ["email"]
    assert len(frame) == 2

    filtered = connector.read_query(
        "SELECT firstname FROM contacts WHERE amount > ?", (15.0,)
    )
    assert filtered["firstname"].tolist() == ["Bob"]


def test_sqlite_lists_real_tables(tmp_path):
    path = tmp_path / "real.db"
    _make_sqlite(path)
    listing = get_database("sqlite", database=str(path)).list_tables()
    assert listing.tables == ["contacts"]


def test_sqlite_reads_feed_the_pipeline(tmp_path, samples_dir):
    """The frame a database read returns runs through run_pipeline unchanged."""
    from app_files.pipeline import run_pipeline

    path = tmp_path / "contacts.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE contacts (\"First Name\" TEXT, \"Email Address\" TEXT)")
    connection.executemany(
        "INSERT INTO contacts VALUES (?, ?)",
        [("Ann", "ANN@x.com"), ("Bob", "bob@x.com")],
    )
    connection.commit()
    connection.close()

    frame = read_database("sqlite", table="contacts", database=str(path))
    result = run_pipeline(frame, crm="hubspot")
    assert list(result.clean_frame["email"]) == ["ann@x.com", "bob@x.com"]


# ------------------------------------------------- DSNs for server providers
def test_postgres_dsn_encodes_the_password():
    connector = get_database(
        "postgres",
        host="db.internal", port=5432, database="crm",
        user="svc", password="p@ss/word:x",
    )
    dsn = connector.connection_string()
    assert dsn.startswith("postgresql://svc:")
    assert "p%40ss%2Fword%3Ax" in dsn
    assert dsn.endswith("@db.internal:5432/crm")


def test_mysql_and_sqlserver_and_snowflake_dsn_shapes():
    mysql = get_database("mysql", host="h", database="d", user="u", password="p")
    assert mysql.connection_string() == "mysql://u:p@h:3306/d"

    sqlserver = get_database("sqlserver", host="h", database="d", user="u", password="p")
    assert sqlserver.connection_string().startswith("DRIVER={ODBC Driver 18 for SQL Server};")
    assert "SERVER=h,1433;" in sqlserver.connection_string()

    snowflake = get_database(
        "snowflake", database="d", user="u", password="p",
        environ={"SNOWFLAKE_ACCOUNT": "acct", "SNOWFLAKE_WAREHOUSE": "wh"},
    )
    assert snowflake.connection_string().startswith("snowflake://u:p@acct/d?warehouse=wh")


def test_sqlserver_password_with_brace_is_escaped():
    connector = get_database(
        "sqlserver", host="h", database="d", user="u", password="a}b"
    )
    assert "PWD={a}}b}" in connector.connection_string()


def test_missing_credentials_are_named():
    connector = get_database("postgres", environ={})
    status = connector.check_credentials()
    assert status["ready"] is False
    assert "POSTGRES_PASSWORD" in status["missing"]


# ---------------------------------------------- provider-agnostic read path
class _FakeCursor:
    def __init__(self):
        self.description = [("id",), ("name",)]
        self.executed = None

    def execute(self, sql, params):
        self.executed = (sql, params)

    def fetchall(self):
        return [(1, "Ann"), (2, "Bob")]

    def close(self):
        pass


class _FakeConnection:
    def __init__(self):
        self.cur = _FakeCursor()
        self.closed = False

    def cursor(self):
        return self.cur

    def close(self):
        self.closed = True


def test_server_provider_reads_through_the_injected_connection():
    """A server provider uses the same read path and issues the right SQL."""
    connection = _FakeConnection()
    connector = get_database(
        "postgres", database="crm",
        connect=lambda **kwargs: connection,
        environ={},
    )
    frame = connector.read_query("SELECT id, name FROM contacts")
    assert frame["name"].tolist() == ["Ann", "Bob"]
    assert connection.cur.executed[0].lower().startswith("select id, name")
    assert connection.closed is True


def test_read_table_quotes_columns_and_applies_limit():
    connection = _FakeConnection()
    connector = get_database("mysql", connect=lambda **kwargs: connection, environ={})
    connector.read_table("contacts", columns=["id", "name"], limit=5)
    sql = connection.cur.executed[0]
    assert "SELECT id, name FROM contacts" in sql
    assert sql.endswith("LIMIT 5")


def test_read_table_rejects_a_non_identifier():
    connector = get_database("sqlite", database=":memory:")
    with pytest.raises(DatabaseError):
        connector.read_table("contacts; DROP TABLE t")


# --------------------------------------------------------------- registry
def test_registry_has_the_five_providers():
    assert set(available_databases()) == {"sqlite", "postgres", "mysql", "sqlserver", "snowflake"}


def test_unknown_database_is_rejected():
    with pytest.raises(DatabaseError):
        get_database("oracle", environ={})


def test_credential_report_covers_every_provider():
    report = database_credential_report(environ={})
    assert len(report) == 5
    by_name = {entry["provider"]: entry for entry in report}
    assert by_name["sqlite"]["ready"] is True
    assert by_name["postgres"]["ready"] is False


def test_database_driver_gap_names_the_pip_package():
    """A missing driver is a clear install hint, not an ImportError traceback."""
    connector = get_database("postgres", host="h", database="d", user="u", password="p")
    with pytest.raises(DatabaseError) as caught:
        connector.connect()

    # Either the driver is installed (and connect fails for another reason) or
    # the message names the install. Only the latter is guaranteed offline.
    if "library" in str(caught.value):
        assert "pip install" in str(caught.value)