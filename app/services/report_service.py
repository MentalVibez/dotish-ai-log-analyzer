import re
from datetime import datetime

from app.models.analysis_result import AnalysisResult
from app.models.log_event import LogEvent

# Max number of recurring issues to return in API (top N by count)
TOP_RECURRING_N = 10


def _normalize_message(msg: str) -> str:
    """Collapse whitespace and strip for grouping."""
    return re.sub(r"\s+", " ", (msg or "").strip())


def _recurring_issues(events: list[LogEvent], top_n: int = TOP_RECURRING_N) -> list[dict]:
    """Group events by normalized message, count, return top N by count (desc)."""
    counts: dict[str, int] = {}
    for e in events:
        key = _normalize_message(e.message)
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])[:top_n]
    return [{"message": msg, "count": count} for msg, count in sorted_items]


def format_for_api(result: AnalysisResult) -> dict:
    """Format AnalysisResult for API JSON response (sort by time, add recurring issues)."""
    def sort_events(events: list[LogEvent]) -> list[dict]:
        sorted_events = sorted(
            events,
            key=lambda e: (e.timestamp or datetime.min, e.message),
        )
        return [e.model_dump(mode="json") for e in sorted_events]

    all_events = result.errors + result.warnings
    recurring = _recurring_issues(all_events, top_n=TOP_RECURRING_N)

    return {
        "errors": sort_events(result.errors),
        "warnings": sort_events(result.warnings),
        "recurring_issues": recurring,
        "root_causes": result.root_causes,
        "suggested_fixes": [f.model_dump() for f in result.suggested_fixes],
        "summary": result.summary,
    }
