from datetime import datetime

from app.models.analysis_result import AnalysisResult
from app.models.log_event import LogEvent


def format_for_api(result: AnalysisResult) -> dict:
    """Format AnalysisResult for API JSON response (e.g. group by severity, sort by time)."""
    def sort_events(events: list[LogEvent]) -> list[dict]:
        sorted_events = sorted(
            events,
            key=lambda e: (e.timestamp or datetime.min, e.message),
        )
        return [e.model_dump(mode="json") for e in sorted_events]

    return {
        "errors": sort_events(result.errors),
        "warnings": sort_events(result.warnings),
        "root_causes": result.root_causes,
        "suggested_fixes": [f.model_dump() for f in result.suggested_fixes],
        "summary": result.summary,
    }
