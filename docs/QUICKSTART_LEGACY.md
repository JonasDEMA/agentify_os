# 🚀 Legacy CPA Scheduler/Planner - Quick Start

**This is the legacy documentation for the original CPA Scheduler/Planner.**

The CPA Scheduler/Planner is now integrated as a **tool category** within the **Agent Standard v1** framework. For the new Agent Standard v1 documentation, see [Agent Standard v1 Quick Start](../core/agent_standard/QUICKSTART.md).

---

## 📋 **Prerequisites**

- Python 3.11+
- Poetry
- Docker & Docker Compose (optional)
- Redis (or use Docker)
- OpenAI API Key

---

## 🏗️ **Local Setup**

### **1. Clone the repository**

```bash
git clone <repository-url>
cd 01_CPA
```

### **2. Install dependencies**

```bash
poetry install
```

### **3. Configure environment**

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### **4. Start Redis**

```bash
docker-compose up redis -d
```

### **5. Run database migrations**

```bash
poetry run alembic upgrade head
```

### **6. Install Playwright browsers**

```bash
poetry run playwright install chromium
```

### **7. Start the scheduler**

```bash
poetry run uvicorn scheduler.main:app --reload
```

### **8. Access the API**

- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🐳 **Docker Setup**

### **1. Build and start all services**

```bash
docker-compose up -d
```

### **2. View logs**

```bash
docker-compose logs -f scheduler
```

### **3. Stop services**

```bash
docker-compose down
```

---

## 📊 **With Observability Stack**

```bash
docker-compose --profile observability up -d
```

**Access:**
- Jaeger UI: http://localhost:16686
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)

---

## 🌐 **API Endpoints**

### **Inbound Gate**
- `POST /schedule` - Schedule a new task
- `POST /lam/message` - Receive LAM message
- `GET /health` - Health check

### **Job Management**
- `GET /jobs` - List jobs (paginated)
- `GET /jobs/{job_id}` - Get job status
- `DELETE /jobs/{job_id}` - Cancel job
- `POST /jobs/{job_id}/retry` - Retry failed job
- `WS /ws/jobs/{job_id}` - Live job updates (WebSocket)

### **Monitoring**
- `GET /metrics` - Prometheus metrics
- `GET /audit` - Query audit log

---

## 🔐 **Security**

- **Authentication**: API Key (Header: `X-API-Key`)
- **Rate Limiting**: Per IP and per API key
- **Policy Engine**: App allowlist, action blacklist, PII detection
- **Audit Trail**: Every action logged with screenshot
- **Secrets Management**: Environment variables

---

## 📊 **Monitoring**

- **Tracing**: OpenTelemetry → Jaeger
- **Metrics**: Prometheus
- **Dashboards**: Grafana
- **Logging**: structlog (JSON format)

---

## 🧪 **Testing**

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/core/test_task_graph.py

# Run integration tests
poetry run pytest tests/integration/

# Run load tests
poetry run locust -f tests/load/locustfile.py
```

---

## 🔧 **Development**

### **Code Quality**

```bash
# Linting
poetry run ruff check .

# Type checking
poetry run mypy scheduler/

# Formatting
poetry run black .

# Pre-commit hooks
poetry run pre-commit install
poetry run pre-commit run --all-files
```

---

## 🚢 **Deployment**

### **Railway**

1. Create new project on Railway
2. Connect GitHub repository
3. Add Redis add-on
4. Set environment variables (see `.env.example`)
5. Deploy from `main` branch

See [docs/DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide.

---

## 🛣️ **Roadmap**

- [x] Project setup
- [ ] Phase 1: Foundation & Core (LAM, Task Graph, Intent Router)
- [ ] Phase 2: API & Orchestration
- [ ] Phase 3: LLM Integration
- [ ] Phase 4: Database & Persistence
- [ ] Phase 5: Minimal CPA Integration (Playwright, Mail)
- [ ] Phase 6: Observability & Security
- [ ] Phase 7: Deployment & DevOps
- [ ] Phase 8: Documentation & Testing
- [ ] Phase 9: Advanced Features (Agent Discovery, Human-in-the-Loop)

See [docs/TODO.md](TODO.md) for detailed task list.

---

## 📚 **Documentation**

- [Architecture](ARCHITECTURE.md) - System architecture and design
- [TODO](TODO.md) - Development roadmap and tasks
- [LAM Protocol](LAM_PROTOCOL.md) - LAM message specification (coming soon)

---

## 🔗 **Migration to Agent Standard v1**

The legacy CPA Scheduler/Planner is now integrated as a **tool category** within the Agent Standard v1 framework.

**Benefits of migrating:**
- ✅ Runtime-active ethics
- ✅ Health monitoring
- ✅ Four-eyes principle
- ✅ Universal deployment (Cloud/Edge/Desktop)
- ✅ 3 lines to compliance

**Migration Guide:**

See [Agent Standard v1 Quick Start](../core/agent_standard/QUICKSTART.md) for the new framework.

---

**For new projects, we recommend using Agent Standard v1 instead of the legacy CPA Scheduler/Planner.**

**See [Agent Standard v1 Quick Start](../core/agent_standard/QUICKSTART.md) to get started! 🚀**

