"""Layer 10 — Intelligence.

Three capabilities that make the tool hard to compare with anything at this
price: anomaly detection against a stored baseline, suggestions derived from
the real profile, and natural-language filtering.

Every module here is deterministic and offline. None of them calls a network
service, and each reports the measurement behind its output so a claim can be
checked.

Turning a sentence into executable rules is deliberately *not* here. That is
`app_files/rules/builder.py`, driven by a form rather than a model, so it needs
no API key, no network, and gives the same YAML for the same input every time.

Calls into the frozen core; never modifies it.
"""

from app_files.intelligence.anomaly import (
    Anomaly,
    AnomalyReport,
    Baseline,
    clear_baselines,
    compare_to_baseline,
    detect,
    record_baseline,
    render_anomaly_html,
    shape_of,
)
from app_files.intelligence.nl_query import QueryResult, answer, query
from app_files.intelligence.suggestions import (
    Suggestion,
    SuggestionSet,
    render_suggestions_html,
    suggest,
    suggestion_texts,
)

__all__ = [
    "Anomaly",
    "AnomalyReport",
    "Baseline",
    "QueryResult",
    "Suggestion",
    "SuggestionSet",
    "answer",
    "clear_baselines",
    "compare_to_baseline",
    "detect",
    "query",
    "record_baseline",
    "render_anomaly_html",
    "render_suggestions_html",
    "shape_of",
    "suggest",
    "suggestion_texts",
]