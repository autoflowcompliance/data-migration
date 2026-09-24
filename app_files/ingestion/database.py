"""Direct database reads: PostgreSQL, MySQL, SQL Server and SQLite.

A connector that returns the same normalized DataFrame the file reader returns,
so nothing downstream knows the difference between a CSV upload and a table
read. That is the whole contract, and the tests hold it: the same rows read
from a real SQLite database and from a CSV of those rows produce frames that
compare equal.

Design decisions that matter:

* **No SQLAlchemy.** The drivers already exist and every one of them is
  DB-API 2.0. Adding an ORM layer to run ``SELECT * FROM t`` would be weight
  without benefit. A URL is parsed into a DB-API connect call.
* **Values are stringified, not typed.** The file adapters return strings; a
  database connector that returned ints would make the cleaner behave
  differently on the same logical data. Every value is converted the same way
  the adapter does it, so ``123`` and ``"123"`` reach the cleaner identically.
  This also sidesteps the SQL numeric-affinity trap entirely: nothing is ever
  handed to pandas as a number in the first place.
* **A password is never required to be in the URL.** Committing a connection
  string with a password into a config file is how credentials leak. A URL may
  name an environment variable (``password_env=PGPASSWORD``) or rely on the
  driver's own environment/file-based auth (``~/.pgpass``, MySQL option files,
  ``~/.my.cnf``).
* **SQL Server and MySQL need their driver.** If it is absent, the error names
  the package to install rather than raising ``ImportError`` from three frames
  down.
* **SQLite is the real, tested path.** It is in the standard library, so the
  whole connector — URL parsing, query construction, cursor iteration,
  stringification — runs against a genuine database in the suite. The other
  three dialects share that code and differ only in the dialect module name and
  placeholder style, which the tests pin.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import pandas as pd


class DatabaseError(RuntimeError):
    """Raised when a database cannot be read."""


class MissingDriver(DatabaseError):
    """The DB-API driver for this dialect is not installed."""

    def __init__(self, dialect: str, module: str, package: str) -> None:
        self.dialect = dialect
        self.module = module
        self.package = package
        super().__init__(
            f"{dialect} needs the driver '{package}'. Install it with "
            f"`pip install {package}` and try again."
        )


#: dialect -> (DB-API module, pip package, default port)
DIALECTS: dict[str, tuple[str, str, int]] = {
    "postgresql": ("psycopg2", "psycopg2-binary", 5432),
    "postgres": ("psycopg2", "psycopg2-binary", 5432),
    "mysql": ("pymysql", "PyMySQL", 3306),
    "mariadb": ("pymysql", "PyMySQL", 3306),
    "mssql": ("pyodbc", "pyodbc", 1433),
    "sqlserver": ("pyodbc", "pyodbc", 1433),
    "sqlite": (":stdlib:", "sqlite3", 0),
    "duckdb": ("duckdb", "duckdb", 0),
}


@dataclass
class DatabaseTarget:
    """A parsed connection URL, without the password resolved."""

    dialect: str
    host: str = ""
    port: int = 0
    username: str = ""
    database: str = ""
    password: str = ""
    options: dict[str, str] = field(default_factory=dict)
    password_env: str = ""

    @property
    def driver_module(self) -> str:
        return DIALECTS[self.dialect][0]

    @property
    def driver_package(self) -> str:
        return DIALECTS[self.dialect][1]

    def resolved_password(self, environ: dict[str, str] | None = None) -> str:
        """The password, from the URL or the named environment variable.

        The environment variable is deliberately the only fallback, and it is
        named in the URL rather than guessed: scanning a list of conventional
        variable names turns a typo into a silent connection attempt as the
        wrong user.
        """
        if self.password:
            return self.password
        if self.password_env:
            value = (environ or os.environ).get(self.password_env)
            if value:
                return value
            raise DatabaseError(
                f"password_env={self.password_env} names an environment variable "
                f"that is not set."
            )
        return ""

    def display(self) -> str:
        """A URL safe to log: no password, whatever its source."""
        base = f"{self.dialect}://"
        if self.username:
            base += f"{self.username}@"
        base += self.host or self.database
        if self.port and self.dialect not in ("sqlite", "duckdb"):
            base += f":{self.port}"
        return base


def parse_url(url: str) -> DatabaseTarget:
    """Parse a database URL into a :class:`DatabaseTarget`.

    Accepted forms::

        postgresql://user@host:5432/dbname?password_env=PGPASSWORD
        mysql://user:pass@host/dbname
        mssql+pyodbc://user@host/dbname
        sqlite:///relative/path.db
        sqlite:////absolute/path.db
        duckdb:///path.duckdb
    """
    raw = str(url).strip()
    if not raw:
        raise DatabaseError("Empty database URL.")
    if "://" not in raw:
        raise DatabaseError(
            f"Database URL {raw!r} has no scheme. Expected e.g. "
            f"postgresql://user@host/dbname."
        )
    scheme, _, remainder = raw.partition("://")
    dialect = scheme.split("+", 1)[0].lower()
    if dialect not in DIALECTS:
        raise DatabaseError(
            f"Unknown dialect {dialect!r}. Known: {', '.join(sorted(DIALECTS))}"
        )

    if dialect in ("sqlite", "duckdb"):
        # SQLAlchemy's convention, and the one users already know:
        #   sqlite:///relative.db    -> remainder "/relative.db"    -> relative
        #   sqlite:////absolute.db   -> remainder "//absolute.db"    -> absolute
        #   sqlite://:memory:        -> remainder ":memory:"         -> in-memory
        # So exactly one leading slash is the separator, and anything beyond it
        # is part of the path. Stripping both slashes turns an absolute path
        # into a relative one and silently opens (or creates) the wrong file.
        path = remainder.split("?", 1)[0]
        query = parse_qs(remainder.split("?", 1)[1]) if "?" in remainder else {}
        database = unquote(path[1:]) if path.startswith("/") else unquote(path)
        return DatabaseTarget(
            dialect=dialect,
            database=database,
            options={key: value[0] for key, value in query.items()},
        )

    parsed = urlparse(raw)
    query = {key: value[0] for key, value in parse_qs(parsed.query).items()}
    password_env = query.pop("password_env", "")
    database = parsed.path.lstrip("/") if parsed.path else ""
    default_port = DIALECTS[dialect][2]
    return DatabaseTarget(
        dialect=dialect,
        host=parsed.hostname or "",
        port=parsed.port or default_port,
        username=unquote(parsed.username) if parsed.username else "",
        database=unquote(database),
        password=unquote(parsed.password) if parsed.password else "",
        options=query,
        password_env=password_env,
    )


def connect(target: DatabaseTarget, environ: dict[str, str] | None = None):
    """Open a DB-API connection for ``target``.

    SQLite is the standard library. Everything else is imported by name, with
    the missing driver reported as an install instruction.
    """
    password = target.resolved_password(environ)
    if target.dialect == "sqlite":
        path = target.database
        if path not in (":memory:", ""):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(path or ":memory:")

    module_name = target.driver_module
    try:
        module = __import__(module_name)
    except ImportError as exc:
        raise MissingDriver(target.dialect, module_name, target.driver_package) from exc

    if module_name == "psycopg2":
        return module.connect(
            host=target.host,
            port=target.port,
            user=target.username,
            password=password,
            dbname=target.database,
            **{key: value for key, value in target.options.items() if key != "password_env"},
        )
    if module_name == "pymysql":
        return module.connect(
            host=target.host,
            port=target.port,
            user=target.username,
            password=password,
            database=target.database,
            **{key: value for key, value in target.options.items() if key != "password_env"},
        )
    if module_name == "pyodbc":
        parts = [
            "DRIVER={ODBC Driver 18 for SQL Server}",
            f"SERVER={target.host},{target.port}",
        ]
        if target.database:
            parts.append(f"DATABASE={target.database}")
        if target.username:
            parts.append(f"UID={target.username}")
        if password:
            parts.append(f"PWD={password}")
        parts.append("TrustServerCertificate=yes")
        return module.connect(";".join(parts))
    if module_name == "duckdb":
        return module.connect(database=target.database or ":memory:")

    raise DatabaseError(f"No connect recipe for driver {module_name!r}.")


def _stringify_value(value: Any) -> str:
    """The same blank-for-NULL, str-otherwise rule the file adapters use."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value).strip()


