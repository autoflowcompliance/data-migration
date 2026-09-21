"""Generate a licence for a buyer.

Usage:
    python tools/make_license.py buyer@acme.com
    python tools/make_license.py buyer@acme.com --issued 2025-06-01 --out licence.json

Paste the printed JSON into an email. The buyer pastes it into Settings →
Activate a licence, or saves it as ``~/.dataready/license.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_files.licensing import sign  # noqa: E402
from app_files.licensing.loader import write_license  # noqa: E402


def make_license(email: str, issued: str | None = None, version: str = "1.0") -> dict:
    """Build a signed licence document for ``email``."""
    issued_date = issued or date.today().isoformat()
    return {
        "email": email,
        "issued": issued_date,
        "version": version,
        "signature": sign(email, issued_date),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a DataFlow licence.")
    parser.add_argument("email", help="the buyer's email address")
    parser.add_argument("--issued", default=None, help="issue date (YYYY-MM-DD), default today")
    parser.add_argument("--version", default="1.0", help="licence version")
    parser.add_argument("--out", type=Path, default=None, help="also write to this file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if "@" not in args.email:
        print(f"warning: {args.email!r} does not look like an email address", file=sys.stderr)

    data = make_license(args.email, args.issued, args.version)
    print(json.dumps(data, indent=2))
    if args.out:
        path = write_license(data, args.out)
        print(f"\nWrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())