#!/usr/bin/env bash
set -euo pipefail

# Robust wait-for-db and migration entrypoint.
# This script will:
#  - parse DATABASE_URL (if present)
#  - wait up to N attempts for the DB to accept connections
#  - run `alembic upgrade head` (idempotent)
#  - start the app

DB_WAIT_SECONDS=${DB_WAIT_SECONDS:-120}
DB_CHECK_INTERVAL=${DB_CHECK_INTERVAL:-1}

echo "Entry point: waiting up to ${DB_WAIT_SECONDS}s for Postgres (if DATABASE_URL is set)..."
if [ -z "${DATABASE_URL:-}" ]; then
    echo "No DATABASE_URL provided, skipping DB wait/migrations."
else
    python - <<'PY'
import os, sys, time
from sqlalchemy import create_engine

url = os.environ.get('DATABASE_URL')
if not url:
        print('No DATABASE_URL found; skipping DB wait')
        sys.exit(0)

engine = create_engine(url)
deadline = time.time() + int(os.environ.get('DB_WAIT_SECONDS', '120'))
while time.time() < deadline:
    try:
        with engine.connect() as conn:
            # SQLAlchemy 2.x: use exec_driver_sql for raw SQL strings
            conn.exec_driver_sql('SELECT 1')
        print('Postgres is up')
        sys.exit(0)
    except Exception as e:
        # Print exception details to help debugging connection issues
        print('Postgres not ready, retrying... exception:', repr(e), flush=True)
        time.sleep(int(os.environ.get('DB_CHECK_INTERVAL', '1')))

print('Timed out waiting for Postgres', file=sys.stderr)
sys.exit(1)
PY

    echo "Applying Alembic migrations..."
    # Run migrations; allow failures in CI/dev but surface them in logs
    if ! alembic upgrade head; then
        echo "alembic upgrade failed; continuing — check logs" >&2
    fi
fi

echo "Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
