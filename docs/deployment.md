# Deployment

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env   # edit if needed
uvicorn app.main:app --reload
# Or: python scripts/run_local.py
```

Ollama must be running (e.g. `ollama run llama2`) for full analysis.

## Docker

Build and run (from repo root):

```bash
docker build -f deployment/docker/Dockerfile -t ai-log-analyzer .
docker run -p 8000:8000 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 ai-log-analyzer
```

With Compose:

```bash
docker compose -f deployment/docker/docker-compose.yml up --build
```

Set `OLLAMA_BASE_URL` to your Ollama host (same machine, another container, or external URL).

## Production (VPS / EC2)

1. Run the app in Docker (or systemd + venv; see `deployment/aws/systemd.service`).
2. Put Nginx (or Caddy) in front; config example: `deployment/nginx/default.conf`.
3. Optional: RDS for PostgreSQL, S3 for artifacts, CloudWatch for logs — when those features are added.

See `deployment/aws/ec2-deploy.md` and `deployment/aws/architecture.md` for AWS details.

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama API base URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name | `llama2` |
| `CORS_ORIGINS` | Comma-separated origins or `*` | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_LOG_LINES` | Max lines sent to LLM | `5000` |
