# Convenience targets for AI Log Analyzer

.PHONY: install run test lint docker-build docker-up

install:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check app tests

docker-build:
	docker build -f deployment/docker/Dockerfile -t ai-log-analyzer .

docker-up:
	docker compose -f deployment/docker/docker-compose.yml up --build
