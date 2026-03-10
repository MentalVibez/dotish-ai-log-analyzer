from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel

from app.services.analysis_service import analyze
from app.services.report_service import format_for_api

router = APIRouter(prefix="/api", tags=["analysis"])


class AnalyzeBody(BaseModel):
    log_content: str
    parser_hint: str | None = None


@router.post("/analysis/run")
async def run_analysis(body: AnalyzeBody):
    """Run AI analysis on log content (errors, warnings, root causes, suggested fixes)."""
    if not body.log_content.strip():
        raise HTTPException(400, "log_content cannot be empty")
    result = analyze(body.log_content, parser_hint=body.parser_hint)
    return format_for_api(result)


@router.post("/analyze")
async def analyze_upload(
    file: UploadFile = File(..., description=".log or .txt file"),
    parser_hint: str | None = Form(None),
):
    """Upload a log file and return full AI analysis in one call (recommended for UI)."""
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    if not file.filename.endswith((".log", ".txt")):
        raise HTTPException(400, "Only .log and .txt files are allowed")
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(400, f"Could not decode file: {e}") from e
    if not text.strip():
        raise HTTPException(400, "File is empty")
    result = analyze(text, parser_hint=parser_hint)
    return format_for_api(result)
