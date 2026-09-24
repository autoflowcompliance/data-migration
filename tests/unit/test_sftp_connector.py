"""The SFTP connector, driven through a fake paramiko client."""

from __future__ import annotations

import io
import stat

import pytest

from app_files.distribution.connectors import (
    ConnectorError,
    MissingCredentials,
    SFTPConnector,
    get_connector,
    pull,
)

CSV = b"email,name\nann@x.com,Ann\n"


class FakeHandle(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class FakeSFTPClient:
    def __init__(self, files=None, directories=None):
        self.files = files or {}
        self.directories = directories or {}
        self.opened: list[tuple[str, str]] = []

    def open(self, path, mode="rb"):
        self.opened.append((path, mode))
        if path not in self.files:
            raise FileNotFoundError(path)
        return FakeHandle(self.files[path])

    def listdir_attr(self, path):
        if path not in self.directories:
            raise FileNotFoundError(path)
        return self.directories[path]


class FakeAttr:
    def __init__(self, filename, size=10, mtime=1.0, mode=stat.S_IFREG):
        self.filename = filename
        self.st_size = size
        self.st_mtime = mtime
        self.st_mode = mode


def test_sftp_is_registered():
    assert isinstance(get_connector("sftp"), SFTPConnector)


def test_sftp_is_offered_under_a_clear_label():
    from app_files.distribution.connectors import PROVIDER_LABELS

    assert "SFTP" in PROVIDER_LABELS["sftp"]


def test_fetch_reads_the_remote_file():
    client = FakeSFTPClient(files={"/inbox/contacts.csv": CSV})
    connector = SFTPConnector(host="files.example.com", path="/inbox/contacts.csv", client=client)
    payload = connector.fetch()
    assert payload.name == "contacts.csv"
    assert payload.data == CSV
    assert payload.location == "sftp://files.example.com/inbox/contacts.csv"
    assert client.opened == [("/inbox/contacts.csv", "rb")]


def test_fetch_defaults_to_the_constructed_path():
    client = FakeSFTPClient(files={"data.csv": CSV})
    connector = SFTPConnector(path="data.csv", client=client)
    assert connector.fetch().data == CSV


def test_fetch_accepts_an_explicit_path():
    client = FakeSFTPClient(files={"other.csv": CSV})
    connector = SFTPConnector(path="data.csv", client=client)
    assert connector.fetch("other.csv").name == "other.csv"


def test_a_missing_remote_file_is_a_clear_error():
    connector = SFTPConnector(host="h", path="gone.csv", client=FakeSFTPClient())
    with pytest.raises(ConnectorError, match="Could not read gone.csv"):
        connector.fetch()


def test_fetch_needs_a_path():
    connector = SFTPConnector(host="h", client=FakeSFTPClient())
    with pytest.raises(ConnectorError, match="needs a remote path"):
        connector.fetch()


def test_list_files_returns_only_files():
    directory = [
        FakeAttr("a.csv"),
        FakeAttr("sub", mode=stat.S_IFDIR),
        FakeAttr("b.csv"),
    ]
    client = FakeSFTPClient(directories={"/inbox": directory})
    connector = SFTPConnector(host="h", client=client)
    listing = connector.list_files("/inbox")
    assert [f["name"] for f in listing.files] == ["/inbox/a.csv", "/inbox/b.csv"]


def test_listing_a_missing_directory_is_a_clear_error():
    connector = SFTPConnector(host="h", client=FakeSFTPClient())
    with pytest.raises(ConnectorError, match="Could not list"):
        connector.list_files("/nope")


def test_credentials_come_from_the_environment():
    environ = {"SFTP_HOST": "files.example.com", "SFTP_USER": "ann"}
    connector = SFTPConnector(environ=environ)
    assert connector.host == "files.example.com"
    assert connector.username == "ann"
    assert connector.check_credentials()["ready"] is True


def test_missing_credentials_are_reported():
    connector = SFTPConnector(environ={})
    status = connector.check_credentials()
    assert status["ready"] is False
    assert set(status["missing"]) == {"SFTP_HOST", "SFTP_USER"}


def test_connecting_without_a_library_or_host_reports_clearly(monkeypatch):
    connector = SFTPConnector(environ={})
    # paramiko is not a declared dependency, so this raises the install hint
    # (or the missing-host error if it is installed) — both are clear.
    with pytest.raises(ConnectorError):
        connector.client()


def test_pull_routes_the_path_argument():
    client = FakeSFTPClient(files={"k.csv": CSV})
    connector = SFTPConnector(client=client)
    # pull builds the connector from kwargs; inject the client through kwargs.
    payload = pull("sftp", client=client, path="k.csv")
    assert payload.data == CSV


def test_a_password_is_required_when_no_key_is_set(monkeypatch):
    connector = SFTPConnector(environ={"SFTP_HOST": "h", "SFTP_USER": "ann"})
    with pytest.raises(MissingCredentials, match="SFTP_PASSWORD"):
        connector.require("SFTP_PASSWORD", "SFTP password or key file")