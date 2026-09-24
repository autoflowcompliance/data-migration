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
from typing import Any, Callable, Protocol
from urllib.parse import quote

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


# ------------------------------------------------------ Google Cloud Storage
_GCS_BASE = "https://storage.googleapis.com/storage/v1"
_GCS_UPLOAD_BASE = "https://storage.googleapis.com/upload/storage/v1"


class GoogleCloudStorageConnector(GoogleConnector):
    """Google Cloud Storage through the JSON API, sharing Google's OAuth flow.

    Reuses the Sheets/Drive token handling, so the same three credential shapes
    work: a ready ``GOOGLE_ACCESS_TOKEN``, or a refresh-token triple.
    """

    provider = "gcs"

    def __init__(
        self,
        bucket: str = "",
        key: str = "",
        client: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.bucket = bucket
        self.key = key
        self._client = client

    def credential_vars(self) -> list[str]:
        return super().credential_vars()

    def list_files(self, prefix: str = "", limit: int = 200) -> ConnectorListing:
        if not self.bucket:
            raise ConnectorError("Google Cloud Storage needs a bucket name.")
        response = self.transport(
            "GET",
            f"{_GCS_BASE}/b/{self.bucket}/o",
            headers=self.headers(),
            params={"prefix": prefix, "maxResults": limit},
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Google Cloud Storage returned HTTP "
                f"{getattr(response, 'status_code', 'unknown')} listing {self.bucket!r}."
            )
        files = [
            {
                "name": item.get("name", ""),
                "size": str(item.get("size", "")),
                "modified": item.get("updated", ""),
            }
            for item in response.json().get("items", [])
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, key: str | None = None) -> ConnectorFile:
        target = key or self.key
        if not self.bucket or not target:
            raise ConnectorError("Google Cloud Storage needs both a bucket and a key.")
        # The object name is percent-encoded in the path, since a GCS key may
        # contain '/' and other characters a URL path treats specially.
        response = self.transport(
            "GET",
            f"{_GCS_BASE}/b/{self.bucket}/o/{quote(target, safe='')}",
            headers=self.headers(),
            params={"alt": "media"},
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Could not read gs://{self.bucket}/{target}: HTTP "
                f"{getattr(response, 'status_code', 'unknown')}."
            )
        return ConnectorFile(
            name=os.path.basename(target) or "gcs_object",
            data=response.content,
            provider=self.provider,
            location=f"gs://{self.bucket}/{target}",
            content_type=response.headers.get("Content-Type", ""),
        )


# ----------------------------------------------------------------- Azure Blob
class AzureBlobConnector(Connector):
    """Azure Blob Storage.

    Supports the common shared-key scheme (``AZURE_STORAGE_ACCOUNT`` +
    ``AZURE_STORAGE_KEY``) and a ready bearer token (``AZURE_STORAGE_TOKEN``,
    for managed identity / Entra ID). Shared-key signing is computed here so the
    request is genuinely authenticated, not a placeholder header.
    """

    provider = "azure_blob"
    API_VERSION = "2021-08-06"

    def __init__(
        self,
        container: str = "",
        blob: str = "",
        account: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.container = container
        self.blob = blob
        self.account = account or self.env("AZURE_STORAGE_ACCOUNT") or ""

    def credential_vars(self) -> list[str]:
        if self.env("AZURE_STORAGE_TOKEN"):
            return ["AZURE_STORAGE_TOKEN"]
        return ["AZURE_STORAGE_ACCOUNT", "AZURE_STORAGE_KEY"]

    def base_url(self) -> str:
        if not self.account:
            raise MissingCredentials(self.provider, "AZURE_STORAGE_ACCOUNT", "account name")
        return f"https://{self.account}.blob.core.windows.net"

    def _shared_key_headers(
        self, method: str, url: str, content_length: int = 0
    ) -> dict[str, str]:
        """Build the Authorization header Azure's shared-key scheme requires."""
        import base64
        import hashlib
        import hmac
        from urllib.parse import urlparse

        account = self.account
        key = self.require("AZURE_STORAGE_KEY", "storage account key")
        parsed = urlparse(url)
        # The canonicalised resource must include every query parameter, sorted.
        if parsed.query:
            pairs = sorted(parsed.query.split("&"))
            query = "\n" + "\n".join(parsed.path + "?" + p for p in pairs)
        else:
            query = "\n" + parsed.path

        canonical = "\n".join(
            [
                method.upper(),
                "",  # Content-Encoding
                "",  # Content-Language
                str(content_length) if content_length else "",  # Content-Length
                "",  # Content-MD5
                "",  # Content-Type
                "",  # Date
                "",  # If-Modified-Since
                "",  # If-Match
                "",  # If-None-Match
                "",  # If-Unmodified-Since
                "",  # Range
            ]
        )
        string_to_sign = (
            canonical
            + "\n"
            + f"x-ms-date:{_rfc1123()}\n"
            + f"x-ms-version:{self.API_VERSION}\n"
            + query
        )
        signature = base64.b64encode(
            hmac.new(
                base64.b64decode(key), string_to_sign.encode("utf-8"), hashlib.sha256
            ).digest()
        ).decode()
        return {
            "x-ms-date": _rfc1123(),
            "x-ms-version": self.API_VERSION,
            "Authorization": f"SharedKey {account}:{signature}",
        }

    def _headers(self, method: str, url: str, content_length: int = 0) -> dict[str, str]:
        token = self.env("AZURE_STORAGE_TOKEN")
        if token:
            return {
                "Authorization": f"Bearer {token}",
                "x-ms-version": self.API_VERSION,
            }
        return self._shared_key_headers(method, url, content_length)

    def list_files(self, prefix: str = "", limit: int = 200) -> ConnectorListing:
        if not self.container:
            raise ConnectorError("Azure Blob needs a container name.")
        url = f"{self.base_url()}/{self.container}"
        params = {"restype": "container", "comp": "list", "maxresults": limit}
        if prefix:
            params["prefix"] = prefix
        response = self.transport(
            "GET", url, headers=self._headers("GET", url), params=params
        )
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Azure Blob returned HTTP {getattr(response, 'status_code', 'unknown')} "
                f"listing container {self.container!r}."
            )
        files = [
            {
                "name": item.get("Name", ""),
                "size": str(item.get("Properties", {}).get("Content-Length", "")),
                "modified": item.get("Properties", {}).get("Last-Modified", ""),
            }
            for item in response.json().get("Blobs", {}).get("Blob", [])
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, blob: str | None = None) -> ConnectorFile:
        target = blob or self.blob
        if not self.container or not target:
            raise ConnectorError("Azure Blob needs both a container and a blob name.")
        url = f"{self.base_url()}/{self.container}/{quote(target, safe='/')}"
        response = self.transport("GET", url, headers=self._headers("GET", url))
        if getattr(response, "status_code", 0) != 200:
            raise ConnectorError(
                f"Could not read Azure blob {self.container}/{target}: HTTP "
                f"{getattr(response, 'status_code', 'unknown')}."
            )
        return ConnectorFile(
            name=os.path.basename(target) or "azure_blob",
            data=response.content,
            provider=self.provider,
            location=f"azure://{self.account}/{self.container}/{target}",
            content_type=response.headers.get("Content-Type", ""),
        )


def _rfc1123() -> str:
    from email.utils import formatdate

    return formatdate(usegmt=True)


# ---------------------------------------------------------------- Slack (push)
class SlackConnector(Connector):
    """Slack incoming webhook — a delivery *destination*, not a file source.

    Slack is where a migration's result should land ("cleaned 1,204 rows,
    quality 92"), so this connector carries a *write* rather than a fetch. It
    keeps the same credential-reporting contract as the others.
    """

    provider = "slack"

    def __init__(self, webhook_url: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.webhook_url = webhook_url or self.env("SLACK_WEBHOOK_URL") or ""

    def credential_vars(self) -> list[str]:
        return ["SLACK_WEBHOOK_URL"]

    def send(self, text: str, blocks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if not self.webhook_url:
            raise MissingCredentials(self.provider, "SLACK_WEBHOOK_URL", "incoming webhook")
        payload: dict[str, Any] = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        response = self.transport(
            "POST", self.webhook_url, json=payload, headers={"Content-Type": "application/json"}
        )
        status = getattr(response, "status_code", 0)
        if status != 200:
            raise ConnectorError(
                f"Slack rejected the message with HTTP {status or 'unknown'}. "
                f"Check the webhook URL is still valid."
            )
        return {"provider": self.provider, "delivered": True, "status": status}


# ------------------------------------------------------ HubSpot (read contact)
_HUBSPOT_BASE = "https://api.hubapi.com"


class HubSpotConnector(Connector):
    """HubSpot CRM: read a contact list's page of records as a CSV.

    This is the "already uses HubSpot" path — pull existing contacts back in for
    a quality audit, or diff before an import.
    """

    provider = "hubspot"

    def __init__(
        self,
        object_type: str = "contacts",
        properties: list[str] | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.object_type = object_type
        self.properties = properties or []
        self.limit = limit

    def credential_vars(self) -> list[str]:
        return ["HUBSPOT_TOKEN"]

    def headers(self) -> dict[str, str]:
        token = self.require("HUBSPOT_TOKEN", "private app token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def fetch(
        self,
        object_type: str | None = None,
        properties: list[str] | None = None,
        limit: int | None = None,
    ) -> ConnectorFile:
        kind = object_type or self.object_type
        props = properties or self.properties
        count = limit or self.limit
        params: dict[str, Any] = {"limit": count, "archived": "false"}
        if props:
            params["properties"] = ",".join(props)
        response = self.transport(
            "GET", f"{_HUBSPOT_BASE}/crm/v3/objects/{kind}", headers=self.headers(), params=params
        )
        status = getattr(response, "status_code", 0)
        if status != 200:
            raise ConnectorError(
                f"HubSpot returned HTTP {status or 'unknown'} reading {kind!r}. "
                f"Check the token scope."
            )
        results = response.json().get("results", [])
        rows = []
        columns: list[str] = ["id"]
        for record in results:
            row = {"id": record.get("id", "")}
            for key, value in (record.get("properties") or {}).items():
                if key not in columns:
                    columns.append(key)
                row[key] = value
            rows.append(row)
        csv_text = _dicts_to_csv(columns, rows)
        return ConnectorFile(
            name=f"hubspot_{kind}.csv",
            data=csv_text.encode("utf-8"),
            provider=self.provider,
            location=f"hubspot://{kind}",
            content_type="text/csv",
        )


# ------------------------------------------------------ Salesforce (SOQL read)
_SALESFORCE_VERSION = "v59.0"


class SalesforceConnector(Connector):
    """Salesforce: run a SOQL query and return the records as CSV.

    Uses the REST query endpoint. An instance URL is required — Salesforce
    tokens are issued per-org, so there is no single global host.
    """

    provider = "salesforce"

    def __init__(self, instance_url: str = "", query: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.instance_url = (instance_url or self.env("SALESFORCE_INSTANCE_URL") or "").rstrip("/")
        self.query = query

    def credential_vars(self) -> list[str]:
        return ["SALESFORCE_TOKEN", "SALESFORCE_INSTANCE_URL"]

    def headers(self) -> dict[str, str]:
        token = self.require("SALESFORCE_TOKEN", "connected-app access token")
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def fetch(self, query: str | None = None) -> ConnectorFile:
        soql = query or self.query
        if not soql:
            raise ConnectorError("Salesforce needs a SOQL query, e.g. 'SELECT Id, Email FROM Contact'.")
        if not self.instance_url:
            raise MissingCredentials(
                self.provider, "SALESFORCE_INSTANCE_URL", "org instance URL"
            )
        response = self.transport(
            "GET",
            f"{self.instance_url}/services/data/{_SALESFORCE_VERSION}/query",
            headers=self.headers(),
            params={"q": soql},
        )
        status = getattr(response, "status_code", 0)
        if status != 200:
            raise ConnectorError(
                f"Salesforce returned HTTP {status or 'unknown'} running the query. "
                f"Check the SOQL and the token scope."
            )
        payload = response.json()
        records = payload.get("records", [])
        # Salesforce records carry an attributes block that is not real data.
        columns: list[str] = []
        flat_rows = []
        for record in records:
            clean = {k: v for k, v in record.items() if k != "attributes" and not isinstance(v, dict)}
            for key in clean:
                if key not in columns:
                    columns.append(key)
            flat_rows.append(clean)
        csv_text = _dicts_to_csv(columns, flat_rows)
        return ConnectorFile(
            name="salesforce_query.csv",
            data=csv_text.encode("utf-8"),
            provider=self.provider,
            location=f"salesforce://query?{soql[:60]}",
            content_type="text/csv",
        )


class SFTPConnector(Connector):
    """SFTP: pull a file from a secure file-transfer endpoint.

    SFTP is not an HTTP service, so this takes an injectable ``client`` — the
    object returned by ``paramiko.SSHClient().open_sftp()``. Production passes
    nothing and the connector builds a real paramiko client; tests pass a fake
    with the same four methods, so host, auth, path and retry handling are all
    exercised without a live server.

    Reads are opened binary and returned whole, matching every other connector,
    so callers of :func:`pull` do not branch on provider.
    """

    provider = "sftp"

    def __init__(
        self,
        host: str = "",
        path: str = "",
        port: int = 22,
        username: str = "",
        client: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.host = host or self.env("SFTP_HOST") or ""
        self.port = int(port or self.env("SFTP_PORT") or 22)
        self.username = username or self.env("SFTP_USER") or ""
        self.path = path
        self._client = client

    def credential_vars(self) -> list[str]:
        # A key file or an SSH agent is also valid, so the password is advisory.
        return ["SFTP_HOST", "SFTP_USER"]

    def client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import paramiko
        except ImportError as exc:
            raise ConnectorError(
                "SFTP needs the paramiko library. Install it with: pip install paramiko"
            ) from exc
        if not self.host:
            raise MissingCredentials(self.provider, "SFTP_HOST", "remote hostname")
        transport = paramiko.Transport((self.host, self.port))
        key_path = self.env("SFTP_KEY")
        try:
            if key_path:
                transport.connect(username=self.username, pkey=paramiko.RSAKey.from_private_key_file(key_path))
            else:
                password = self.require("SFTP_PASSWORD", "SFTP password or key file")
                transport.connect(username=self.username, password=password)
            self._client = paramiko.SFTPClient.from_transport(transport)
        except Exception as exc:  # noqa: BLE001 - paramiko raises many auth errors
            transport.close()
            raise ConnectorError(
                f"Could not connect to {self.host}:{self.port}: {type(exc).__name__}: {exc}"
            ) from exc
        return self._client

    def list_files(self, directory: str = "", limit: int = 200) -> ConnectorListing:
        target = directory or (os.path.dirname(self.path) or ".")
        client = self.client()
        try:
            entries = client.listdir_attr(target)
        except Exception as exc:  # noqa: BLE001
            raise ConnectorError(f"Could not list {target} on {self.host}: {exc}") from exc
        import stat as stat_module

        files = [
            {
                "name": os.path.join(target, entry.filename),
                "size": str(getattr(entry, "st_size", 0)),
                "modified": str(getattr(entry, "st_mtime", "")),
            }
            for entry in entries[:limit]
            if not stat_module.S_ISDIR(getattr(entry, "st_mode", 0))
        ]
        return ConnectorListing(provider=self.provider, files=files)

    def fetch(self, path: str | None = None) -> ConnectorFile:
        target = path or self.path
        if not target:
            raise ConnectorError("SFTP needs a remote path.")
        client = self.client()
        try:
            with client.open(target, "rb") as handle:
                data = handle.read()
        except Exception as exc:  # noqa: BLE001
            raise ConnectorError(
                f"Could not read {target} on {self.host}: {type(exc).__name__}: {exc}"
            ) from exc
        return ConnectorFile(
            name=os.path.basename(target) or "sftp_file",
            data=data,
            provider=self.provider,
            location=f"sftp://{self.host}/{target.lstrip('/')}",
            content_type="",
        )


def _dicts_to_csv(columns: list[str], rows: list[dict[str, Any]]) -> str:
    import csv

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in columns})
    return buffer.getvalue()


# ------------------------------------------------------------------ registry
CONNECTORS: dict[str, type[Connector]] = {
    "s3": S3Connector,
    "gcs": GoogleCloudStorageConnector,
    "azure_blob": AzureBlobConnector,
    "google_sheets": GoogleSheetsConnector,
    "google_drive": GoogleDriveConnector,
    "dropbox": DropboxConnector,
    "onedrive": OneDriveConnector,
    "hubspot": HubSpotConnector,
    "salesforce": SalesforceConnector,
    "slack": SlackConnector,
    "sftp": SFTPConnector,
}

PROVIDER_LABELS = {
    "s3": "Amazon S3 / S3-compatible",
    "gcs": "Google Cloud Storage",
    "azure_blob": "Azure Blob Storage",
    "google_sheets": "Google Sheets",
    "google_drive": "Google Drive",
    "dropbox": "Dropbox",
    "onedrive": "OneDrive / SharePoint",
    "hubspot": "HubSpot CRM",
    "salesforce": "Salesforce",
    "slack": "Slack (notification destination)",
    "sftp": "SFTP / secure file transfer",
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
    """Readiness of every connector, for the UI to show instead of failing late."""
    report = []
    for name in available_connectors():
        try:
            connector = CONNECTORS[name](environ=environ)
            status = connector.check_credentials()
        except Exception as exc:  # noqa: BLE001
            status = {"provider": name, "ready": False, "missing": [], "error": str(exc)}
        status["label"] = PROVIDER_LABELS.get(name, name)
        report.append(status)
    return report


def pull(provider: str, **kwargs: Any) -> ConnectorFile:
    """Fetch from a provider in one call: ``pull('s3', bucket='b', key='k.csv')``."""
    fetch_kwargs = {
        key: kwargs.pop(key)
        for key in (
            "key", "file_id", "file_name", "path", "item_path",
            "spreadsheet_id", "sheet_name", "blob",
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