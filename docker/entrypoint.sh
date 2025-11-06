#!/bin/sh
set -e

# (Optional) DB migrations
if [ "$RUN_DB_MIGRATIONS" = "1" ] && command -v alembic >/dev/null 2>&1; then
  echo "Running alembic upgrade head..."
  alembic upgrade head || echo "Alembic not configured; skipping"
fi

# Start FastAPI
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
