"""Verify an installed copy of DataReady.

Usage:
    python tools/verify_install.py
    python tools/verify_install.py --json

Runs the same checks the ``/verify`` page shows, but from the command line so a
support engineer can ask a buyer to run one command and paste the output. Exits
non-zero when something is broken.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_files.interface.web.pages.verify import run_checks  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify this DataReady install.")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    results = run_checks()
    if args.json:
        print(
            json.dumps(
                [
                    {"name": check.name, "passed": check.passed, "detail": check.detail}
                    for check in results
                ],
                indent=2,
            )
        )
    else:
        width = max(len(check.name) for check in results) + 2
        for check in results:
            mark = "PASS" if check.passed else "FAIL"
            print(f"[{mark}] {check.name.ljust(width)} {check.detail}")
        passed = sum(1 for check in results if check.passed)
        print(f"\n{passed} of {len(results)} checks passed.")

    failed = [check for check in results if not check.passed]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())