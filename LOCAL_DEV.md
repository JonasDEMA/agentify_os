# 🚀 Local Development Guide

**Quick guide for running FastAPI services locally with Swagger UI**

---

## ✅ Currently Running Services

| Service | Port | Swagger UI | Health | Status |
|---------|------|------------|--------|--------|
| **Scheduler** | 8000 | [http://localhost:8000/docs](http://localhost:8000/docs) | [/health](http://localhost:8000/health) | ✅ Running |
| **Server** | 8001 | [http://localhost:8001/docs](http://localhost:8001/docs) | [/health](http://localhost:8001/health) | ✅ Running |
| **Redis** | 6379 | - | Docker: `cpa-redis` | ✅ Running |

**Quick Check:**
```bash
# Scheduler
curl http://localhost:8000/health

# Server  
curl http://localhost:8001/health

# Redis (via Docker)
docker exec cpa-redis redis-cli ping
```

---

## 📋 Quick Start

### Option 1: Interactive Script (Recommended)

```bash
./dev-local.sh
```

Select the service(s) you want to run:
- **1** - Scheduler only (port 8000)
- **2** - Server only (port 8001)  
- **3** - Calculation Agent only (port 8002)
- **4** - All services in parallel

### Option 2: Manual Commands

See [Manual Setup](#manual-setup) below.

---

## 🌐 Service Overview & Swagger URLs

| Service | Port | Swagger UI | Health Check | Description |
|---------|------|------------|--------------|-------------|
| **Scheduler** | 8000 | [http://localhost:8000/docs](http://localhost:8000/docs) | [/health](http://localhost:8000/health) | Job orchestration & task queue |
| **Server** | 8001 | [http://localhost:8001/docs](http://localhost:8001/docs) | [/health](http://localhost:8001/health) | Agent monitoring, logs, screenshots |
| **Calculation Agent** | 8002 | [http://localhost:8002/docs](http://localhost:8002/docs) | [/health](http://localhost:8002/health) | Example test agent (math operations) |

**Additional Endpoints:**
- **ReDoc** (alternative docs): Available at `/redoc` for each service
- **OpenAPI JSON**: Available at `/openapi.json` for each service

---

## 📚 API Endpoints Overview

### Scheduler (port 8000)

**Jobs API:**
- `POST /jobs` - Submit new job
- `GET /jobs/{job_id}` - Get job status
- `GET /jobs` - List all jobs
- `DELETE /jobs/{job_id}` - Cancel job

**Health & Status:**
- `GET /health` - Service health check
- `GET /` - Welcome message with version

### Server (port 8001)

**Agents API:**
- `GET /api/v1/agents` - List all agents
- `POST /api/v1/agents` - Register new agent
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `DELETE /api/v1/agents/{agent_id}` - Delete agent

**Logs API:**
- `GET /api/v1/logs` - Get logs (filterable by agent, level, time)
- `POST /api/v1/logs` - Add log entry

**Screenshots API:**
- `GET /api/v1/screenshots` - List screenshots
- `GET /api/v1/screenshots/{screenshot_id}` - Get screenshot details
- `POST /api/v1/screenshots` - Upload screenshot

### Calculation Agent (port 8002)

**Agent Communication Protocol:**
- `POST /agent/message` - Send message to agent (Agent Standard v1 protocol)
- `GET /health` - Agent health check
- `GET /manifest` - Get agent manifest (capabilities, ethics, etc.)

---

## 🛠️ Manual Setup

### Prerequisites

```bash
# Python 3.11+
python3 --version

# Poetry (recommended) or pip
poetry --version

# Redis (required for scheduler)
redis-cli ping
# If not running: brew install redis && redis-server
```

### 1. Install Dependencies

**Using Poetry (recommended):**
```bash
poetry install
```

**Using pip:**
```bash
pip install -e .
```

### 2. Environment Setup

```bash
# .env file already created from .env.example
# Edit if needed:
nano .env
```

Key variables:
- `REDIS_URL` - Redis connection (default: `redis://localhost:6379/0`)
- `DATABASE_URL` - SQLite path (default: `sqlite:///./data/scheduler.db`)
- `OPENAI_API_KEY` - Optional, for LLM features
- `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR

### 3. Create Data Directories

```bash
mkdir -p data logs uploads/screenshots
```

### 4. Start Services Individually

**Scheduler:**
```bash
poetry run uvicorn scheduler.main:app --host 0.0.0.0 --port 8000 --reload
# Or with pip: python -m uvicorn scheduler.main:app --host 0.0.0.0 --port 8000 --reload
```

**Server:**
```bash
PORT=8001 poetry run uvicorn server.main:app --host 0.0.0.0 --port 8001 --reload
```

**Calculation Agent:**
```bash
cd platform/agentify/agents/calculation_agent
pip install -r requirements.txt
PORT=8002 python main.py
```

---

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Start scheduler + Redis
docker-compose up scheduler redis

# Access Swagger:
open http://localhost:8000/docs
```

For observability (Jaeger, Prometheus, Grafana):
```bash
docker-compose --profile observability up
```

---

## 🧪 Testing the APIs

### Using Swagger UI

1. Navigate to any service's Swagger page (e.g., http://localhost:8000/docs)
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"
5. View response

### Using curl

**Scheduler - Submit Job:**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-001",
    "tasks": [
      {
        "task_id": "task-1",
        "action": "click",
        "selector": "500,300"
      }
    ]
  }'
```

**Server - Register Agent:**
```bash
curl -X POST http://localhost:8001/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent-001",
    "name": "Test Agent",
    "status": "active",
    "capabilities": ["testing"]
  }'
```

**Calculation Agent - Calculate:**
```bash
curl -X POST http://localhost:8002/agent/message \
  -H "Content-Type: application/json" \
  -d '{
    "type": "request",
    "sender": "test-client",
    "to": ["agent.calculator.calculation"],
    "intent": "calculate",
    "payload": {
      "a": 5,
      "b": 3,
      "op": "+"
    }
  }'
```

---

## 🔍 Exploring the Code

### Key Files by Service

**Scheduler:**
- `scheduler/main.py` - FastAPI app entry point
- `scheduler/api/jobs.py` - Jobs endpoints
- `scheduler/queue/job_queue.py` - Redis-backed job queue
- `scheduler/config/settings.py` - Configuration

**Server:**
- `server/main.py` - FastAPI app entry point
- `server/api/v1/agents.py` - Agents API
- `server/api/v1/logs.py` - Logs API
- `server/api/v1/screenshots.py` - Screenshots API
- `server/db/models.py` - SQLAlchemy models

**Calculation Agent:**
- `platform/agentify/agents/calculation_agent/main.py` - Agent implementation
- `platform/agentify/agents/calculation_agent/manifest.json` - Agent Standard v1 manifest

---

## 🐛 Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server --daemonize yes

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process (replace PID)
kill -9 <PID>

# Or use a different port
PORT=8080 uvicorn scheduler.main:app --port 8080
```

### Import Errors
```bash
# Reinstall dependencies
poetry install --no-cache

# Or with pip
pip install -e . --force-reinstall
```

### Database Issues
```bash
# Remove and recreate SQLite DB
rm data/scheduler.db
# DB will be recreated on next startup
```

---

## 📖 Additional Resources

- **Main README**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Agent Standard**: [core/agent_standard/README.md](core/agent_standard/README.md)
- **Agentify Platform**: [platform/agentify/README.md](platform/agentify/README.md)

---

## 💡 Tips

- **Auto-reload enabled**: Changes to Python files automatically restart the service
- **Structured logging**: All logs use JSON format (see `logs/` directory)
- **Health checks**: Use `/health` endpoints to verify services are running
- **CORS**: Pre-configured for `localhost:3000` (React) and `localhost:8080`
- **API versioning**: Server uses `/api/v1/` prefix for future compatibility

---

**Happy coding! 🚀**
