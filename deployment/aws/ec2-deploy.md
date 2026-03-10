# Deploy to EC2

1. **Launch EC2** (e.g. t3.small, Ubuntu 22.04). Security group: allow 80, 443, 22 from your IP or 0.0.0.0/0 for 80/443 if public demo.

2. **On the instance**:
   - Install Docker, Docker Compose, and (optional) Nginx.
   - Clone the repo or copy the built image from a registry.

3. **Run the app**:
   - With Docker: `docker run -d -p 8000:8000 -e OLLAMA_BASE_URL=... your-registry/ai-log-analyzer:latest`
   - Or use the systemd unit in `systemd.service` and run uvicorn in a venv.

4. **Reverse proxy**: Point Nginx (see `deployment/nginx/default.conf`) at `127.0.0.1:8000`. Reload Nginx.

5. **Ollama**: Run Ollama on the same instance (e.g. in Docker or systemd) or on another host; set `OLLAMA_BASE_URL` accordingly.

6. **Optional**: Use GitHub Actions (see `.github/workflows/deploy.yml`) to build image, push to ECR, and SSH to EC2 to pull and restart.
