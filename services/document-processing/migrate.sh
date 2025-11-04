#!/usr/bin/env bash
set -euo pipefail

# Simple migration runner for the document-processing service
# Usage:
#   ./migrate.sh upgrade head
#   ./migrate.sh downgrade -1
#   ./migrate.sh revision -m "message" --autogenerate

cd "$(dirname "$0")"

export DATABASE_URL=${DATABASE_URL:-postgresql://researcher:researcher_pass@localhost:5432/research_papers}

echo "Using DATABASE_URL: $DATABASE_URL"

. ../..//.venv/bin/activate 2>/dev/null || true

alembic -c alembic.ini $@
