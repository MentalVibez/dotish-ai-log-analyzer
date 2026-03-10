from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.models.log_event import LogEvent, LogLevel
from app.models.analysis_result import AnalysisResult, SuggestedFix


def _load_prompt(name: str) -> str:
    path = Path(__file__).parent / "prompts" / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _parse_extraction_response(text: str) -> tuple[list[str], list[str], list[str]]:
    """Parse ---ERRORS---, ---WARNINGS---, ---ROOT_CAUSES--- sections from LLM output."""
    errors: list[str] = []
    warnings: list[str] = []
    root_causes: list[str] = []

    section = None
    for line in text.splitlines():
        line = line.strip()
        if line == "---ERRORS---":
            section = "errors"
            continue
        if line == "---WARNINGS---":
            section = "warnings"
            continue
        if line == "---ROOT_CAUSES---":
            section = "root_causes"
            continue
        if not line or line.lower() == "none":
            continue
        if section == "errors":
            errors.append(line)
        elif section == "warnings":
            warnings.append(line)
        elif section == "root_causes":
            root_causes.append(line)

    return errors, warnings, root_causes


def _parse_fixes_response(text: str, cause: str) -> list[str]:
    """Parse bullet list of fixes from LLM output."""
    fixes: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip common bullet chars
        for prefix in ("- ", "* ", "• ", "1. ", "2. ", "3. "):
            if line.startswith(prefix):
                line = line[len(prefix) :].strip()
                break
        if line:
            fixes.append(line)
    return fixes if fixes else [text.strip()] if text.strip() else []


def get_llm():
    """Return configured ChatOllama instance."""
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.1,
    )


def extract_errors_warnings_root_causes(log_content: str) -> tuple[list[str], list[str], list[str]]:
    """Run extraction chain and return (errors, warnings, root_causes) as string lists."""
    prompt_text = _load_prompt("extraction_prompt")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a DevOps log analyst. Respond only with the requested sections."),
            ("human", prompt_text),
        ]
    )
    chain = prompt | get_llm() | StrOutputParser()
    result = chain.invoke({"log_content": log_content})
    return _parse_extraction_response(result)


def suggest_fixes_for_root_cause(root_cause: str) -> list[str]:
    """Get suggested fixes for one root cause."""
    prompt_text = _load_prompt("fixes_prompt")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a DevOps engineer. Respond with a short bullet list of fixes."),
            ("human", prompt_text),
        ]
    )
    chain = prompt | get_llm() | StrOutputParser()
    result = chain.invoke({"root_cause": root_cause})
    return _parse_fixes_response(result, root_cause)


def run_full_analysis(
    log_content: str,
    parsed_errors: list[LogEvent],
    parsed_warnings: list[LogEvent],
) -> AnalysisResult:
    """
    Run extraction + fixes and merge with parser output.
    Uses parser results for errors/warnings when available; uses LLM for root causes and fixes.
    """
    errors_str, warnings_str, root_causes = extract_errors_warnings_root_causes(log_content)

    # Prefer structured LogEvents from parser when we have them; else create from LLM strings
    errors: list[LogEvent] = list(parsed_errors)
    if not errors and errors_str:
        for msg in errors_str:
            errors.append(
                LogEvent(level=LogLevel.ERROR, message=msg, source="llm", raw=msg)
            )

    warnings_list: list[LogEvent] = list(parsed_warnings)
    if not warnings_list and warnings_str:
        for msg in warnings_str:
            warnings_list.append(
                LogEvent(level=LogLevel.WARNING, message=msg, source="llm", raw=msg)
            )

    suggested_fixes: list[SuggestedFix] = []
    for cause in root_causes:
        fixes = suggest_fixes_for_root_cause(cause)
        for fix in fixes:
            suggested_fixes.append(SuggestedFix(cause=cause, fix=fix))

    return AnalysisResult(
        errors=errors,
        warnings=warnings_list,
        root_causes=root_causes,
        suggested_fixes=suggested_fixes,
        summary=None,
    )
