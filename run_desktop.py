"""Frozen-application entry point (what PyInstaller packages).

Delegates to :mod:`app_files.onboarding.desktop`. Kept as a tiny file at the
repository root so the packaged executable has a stable, obvious entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

# When frozen, the PyInstaller bootloader sets sys._MEIPASS; add the bundle
# root so `app_files` imports resolve inside the packaged app.
if getattr(sys, "frozen", False):  # pragma: no cover - only true when packaged
    bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    if str(bundle) not in sys.path:
        sys.path.insert(0, str(bundle))

from app_files.onboarding.desktop import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())