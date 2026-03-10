from app.config import settings
from app.models.analysis_result import AnalysisResult
from app.ai.llm_client import run_full_analysis
from app.services.parsing_service import parse


def analyze(log_content: str, parser_hint: str | None = None) -> AnalysisResult:
    """
    Parse log content, then run AI extraction for root causes and suggested fixes.
    Errors and warnings come from the parser when available; LLM supplements and provides root causes + fixes.
    """
    events = parse(log_content, parser_hint=parser_hint)
    max_lines = settings.max_log_lines
    lines = log_content.splitlines()
    if len(lines) > max_lines:
        log_content = "\n".join(lines[:max_lines]) + "\n... (truncated)"
    parsed_errors = [e for e in events if e.level.value == "error"]
    parsed_warnings = [e for e in events if e.level.value == "warning"]
    return run_full_analysis(log_content, parsed_errors, parsed_warnings)
