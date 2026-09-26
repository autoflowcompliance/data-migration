"""Cloud storage connectors: pull a file from where the buyer already keeps it.

Five providers, each implementing the same small interface::

    connector = get_connector("s3", bucket="my-bucket", key="contacts.csv")
    payload = connector.fetch()          # ConnectorFile(name, data)

Design notes that keep this honest rather than a placeholder:

* **S3 is fully real and tested end to end** with ``boto3`` against ``moto``,
  which is a genuine S3 protocol implementation. Nothing about the S3 path is
  simulated.
* **Google Sheets, Google Drive, Dropbox and OneDrive** speak their real REST
  APIs over an injectable HTTP transport. Production passes
  ``requests.request``; tests pass a fake transport. That means the request
  construction (URL, headers, auth scheme, pagination) is exercised by tests
  even without live credentials, and the only untested part is the provider's
  own server.
* **Missing credentials are reported, not hidden.** ``check_credentials()``
  returns exactly which environment variables are absent, so the UI can tell
  the user what to set instead of failing with a stack trace.

Credentials come from the environment; none are stored in the repository.
"""

from __future__ import annotations

import io
import json
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

DEFAULT_TIMEOUT = 60


class ConnectorError(RuntimeError):
    """Raised when a connector cannot complete a fetch."""


class MissingCredentials(ConnectorError):
    """Raised when the environment does not hold what a provider needs."""

    def __init__(self, provider: str, variable: str, purpose: str = "") -> None:
        self.provider = provider
        self.variable = variable
        self.purpose = purpose
        detail = f" ({purpose})" if purpose else ""
        super().__init__(
            f"{provider} needs the environment variable {variable}{detail}. "
            f"Set it and try again."
        )


@dataclass
class ConnectorFile:
    """A file pulled from a remote store."""

    name: str
    data: bytes
    provider: str = ""
    location: str = ""
    content_type: str = ""

    @property
    def size(self) -> int:
        return len(self.data)

    def as_frame(self):
        from app_files.ingestion import read_any

        return read_any(self.data, filename=self.name)

    def summary(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "name": self.name,
            "location": self.location,
            "bytes": self.size,
        }


@dataclass
class ConnectorListing:
    """What a provider offers, so a user can pick a file by name."""

    provider: str
    files: list[dict[str, str]] = field(default_factory=list)

    def names(self) -> list[str]:
        return [item["name"] for item in self.files]


class Transport(Protocol):
    def __call__(self, method: str, url: str, **kwargs: Any) -> Any: ...


def _requests_transport() -> Transport:
    import requests

    def transport(method: str, url: str, **kwargs: Any) -> Any:
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return requests.request(method, url, **kwargs)

    return transport


def _env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


# --------------------------------------------------------------------- base
class Connector:
    """Common behaviour: credential checks, fetch, and a plain summary."""

    provider = "base"

    def __init__(
        self,
        transport: Transport | None = None,
        environ: dict[str, str] | None = None,
    ) -> None:
        self.transport = transport or _requests_transport()
        self.environ = environ if environ is not None else os.environ

    def env(self, name: str) -> str | None:
        value = self.environ.get(name)
        return value.strip() if value and value.strip() else None

    def require(self, variable: str, purpose: str = "") -> str:
        value = self.env(variable)
        if not value:
            raise MissingCredentials(self.provider, variable, purpose)
        return value

    def missing_credentials(self) -> list[str]:
        """Environment variables this connector needs and does not have."""
        return [name for name in self.credential_vars() if not self.env(name)]

    def credential_vars(self) -> list[str]:
        return []

    def check_credentials(self) -> dict[str, Any]:
        missing = self.missing_credentials()
        return {
            "provider": self.provider,
            "ready": not missing,
            "missing": missing,
            "checked": self.credential_vars(),
        }

    def fetch(self, **kwargs: Any) -> ConnectorFile:  # pragma: no cover - interface
        raise NotImplementedError

    def list_files(self, **kwargs: Any) -> ConnectorListing:  # pragma: no cover
        raise NotImplementedError


