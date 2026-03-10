# API

Base URL: `/` (e.g. `http://localhost:8000`).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serve static UI (index.html). |
| GET | `/health` | Health check; returns `{"status": "ok"}`. |
| POST | `/api/analyze` | Multipart form with `file` (log file). Full pipeline: upload → parse → LLM analysis → report. |
| POST | `/api/logs/upload` | Multipart form with `file`. Upload and parse only; returns parsed log events. |
| POST | `/api/analysis/run` | JSON body `{"log_content": "..."}`. Run analysis on raw text (no upload). Optional `parser_hint`: `nginx`, `syslog`, or `docker`. |

## Response shape (analysis endpoints)

Analysis responses include: `errors`, `warnings`, **`recurring_issues`** (list of `{ "message", "count" }`, top recurring by count), `root_causes`, `suggested_fixes`, `summary`.

## OpenAPI

Interactive docs: `/docs` (Swagger UI). Schema: `/openapi.json`.
