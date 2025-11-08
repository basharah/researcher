#!/usr/bin/env bash

# Lightweight e2e start script that ensures DB migrations are applied before bringing
# up the rest of the services. Uses the one-shot `migrate` service defined in
# `docker-compose.yml` which runs `alembic upgrade head` and exits with non-zero on
# failure.

set -euo pipefail

echo "🚀 Research Paper Chatbot - e2e start (migrate -> compose up)"

# Ensure .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example (edit as needed)..."
    cp .env.example .env || true
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "Docker doesn't appear to be running. Start Docker and try again." >&2
    exit 1
fi

echo "🧪 Building images and running migrations (one-shot 'migrate' service)..."

# Build images so the migrate service has the correct image to run
docker-compose build --pull migrate

# Run the migrate service as a one-shot. This will run alembic upgrade head inside
# the document-processing image and then exit. It depends on postgres and redis
# being healthy (see docker-compose healthchecks). If this fails, the script exits.
docker-compose run --rm migrate

echo "✅ Migrations applied successfully. Starting remaining services..."

# Now bring up the stack (build as needed). Use the phase4 profile which includes
# the api-gateway and other higher-level services if you want the full stack.
docker-compose --profile phase4 up -d --build

echo "🌐 All services started. Check health endpoint: http://localhost:8000/api/v1/health"
echo "To stop everything: docker-compose down"