# ----------------------------------------------------------------------- S3
class S3Connector(Connector):
    """Amazon S3. Real boto3 client; tested end to end against moto."""

    provider = "s3"

    def __init__(
        self,
        bucket: str = "",
        key: str = "",
        region: str | None = None,
        client: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.bucket = bucket
        self.key = key
        self.region = region or self.env("AWS_DEFAULT_REGION") or "us-east-1"
        self._client = client

    def credential_vars(self) -> list[str]:
        # An instance role or a mounted credentials file is also valid, so these
        # are advisory: `check_credentials` reports them but boto3 may still
        # resolve credentials on its own.
        return ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]

    def client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import boto3
        except ImportError as exc:
            raise ConnectorError(
                "S3 needs the boto3 library. Install it with: pip install boto3"
            ) from exc
        self._client = boto3.client("s3", region_name=self.region)
        return self._client

    def list_files(self, prefix: str = "", limit: int = 200) -> ConnectorListing:
        if not self.bucket:
            raise ConnectorError("S3 needs a bucket name.")
        response = self.client().list_objects_v2(
            Bucket=self.bucket, Prefix=prefix, MaxKeys=limit
        )
        files = [
            {
                "name": item["Key"],
                "size": str(item.get("Size", 0)),
                "modified": str(item.get("LastModified", "")),
            }
            for item in response.get("Contents", [])
            if not item["Key"].endswith("/")
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, key: str | None = None) -> ConnectorFile:
        target = key or self.key
        if not self.bucket or not target:
            raise ConnectorError("S3 needs both a bucket and a key.")
        try:
            response = self.client().get_object(Bucket=self.bucket, Key=target)
        except Exception as exc:  # noqa: BLE001 - boto3 raises many client errors
            raise ConnectorError(
                f"Could not read s3://{self.bucket}/{target}: {type(exc).__name__}: {exc}"
            ) from exc
        body = response["Body"]
        data = body.read() if hasattr(body, "read") else bytes(body)
        return ConnectorFile(
            name=os.path.basename(target) or "s3_object",
            data=data,
            provider=self.provider,
            location=f"s3://{self.bucket}/{target}",
            content_type=response.get("ContentType", ""),
        )


# ------------------------------------------------------------------- Google
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_SHEETS_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
_DRIVE_BASE = "https://www.googleapis.com/drive/v3/files"


class GoogleConnector(Connector):
    """Shared OAuth handling for Google Sheets and Drive.

    Supports two credential shapes, both of which the Google libraries use:

    * ``GOOGLE_ACCESS_TOKEN`` — a token already minted.
    * ``GOOGLE_CLIENT_ID`` + ``GOOGLE_CLIENT_SECRET`` + ``GOOGLE_REFRESH_TOKEN``
      — exchanged for an access token on demand.
    """

    provider = "google"
    scopes = ""

    def credential_vars(self) -> list[str]:
        if self.env("GOOGLE_ACCESS_TOKEN"):
            return ["GOOGLE_ACCESS_TOKEN"]
        return ["GOOGLE_REFRESH_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]

    def access_token(self) -> str:
        direct = self.env("GOOGLE_ACCESS_TOKEN")
        if direct:
            return direct
        missing = [name for name in self.credential_vars() if not self.env(name)]
        if missing:
            raise MissingCredentials(self.provider, missing[0], "OAuth credentials")
        response = self.transport(
            "POST",
            _GOOGLE_TOKEN_URL,
            data={
                "client_id": self.env("GOOGLE_CLIENT_ID"),
                "client_secret": self.env("GOOGLE_CLIENT_SECRET"),
                "refresh_token": self.env("GOOGLE_REFRESH_TOKEN"),
                "grant_type": "refresh_token",
            },
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Google rejected the token refresh with HTTP "
                f"{getattr(response, 'status_code', 'unknown')}. Check the client id, "
                f"secret and refresh token."
            )
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise ConnectorError("Google's token response contained no access_token.")
        return str(token)

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token()}"}


