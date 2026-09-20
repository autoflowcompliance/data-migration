"""Arrow-safe table rendering for the web UI.

The mapper emits object columns that hold floats *and* blank strings (for
example ``confidence``). Arrow cannot represent that in a single column, so
Streamlit logs a full traceback and silently coerces the data before rendering.
Coercing the types here — in the display layer — keeps the console clean without
touching the frozen mapper.

Kept in its own module rather than imported from ``app.py`` because importing a
Streamlit entrypoint executes it, which would re-run the whole main page from
inside a subpage.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    return str(value).strip() == ""


def arrow_safe(frame: pd.DataFrame) -> pd.DataFrame:
    """Copy ``frame`` with mixed-type object columns stringified.

    Stringifying is lossless for display and always serializes.
    """
    safe = frame.copy()
    for column in safe.columns:
        if safe[column].dtype != object:
            continue
        blank = safe[column].map(is_blank)
        non_blank = safe[column][~blank]
        if non_blank.empty:
            continue
        numeric = pd.to_numeric(non_blank, errors="coerce").notna()
        if numeric.any() and (blank.any() or not numeric.all()):
            safe[column] = safe[column].map(lambda v: "" if is_blank(v) else str(v))
    return safe


def show(frame: pd.DataFrame, **kwargs) -> None:
    """``st.dataframe`` that can always be serialized by Arrow.

    Accepts and drops the deprecated ``use_container_width`` so existing call
    sites keep working while the replacement width is applied.
    """
    kwargs.pop("use_container_width", None)
    st.dataframe(arrow_safe(frame), width="stretch", **kwargs)