def _quote_identifier(name: str, dialect: str) -> str:
    """Quote a table name for the dialect, refusing anything with a quote in it.

    Table names are configuration, not user input, but a name carrying a quote
    or a semicolon is how a config file becomes SQL injection. Reject it.
    """
    if not name or any(char in name for char in '"\'`;\\'):
        raise DatabaseError(f"Unsafe table name: {name!r}")
    if "." in name:
        return ".".join(_quote_identifier(part, dialect) for part in name.split("."))
    if dialect in ("mysql", "mariadb"):
        return f"`{name}`"
    if dialect in ("mssql", "sqlserver"):
        return f"[{name}]"
    return f'"{name}"'


def list_tables(
    target: DatabaseTarget, *, schema: str | None = None, environ: dict[str, str] | None = None
) -> list[str]:
    """Table names in the target database, for a UI to offer a choice."""
    connection = connect(target, environ)
    try:
        cursor = connection.cursor()
        if target.dialect in ("mysql", "mariadb"):
            cursor.execute("SHOW TABLES")
            return sorted(str(row[0]) for row in cursor.fetchall())
        if target.dialect in ("mssql", "sqlserver"):
            cursor.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_TYPE = 'BASE TABLE'" + (" AND TABLE_SCHEMA = ?" if schema else ""),
                (schema,) if schema else (),
            )
            return sorted(str(row[0]) for row in cursor.fetchall())
        if target.dialect == "sqlite":
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            return [str(row[0]) for row in cursor.fetchall()]
        if target.dialect == "duckdb":
            cursor.execute("SELECT table_name FROM information_schema.tables")
            return sorted(str(row[0]) for row in cursor.fetchall())
        cursor.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s ORDER BY table_name",
            (schema or "public",),
        )
        return [str(row[0]) for row in cursor.fetchall()]
    finally:
        connection.close()


