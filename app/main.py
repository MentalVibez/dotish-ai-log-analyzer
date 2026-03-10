from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.logs import router as logs_router
from app.api.analysis import router as analysis_router

app = FastAPI(
    title="AI Log Analyzer",
    description="Upload .log files; AI extracts errors, warnings, root causes, and suggested fixes.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router)
app.include_router(analysis_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve simple UI: / returns index.html, other static assets under /static
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    @app.get("/")
    async def serve_ui():
        return FileResponse(static_dir / "index.html")

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
