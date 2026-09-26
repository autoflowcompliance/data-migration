# Direct connectors

Read a dataset from where it already lives — a database, an SFTP server, cloud
storage — instead of exporting it to a file first. Every connector returns the
same normalized DataFrame the file reader returns, so nothing downstream knows
the difference.

```bash
python -m app_files.cli pull database --url sqlite:///crm.db --table contacts -o output
python -m app_files.cli pull s3 --bucket my-data --key exports/contacts.csv -o output
python -m app_files.cli pull sftp --path /inbox/contacts.csv -o output
```

From Python:

```python
from app_files.distribution.connectors import get_connector

payload = get_connector("database", url="postgresql://reader@warehouse/crm",
                        table="contacts").fetch()
frame = payload.as_frame()          # a DataFrame of strings, like any upload
```

## Providers

| Provider | Aliases | Credentials |
|---|---|---|
| Amazon S3 | `s3` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (or an instance role) |
| Google Sheets | `google_sheets` | `GOOGLE_ACCESS_TOKEN`, or client id/secret + refresh token |
| Google Drive | `google_drive` | as above |
| Dropbox | `dropbox` | `DROPBOX_ACCESS_TOKEN` |
| OneDrive / SharePoint | `onedrive` | `MS_ACCESS_TOKEN` |
| SFTP | `sftp` | `SFTP_HOST`, `SFTP_USERNAME`, and `SFTP_KEY` or `SFTP_PASSWORD` |
| SQL database | `database`, `postgresql`, `mysql`, `mssql`, `sqlite` | `DATABASE_URL` or `--url` |

`credential_report()` returns exactly which variables are missing for each
provider, so a UI can say what to set rather than failing with a stack trace.

## Databases

A URL selects the dialect. The driver for PostgreSQL (`psycopg2-binary`), MySQL
(`PyMySQL`) or SQL Server (`pyodbc`) must be installed; if it is not, the error
names the package. SQLite and DuckDB need nothing extra.

```
postgresql://user@host:5432/dbname
mysql://user:pass@host/dbname
mssql://user@host/dbname
sqlite:///relative.db
sqlite:////absolute/path.db
```

### Passwords

A password may be in the URL, but it should not be, because a URL in a config
file or a shell history is a committed secret. Two better options:

- `?password_env=PGPASSWORD` names an environment variable. The variable is
  named, not guessed: scanning a list of conventional names turns a typo into a
  silent attempt as the wrong user.
- omit the password entirely and let the driver use its own file-based auth
  (`~/.pgpass`, MySQL option files).

`DatabaseTarget.display()` never includes a password, so a URL is safe to log.

### Read-only, on purpose

`execute_query` refuses anything that is not a `SELECT` or `WITH`, refuses
multiple statements, and refuses SQL comments. `read_table`'s `where` argument
is a raw fragment — a deliberate, documented choice, because a structured
filter cannot express the predicates buyers actually use — and it refuses
statement separators and comments. Table names carrying a quote or a semicolon
are rejected.

This is a migration tool, not a query console. Nothing here should ever write
to a production database.

### Values are strings

A column of integers in the database arrives as strings, exactly as `123` in a
CSV does. That keeps the cleaner's behaviour identical on the same logical
data, and it sidesteps SQL numeric affinity entirely: nothing is handed to
pandas as a number, so nothing can be silently rewritten.

`NULL` becomes `""`, the same as a blank CSV cell.

## SFTP

`paramiko` is needed for a live server. The client is injectable, so the
request construction — connect, open, read, close — is exercised by tests
against a fake client; the only part a test cannot reach is the remote host's
own behaviour. A key is preferred over a password.

## What is proven

- `tests/unit/test_database_connectors.py` — 57 tests against a real SQLite
  database: URL parsing, absolute vs relative paths, password handling, null
  handling, query safety, identifier quoting per dialect, and the SFTP request
  construction.
- `tests/integration/test_database_pipeline.py` — a table read and a CSV of the
  same rows produce an identical pipeline result.
- `tests/integration/test_postgres_live.py` — the connector against a real
  PostgreSQL server. SQLite needs no server, no driver and no password, so it
  cannot catch a broken PostgreSQL path; this test opens a real socket through
  psycopg2. It skips when no server is reachable, so it never fails a machine
  without one. Start it with:

  ```bash
  docker run -d --name pgtest \
      -e POSTGRES_PASSWORD=testpw -e POSTGRES_USER=testuser \
      -e POSTGRES_DB=testdb -p 55432:5432 postgres:16-alpine
  pip install psycopg2-binary
  PGTEST_PW=testpw python -m pytest tests/integration/test_postgres_live.py -q
  ```

  CI starts the same container and points the test at it with
  `DATAREADY_TEST_POSTGRES_URL`.
- `tests/regression/test_database_golden.py` — a committed `crm.db` SQLite
  file and the exact frame it must produce.
- `tests/integration/test_cli_and_tools.py` — `pull` end to end through the CLI.

## A refused connection is a DatabaseError

A wrong password, an unreachable host or a missing route is the most common
failure a buyer hits. `connect` reports it as `DatabaseError`, the type every
caller documents as the one to catch, and scrubs the password from the message
because some drivers echo the DSN they were handed. `MissingDriver` still
propagates unchanged, so a missing package is reported as an install
instruction rather than a connection failure. Both are pinned by tests that
need no server.
