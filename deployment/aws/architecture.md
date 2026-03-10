# AWS architecture (target)

Phase 1 production target for portfolio / single-VPS scale:

- **EC2**: Run the app in Docker (or systemd + venv). Nginx or Caddy on the same instance as reverse proxy.
- **RDS PostgreSQL**: Managed DB when you add persistence (log events, analyses, alerts). Optional for MVP.
- **S3**: Store uploaded log files and report artifacts when you need durable storage. Optional for MVP.
- **CloudWatch**: App logs and metrics. Optional for MVP; can start with stdout and Docker logs.

## Flow

```
Internet → (ALB or Nginx on EC2) → App container (port 8000) → Ollama (same host or separate)
                                        ↓
                              RDS (when added)
                                        ↓
                              S3 (when added)
```

Start with EC2 + Docker + Nginx; add RDS and S3 when you implement persistence and artifact storage.
