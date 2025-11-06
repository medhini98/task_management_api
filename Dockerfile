# Slim Python base (psycopg[binary] works without system libs)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Install system deps only if you later add packages needing them
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential curl && rm -rf /var/lib/apt/lists/*

# Copy and install deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir pydantic-settings

# Copy the rest of the app
COPY . /app

# Entry script runs Alembic, then starts Uvicorn
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Default command can be overridden by docker-compose
CMD ["/entrypoint.sh"]