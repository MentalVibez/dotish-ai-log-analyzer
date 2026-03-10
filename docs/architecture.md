# Architecture

## Overview

AI Log Analyzer is a FastAPI app that accepts log file uploads, parses them (Nginx, Syslog, Docker), and uses an LLM (Ollama or other providers) to extract errors, warnings, root causes, and suggested fixes.

## Pipeline (current)

End-to-end flow:

1. **Parser extraction** — Detect log format (Nginx, Syslog, Docker) and parse lines into structured `LogEvent` (timestamp, level, message, source).
2. **Normalization** — Events are sorted and passed to the next stage; message text is normalized where needed (e.g. for grouping).
3. **Duplicate grouping** — Errors and warnings are grouped by normalized message; counts are computed and the top recurring issues are included in the API response (`recurring_issues`).
4. **Root-cause inference** — The LLM receives the (possibly truncated) log text plus parsed errors/warnings and infers root causes.
5. **Remediation generation** — The LLM suggests fixes per root cause; results are returned as errors, warnings, recurring_issues, root_causes, suggested_fixes, and optional summary.

```
Upload → Parser extraction → Normalization → Duplicate grouping → LLM (root-cause + fixes) → Report
```

- **API**: FastAPI; routes under `/api/` for upload, parse-only, and full analysis.
- **Parsers**: Pluggable (Nginx error/access, Syslog RFC 5424 and BSD-style, Docker JSON and raw). Parser hint: `nginx`, `syslog`, or `docker`.
- **AI**: LangChain + Ollama by default; configurable via `OLLAMA_BASE_URL` / `OLLAMA_MODEL`. Prompts in `app/ai/prompts/` for extraction and fixes.
- **Report**: Errors, warnings, **recurring_issues** (message + count), root causes, suggested fixes, summary.

## Production target (Phase 1)

- **Compute**: Single VPS or EC2; app in Docker behind Nginx or Caddy.
- **Database**: PostgreSQL (RDS or managed) when persistence is added.
- **Storage**: S3-compatible object storage for uploaded logs/reports when needed.
- **Queue**: Redis only when background jobs (e.g. Celery/Dramatiq) are introduced.
- **CI/CD**: GitHub Actions for lint and tests; optional deploy workflow for EC2.

See [deployment.md](deployment.md) and `deployment/aws/` for runbooks.

## Pipeline (future)

Planned extensions:

- **Pattern clustering** — Group similar messages (e.g. by pattern or fingerprint) before root-cause inference.
- **Persistence** — Store analyses, history, and alerts (PostgreSQL).
- **Alerting** — Notify on severity or recurrence (Slack, webhook, email).
- **RAG over known incidents** — Use past analyses and runbooks to improve suggestions (e.g. LlamaIndex).
