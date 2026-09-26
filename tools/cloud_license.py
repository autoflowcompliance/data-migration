"""Manage a cloud/SaaS subscription: trials, seats and meter readings.

Usage:
    python tools/cloud_license.py issue-trial buyer@acme.com --days 14
    python tools/cloud_license.py activate acme@example.com --seats 5 --expires 2027-01-01
    python tools/cloud_license.py add-seat alice
    python tools/cloud_license.py release-seat alice
    python tools/cloud_license.py status
    python tools/cloud_license.py usage
    python tools/cloud_license.py convert

Where this differs from ``tools/make_license.py``: that tool signs an offline
licence and prints it for the buyer to paste in. This one manages the state of
a hosted subscription — who holds a seat and what has been metered. It is the
operator's tool, run on the server, not the buyer's.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_files.licensing import sign
from app_files.licensing.cloud import (
    DEFAULT_TRIAL_DAYS,
    CloudLicense,
    CloudLicenseError,
)


def _emit(payload: dict) -> int:
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a DataFlow cloud subscription.")
    sub = parser.add_subparsers(dest="command", required=True)

    trial = sub.add_parser("issue-trial", help="start a time-limited trial")
    trial.add_argument("email")
    trial.add_argument("--days", type=int, default=DEFAULT_TRIAL_DAYS)

    activate = sub.add_parser("activate", help="register a signed subscription")
    activate.add_argument("account")
    activate.add_argument("--issued", required=True, help="issue timestamp (YYYY-MM-DDTHH:MM:SS)")
    activate.add_argument("--seats", type=int, default=1)
    activate.add_argument("--plan", default="team")
    activate.add_argument("--expires", default="")
    activate.add_argument(
        "--trial-days",
        type=int,
        default=None,
        help="make this a trial of N days instead of a dated subscription",
    )

    seat = sub.add_parser("add-seat", help="give a named person a seat")
    seat.add_argument("name")

    release = sub.add_parser("release-seat", help="free a named person's seat")
    release.add_argument("name")

    sub.add_parser("convert", help="mark a trial converted to a paid plan")
    sub.add_parser("status", help="show the license as a settings page would")
    sub.add_parser("usage", help="show metered runs and rows")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    licence = CloudLicense()
    try:
        if args.command == "issue-trial":
            config = licence.issue_trial(args.email, args.days)
            return _emit({"status": "trial started", **config.trial.as_dict()})
        if args.command == "activate":
            config = licence.activate(
                account=args.account,
                issued=args.issued,
                signature=sign(args.account, args.issued),
                seats=args.seats,
                plan=args.plan,
                expires=args.expires,
                trial_days=args.trial_days,
            )
            return _emit({"status": "activated", **config.as_dict()})
        if args.command == "add-seat":
            return _emit({"status": "seat added", **licence.add_seat(args.name).as_dict()})
        if args.command == "release-seat":
            licence.release_seat(args.name)
            return _emit({"status": "seat released", "name": args.name})
        if args.command == "convert":
            return _emit({"status": "converted", **licence.convert().as_dict()})
        if args.command == "status":
            return _emit(licence.status())
        if args.command == "usage":
            return _emit(licence.usage())
    except CloudLicenseError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
