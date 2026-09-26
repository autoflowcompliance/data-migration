"""Profiling layer: five-dimension data quality scoring."""

from app_files.profiling.baseline import (
    DEFAULT_DROP_THRESHOLD,
    BaselineComparison,
    DimensionDrift,
    compare_to_baseline,
    compare_to_stored_baseline,
)
from app_files.profiling.binding import (
    QualityHistory,
    pin_baseline,
    record_quality,
    source_key,
)
from app_files.profiling.dimension_anomaly import (
    MIN_SAMPLES,
    DimensionAnomaly,
    DimensionAnomalyReport,
    DimensionRange,
    detect_dimension_anomalies,
    learn_ranges,
)
from app_files.profiling.dimensions import DIMENSIONS, evaluable_dimensions
from app_files.profiling.column_stats import (
    ColumnStats,
    column_statistics,
    summarize_column,
)
from app_files.profiling.outliers import (
    METHODS as OUTLIER_METHODS,
    OutlierResult,
    detect_outliers,
    iqr_outliers,
    isolation_forest_outliers,
    zscore_outliers,
)
from app_files.profiling.patterns import (
    InferredPattern,
    infer_column_pattern,
    infer_pattern,
    match_rate,
)
from app_files.profiling.profiling_block import (
    ProfilingBinding,
    ProfilingBlockError,
    bind_profiling,
    profiling_from_config,
)
from app_files.profiling.registry import (
    PROFILER_KIND,
    get_profiler,
    profiler_names,
    register_profiler,
)
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
from app_files.profiling.trends import (
    QualityPoint,
    TrendStore,
    render_trend_html,
    trend_db_path,
    trend_direction,
)

__all__ = [
    "DEFAULT_DROP_THRESHOLD",
    "DIMENSIONS",
    "MIN_SAMPLES",
    "DIMENSION_NAMES",
    "OUTLIER_METHODS",
    "BaselineComparison",
    "ColumnStats",
    "DimensionAnomaly",
    "DimensionAnomalyReport",
    "DimensionDrift",
    "DimensionRange",
    "InferredPattern",
    "OutlierResult",
    "PROFILER_KIND",
    "Profile",
    "ProfilingBinding",
    "ProfilingBlockError",
    "QualityHistory",
    "QualityPoint",
    "TrendStore",
    "bind_profiling",
    "column_statistics",
    "compare_to_baseline",
    "compare_to_stored_baseline",
    "detect_outliers",
    "detect_dimension_anomalies",
    "evaluable_dimensions",
    "get_profiler",
    "infer_column_pattern",
    "infer_pattern",
    "iqr_outliers",
    "isolation_forest_outliers",
    "match_rate",
    "pin_baseline",
    "profile",
    "profiler_names",
    "profiling_from_config",
    "register_profiler",
    "learn_ranges",
    "record_quality",
    "source_key",
    "profile_and_render",
    "render_qa_report_with_profile",
    "render_trend_html",
    "scorecard_rows",
    "summarize_column",
    "trend_db_path",
    "trend_direction",
    "zscore_outliers",
]