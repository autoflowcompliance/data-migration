"""Cloud and SaaS licensing: seats, usage metering, and trials.

The offline path in :mod:`app_files.licensing.loader` stays exactly as it is: a
signed JSON file, verified locally, no network. This module adds a second path
*alongside* it, for a subscription install where the truth lives on a server.

The design rule both paths share: neither reaches into the other. ``cloud.py``
imports the offline verifier to *delegate* a signature check, never to change
its behaviour. An install with no cloud config resolves through the offline
loader and behaves as it always did.

Three things a subscription needs that a signed file cannot express:

* **Seats.** A seat is a named activation. Activating past the seat count is
  refused — that is the whole point of selling seats, and a check that only
  warns is a check that gets ignored.
* **Metering.** Runs and rows consumed, per billing period. Recorded here so an
  invoice can be reconstructed from what actually ran.
* **Trials.** A time-limited license that expires on a date. Expiry is computed
  from the trial's own ``expires`` field, not from "issued + N days", so a
  shortened trial is possible and a clock change on the client cannot extend it.

The store is a JSON file under ``AUTOFLOW_HOME`` — the same state-home
convention every other stateful layer uses.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app_files.licensing.signing import signature_matches

DEFAULT_TRIAL_DAYS = 14
_ISO = "%Y-%m-%dT%H:%M:%S"


class CloudLicenseError(ValueError):
    """Raised on a seat limit, an expired trial, or a malformed cloud config."""


def cloud_dir() -> Path:
    """Where cloud licensing state lives. ``AUTOFLOW_HOME`` overrides for tests."""
    override = os.getenv("AUTOFLOW_HOME")
    if override:
        return Path(override) / "cloud_license"
    return Path(__file__).resolve().parent.parent.parent / "cloud_license"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(moment: str | None) -> datetime | None:
    if not moment:
        return None
    try:
        parsed = datetime.strptime(moment[:19], _ISO)
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc)


def _fmt(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime(_ISO)


@dataclass
class Trial:
    """A time-limited license. Expiry is a date, not a duration."""

    email: str
    started: str
    expires: str
    plan: str = "trial"
    converted: bool = False

    @classmethod
    def issue(cls, email: str, days: int = DEFAULT_TRIAL_DAYS, plan: str = "trial") -> Trial:
        if days <= 0:
            raise CloudLicenseError("A trial must last at least one day.")
        started = _now()
        return cls(
            email=str(email),
            started=_fmt(started),
            expires=_fmt(started + timedelta(days=days)),
            plan=plan,
        )

    def is_expired(self, at: datetime | None = None) -> bool:
        deadline = _parse(self.expires)
        if deadline is None:
            return True
        return (at or _now()) >= deadline

    def days_remaining(self, at: datetime | None = None) -> int:
        deadline = _parse(self.expires)
        if deadline is None:
            return 0
        # Round up: a trial issued for 14 days must read "14 days left" the
        # instant it is issued. Truncating shows 13, because the deadline is
        # computed from the issue instant and "now" is microseconds later.
        seconds = (deadline - (at or _now())).total_seconds()
        if seconds <= 0:
            return 0
        return int(-(-seconds // 86400))

    def as_dict(self) -> dict[str, Any]:
        return {
            "email": self.email,
            "started": self.started,
            "expires": self.expires,
            "plan": self.plan,
            "converted": self.converted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Trial:
        return cls(
            email=str(data["email"]),
            started=str(data.get("started", "")),
            expires=str(data.get("expires", "")),
            plan=str(data.get("plan", "trial")),
            converted=bool(data.get("converted", False)),
        )


@dataclass
class Seat:
    """One named activation."""

    name: str
    activated_at: str
    seat_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    active: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "seat_id": self.seat_id,
            "name": self.name,
            "activated_at": self.activated_at,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Seat:
        return cls(
            name=str(data["name"]),
            activated_at=str(data.get("activated_at", "")),
            seat_id=str(data.get("seat_id", uuid.uuid4().hex[:12])),
            active=bool(data.get("active", True)),
        )


@dataclass
class CloudConfig:
    """The subscription's terms, and what a cloud verification returns."""

    account: str
    seats: int = 1
    plan: str = "team"
    issued: str = ""
    expires: str = ""
    signature: str = ""
    seats_used: list[Seat] = field(default_factory=list)
    trial: Trial | None = None
    runs: int = 0
    rows: int = 0
    period_start: str = ""

    # ------------------------------------------------------------- verification
    def verify_signature(self) -> bool:
        """Check the activation against the signing key.

        Delegates to the offline verifier's key so a cloud license and an
        offline one cannot be signed by different keys; the account plays the
        role the offline ``email`` does.
        """
        if not (self.account and self.issued and self.signature):
            return False
        return signature_matches(self.account, self.issued, self.signature)

    def is_expired(self, at: datetime | None = None) -> bool:
        if self.trial is not None:
            return self.trial.is_expired(at)
        deadline = _parse(self.expires)
        if deadline is None:
            return False
        return (at or _now()) >= deadline

    @property
    def active_seats(self) -> list[Seat]:
        return [seat for seat in self.seats_used if seat.active]

    @property
    def seats_remaining(self) -> int:
        return max(0, self.seats - len(self.active_seats))

    def as_dict(self) -> dict[str, Any]:
        return {
            "account": self.account,
            "seats": self.seats,
            "plan": self.plan,
            "issued": self.issued,
            "expires": self.expires,
            "signature": self.signature,
            "seats_used": [seat.as_dict() for seat in self.seats_used],
            "trial": self.trial.as_dict() if self.trial else None,
            "runs": self.runs,
            "rows": self.rows,
            "period_start": self.period_start,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CloudConfig:
        trial = data.get("trial")
        return cls(
            account=str(data["account"]),
            seats=int(data.get("seats", 1)),
            plan=str(data.get("plan", "team")),
            issued=str(data.get("issued", "")),
            expires=str(data.get("expires", "")),
            signature=str(data.get("signature", "")),
            seats_used=[Seat.from_dict(item) for item in data.get("seats_used", [])],
            trial=Trial.from_dict(trial) if isinstance(trial, dict) else None,
            runs=int(data.get("runs", 0)),
            rows=int(data.get("rows", 0)),
            period_start=str(data.get("period_start", "")),
        )


class CloudLicenseStore:
    """A subscription's state on disk."""

    def __init__(self, base: Path | None = None):
        self.base = Path(base) if base else cloud_dir()

    @property
    def path(self) -> Path:
        return self.base / "cloud_license.json"

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> CloudConfig | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        try:
            return CloudConfig.from_dict(data)
        except (KeyError, TypeError, ValueError):
            return None

    def save(self, config: CloudConfig) -> Path:
        self.base.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(config.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return self.path

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()


class CloudLicense:
    """The operations a subscription install performs on its license."""

    def __init__(self, store: CloudLicenseStore | None = None):
        self.store = store or CloudLicenseStore()

    # -------------------------------------------------------------- activation
    def activate(
        self,
        account: str,
        issued: str,
        signature: str,
        seats: int = 1,
        plan: str = "team",
        expires: str = "",
        trial_days: int | None = None,
    ) -> CloudConfig:
        """Register a signed subscription, refusing a bad signature outright.

        Not verifying here would mean the first check happens on a later run,
        after an operator has already handed out access.
        """
        if not signature_matches(account, issued, signature):
            raise CloudLicenseError("Cloud license signature does not match.")
        trial = Trial.issue(account, trial_days) if trial_days else None
        config = CloudConfig(
            account=str(account),
            seats=int(seats),
            plan=str(trial.plan if trial else plan),
            issued=str(issued),
            expires=str(trial.expires if trial else expires),
            signature=str(signature),
            trial=trial,
            period_start=_fmt(_now()),
        )
        self.store.save(config)
        return config

    def issue_trial(self, email: str, days: int = DEFAULT_TRIAL_DAYS) -> CloudConfig:
        """Self-service trial: no signature to check yet, expiry enforced."""
        trial = Trial.issue(email, days)
        config = CloudConfig(
            account=str(email),
            seats=1,
            plan=trial.plan,
            issued=trial.started,
            expires=trial.expires,
            trial=trial,
            period_start=trial.started,
        )
        self.store.save(config)
        return config

    def convert(self) -> CloudConfig:
        """Mark the trial converted, keeping its history."""
        config = self._require()
        if config.trial is None:
            raise CloudLicenseError("This license is not a trial.")
        config.trial.converted = True
        config.plan = "team"
        self.store.save(config)
        return config

    # ------------------------------------------------------------------- seats
    def add_seat(self, name: str) -> Seat:
        config = self._require()
        if config.is_expired():
            raise CloudLicenseError("The subscription has expired.")
        if len(config.active_seats) >= config.seats:
            raise CloudLicenseError(
                f"All {config.seats} seat(s) are in use. Buy another seat to add "
                f"{name!r}."
            )
        if any(seat.name == name and seat.active for seat in config.seats_used):
            raise CloudLicenseError(f"{name!r} already holds an active seat.")
        seat = Seat(name=str(name), activated_at=_fmt(_now()))
        config.seats_used.append(seat)
        self.store.save(config)
        return seat

    def release_seat(self, name: str) -> None:
        config = self._require()
        for seat in config.seats_used:
            if seat.name == name and seat.active:
                seat.active = False
                self.store.save(config)
                return
        raise CloudLicenseError(f"No active seat for {name!r}.")

    # ---------------------------------------------------------------- metering
    def record_run(self, rows: int = 0) -> dict[str, Any]:
        """Meter one run. Returns the totals for the current period."""
        config = self._require()
        config.runs += 1
        config.rows += max(0, int(rows))
        self.store.save(config)
        return {"runs": config.runs, "rows": config.rows,
                "period_start": config.period_start}

    def usage(self) -> dict[str, Any]:
        config = self._require()
        return {
            "account": config.account,
            "plan": config.plan,
            "runs": config.runs,
            "rows": config.rows,
            "seats": config.seats,
            "seats_used": len(config.active_seats),
            "seats_remaining": config.seats_remaining,
            "period_start": config.period_start,
            "expired": config.is_expired(),
        }

    def status(self) -> dict[str, Any]:
        """What a settings page reads. Never raises on a missing license."""
        config = self.store.load()
        if config is None:
            return {"mode": "offline", "cloud": False}
        body = {"mode": "cloud", "cloud": True, **config.as_dict()}
        body["seats_used"] = [seat.as_dict() for seat in config.active_seats]
        body["seats_remaining"] = config.seats_remaining
        body["expired"] = config.is_expired()
        body["signature_valid"] = config.verify_signature() if config.signature else None
        if config.trial is not None:
            body["trial_days_remaining"] = config.trial.days_remaining()
        return body

    # ------------------------------------------------------------------ helpers
    def is_active(self) -> bool:
        """True when a verified, unexpired cloud license is present."""
        config = self.store.load()
        if config is None or config.is_expired():
            return False
        if config.trial is not None:
            return not config.trial.is_expired()
        return config.verify_signature()

    def _require(self) -> CloudConfig:
        config = self.store.load()
        if config is None:
            raise CloudLicenseError("No cloud license is configured.")
        return config


def default_store() -> CloudLicenseStore:
    return CloudLicenseStore()


__all__ = [
    "DEFAULT_TRIAL_DAYS",
    "CloudConfig",
    "CloudLicense",
    "CloudLicenseError",
    "CloudLicenseStore",
    "Seat",
    "Trial",
    "cloud_dir",
    "default_store",
]
