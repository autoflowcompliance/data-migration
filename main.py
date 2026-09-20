"""Launch the NiceGUI app. ``python main.py`` from the repo root."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_files.interface.web.main import main  # noqa: E402

if __name__ in {"__main__", "__mp_main__"}:
    main()