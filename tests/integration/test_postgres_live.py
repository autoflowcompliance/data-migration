"""Read a real PostgreSQL server, not a stub.

The connector's unit tests pin URL parsing and SQL construction against SQLite.
SQLite is in the standard library, so it is always available and always runs —
but it is also the one dialect that needs no network, no driver and no server.
That leaves the claim a buyer actually cares about untested: that the connector
talks to PostgreSQL.

This test runs against a genuine ``postgres`` server and drives the connector's
real DB-API path — psycopg2 opening a socket, the server executing the query,
the cursor returning typed rows that the connector stringifies. Nothing here is
faked: a bug in the placeholder style, the identifier quoting, the password
lookup or the value stringification fails this test and would not fail the
SQLite one.

A server is not always present, so the test skips when there is none rather
than failing. It looks for a URL in ``DATAREADY_TEST_POSTGRES_URL`` first, so CI
can point it at a service container, then falls back to the local port the
development container uses. A skip is reported, not silently green.

Set it up with::

    docker run -d --name pgtest \\
        -e POSTGRES_PASSWORD=testpw -e POSTGRES_USER=testuser \\
        -e POSTGRES_DB=testdb -p 55432:5432 postgres:16-alpine
    pip install psycopg2-binary
    DATAREADY_TEST_POSTGRES_URL=postgresql://testuser@127.0.0.1:55432/testdb \\
        python -m pytest tests/integration/test_postgres_live.py -q
"""

from __future__ import annotations

import os

import pytest

from app_files.ingestion.database import read_table

#: The development container's port. CI overrides the whole URL.
DEFAULT_URL = "postgresql://testuser@127.0.0.1:55432/testdb?password_env=PGTEST_PW"
DEFAULT_PASSWORD = "testpw"

ROWS = [
    ("John", "Smith", "john@acme.com", "(617) 498-3000", "1,000.00"),
    ("Jon", "Smith", "jon@acme.com", "617.498.3001", "980"),
    ("Jane", "Doe", "jane@acme.com", "+1 512 876 5432", "500.00"),
]


def _url() -> str:
    return os.environ.get("DATAREADY_TEST_POSTGRES_URL", DEFAULT_URL)


def _reachable(url: str) -> bool:
    try:
        import psycopg2
    except ImportError:
        return False
    from app_files.ingestion.database import parse_url

    target = parse_url(url)
    try:
        connection = psycopg2.connect(
            host=target.host,
            port=target.port,
            user=target.username,
            password=os.environ.get("PGTEST_PW", DEFAULT_PASSWORD),
            dbname=target.database,
            connect_timeout=3,
        )
    except Exception:  # noqa: BLE001 - any driver/socket error means "no server"
        return False
    connection.close()
    return True


pytestmark = pytest.mark.skipif(
    not _reachable(_url()),
    reason=(
        "no PostgreSQL server reachable; set DATAREADY_TEST_POSTGRES_URL or start "
        "the container described in this module's docstring"
    ),
)


@pytest.fixture(scope="module")
def seeded():
    """Create the table on the real server and hand back its URL."""
    import psycopg2

    from app_files.ingestion.database import parse_url

    url = _url()
    target = parse_url(url)
    connection = psycopg2.connect(
        host=target.host,
        port=target.port,
        user=target.username,
        password=os.environ.get("PGTEST_PW", DEFAULT_PASSWORD),
        dbname=target.database,
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS live_contacts")
        cursor.execute(
            "CREATE TABLE live_contacts ("
            "first_name TEXT, last_name TEXT, email TEXT, phone TEXT, amount TEXT)"
        )
        cursor.executemany(
            "INSERT INTO live_contacts VALUES (%s, %s, %s, %s, %s)", ROWS
        )
    connection.close()
    return url


def test_reads_a_real_postgres_table(seeded):
    frame = read_table(
        seeded, "live_contacts", environ={"PGTEST_PW": os.environ.get("PGTEST_PW", DEFAULT_PASSWORD)}
    )
    assert frame.shape == (3, 5)
    assert list(frame.columns) == ["first_name", "last_name", "email", "phone", "amount"]


def test_values_arrive_as_strings(seeded):
    """The connector stringifies so a database read reaches the cleaner the same
    way a CSV upload does. A driver handing back ints would change behaviour on
    identical logical data."""
    frame = read_table(
        seeded, "live_contacts", environ={"PGTEST_PW": os.environ.get("PGTEST_PW", DEFAULT_PASSWORD)}
    )
    assert all(str(dtype) == "object" for dtype in frame.dtypes)
    assert frame.loc[frame["first_name"] == "Jane", "phone"].iloc[0] == "+1 512 876 5432"


def test_the_password_comes_from_the_environment_not_the_url(seeded):
    """The URL names the variable; the value is passed in. A connection string
    with the password inline is how a credential ends up committed."""
    assert "testpw" not in seeded
    assert "password_env=PGTEST_PW" in seeded
    frame = read_table(seeded, "live_contacts", environ={"PGTEST_PW": "testpw"})
    assert len(frame) == 3


def test_a_wrong_password_is_reported_not_swallowed(seeded):
    from app_files.ingestion.database import DatabaseError

    with pytest.raises(DatabaseError):
        read_table(seeded, "live_contacts", environ={"PGTEST_PW": "definitely-wrong"})


def test_the_real_frame_matches_a_csv_of_the_same_rows(seeded, tmp_path):
    """The "nothing downstream knows the difference" contract, against a real
    server rather than SQLite."""
    import csv

    import pandas as pd

    frame = read_table(
        seeded, "live_contacts", environ={"PGTEST_PW": os.environ.get("PGTEST_PW", DEFAULT_PASSWORD)}
    )
    path = tmp_path / "same_rows.csv"
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["first_name", "last_name", "email", "phone", "amount"])
        writer.writerows(ROWS)
    from_file = pd.read_csv(path, dtype=str, keep_default_na=False)

    assert frame.shape == from_file.shape
    assert list(frame.columns) == list(from_file.columns)
    assert frame.to_dict("records") == from_file.to_dict("records")
