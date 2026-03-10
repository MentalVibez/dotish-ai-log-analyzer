# Architecture

## Overview

AI Log Analyzer is a FastAPI app that accepts log file uploads, parses them (Nginx, Syslog), and uses an LLM (Ollama or other providers) to extract errors, warnings, root causes, and suggested fixes.

## Pipeline

```
Upload (.log) → Parsing (Nginx / Syslog) → LLM extraction (errors, warnings, root causes) → Report (with suggested fixes)
```

- **API**: FastAPI; routes under `/api/` for upload, parse-only, and full analysis.
- **Parsers**: Pluggable (base, Nginx error/access, Syslog RFC 5424 and BSD-style). Output: structured log events.
- **AI**: LangChain + Ollama by default; configurable via `OLLAMA_BASE_URL` / `OLLAMA_MODEL`. Prompts in `app/ai/prompts/` for extraction and fixes. Designed so the LLM provider can be swapped via env (e.g. OpenAI/Claude later).
- **Report**: Combined errors, warnings, root causes, and suggested fixes returned as JSON and shown in the simple UI.

## Production target (Phase 1)

- **Compute**: Single VPS or EC2; app in Docker behind Nginx or Caddy.
- **Database**: PostgreSQL (RDS or managed) when persistence is added.
- **Storage**: S3-compatible object storage for uploaded logs/reports when needed.
- **Queue**: Redis only when background jobs (e.g. Celery/Dramatiq) are introduced.
- **CI/CD**: GitHub Actions for lint and tests; optional deploy workflow for EC2.

See [deployment.md](deployment.md) and `deployment/aws/` for runbooks.
