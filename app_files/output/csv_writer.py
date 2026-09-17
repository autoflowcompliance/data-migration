"""CSV writer — the format the tool already produced, behind a common interface.

Kept for symmetry with the other writers so ``output_format`` can select any
of them the same way.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write(df: pd.DataFrame, path: str | Path) -> Path:
    """Write ``df`` to ``path`` as CSV and return the path written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path