def read_table(
    url: str | DatabaseTarget,
    table: str,
    *,
    columns: list[str] | None = None,
    where: str = "",
    limit: int | None = None,
    environ: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Read ``table`` into a string DataFrame.

    ``where`` is a raw SQL fragment, and that is a deliberate, documented
    choice: a structured filter language cannot express the predicates buyers
    actually use, and this value comes from configuration authored by the same
    person who has the database password. It is *not* a place to put user
    input, and the docstring says so.
    """
    target = url if isinstance(url, DatabaseTarget) else parse_url(url)
    if where and any(token in where for token in (";", "--", "/*")):
        raise DatabaseError(
            f"where clause may not contain statement separators or comments: {where!r}"
        )

    if columns:
        selection = ", ".join(_quote_identifier(col, target.dialect) for col in columns)
    else:
        selection = "*"
    statement = f"SELECT {selection} FROM {_quote_identifier(table, target.dialect)}"
    if where:
        statement += f" WHERE {where}"
    if limit is not None:
        statement += f" LIMIT {int(limit)}"

    connection = connect(target, environ)
    try:
        cursor = connection.cursor()
        cursor.execute(statement)
        header = [str(description[0]).strip() for description in cursor.description or []]
        rows = [[_stringify_value(value) for value in row] for row in cursor.fetchall()]
    except Exception as exc:  # noqa: BLE001 - driver error types are many
        raise DatabaseError(f"Reading {table} failed: {exc}") from exc
    finally:
        connection.close()

    return pd.DataFrame(rows, columns=header, dtype=object)


def execute_query(
    url: str | DatabaseTarget, statement: str, *, environ: dict[str, str] | None = None
) -> pd.DataFrame:
    """Run a read-only ``SELECT`` and return the same string DataFrame.

    A statement that is not a ``SELECT`` is refused. A migration tool that
    accepts arbitrary statements against a production database is a foot-gun,
    and this function is only ever used to read.
    """
    text = statement.strip()
    if not text.lower().startswith(("select", "with")):
        raise DatabaseError("Only SELECT/WITH statements are allowed here.")
    if ";" in text.rstrip(";"):
        raise DatabaseError("Multiple statements are not allowed.")
    if any(token in text for token in ("--", "/*")):
        raise DatabaseError("SQL comments are not allowed in a query.")

    target = url if isinstance(url, DatabaseTarget) else parse_url(url)
    connection = connect(target, environ)
    try:
        cursor = connection.cursor()
        cursor.execute(text)
        header = [str(description[0]).strip() for description in cursor.description or []]
        rows = [[_stringify_value(value) for value in row] for row in cursor.fetchall()]
    finally:
        connection.close()
    return pd.DataFrame(rows, columns=header, dtype=object)


def available_drivers() -> dict[str, bool]:
    """Which dialects have their driver importable, for a UI to show."""
    report: dict[str, bool] = {}
    for dialect, (module, _package, _port) in DIALECTS.items():
        if module == ":stdlib:":
            report[dialect] = True
            continue
        try:
            __import__(module)
            report[dialect] = True
        except ImportError:
            report[dialect] = False
    return report


__all__ = [
    "DIALECTS",
    "DatabaseError",
    "DatabaseTarget",
    "MissingDriver",
    "available_drivers",
    "connect",
    "execute_query",
    "list_tables",
    "parse_url",
    "read_table",
]
