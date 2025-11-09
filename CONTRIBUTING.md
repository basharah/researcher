# Contributing to Research Paper Analysis Chatbot

Thanks for your interest in contributing! This project is a FastAPI microservices system with PostgreSQL + pgvector and Redis, orchestrated via Docker Compose. This guide helps you get set up, make changes safely, and submit quality contributions.

## TL;DR

- Start services with migrations applied: `./scripts/start.sh`
- Run unit/integration tests: `pytest` and `./scripts/test-*.sh`
- Never hardcode config; use `config.py` + `.env`
- Keep PRs focused, with docs and tests updated

## Project Layout

- `services/` — FastAPI services (api-gateway, document-processing, vector-db, llm-service)
- `docs/` — Architecture and guides (PHASE2/3/4, GPU, Auth, etc.)
- `scripts/` — Start/test/verify helpers
- `tests/` — Python unit/integration tests
- `docker-compose.yml` — Orchestration entry point

## Prerequisites

- Docker + Docker Compose
- Python 3.11 (for local testing/linting)
- NVIDIA GPU optional (vector-db/llm-service can use CUDA)

## Development Workflow

1. Clone and prepare env
   - Copy `.env.example` to `.env` and adjust values as needed
2. Start stack (migration-first)
   - `./scripts/start.sh`
   - Wait until `http://localhost:8000/api/v1/health` is healthy
3. Develop in small, testable increments
4. Run tests locally before opening a PR

## Database Migrations (Alembic)

Migrations live under `services/document-processing/alembic/versions/`.

- Create a new migration:
  - Inside the container or using the image: `alembic revision --autogenerate -m "your message"`
- Apply migrations:
  - Automatically via `./scripts/start.sh` (one-shot `migrate` service)
  - Or manually: `docker-compose run --rm migrate`
- Ordering:
  - Keep `down_revision` chains correct. Base table migrations must precede column additions.
- Validating:
  - Check `docker logs -f migrate-service` during development, or rely on the start script logs.

## Coding Standards

- Python: prefer type hints and docstrings for public functions
- Avoid global mutable state; prefer dependency injection where practical
- Follow existing patterns for settings, clients, and background tasks
- Do not commit secrets; `.env` should never contain production keys in commits

## Docs Style (Markdown)

- Add/update docs under `docs/` when you change behavior or public APIs
- Use fenced code blocks with language tags (e.g., ` ```bash`, ` ```python`, ` ```json`)
- Lint rules to keep in mind:
  - MD031: add blank lines around fenced code blocks
  - MD032: add blank lines around lists
  - MD036: avoid emphasis as headings (use `####` etc.)

## Testing

- Unit tests: `pytest` (configured via `pytest.ini`)
- Integration tests:
  - `./scripts/test-phase2-integration.sh` (Vector DB)
  - `./scripts/test-phase4-integration.sh` (API Gateway workflow)
  - `./scripts/test-extraction-endpoints.sh` (extraction)
- When you change public behavior, add/adjust tests accordingly

## Commit & PR Guidelines

- Keep PRs small, focused, and with a clear title/description
- Include:
  - What changed and why
  - How you tested (commands, screenshots, outputs)
  - Any migration notes
- Link related issues
- Avoid noisy diffs (don’t reformat unrelated code/files)

## Security & Secrets

- Never commit API keys or secrets
- Use environment variables and Pydantic settings (`config.py`)
- If you suspect a secret leak, rotate the key and open an issue

## Troubleshooting

- Vector DB first-run is slow (model download). Check `docker logs -f vector-db-service`
- GPUs: ensure NVIDIA Container Toolkit and proper `CUDA_VISIBLE_DEVICES`
- If migrations hang, verify `migrate-service` exits and health checks pass

## Questions?

Open an issue or start a discussion. We’re happy to help you land a great PR!
