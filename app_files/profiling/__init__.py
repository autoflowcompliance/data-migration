"""Profiling layer: five-dimension data quality scoring."""

from app_files.profiling.dimensions import DIMENSIONS
from app_files.profiling.profiler import (
    DIMENSION_NAMES,
    Profile,
    profile,
    scorecard_rows,
)
from app_files.profiling.report import (
    profile_and_render,
    render_qa_report_with_profile,
)

__all__ = [
    "DIMENSIONS",
    "DIMENSION_NAMES",
    "Profile",
    "profile",
    "profile_and_render",
    "render_qa_report_with_profile",
    "scorecard_rows",
]