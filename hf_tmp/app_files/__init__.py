"""AutoFlow data migration tool: clean, map, validate and audit CRM exports."""

from .pipeline import PipelineResult, run_pipeline

__all__ = ["PipelineResult", "run_pipeline"]
__version__ = "0.1.0"
