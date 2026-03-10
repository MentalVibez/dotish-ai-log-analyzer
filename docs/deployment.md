# Deployment

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env   # edit if needed
uvicorn app.main:app --reload
# Or: python scripts/run_local.py
```

Ollama must be running (e.g. `ollama run llama2`) for full analysis.

**Local defaults:** `.env.example` uses `CORS_ORIGINS=*` and `OLLAMA_MODEL=llama2`. These are for **local/dev only**. Do not use `*` for CORS in production.

---

## Production defaults and security

- **CORS:** `CORS_ORIGINS=*` is **local-only**. In production, set `CORS_ORIGINS` to your front-end origin(s), e.g. `https://your-app.com`. The app uses `allow_credentials=True`; with `*` that is not a safe production posture.
- **Ollama model:** The default `OLLAMA_MODEL=llama2` is a dev convenience. In production, set the model you actually run (e.g. `mistral`, `llama3`).
- **Reverse proxy:** Run the app behind Nginx or Caddy. Terminate TLS at the proxy and lock `CORS_ORIGINS` to the proxy’s public host (or your front-end domain). See `deployment/nginx/default.conf`.

Example **production** env (override per environment; never commit secrets):

```bash
CORS_ORIGINS=https://your-frontend.example.com
OLLAMA_BASE_URL=http://ollama.internal:11434
OLLAMA_MODEL=mistral
LOG_LEVEL=INFO
MAX_LOG_LINES=5000
```

---

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

| Variable | Description | Default | Production |
|----------|-------------|---------|------------|
| `OLLAMA_BASE_URL` | Ollama API base URL | `http://localhost:11434` | Set to your Ollama host |
| `OLLAMA_MODEL` | Model name | `llama2` (dev default) | Set to deployed model |
| `CORS_ORIGINS` | Comma-separated origins or `*` | `*` (local-only) | **Do not use `*`**; set to front-end origin(s) |
| `LOG_LEVEL` | Logging level | `INFO` | As needed |
| `MAX_LOG_LINES` | Max lines sent to LLM | `5000` | As needed |
