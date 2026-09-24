"""Push a deliverable straight to its destination.

Today the output layer writes files and the user moves them. This closes the
last gap: a run delivers without a human downloading it.

Each destination is a small object with a ``deliver(data, filename)`` method
returning a receipt. The network client is injectable so the tests drive a real
local listener or a fake, and so a deployment can supply its own credentials
story. S3 and email have real implementations (boto3, smtplib); SFTP and
Sheets are transport-driven, because pulling paramiko and an OAuth flow into
the core would be a heavier dependency than the feature earns.

No destination raises into a run: a failed push is a receipt with
``delivered=False``, because correct output must not be lost to a dead mailbox.
"""

from __future__ import annotations

import smtplib
from collections.abc import Callable
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Protocol


@dataclass
class DeliveryReceipt:
    destination: str
    delivered: bool
    detail: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "destination": self.destination,
            "delivered": self.delivered,
            "detail": self.detail,
        }


class Destination(Protocol):
    name: str

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt: ...


#: Named destination factories, for plugins and for config-driven delivery.
#: A factory takes the config mapping and returns a ``Destination``.
DESTINATION_TYPES: dict[str, Callable[[dict[str, Any]], Destination]] = {}


def register_destination(
    name: str,
    factory: Callable[[dict[str, Any]], Destination],
    override: bool = False,
) -> Callable[[dict[str, Any]], Destination]:
    """Add a destination type. The plugin system's registration point.

    A factory, not a class: a destination almost always needs configuration
    (a URL, a bucket, credentials) before it is usable, and a factory is where
    that configuration is validated.
    """
    key = str(name).strip().lower()
    if not key:
        raise ValueError("A destination needs a name")
    if not callable(factory):
        raise ValueError(f"Destination {name!r} must be a factory, got {type(factory).__name__}")
    if key in DESTINATION_TYPES and not override:
        raise ValueError(
            f"Destination {name!r} already exists. Pass override=True to replace it."
        )
    DESTINATION_TYPES[key] = factory
    return factory


def build_destination(name: str, config: dict[str, Any] | None = None) -> Destination:
    key = str(name).strip().lower()
    try:
        factory = DESTINATION_TYPES[key]
    except KeyError:
        raise ValueError(
            f"Unknown destination {name!r}. Known: {', '.join(sorted(DESTINATION_TYPES))}"
        ) from None
    return factory(dict(config or {}))


def registered_destinations() -> list[str]:
    return sorted(DESTINATION_TYPES)


# --------------------------------------------------------------- local file


@dataclass
class FileDestination:
    """Write to a directory. The baseline every other destination is compared to."""

    directory: str | Path
    name: str = "file"

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt:
        try:
            target = Path(self.directory)
            target.mkdir(parents=True, exist_ok=True)
            (target / filename).write_bytes(data)
        except OSError as exc:
            return DeliveryReceipt(self.name, False, str(exc))
        return DeliveryReceipt(self.name, True, str(Path(self.directory) / filename))


# --------------------------------------------------------------------- S3


@dataclass
class S3Destination:
    """Upload to S3. The client is built lazily so importing this costs nothing."""

    bucket: str
    prefix: str = ""
    client: Any = None
    name: str = "s3"

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        # Imported on first use so the dependency stays optional; boto3 ships no
        # type stubs, so the import is explicitly untyped.
        import boto3  # type: ignore[import-untyped]

        self.client = boto3.client("s3")
        return self.client

    def key_for(self, filename: str) -> str:
        return f"{self.prefix.rstrip('/')}/{filename}" if self.prefix else filename

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt:
        key = self.key_for(filename)
        try:
            self._client().put_object(Bucket=self.bucket, Key=key, Body=data)
        except Exception as exc:  # noqa: BLE001 - returned, not raised
            return DeliveryReceipt(self.name, False, f"{type(exc).__name__}: {exc}")
        return DeliveryReceipt(self.name, True, f"s3://{self.bucket}/{key}")


# ------------------------------------------------------------------- email


@dataclass
class EmailDestination:
    """Email a deliverable as an attachment.

    The SMTP factory is injectable so a test can drive the real message-building
    path without a server.
    """

    to: list[str]
    sender: str = "dataflow@localhost"
    subject: str = "DataFlow deliverable"
    host: str = "localhost"
    port: int = 25
    body: str = "Your DataFlow run has completed. The output is attached."
    smtp_factory: Callable[..., Any] | None = None
    name: str = "email"

    def build_message(self, data: bytes, filename: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = ", ".join(self.to)
        message["Subject"] = self.subject
        message.set_content(self.body)
        message.add_attachment(
            data, maintype="application", subtype="octet-stream", filename=filename
        )
        return message

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt:
        try:
            message = self.build_message(data, filename)
            factory = self.smtp_factory or smtplib.SMTP
            with factory(self.host, self.port) as server:
                server.send_message(message)
        except Exception as exc:  # noqa: BLE001
            return DeliveryReceipt(self.name, False, f"{type(exc).__name__}: {exc}")
        return DeliveryReceipt(self.name, True, f"emailed {filename} to {', '.join(self.to)}")


# ------------------------------------------------------------------- SFTP


@dataclass
class SFTPDestination:
    """Upload over SFTP through an injected transport.

    ``transport(host, remote_path, data, username) -> None``. Supplying paramiko
    by default would add a C-extension dependency to every install for a feature
    many never enable, so the caller wires the client in.
    """

    host: str
    remote_dir: str
    username: str = ""
    transport: Callable[[str, str, bytes, str], None] | None = None
    name: str = "sftp"

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt:
        if self.transport is None:
            return DeliveryReceipt(
                self.name, False, "No SFTP transport configured; pass transport=..."
            )
        remote = f"{self.remote_dir.rstrip('/')}/{filename}"
        try:
            self.transport(self.host, remote, data, self.username)
        except Exception as exc:  # noqa: BLE001
            return DeliveryReceipt(self.name, False, f"{type(exc).__name__}: {exc}")
        return DeliveryReceipt(self.name, True, f"{self.username}@{self.host}:{remote}")


# ----------------------------------------------------------------- Sheets


@dataclass
class GoogleSheetsDestination:
    """Append rows to a sheet through an injected transport.

    The Sheets API needs an OAuth flow that does not belong in the core, so the
    caller supplies ``transport(url, data, headers) -> status``. This keeps the
    destination itself testable and dependency-free.
    """

    url: str
    transport: Callable[[str, bytes, dict[str, str]], int] | None = None
    headers: dict[str, str] = field(default_factory=dict)
    name: str = "google_sheets"

    def deliver(self, data: bytes, filename: str) -> DeliveryReceipt:
        if self.transport is None:
            return DeliveryReceipt(
                self.name, False, "No Sheets transport configured; pass transport=..."
            )
        headers = {"Content-Type": "application/octet-stream", **self.headers}
        try:
            status = self.transport(self.url, data, headers)
        except Exception as exc:  # noqa: BLE001
            return DeliveryReceipt(self.name, False, f"{type(exc).__name__}: {exc}")
        delivered = 200 <= int(status) < 300
        return DeliveryReceipt(self.name, delivered, None if delivered else f"HTTP {status}")


def push(
    data: bytes, filename: str, destinations: list[Destination]
) -> list[DeliveryReceipt]:
    """Deliver the same payload to every destination, collecting receipts."""
    return [destination.deliver(data, filename) for destination in destinations]


def push_file(
    path: str | Path, destinations: list[Destination]
) -> list[DeliveryReceipt]:
    location = Path(path)
    return push(location.read_bytes(), location.name, destinations)
