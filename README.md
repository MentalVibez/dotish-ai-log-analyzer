# AI Log Analyzer

DevOps engineers often spend a lot of time scanning logs and hunting for root causes. This app lets you upload `.log` files and get **errors**, **warnings**, **suspected root causes**, and **suggested fixes** from an AI (Ollama) in one step.

## Features

- **Upload `.log` files** (and optionally `.txt`)
- **Parsing** for Nginx (error + access) and Syslog (RFC 5424 and BSD-style)
- **AI extraction** of errors, warnings, and suspected root causes (LangChain + Ollama)
- **Suggested fixes** per root cause
- **Simple web UI**: file picker + “Analyze” → results in one call

## Tech stack (current & preferred)

| Layer | Choice | Notes |
|-------|--------|--------|
| **API** | FastAPI | In use |
| **Schemas** | Pydantic | In use |
| **Logging** | Python `logging` or **structlog** | Preferred for app logs |
| **Workers** | Celery / RQ / **Dramatiq** | For async analysis jobs later |
| **Persistence** | **PostgreSQL** | For logs, analyses, alerts later |
| **Queue / cache** | **Redis** | For worker queue and caching |
| **Search** | OpenSearch or **Elasticsearch** | When full-text search matters |
| **LLM** | **Ollama** (local) or API-based (OpenAI/Claude) | Depends on budget and latency needs |

Current MVP uses FastAPI, Pydantic, and LangChain + Ollama; the rest of this stack is the target for later phases.

## Quick start

1. **Install Ollama** and run a model (e.g. `ollama run llama2` or `ollama run mistral`).

2. **Clone and install**:
   ```bash
   cd dotish-ai-log-analyzer
   pip install -r requirements.txt
   ```

3. **Configure** (optional): copy `.env.example` to `.env` and set:
   - `OLLAMA_BASE_URL` (default `http://localhost:11434`)
   - `OLLAMA_MODEL` (default `llama2`)

4. **Run the app**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Or: `python scripts/run_local.py`

5. Open **http://localhost:8000** for the UI, or call the API:
   - **POST /api/analyze** — multipart form with `file` (recommended)
   - **POST /api/logs/upload** — upload only, returns parsed events
   - **POST /api/analysis/run** — JSON body `{"log_content": "..."}` for analysis

## Log size

Very large files are truncated to `MAX_LOG_LINES` (default 5000) before sending to the LLM. Set this in `.env` if needed.

## Project structure (MVP)

```
app/
├── main.py           # FastAPI app, CORS, static UI
├── config.py         # Settings (Ollama, limits)
├── api/
│   ├── logs.py       # POST /api/logs/upload
│   └── analysis.py   # POST /api/analyze, POST /api/analysis/run
├── services/
│   ├── parsing_service.py
│   ├── analysis_service.py
│   └── report_service.py
├── parsers/
│   ├── base_parser.py
│   ├── nginx_parser.py
│   └── syslog_parser.py
├── ai/
│   ├── llm_client.py
│   └── prompts/
├── models/
│   ├── log_event.py
│   └── analysis_result.py
└── static/           # Simple UI
tests/
sample_data/          # Example nginx + syslog logs
scripts/               # run_local.py, seed_sample_logs.py
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Unit tests cover parsers and services. Integration tests that call Ollama may be skipped if Ollama is not running.

## Future (aligned with preferred stack)

- **Persistence**: PostgreSQL for log events, analyses, alerts
- **Workers**: Celery, RQ, or Dramatiq with Redis for background analysis and alerts
- **Logging**: structlog (or Python logging) for request and pipeline logs
- **Search**: OpenSearch or Elasticsearch when log search becomes important
- **Detectors**: spike, error-pattern, auth-failure, latency (running in workers)
- **Integrations**: Slack, email, Prometheus, Grafana, S3
- **Frontend**: React (optional)
- **RAG**: LlamaIndex for past incidents/runbooks when needed
