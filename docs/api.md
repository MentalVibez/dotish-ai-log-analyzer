# API

Base URL: `/` (e.g. `http://localhost:8000`).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serve static UI (index.html). |
| GET | `/health` | Health check; returns `{"status": "ok"}`. |
| POST | `/api/analyze` | Multipart form with `file` (log file). Full pipeline: upload → parse → LLM analysis → report. |
| POST | `/api/logs/upload` | Multipart form with `file`. Upload and parse only; returns parsed log events. |
| POST | `/api/analysis/run` | JSON body `{"log_content": "..."}`. Run analysis on raw text (no upload). |

## OpenAPI

Interactive docs: `/docs` (Swagger UI). Schema: `/openapi.json`.
