# VS Code Dev Container – Development Guide

This project includes a Dev Container setup to give you a consistent, preconfigured development environment with Docker access. It lets you run the full microservices stack (via Docker Compose) from inside VS Code with Python tooling, linting, and port forwarding ready to go.

## What You Get

- Python 3.11 toolchain (linting, debugging ready)
- Access to host Docker Engine (Docker Outside of Docker)
- Port forwarding for API Gateway, services, Postgres, Redis
- Helpful VS Code extensions preinstalled (Python, Pylance, Docker, Markdownlint)

## Prerequisites

- Docker Engine installed and running
- VS Code + Dev Containers extension
- NVIDIA GPUs (optional) with NVIDIA Container Toolkit installed on the host if you want GPU acceleration for vector-db / llm-service (the services get GPU from host; the dev container itself does not need GPU)

## Open in Dev Container

1. Copy `.env.example` to `.env` in the repo root and adjust values as needed.
2. In VS Code, run:
   - Command Palette → “Dev Containers: Reopen in Container”
3. Wait for the container to build and start. The first time can take a few minutes.

Notes:

- The dev container mounts your workspace at `/workspaces/researcher`.
- Docker is available inside the container via the mounted socket. The config also sets an alias so `docker-compose` maps to `docker compose`.

## Start the Stack (Migration-first)

From the VS Code integrated terminal (inside the dev container):

```bash
./scripts/start.sh
```

This will:

- Build images
- Run Alembic migrations via the one-shot `migrate` service
- Start all Phase 4 services in detached mode

Check health:

```bash
curl -s http://localhost:8000/api/v1/health | jq
```

If vector-db starts a bit slower the gateway may show “degraded” briefly; it should turn healthy after a moment.

## Common Commands

```bash
# Full stack up/down
docker compose --profile phase4 up -d
docker compose down

# Tail logs for a service
docker compose logs -f api-gateway

# Rebuild a single service
docker compose build vector-db && docker compose up -d vector-db

# Run only core DB/cache + document-processing
docker compose up -d postgres redis document-processing
```

Tip: The dev container sets an alias so `docker-compose` works as `docker compose` as well.

## GPU Acceleration (Optional)

- Ensure NVIDIA Container Toolkit is installed on the host.
- The compose file already requests GPUs for vector-db (GPU 0) and llm-service (GPU 1) via `deploy.resources.reservations`.
- Verify with:

```bash
./scripts/verify-gpu.sh
```

If the vector-db logs show `Device: cpu`, double-check host drivers/toolkit and rebuild the service image.

## Running Tests

You can run repository tests from inside the dev container as usual:

```bash
pytest -q
```

Some integration tests expect services to be up (API endpoints, DB connections).

## Environment and Secrets

- Add your API keys (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) to `.env`.
- The compose file passes relevant variables into services.

## Troubleshooting

- Docker not found in the dev container:
  - Ensure the Dev Container has the Docker socket mounted (it’s set in `.devcontainer/devcontainer.json`).
- `docker-compose` not found:
  - Use `docker compose` (space). The dev container attempts to alias `docker-compose` → `docker compose` in `~/.bashrc`/`~/.zshrc`.
- Health shows “degraded”:
  - Wait a few seconds and re-check. First run downloads the Sentence Transformers model.
- GPU not used:
  - Confirm host NVIDIA toolkit and drivers. Rebuild vector-db image after any GPU setup changes.

## Exposed Ports

- 8000: API Gateway
- 8001: Document Processing
- 8002: Vector DB
- 8003: LLM Service
- 5432: PostgreSQL
- 6379: Redis

## Exiting and Cleanup

```bash
docker compose down
```

To remove volumes too (DB/cache data):

```bash
docker compose down -v
```

Happy hacking!
