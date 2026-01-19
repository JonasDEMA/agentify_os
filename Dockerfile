# Multi-stage build for CPA Scheduler
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY scheduler/ ./scheduler/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY .env.example ./.env

# Create data directory
RUN mkdir -p data uploads/screenshots

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "PYTHONPATH=. alembic upgrade head && python -m scheduler.main"]