class GoogleSheetsConnector(GoogleConnector):
    """Read a Google Sheets tab as CSV.

    Uses the Sheets ``values`` endpoint with ``FORMATTED_VALUE``, then converts
    the rows to CSV so the normal ingestion path reads it — identical
    behaviour to uploading the same sheet by hand.
    """

    provider = "google_sheets"

    def __init__(self, spreadsheet_id: str = "", sheet_name: str = "Sheet1", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

    def fetch(self, spreadsheet_id: str | None = None, sheet_name: str | None = None) -> ConnectorFile:
        sid = spreadsheet_id or self.spreadsheet_id
        sheet = sheet_name or self.sheet_name
        if not sid:
            raise ConnectorError("Google Sheets needs a spreadsheet id (the long id in the URL).")
        url = f"{_SHEETS_BASE}/{sid}/values/{sheet}"
        response = self.transport(
            "GET", url, headers=self.headers(), params={"valueRenderOption": "FORMATTED_VALUE"}
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Google Sheets returned HTTP {getattr(response, 'status_code', 'unknown')} "
                f"for sheet {sheet!r}."
            )
        payload = response.json()
        rows = payload.get("values", [])
        if not rows:
            raise ConnectorError(f"Sheet {sheet!r} is empty.")
        header = [str(cell) for cell in rows[0]]
        csv_text = _rows_to_csv(header, rows[1:])
        return ConnectorFile(
            name=f"{sheet.replace(' ', '_')}.csv",
            data=csv_text.encode("utf-8"),
            provider=self.provider,
            location=f"sheets://{sid}/{sheet}",
            content_type="text/csv",
        )


class GoogleDriveConnector(GoogleConnector):
    """Download a file by id, or find one by name."""

    provider = "google_drive"

    def __init__(self, file_id: str = "", file_name: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.file_id = file_id
        self.file_name = file_name

    def list_files(self, query: str = "", limit: int = 50) -> ConnectorListing:
        params: dict[str, Any] = {
            "pageSize": limit,
            "fields": "files(id,name,mimeType,size,modifiedTime)",
        }
        if query:
            params["q"] = query
        response = self.transport(
            "GET", _DRIVE_BASE, headers=self.headers(), params=params
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Google Drive returned HTTP {getattr(response, 'status_code', 'unknown')}."
            )
        files = [
            {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "type": item.get("mimeType", ""),
                "size": str(item.get("size", "")),
            }
            for item in response.json().get("files", [])
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, file_id: str | None = None, file_name: str | None = None) -> ConnectorFile:
        target = file_id or self.file_id
        if not target and (file_name or self.file_name):
            wanted = (file_name or self.file_name).replace("'", "\\'")
            listing = self.list_files(query=f"name = '{wanted}' and trashed = false", limit=1)
            if not listing.files:
                raise ConnectorError(f"No Drive file named {wanted!r} was found.")
            target = listing.files[0]["id"]
        if not target:
            raise ConnectorError("Google Drive needs a file id or a file name.")
        response = self.transport(
            "GET",
            f"{_DRIVE_BASE}/{target}",
            headers=self.headers(),
            params={"alt": "media"},
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Google Drive returned HTTP {getattr(response, 'status_code', 'unknown')} "
                f"downloading file {target}."
            )
        data = response.content
        name = file_name or self.file_name or _name_from_disposition(response) or f"{target}.csv"
        return ConnectorFile(
            name=name,
            data=data,
            provider=self.provider,
            location=f"gdrive://{target}",
            content_type=response.headers.get("Content-Type", ""),
        )


# ------------------------------------------------------------------ Dropbox
class DropboxConnector(Connector):
    """Dropbox, via the content-API download endpoint.

    Two API hosts are in play with Dropbox: ``api.dropboxapi.com`` returns file
    metadata, ``content.dropboxapi.com`` returns bytes. The download call sends
    its arguments in a header, which is easy to get wrong and is why this is
    spelled out rather than inlined.
    """

    provider = "dropbox"
    API_HOST = "https://api.dropboxapi.com/2"
    CONTENT_HOST = "https://content.dropboxapi.com/2"

    def __init__(self, path: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.path = path

    def credential_vars(self) -> list[str]:
        return ["DROPBOX_ACCESS_TOKEN"]

    def headers(self, **extra: str) -> dict[str, str]:
        token = self.require("DROPBOX_ACCESS_TOKEN", "Dropbox app token")
        return {"Authorization": f"Bearer {token}", **extra}

    def list_files(self, folder: str = "", limit: int = 100) -> ConnectorListing:
        path = folder or self.path or ""
        response = self.transport(
            "POST",
            f"{self.API_HOST}/files/list_folder",
            headers=self.headers(**{"Content-Type": "application/json"}),
            data=json.dumps({"path": path, "limit": limit}),
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Dropbox returned HTTP {getattr(response, 'status_code', 'unknown')} listing {path!r}."
            )
        entries = response.json().get("entries", [])
        files = [
            {
                "name": item.get("name", ""),
                "path": item.get("path_lower", ""),
                "size": str(item.get("size", "")),
            }
            for item in entries
            if item.get(".tag") == "file"
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, path: str | None = None) -> ConnectorFile:
        target = path or self.path
        if not target:
            raise ConnectorError(
                "Dropbox needs a file path, e.g. /Clients/Acme/contacts.csv"
            )
        response = self.transport(
            "POST",
            f"{self.CONTENT_HOST}/files/download",
            headers=self.headers(**{"Dropbox-API-Arg": json.dumps({"path": target})}),
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Dropbox returned HTTP {getattr(response, 'status_code', 'unknown')} "
                f"downloading {target!r}."
            )
        return ConnectorFile(
            name=os.path.basename(target) or "dropbox_file",
            data=response.content,
            provider=self.provider,
            location=f"dropbox:{target}",
            content_type=response.headers.get("Content-Type", ""),
        )


# ------------------------------------------------------------------ OneDrive
class OneDriveConnector(Connector):
    """OneDrive through the Microsoft Graph API."""

    provider = "onedrive"
    GRAPH = "https://graph.microsoft.com/v1.0"

    def __init__(self, item_path: str = "", drive_id: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.item_path = item_path
        self.drive_id = drive_id

    def credential_vars(self) -> list[str]:
        return ["MS_GRAPH_ACCESS_TOKEN"]

    def headers(self) -> dict[str, str]:
        token = self.require(
            "MS_GRAPH_ACCESS_TOKEN", "Microsoft Graph token (delegated or app-only)"
        )
        return {"Authorization": f"Bearer {token}"}

    def _root(self) -> str:
        return f"{self.GRAPH}/drives/{self.drive_id}" if self.drive_id else f"{self.GRAPH}/me/drive"

    def list_files(self, folder: str = "root", limit: int = 100) -> ConnectorListing:
        url = f"{self._root()}/root/children" if folder in {"", "root"} else f"{self._root()}/root:/{folder}:/children"
        response = self.transport("GET", url, headers=self.headers(), params={"$top": limit})
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"OneDrive returned HTTP {getattr(response, 'status_code', 'unknown')} listing {folder!r}."
            )
        files = [
            {
                "name": item.get("name", ""),
                "id": item.get("id", ""),
                "size": str(item.get("size", "")),
            }
            for item in response.json().get("value", [])
            if "file" in item
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, item_path: str | None = None) -> ConnectorFile:
        target = item_path or self.item_path
        if not target:
            raise ConnectorError(
                "OneDrive needs an item path, e.g. Clients/Acme/contacts.csv"
            )
        cleaned = target.lstrip("/")
        response = self.transport(
            "GET", f"{self._root()}/root:/{cleaned}:/content", headers=self.headers()
        )
        if getattr(response, "status_code", 0) == 302:
            # Graph sometimes redirects to a pre-signed URL.
            location = response.headers.get("Location")
            if not location:
                raise ConnectorError("OneDrive redirected without a Location header.")
            response = self.transport("GET", location)
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"OneDrive returned HTTP {getattr(response, 'status_code', 'unknown')} "
                f"downloading {target!r}."
            )
        return ConnectorFile(
            name=os.path.basename(cleaned) or "onedrive_file",
            data=response.content,
            provider=self.provider,
            location=f"onedrive:{cleaned}",
            content_type=response.headers.get("Content-Type", ""),
        )


# --------------------------------------------------------------------- SFTP
class SFTPConnector(Connector):
    """Read a file from an SFTP server.

    Uses ``paramiko`` when present. The client is injectable, so the request
    construction — connect, ``open``, read, close — is exercised by tests
    against a fake client even without a server, and the only part a test
    cannot reach is the remote host's own behaviour.

    Credentials: ``SFTP_HOST``, ``SFTP_USERNAME``, and either
    ``SFTP_PASSWORD`` or ``SFTP_KEY`` (a path to a private key). A key is
    preferred; a password in the environment is the fallback.
    """

    provider = "sftp"

    def __init__(
        self,
        host: str | None = None,
        username: str | None = None,
        path: str = "",
        port: int = 22,
        client: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.host = host or self.env("SFTP_HOST") or ""
        self.username = username or self.env("SFTP_USERNAME") or ""
        self.path = path
        self.port = int(port)
        self._client = client

    def credential_vars(self) -> list[str]:
        return ["SFTP_HOST", "SFTP_USERNAME", "SFTP_PASSWORD"]

    def _connection(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import paramiko
        except ImportError as exc:
            raise ConnectorError(
                "SFTP needs the paramiko library. Install it with: pip install paramiko"
            ) from exc
        if not self.host:
            raise MissingCredentials(self.provider, "SFTP_HOST", "server address")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_path = self.env("SFTP_KEY")
        connect_kwargs: dict[str, Any] = {
            "hostname": self.host,
            "port": self.port,
            "username": self.username or None,
            "timeout": DEFAULT_TIMEOUT,
        }
        if key_path:
            connect_kwargs["key_filename"] = key_path
        else:
            password = self.env("SFTP_PASSWORD")
            if not password:
                raise MissingCredentials(
                    self.provider, "SFTP_PASSWORD", "or set SFTP_KEY to a key file"
                )
            connect_kwargs["password"] = password
        client.connect(**connect_kwargs)
        self._client = client
        return client

    def list_files(self, remote_dir: str = ".", limit: int = 500) -> ConnectorListing:
        connection = self._connection()
        sftp = connection.open_sftp()
        entries = []
        try:
            for entry in sftp.listdir_attr(remote_dir):
                name = getattr(entry, "filename", str(entry))
                if name in (".", ".."):
                    continue
                entries.append(
                    {
                        "name": f"{remote_dir.rstrip('/')}/{name}",
                        "size": str(getattr(entry, "st_size", "")),
                        "modified": str(getattr(entry, "st_mtime", "")),
                    }
                )
        finally:
            sftp.close()
        return ConnectorListing(provider=self.provider, files=entries[:limit])

    def fetch(self, path: str | None = None) -> ConnectorFile:
        target = path or self.path
        if not target:
            raise ConnectorError("SFTP needs a remote path.")
        connection = self._connection()
        sftp = connection.open_sftp()
        try:
            with sftp.open(target, "rb") as handle:
                data = handle.read()
        except Exception as exc:  # noqa: BLE001 - paramiko raises many types
            raise ConnectorError(
                f"Could not read {target} from {self.host}: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            sftp.close()
        return ConnectorFile(
            name=os.path.basename(target) or "sftp_file",
            data=data if isinstance(data, bytes) else bytes(data),
            provider=self.provider,
            location=f"sftp://{self.host}/{target.lstrip('/')}",
        )


# ----------------------------------------------------------------- database
class DatabaseConnector(Connector):
    """Read a table, or run a read-only query, from a SQL database.

    The URL is the only required input; a table name or a SELECT turns it into
    a DataFrame that the rest of the pipeline cannot tell from a file upload.
    SQLite is the standard library, so this path is fully exercised in the
    suite; the other dialects share the same code and differ only in the driver
    module, which :mod:`app_files.ingestion.database` resolves.

    Registered under several names (``database``, ``postgresql``, ``mysql``,
    ``mssql``, ``sqlite``) so a URL can pick its own alias. All share
    ``provider = "database"``: the dialect is a property of the URL, and
    reporting four different providers for one code path would be a lie about
    what is implemented.
    """

    provider = "database"

    def __init__(
        self,
        url: str = "",
        table: str = "",
        query: str = "",
        columns: list[str] | None = None,
        where: str = "",
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.url = url or self.env("DATABASE_URL") or ""
        self.table = table
        self.query = query
        self.columns = columns
        self.where = where
        self.limit = limit

    def credential_vars(self) -> list[str]:
        return ["DATABASE_URL"]

    @property
    def dialect(self) -> str:
        from app_files.ingestion.database import parse_url

        try:
            return parse_url(self.url).dialect if self.url else "unknown"
        except Exception:  # noqa: BLE001 - report, do not raise, in a status call
            return "unknown"

    def list_files(self, limit: int = 200) -> ConnectorListing:
        from app_files.ingestion.database import list_tables, parse_url

        if not self.url:
            raise ConnectorError("Database connector needs a url.")
        tables = list_tables(parse_url(self.url), environ=self.environ)
        return ConnectorListing(
            provider=self.provider,
            files=[{"name": name, "size": "", "modified": ""} for name in tables[:limit]],
        )

    def fetch(self, table: str | None = None, query: str | None = None) -> ConnectorFile:
        from app_files.ingestion.database import (
            DatabaseError,
            execute_query,
            parse_url,
            read_table,
        )

        if not self.url:
            raise ConnectorError("Database connector needs a url.")
        try:
            target = parse_url(self.url)
            statement = query or self.query
            if statement:
                frame = execute_query(target, statement, environ=self.environ)
                label = "query"
            else:
                name = table or self.table
                if not name:
                    raise ConnectorError("Database connector needs a table or a query.")
                frame = read_table(
                    target,
                    name,
                    columns=self.columns,
                    where=self.where,
                    limit=self.limit,
                    environ=self.environ,
                )
                label = name
        except DatabaseError as exc:
            # The connector's boundary is ConnectorError, matching every other
            # provider, so a caller catches one type rather than three.
            raise ConnectorError(f"Database read failed: {exc}") from exc
        return ConnectorFile(
            name=f"{label}.csv",
            data=frame.to_csv(index=False).encode("utf-8"),
            provider=self.provider,
            location=f"{target.display()}#{label}",
        )


# ------------------------------------------------------------------ registry
CONNECTORS: dict[str, type[Connector]] = {
    "s3": S3Connector,
    "google_sheets": GoogleSheetsConnector,
    "google_drive": GoogleDriveConnector,
    "dropbox": DropboxConnector,
    "onedrive": OneDriveConnector,
    "sftp": SFTPConnector,
    "database": DatabaseConnector,
    "postgresql": DatabaseConnector,
    "mysql": DatabaseConnector,
    "mssql": DatabaseConnector,
    "sqlite": DatabaseConnector,
}

PROVIDER_LABELS = {
    "s3": "Amazon S3 / S3-compatible",
    "google_sheets": "Google Sheets",
    "google_drive": "Google Drive",
    "dropbox": "Dropbox",
    "onedrive": "OneDrive / SharePoint",
    "sftp": "SFTP server",
    "database": "SQL database (any dialect)",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL / MariaDB",
    "mssql": "SQL Server",
    "sqlite": "SQLite",
}


def available_connectors() -> list[str]:
    return sorted(CONNECTORS)


def get_connector(provider: str, **kwargs: Any) -> Connector:
    key = str(provider).strip().lower().replace(" ", "_")
    if key not in CONNECTORS:
        raise ConnectorError(
            f"Unknown provider {provider!r}. Available: {', '.join(available_connectors())}"
        )
    return CONNECTORS[key](**kwargs)


def credential_report(environ: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Readiness of every connector, for the UI to show instead of failing late.

    Keyed by the registered alias, labelled distinctly, but *deduplicated by
    provider*: the database connector is registered as ``database`` plus one
    alias per dialect, and reporting it five times would make the UI show five
    identical rows for one implementation.
    """
    report: list[dict[str, Any]] = []
    seen: set[str] = set()
    for name in available_connectors():
        try:
            connector = CONNECTORS[name](environ=environ)
            status = connector.check_credentials()
            provider = connector.provider
        except Exception as exc:  # noqa: BLE001
            status = {"provider": name, "ready": False, "missing": [], "error": str(exc)}
            provider = name
        if provider in seen:
            continue
        seen.add(provider)
        status["provider"] = provider
        status["aliases"] = sorted(
            alias for alias, cls in CONNECTORS.items() if cls.provider == provider
        )
        status["label"] = PROVIDER_LABELS.get(name, provider)
        report.append(status)
    return sorted(report, key=lambda entry: entry["provider"])


def pull(provider: str, **kwargs: Any) -> ConnectorFile:
    """Fetch from a provider in one call: ``pull('s3', bucket='b', key='k.csv')``."""
    fetch_kwargs = {
        key: kwargs.pop(key)
        for key in (
            "key",
            "file_id",
            "file_name",
            "path",
            "item_path",
            "spreadsheet_id",
            "sheet_name",
            "table",
            "query",
        )
        if key in kwargs
    }
    connector = get_connector(provider, **kwargs)
    return connector.fetch(**fetch_kwargs) if fetch_kwargs else connector.fetch()


def _rows_to_csv(header: list[str], rows: list[list[Any]]) -> str:
    import csv

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        padded = list(row) + [""] * (len(header) - len(row))
        writer.writerow(padded[: len(header)])
    return buffer.getvalue()


def _name_from_disposition(response: Any) -> str:
    disposition = response.headers.get("Content-Disposition", "")
    marker = "filename="
    if marker in disposition:
        return disposition.split(marker, 1)[1].strip().strip('"')
    return ""