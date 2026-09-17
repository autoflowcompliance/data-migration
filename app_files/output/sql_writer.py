"""SQL writer.

Emits plain ``CREATE TABLE`` + ``INSERT INTO`` statements, which is the most
portable form — the file loads into SQLite, MySQL, PostgreSQL and SQL Server
without modification.

Correctness notes:

* Identifiers (table and column names) are quoted and have embedded quotes
  doubled, so a column named ``O"Brien`` cannot break the statement.
* String literals have single quotes doubled per SQL standard.
* ``None``/NaN become ``NULL`` rather than the string ``'nan'``.
* Numeric-looking columns are emitted unquoted so the values arrive as numbers,
  not text.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

# A value that is entirely numeric (optionally signed / decimal) is emitted
# unquoted. Everything else is quoted as a string literal.
_SQL_KEYWORDS = ("SELECT", "FROM", "WHERE", "TABLE", "ORDER", "GROUP", "INSERT", "VALUES", "INDEX")


def quote_identifier(name: str) -> str:
    """Quote an identifier, doubling any embedded quote characters."""
    text = str(name)
    return '"' + text.replace('"', '""') + '"'


def quote_value(value: Any) -> str:
    """Render a Python value as an SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, float) and value != value:  # NaN
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text.strip() == "":
        return "NULL"
    return "'" + text.replace("'", "''") + "'"


def _is_numeric_literal(text: str) -> bool:
    """Whether ``text`` is a plain number that SQL should store as a number.

    Strings that only *look* numeric are excluded, because SQL's numeric
    affinity would silently rewrite them and lose the formatting that carries
    their meaning:

    * a leading ``+`` (phone numbers: ``+14155552671``)
    * a leading zero (account/zip codes: ``01234``)
    * thousands separators, spaces, or underscores

    Everything else must actually parse as a number. Without that final check a
    plain word such as ``John`` would be treated as numeric just for lacking a
    ``+``, a leading zero, or punctuation.
    """
    if text != text.strip():
        return False
    if text.startswith("+"):
        return False
    if len(text) > 1 and text[0] == "0" and text[1] not in ".eE":
        return False
    if "_" in text or "," in text or " " in text:
        return False
    try:
        Decimal(text)
    except InvalidOperation:
        return False
    return True


def _column_type(series: pd.Series) -> str:
    """Pick a portable column type from the data actually present."""
    non_blank = series[series.map(lambda v: not (v is None or str(v).strip() == ""))]
    if len(non_blank) == 0:
        return "TEXT"
    # Anything that isn't already a number must look like a plain numeric
    # literal, otherwise the column is TEXT and formatting is preserved.
    for value in non_blank:
        if isinstance(value, bool):
            return "TEXT"
        if isinstance(value, (int, float)):
            continue
        if not _is_numeric_literal(str(value)):
            return "TEXT"
    return "NUMERIC"


def render_sql(df: pd.DataFrame, table: str = "data", drop_existing: bool = False) -> str:
    """Return the SQL text for ``df`` without writing anything to disk."""
    lines: list[str] = []
    if drop_existing:
        lines.append(f"DROP TABLE IF EXISTS {quote_identifier(table)};")

    columns = ",\n  ".join(
        f"{quote_identifier(column)} {_column_type(df[column])}" for column in df.columns
    )
    lines.append(f"CREATE TABLE {quote_identifier(table)} (\n  {columns}\n);")

    if len(df):
        column_list = ", ".join(quote_identifier(column) for column in df.columns)
        for row in df.itertuples(index=False):
            values = ", ".join(quote_value(value) for value in row)
            lines.append(
                f"INSERT INTO {quote_identifier(table)} ({column_list}) VALUES ({values});"
            )
    return "\n".join(lines) + "\n"


def write(df: pd.DataFrame, path: str | Path, table: str = "data", drop_existing: bool = True) -> Path:
    """Write ``df`` as SQL statements to ``path`` and return the path written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_sql(df, table=table, drop_existing=drop_existing))
    return path