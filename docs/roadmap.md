# Roadmap

## Done (MVP)

- FastAPI app with upload, parsing (Nginx, Syslog), LLM analysis (Ollama), report with suggested fixes.
- Docker and docker-compose for deployment.
- CI: GitHub Actions (lint + tests on push/PR).
- Configurable CORS and env-based settings.
- Docs: architecture, deployment, API.

## Next (Phase 2)

- **Persistence**: PostgreSQL (RDS or managed) for log events, analyses, alerts.
- **Workers**: Redis + Celery or Dramatiq for background analysis and alerts.
- **Logging**: structlog (or Python logging) for request and pipeline logs.
- **Deploy**: EC2 + Nginx (or Caddy); optional CD workflow in GitHub Actions.

## Later

- **Search**: OpenSearch or Elasticsearch for log search.
- **Detectors**: spike, error-pattern, auth-failure, latency (in workers).
- **Integrations**: Slack, email, Prometheus, Grafana, S3 for artifacts.
- **Frontend**: React (optional).
- **RAG**: LlamaIndex for past incidents/runbooks.
