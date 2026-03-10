from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.parsing_service import parse

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.post("/upload")
async def upload_log(
    file: UploadFile = File(..., description=".log or .txt file"),
    parser_hint: str | None = None,
):
    """Upload a log file; returns parsed events (no AI analysis)."""
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    if not file.filename.endswith((".log", ".txt")):
        raise HTTPException(400, "Only .log and .txt files are allowed")
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(400, f"Could not decode file: {e}") from e
    events = parse(text, filename=file.filename, parser_hint=parser_hint)
    return {"events": [e.model_dump(mode="json") for e in events], "count": len(events)}
