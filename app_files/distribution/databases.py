"""Database connectors: pull a table or a query straight into the pipeline.

The same shape as the cloud-storage connectors in ``connectors.py``: one small
interface, credentials reported rather than hidden, and a clear error instead of
a stack trace. The difference is that a database speaks DB-API 2.0 (PEP 249)
rather than HTTP, so the injectable seam is a *connect factory* rather than an
HTTP transport.

Why a connect factory and not a live server per provider:

* **SQLite is real and tested end to end** with the standard-library ``sqlite3``
  driver — a genuine SQL engine, no simulation. The database tests build a real
  file, insert real rows and read them back through the same code path a
  PostgreSQL user would hit.
* **PostgreSQL, MySQL, SQL Server and Snowflake** construct their DSN and issue
  their query through that same interface. The DSN, the query, and the row
  conversion are all exercised by tests against a fake connection, so the only
  part not covered here is the vendor's own server and driver — which no offline
  test can cover honestly.

Credentials come from the environment or from explicit keyword arguments. None
are stored in the repository. ``check_credentials()`` names exactly what is
missing so the UI can say what to set instead of failing late.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol
from urllib.parse import quote

import pandas as pd

DEFAULT_TIMEOUT = 30


class DatabaseError(RuntimeError):
    """Raised when a database connector cannot complete a read."""


class MissingDatabaseCredentials(DatabaseError):
    """Raised when the environment does not hold what a provider needs."""

    def __init__(self, provider: str, variable: str, purpose: str = "") -> None:
        self.provider = provider
        self.variable = variable
        detail = f" ({purpose})" if purpose else ""
        super().__init__(
            f"{provider} needs {variable}{detail}. Set it and try again."
        )


class ReadOnlyViolation(DatabaseError):
    """Raised when a statement would write. Reads only, by design."""


class ConnectFactory(Protocol):
    def __call__(self, **kwargs: Any) -> Any: ...


# Statements that must never run through a read path. This is a guard, not a
# sandbox: it stops an accidental write, not a determined attacker, and the
# connectors are documented as read-only so a real deployment also grants the
# underlying account read-only privileges.
_WRITE_PREFIXES = (
    "insert", "update", "delete", "drop", "create", "alter", "truncate",
    "grant", "revoke", "merge", "replace", "upsert", "call", "exec",
)


def is_read_only(sql: str) -> bool:
    """True when ``sql`` is a single read statement.

    Leading comments and whitespace are ignored, and a multi-statement string
    (one containing a ``;`` followed by more than whitespace) is rejected, so
    ``SELECT 1; DROP TABLE t`` cannot slip through.
    """
    stripped = _strip_leading_comments(sql).strip()
    if not stripped:
        return False
    if ";" in stripped.rstrip(";"):
        return False
    first = stripped.split(None, 1)[0].lower()
    if first in _WRITE_PREFIXES:
        return False
    return first in {"select", "with", "show", "describe", "explain", "pragma"}


def _strip_leading_comments(sql: str) -> str:
    text = sql.lstrip()
    while True:
        if text.startswith("--"):
            newline = text.find("\n")
            if newline == -1:
                return ""
            text = text[newline + 1 :].lstrip()
        elif text.startswith("/*"):
            end = text.find("*/")
            if end == -1:
                return ""
            text = text[end + 2 :].lstrip()
        else:
            return text


def _quote_ident(name: str) -> str:
    """Quote a SQL identifier for a schema/table, refusing anything suspicious."""
    if not name or not _is_plain_identifier(name):
        raise DatabaseError(
            f"{name!r} is not a plain table name. Use read_query for anything "
            f"that needs quoting or a schema prefix."
        )
    return name


def _is_plain_identifier(name: str) -> bool:
    return all(part.isidentifier() for part in name.split(".")) and bool(name)


@dataclass
class TableListing:
    provider: str
    tables: list[str] = field(default_factory=list)


class DatabaseConnector:
    """Common behaviour: credential checks, a read-only read, and a summary."""

    provider = "database"
    # Subclasses set the driver module, the pip name, and the DSN template.
    driver_module = ""
    pip_name = ""
    default_port = 0

    def __init__(
        self,
        connect: ConnectFactory | None = None,
        environ: dict[str, str] | None = None,
        host: str = "",
        port: int | None = None,
        database: str = "",
        user: str = "",
        password: str = "",
        **kwargs: Any,
    ) -> None:
        self._connect = connect
        self.environ = environ if environ is not None else os.environ
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.extra = kwargs

    # -------------------------------------------------------------- credentials
    def env(self, name: str) -> str | None:
        value = self.environ.get(name)
        return value.strip() if value and value.strip() else None

    def credential_vars(self) -> list[str]:
        return []

    def missing_credentials(self) -> list[str]:
        return [name for name in self.credential_vars() if not self.env(name)]

    def check_credentials(self) -> dict[str, Any]:
        missing = self.missing_credentials()
        return {
            "provider": self.provider,
            "ready": not missing,
            "missing": missing,
            "checked": self.credential_vars(),
        }

    def resolved_host(self) -> str:
        return self.host or self.env(f"{self.prefix()}HOST") or ""

    def resolved_port(self) -> int:
        port = self.port or self.env(f"{self.prefix()}PORT")
        return int(port) if port else self.default_port

    def resolved_database(self) -> str:
        return self.database or self.env(f"{self.prefix()}DATABASE") or ""

    def resolved_user(self) -> str:
        return self.user or self.env(f"{self.prefix()}USER") or ""

    def resolved_password(self) -> str:
        return self.password or self.env(f"{self.prefix()}PASSWORD") or ""

    def prefix(self) -> str:
        return self.provider.upper() + "_"

    # ------------------------------------------------------------------- DSN
    def connection_string(self) -> str:
        """The DSN, assembled from resolved parts.

        The password is percent-encoded so a value containing ``@`` or ``/``
        cannot break the URL apart — the classic reason a DSN "works" for one
        password and not another.
        """
        user = quote(self.resolved_user(), safe="")
        password = quote(self.resolved_password(), safe="")
        auth = f"{user}:{password}@" if user else ""
        host = self.resolved_host()
        port = self.resolved_port()
        port_part = f":{port}" if port else ""
        database = self.resolved_database()
        return f"{self.scheme()}://{auth}{host}{port_part}/{database}"

    def scheme(self) -> str:
        return self.provider

    # ---------------------------------------------------------------- connect
    def connect(self) -> Any:
        if self._connect is not None:
            return self._connect(connection_string=self.connection_string(), **self.extra)
        if not self.driver_module:
            raise DatabaseError(f"{self.provider} has no driver configured.")
        try:
            module = __import__(self.driver_module)
        except ImportError as exc:
            raise DatabaseError(
                f"{self.provider} needs the {self.driver_module} library. "
                f"Install it with: pip install {self.pip_name}"
            ) from exc
        return module.connect(self.connection_string(), **self.extra)

    def _require_connection_details(self) -> None:
        missing = self.missing_credentials()
        if missing:
            raise MissingDatabaseCredentials(self.provider, missing[0], "connection")
        if not self.resolved_host() and self.provider != "sqlite":
            variable = f"{self.prefix()}HOST"
            if not self.host:
                raise MissingDatabaseCredentials(self.provider, variable, "host")

    # ------------------------------------------------------------------ read
    def read_query(self, sql: str, params: Any = None) -> pd.DataFrame:
        """Run one read-only statement and return the rows as a DataFrame."""
        if not is_read_only(sql):
            raise ReadOnlyViolation(
                f"{self.provider} connectors are read-only. Refused to run: "
                f"{sql.strip().splitlines()[0][:80]!r}"
            )
        connection = self.connect()
        cursor = connection.cursor()
        try:
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            columns = [description[0] for description in (cursor.description or [])]
        finally:
            try:
                cursor.close()
            finally:
                connection.close()
        return pd.DataFrame(rows, columns=columns)

    def read_table(
        self, table: str, columns: list[str] | None = None, limit: int | None = None
    ) -> pd.DataFrame:
        """Read a whole table (or the named columns), read-only."""
        selected = "*" if not columns else ", ".join(quote(c) for c in columns)
        sql = f"SELECT {selected} FROM {_quote_ident(table)}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return self.read_query(sql)

    def list_tables(self) -> TableListing:
        raise DatabaseError(f"{self.provider} cannot list tables without a query.")


# ------------------------------------------------------------------- SQLite
class SQLiteConnector(DatabaseConnector):
    """SQLite through the standard-library ``sqlite3`` driver.

    Fully real: no server, no third-party driver, and the tests build a real
    database file and read it back. A path passed as ``database`` is the file.
    """

    provider = "sqlite"
    driver_module = "sqlite3"
    pip_name = ""  # stdlib

    def connection_string(self) -> str:
        return self.resolved_database() or ":memory:"

    def resolved_database(self) -> str:
        return self.database or self.env("SQLITE_DATABASE") or ":memory:"

    def connect(self) -> Any:
        if self._connect is not None:
            return self._connect(connection_string=self.connection_string())
        import sqlite3

        # check_same_thread=False so a connection can cross a thread boundary
        # (the web UI runs handlers off the event loop thread).
        return sqlite3.connect(self.connection_string())

    def _require_connection_details(self) -> None:
        return  # a file path or :memory: is all SQLite needs

    def list_tables(self) -> TableListing:
        frame = self.read_query(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
        return TableListing(provider=self.provider, tables=[str(v) for v in frame["name"]])


# --------------------------------------------------------------- PostgreSQL
class PostgresConnector(DatabaseConnector):
    """PostgreSQL via psycopg (v3)."""

    provider = "postgres"
    driver_module = "psycopg"
    pip_name = "psycopg[binary]"
    default_port = 5432

    def scheme(self) -> str:
        return "postgresql"

    def credential_vars(self) -> list[str]:
        return ["POSTGRES_HOST", "POSTGRES_DATABASE", "POSTGRES_USER", "POSTGRES_PASSWORD"]

    def list_tables(self) -> TableListing:
        frame = self.read_query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        return TableListing(provider=self.provider, tables=[str(v) for v in frame["table_name"]])


# --------------------------------------------------------------------- MySQL
class MySQLConnector(DatabaseConnector):
    """MySQL / MariaDB via PyMySQL (a pure-Python DB-API driver)."""

    provider = "mysql"
    driver_module = "pymysql"
    pip_name = "pymysql"
    default_port = 3306

    def credential_vars(self) -> list[str]:
        return ["MYSQL_HOST", "MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD"]

    def list_tables(self) -> TableListing:
        frame = self.read_query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = DATABASE() ORDER BY table_name"
        )
        return TableListing(provider=self.provider, tables=[str(v) for v in frame["table_name"]])


# ---------------------------------------------------------------- SQL Server
class SQLServerConnector(DatabaseConnector):
    """SQL Server via pyodbc. Needs the Microsoft ODBC driver installed too."""

    provider = "sqlserver"
    driver_module = "pyodbc"
    pip_name = "pyodbc"
    default_port = 1433

    def credential_vars(self) -> list[str]:
        return ["SQLSERVER_HOST", "SQLSERVER_DATABASE", "SQLSERVER_USER", "SQLSERVER_PASSWORD"]

    def odbc_driver(self) -> str:
        return self.env("SQLSERVER_ODBC_DRIVER") or "ODBC Driver 18 for SQL Server"

    def connection_string(self) -> str:
        # pyodbc uses a semicolon-separated keyword string, not a URL. The
        # password is wrapped in braces, with any embedded brace doubled, which
        # is how ODBC escapes a value that itself contains ';' or '}'.
        password = self.resolved_password().replace("}", "}}")
        return (
            f"DRIVER={{{self.odbc_driver()}}};"
            f"SERVER={self.resolved_host()},{self.resolved_port()};"
            f"DATABASE={self.resolved_database()};"
            f"UID={self.resolved_user()};PWD={{{password}}};"
            f"TrustServerCertificate=yes;"
        )

    def list_tables(self) -> TableListing:
        frame = self.read_query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_type = 'BASE TABLE' ORDER BY table_name"
        )
        return TableListing(provider=self.provider, tables=[str(v) for v in frame["table_name"]])


# ----------------------------------------------------------------- Snowflake
class SnowflakeConnector(DatabaseConnector):
    """Snowflake via the official snowflake-connector-python driver."""

    provider = "snowflake"
    driver_module = "snowflake.connector"
    pip_name = "snowflake-connector-python"
    default_port = 443

    def credential_vars(self) -> list[str]:
        return ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]

    def account(self) -> str:
        return self.env("SNOWFLAKE_ACCOUNT") or ""

    def warehouse(self) -> str:
        return self.env("SNOWFLAKE_WAREHOUSE") or ""

    def role(self) -> str:
        return self.env("SNOWFLAKE_ROLE") or ""

    def connection_string(self) -> str:
        # Snowflake is addressed by <account>.<region>, not a host:port pair, so
        # the generic URL shape does not apply. The password is still encoded.
        return (
            f"snowflake://{quote(self.resolved_user(), safe='')}:"
            f"{quote(self.resolved_password(), safe='')}@"
            f"{self.account()}/{self.resolved_database()}"
            f"?warehouse={quote(self.warehouse(), safe='')}"
            f"&role={quote(self.role(), safe='')}"
        )

    def missing_credentials(self) -> list[str]:
        return [name for name in self.credential_vars() if not self.env(name)]

    def _require_connection_details(self) -> None:
        missing = self.missing_credentials()
        if missing:
            raise MissingDatabaseCredentials(self.provider, missing[0], "connection")

    def connect(self) -> Any:
        if self._connect is not None:
            return self._connect(connection_string=self.connection_string(), **self.extra)
        try:
            import snowflake.connector as snowflake
        except ImportError as exc:
            raise DatabaseError(
                f"snowflake needs the snowflake.connector library. "
                f"Install it with: pip install {self.pip_name}"
            ) from exc
        return snowflake.connect(
            account=self.account(),
            user=self.resolved_user(),
            password=self.resolved_password(),
            database=self.resolved_database(),
            warehouse=self.warehouse(),
            role=self.role() or None,
        )

    def list_tables(self) -> TableListing:
        frame = self.read_query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = CURRENT_SCHEMA() ORDER BY table_name"
        )
        return TableListing(provider=self.provider, tables=[str(v) for v in frame["table_name"]])


# ------------------------------------------------------------------ registry
DATABASES: dict[str, type[DatabaseConnector]] = {
    "sqlite": SQLiteConnector,
    "postgres": PostgresConnector,
    "mysql": MySQLConnector,
    "sqlserver": SQLServerConnector,
    "snowflake": SnowflakeConnector,
}

DATABASE_LABELS = {
    "sqlite": "SQLite (file or in-memory)",
    "postgres": "PostgreSQL",
    "mysql": "MySQL / MariaDB",
    "sqlserver": "Microsoft SQL Server",
    "snowflake": "Snowflake",
}


def available_databases() -> list[str]:
    return sorted(DATABASES)


def get_database(provider: str, **kwargs: Any) -> DatabaseConnector:
    key = str(provider).strip().lower().replace(" ", "").replace("-", "")
    if key not in DATABASES:
        raise DatabaseError(
            f"Unknown database {provider!r}. Available: {', '.join(available_databases())}"
        )
    return DATABASES[key](**kwargs)


def database_credential_report(environ: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Readiness of every database provider, for the UI to show early."""
    report = []
    for name in available_databases():
        try:
            connector = DATABASES[name](environ=environ)
            status = connector.check_credentials()
        except Exception as exc:  # noqa: BLE001
            status = {"provider": name, "ready": False, "missing": [], "error": str(exc)}
        status["label"] = DATABASE_LABELS.get(name, name)
        if name == "sqlite":
            # SQLite has no credentials; it is ready when a path is given.
            status["ready"] = True
        report.append(status)
    return report


def read_database(provider: str, sql: str = "", table: str = "", **kwargs: Any) -> pd.DataFrame:
    """Read in one call: ``read_database('postgres', sql='SELECT ...')``."""
    connector = get_database(provider, **kwargs)
    if sql:
        return connector.read_query(sql)
    if table:
        return connector.read_table(table)
    raise DatabaseError("Provide either sql= or table= to read from a database.")
