# AI Log Analyzer

[![CI](https://github.com/MentalVibez/dotish-ai-log-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/MentalVibez/dotish-ai-log-analyzer/actions/workflows/ci.yml)

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

## Architecture / AI pipeline

Upload → **parsing** (Nginx / Syslog) → **LLM extraction** (errors, warnings, root causes) → **report** with suggested fixes. The app uses LangChain + Ollama by default; the LLM is configurable via env (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`) so you can swap providers. Prompts live in `app/ai/prompts/`. See [docs/architecture.md](docs/architecture.md) for details.

## Running in production

- **Docker** (from repo root):
  ```bash
  docker build -f deployment/docker/Dockerfile -t ai-log-analyzer .
  docker run -p 8000:8000 -e OLLAMA_BASE_URL=http://your-ollama-host:11434 ai-log-analyzer
  ```
- **Docker Compose**: `docker compose -f deployment/docker/docker-compose.yml up --build`
- Put **Nginx** or Caddy in front; example config: `deployment/nginx/default.conf`. The app exposes `/health` for load balancers.
- Production env vars: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `CORS_ORIGINS`, `LOG_LEVEL`, `MAX_LOG_LINES`. See [docs/deployment.md](docs/deployment.md) and `deployment/aws/` for EC2/VPS.

## Log size

Very large files are truncated to `MAX_LOG_LINES` (default 5000) before sending to the LLM. Set this in `.env` if needed.

## Project structure

```
app/
├── main.py           # FastAPI app, CORS, static UI
├── config.py         # Settings (Ollama, CORS, limits)
├── api/
├── services/
├── parsers/
├── ai/               # LLM client, prompts
├── models/
├── db/               # (future) PostgreSQL
├── workers/          # (future) Celery/Dramatiq
├── detectors/        # (future) spike, error-pattern, etc.
├── integrations/     # (future) Slack, S3, etc.
└── static/
tests/
scripts/              # run_local.py, init_db.py, seed_sample_logs.py
deployment/
├── docker/           # Dockerfile, docker-compose.yml
├── nginx/            # default.conf
└── aws/              # ec2-deploy.md, systemd.service, architecture.md
docs/                 # architecture, deployment, api, roadmap
.github/workflows/    # ci.yml, deploy.yml
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
