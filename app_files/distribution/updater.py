"""Update check for the desktop app.

The desktop build reads an update manifest, compares the published version with
its own, and tells the user if a newer build exists. This is what turns a
one-time purchase into an ongoing relationship without a subscription.

The manifest location is resolved in this order:

1. ``AUTOFLOW_UPDATE_URL`` — an operator override. May be an ``https://`` URL,
   a ``file://`` URL, or a plain filesystem path.
2. No default. If the operator has not set a URL, the app reports that updates
   are not configured rather than pretending to check.

There is deliberately no shipped example.com host. A default pointing at a
domain that does not exist cannot work for a buyer, and silently failing against
it is indistinguishable from a stub. The check is explicit about every failure:
``reachable=False`` with the reason, and never "you are up to date" when it could
not read a manifest.

A ``file://`` manifest or a local path is fully supported, so an operator can
publish updates from a shared drive and the whole path is testable offline.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
from urllib.request import url2pathname

# No shipped default: `manifest_url()` returns None until an operator sets one.
VERSION = "1.0.0"


def manifest_url() -> str | None:
    value = (os.getenv("AUTOFLOW_UPDATE_URL") or "").strip()
    return value or None


def current_version() -> str:
    return os.getenv("AUTOFLOW_VERSION") or VERSION


def parse_version(text: str) -> tuple[int, ...]:
    """``"1.2.3"`` -> ``(1, 2, 3)``. Non-numeric parts sort low rather than raising."""
    parts = []
    for chunk in str(text).strip().lstrip("v").split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def is_newer(candidate: str, than: str) -> bool:
    return parse_version(candidate) > parse_version(than)


@dataclass
class UpdateCheck:
    """The outcome of one check, including 'could not check'."""

    current: str
    latest: str = ""
    update_available: bool = False
    reachable: bool = False
    url: str = ""
    download_url: str = ""
    notes: str = ""
    checked_at: str = ""
    error: str = ""

    @property
    def status(self) -> str:
        if not self.reachable:
            return "CHECK FAILED"
        return "UPDATE AVAILABLE" if self.update_available else "UP TO DATE"

    def as_dict(self) -> dict[str, Any]:
        return {
            "current": self.current,
            "latest": self.latest,
            "update_available": self.update_available,
            "reachable": self.reachable,
            "url": self.url,
            "download_url": self.download_url,
            "status": self.status,
            "error": self.error,
        }

    def message(self) -> str:
        if not self.reachable:
            return (
                f"Could not check for updates ({self.error}). "
                "Your installed version keeps working."
            )
        if self.update_available:
            return (
                f"Version {self.latest} is available (you have {self.current}). "
                + (f"What's new: {self.notes} " if self.notes else "")
                + (f"Download: {self.download_url}" if self.download_url else "")
            ).strip()
        return f"You are up to date (version {self.current})."


def default_transport() -> Callable[..., Any]:
    import requests

    def transport(method: str, url: str, **kwargs: Any) -> Any:
        kwargs.setdefault("timeout", 10)
        return requests.request(method, url, **kwargs)

    return transport


def _local_path(target: str) -> Path | None:
    """The filesystem path a target names, or None if it is a remote URL."""
    parsed = urlparse(target)
    if parsed.scheme == "file":
        return Path(url2pathname(parsed.path))
    if parsed.scheme in ("http", "https"):
        return None
    # No scheme at all: treat it as a path, which is what an operator typing a
    # shared-drive location would write.
    return Path(target).expanduser()


def read_manifest(target: str) -> tuple[str, str]:
    """Return ``(text, error)`` for a local path or a remote URL."""
    path = _local_path(target)
    if path is not None:
        try:
            return path.read_text(encoding="utf-8"), ""
        except FileNotFoundError:
            return "", f"no manifest at {path}"
        except OSError as exc:
            return "", f"{type(exc).__name__}: {exc}"

    import requests

    try:
        response = requests.get(target, timeout=10)
    except Exception as exc:  # noqa: BLE001 - any transport failure is unreachable
        return "", f"{type(exc).__name__}: {exc}"
    if response.status_code != 200:
        return "", f"HTTP {response.status_code}"
    return response.text, ""


def check_for_update(
    transport: Callable[..., Any] | None = None,
    url: str | None = None,
    current: str | None = None,
) -> UpdateCheck:
    """Read the manifest and compare versions.

    Never raises: every failure is reported as ``reachable=False`` with the
    reason, because an offline buyer must not see a crash on startup. Passing
    ``transport`` overrides how the manifest is fetched, which is how tests
    exercise the parse and compare path without a network call.
    """
    target = url or manifest_url()
    mine = current or current_version()
    check = UpdateCheck(
        current=mine,
        url=target or "",
        checked_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    if not target:
        check.error = (
            "no update source is configured; set AUTOFLOW_UPDATE_URL to an "
            "https:// URL or a shared-drive path"
        )
        return check

    if transport is not None:
        try:
            response = transport("GET", target)
        except Exception as exc:  # noqa: BLE001
            check.error = f"{type(exc).__name__}: {exc}"
            return check
        status = getattr(response, "status_code", 0)
        if status != 200:
            check.error = f"HTTP {status}"
            return check
        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            check.error = f"the manifest was not valid JSON ({type(exc).__name__})"
            return check
    else:
        text, error = read_manifest(target)
        if error:
            check.error = error
            return check
        try:
            payload = json.loads(text)
        except Exception as exc:  # noqa: BLE001
            check.error = f"the manifest was not valid JSON ({type(exc).__name__})"
            return check

    check.reachable = True
    check.latest = str(payload.get("version", ""))
    check.download_url = str(payload.get("download_url", ""))
    check.notes = str(payload.get("notes", ""))
    if not check.latest:
        check.error = "the manifest had no 'version' field"
        return check
    check.update_available = is_newer(check.latest, mine)
    return check


def manifest_payload(
    version: str,
    download_url: str = "",
    notes: str = "",
) -> str:
    """Build a manifest for publishing or for tests.

    ``download_url`` has no default: a manifest that points at a build you do
    not host is a broken update, so the caller must supply one.
    """
    return json.dumps(
        {
            "version": version,
            "download_url": download_url,
            "notes": notes,
            "released_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        indent=2,
    )