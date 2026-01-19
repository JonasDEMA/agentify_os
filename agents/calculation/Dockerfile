FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY agents/calculation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scheduler core (for LAM protocol)
COPY scheduler/__init__.py /app/scheduler/
COPY scheduler/core /app/scheduler/core

# Copy calculation agent
COPY agents/calculation /app/agents/calculation

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the agent
CMD ["python", "-m", "uvicorn", "agents.calculation.main:app", "--host", "0.0.0.0", "--port", "8000"]

