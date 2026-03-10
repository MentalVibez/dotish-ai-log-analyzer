# AI Log Analyzer

[![CI](https://github.com/MentalVibez/dotish-ai-log-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/MentalVibez/dotish-ai-log-analyzer/actions/workflows/ci.yml)

**DevOps log-analysis tool** — upload Nginx, Syslog, or Docker logs and get **errors**, **warnings**, **root causes**, and **suggested fixes** from an LLM in one step. Built for ops teams and SRE-style incident triage, not for multi-agent orchestration or general-purpose chat.

> **Portfolio note:** This repo is a **single-purpose DevOps tool** (log parsing → LLM analysis → actionable report). It is separate from [AI Agent Orchestrator](https://github.com/MentalVibez/ai-agent-orchestrator), which is a **multi-agent system** (MCP tool calling, RAG, workflows, OTel tracing). Same stack family (Python, FastAPI); different problem space.

<!-- Screenshot or GIF: upload → analyze → results. Add a file path here when you have one, e.g. docs/screenshot.png or docs/demo.gif -->

---

## How it works

1. **Upload** a log file (Nginx, Syslog, Docker, or plain text).
2. **Parse** — the app detects format and extracts structured events (errors, warnings, timestamps).
3. **Analyze** — an LLM (Ollama by default) reads the parsed log, infers root causes, and suggests fixes.
4. **Report** — you get a single JSON response: errors, warnings, root causes, and suggested fixes (and optionally a short summary).

No manual grep or copy-paste into a chatbot. One request, one response.

---

## Example: Nginx upstream failure

**Before (raw log):**

```
2024/01/15 12:00:00 [error] 1234#0: connect() failed (111: Connection refused) while connecting to upstream
2024/01/15 12:00:01 [warn] 1234#0: upstream server temporarily disabled
127.0.0.1 - - [15/Jan/2024:12:00:04 +0000] "GET /api/users HTTP/1.1" 502 0 "-" "-"
```

**After (what the app returns):**

- **Errors:** `connect() failed (111: Connection refused) while connecting to upstream`; access log 502 on `/api/users`.
- **Warnings:** `upstream server temporarily disabled`.
- **Root cause:** Backend upstream is down or not accepting connections; Nginx is marking it disabled and returning 502.
- **Suggested fix:** Check that the upstream service (e.g. app server) is running and listening; verify firewall and `proxy_pass` target; consider health checks and backup upstreams.

So: upload a failing Nginx log → the app detects repeated upstream/connection errors and 502s → infers backend connectivity → recommends checking upstream health and proxy settings.

---

## Example output

The API returns a structure like this (see `/docs` for the full schema):

```json
{
  "errors": [
    { "level": "error", "message": "connect() failed (111: Connection refused) while connecting to upstream", "source": "nginx" }
  ],
  "warnings": [
    { "level": "warning", "message": "upstream server temporarily disabled", "source": "nginx" }
  ],
  "recurring_issues": [
    { "message": "connect() failed (111: Connection refused) while connecting to upstream", "count": 1 },
    { "message": "upstream server temporarily disabled", "count": 1 }
  ],
  "root_causes": [
    "Upstream backend is not running or not accepting connections; Nginx is returning 502."
  ],
  "suggested_fixes": [
    { "cause": "Upstream unreachable", "fix": "Verify upstream process is running and listening; check proxy_pass address and firewall; add health_check or backup upstream." }
  ],
  "summary": "Repeated connection refused to upstream and 502s indicate backend is down or misconfigured."
}
```

---

## Features

- **Upload `.log` files** (and optionally `.txt`)
- **Parsing** for Nginx (error + access), Syslog (RFC 5424 and BSD-style), and **Docker** (JSON and raw container logs)
- **Duplicate grouping** — recurring errors/warnings are counted and returned as **top recurring issues** in the API
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

---

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

---

## Production and local defaults

**Local development** uses permissive defaults so you can run the app quickly:

- `CORS_ORIGINS=*` — allows any origin (fine for localhost).
- `OLLAMA_MODEL=llama2` — default model name (change to `mistral`, `llama3`, etc. as needed).

**Production** should lock this down:

- Set **`CORS_ORIGINS`** to your real front-end origin(s), e.g. `https://your-app.com`. Do **not** use `*` in production, especially with `allow_credentials=True`.
- Set **`OLLAMA_MODEL`** (or equivalent) to the model you’ve deployed for production.
- Run the app behind a **reverse proxy** (Nginx or Caddy); terminate TLS and restrict origins there as well.

Example production env (override these; do not commit secrets):

```bash
CORS_ORIGINS=https://your-frontend.example.com
OLLAMA_BASE_URL=http://your-ollama-host:11434
OLLAMA_MODEL=mistral
LOG_LEVEL=INFO
MAX_LOG_LINES=5000
```

See [docs/deployment.md](docs/deployment.md) and `deployment/aws/` for full deployment notes.

---

## Running in production

- **Docker** (from repo root):
  ```bash
  docker build -f deployment/docker/Dockerfile -t ai-log-analyzer .
  docker run -p 8000:8000 -e OLLAMA_BASE_URL=http://your-ollama-host:11434 -e CORS_ORIGINS=https://your-frontend.com ai-log-analyzer
  ```
- **Docker Compose**: `docker compose -f deployment/docker/docker-compose.yml up --build`
- Put **Nginx** or Caddy in front; example config: `deployment/nginx/default.conf`. The app exposes `/health` for load balancers.
- Production env vars: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, **`CORS_ORIGINS`** (no `*`), `LOG_LEVEL`, `MAX_LOG_LINES`. See [docs/deployment.md](docs/deployment.md) and `deployment/aws/` for EC2/VPS.

---

## Log size

Very large files are truncated to `MAX_LOG_LINES` (default 5000) before sending to the LLM. Set this in `.env` if needed.

---

## Architecture / AI pipeline

Upload → **parsing** (Nginx / Syslog) → **LLM extraction** (errors, warnings, root causes) → **report** with suggested fixes. The app uses LangChain + Ollama by default; the LLM is configurable via env (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`) so you can swap providers. Prompts live in `app/ai/prompts/`. See [docs/architecture.md](docs/architecture.md) for details.

---

## Evaluation

We maintain a small set of curated log samples and how the app performs on them (parser choice, root cause, fix quality). See [docs/evaluation.md](docs/evaluation.md).

---

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
docs/                 # architecture, deployment, api, evaluation, roadmap
.github/workflows/     # ci.yml, deploy.yml
```

---

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Unit tests cover parsers and services. Integration tests that call Ollama may be skipped if Ollama is not running.

---

## Future (aligned with preferred stack)

- **Persistence**: PostgreSQL for log events, analyses, alerts
- **Workers**: Celery, RQ, or Dramatiq with Redis for background analysis and alerts
- **Logging**: structlog (or Python logging) for request and pipeline logs
- **Search**: OpenSearch or Elasticsearch when log search becomes important
- **Detectors**: spike, error-pattern, auth-failure, latency (running in workers)
- **Integrations**: Slack, email, Prometheus, Grafana, S3
- **Frontend**: React (optional)
- **RAG**: LlamaIndex for past incidents/runbooks when needed
