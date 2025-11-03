# 🤖 CPA Scheduler/Planner

**Central orchestration component for Cognitive Process Automation (CPA)**

The CPA Scheduler/Planner is the heart of the CPA architecture, orchestrating tasks between channels (Email, Chat, Voice) and the CPA Desktop AI using the LAM (Lumina Agent Messages) protocol.

## 🎯 Features

- **LAM Protocol**: Standardized agent-to-agent communication
- **Task Orchestration**: Dependency-based parallel/sequential task execution
- **LLM Integration**: OpenAI GPT-4 for intent routing and task planning
- **Multi-Executor**: Web (Playwright), Email (Graph API), Desktop (UIA)
- **Observability**: OpenTelemetry tracing, Prometheus metrics, Grafana dashboards
- **Security**: API key auth, rate limiting, policy engine, audit trail
- **Scalable**: Redis queue, async execution, horizontal scaling ready

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│ Channels (Email, Chat, Voice)       │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│ Scheduler/Planner                   │
│ • Intent Router                     │
│ • Task Graph Builder                │
│ • Job Queue (Redis)                 │
│ • LAM Protocol Handler              │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│ CPA Desktop AI                      │
│ • Observe/Think/Act/Verify          │
│ • Executors (Playwright, UIA, Mail) │
└─────────────────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Docker & Docker Compose (optional)
- Redis (or use Docker)
- OpenAI API Key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 01_CPA
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Start Redis**
   ```bash
   docker-compose up redis -d
   ```

5. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

6. **Install Playwright browsers**
   ```bash
   poetry run playwright install chromium
   ```

7. **Start the scheduler**
   ```bash
   poetry run uvicorn scheduler.main:app --reload
   ```

8. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Setup

1. **Build and start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f scheduler
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

### With Observability Stack

```bash
docker-compose --profile observability up -d
```

Access:
- Jaeger UI: http://localhost:16686
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [TODO](docs/TODO.md) - Development roadmap and tasks
- [API Examples](docs/API_EXAMPLES.md) - API usage examples (coming soon)
- [LAM Protocol](docs/LAM_PROTOCOL.md) - LAM message specification (coming soon)
- [Executor Guide](docs/EXECUTOR_GUIDE.md) - Custom executor development (coming soon)

## 🧪 Testing

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

## 🔧 Development

### Code Quality

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

### Project Structure

```
01_CPA/
├── scheduler/              # Main application code
│   ├── core/              # Core components (LAM, Task Graph, Intent Router)
│   ├── api/               # FastAPI endpoints
│   ├── orchestrator/      # Task orchestration logic
│   ├── llm/               # LLM provider abstraction
│   ├── queue/             # Job queue (Redis)
│   ├── repository/        # Database repositories
│   ├── executors/         # Task executors (Playwright, Mail, etc.)
│   ├── security/          # Auth, policies, secrets
│   ├── telemetry/         # OpenTelemetry, metrics
│   └── config/            # Configuration files
├── tests/                 # Test suite
├── docs/                  # Documentation
├── data/                  # Data storage (SQLite, screenshots)
└── docker-compose.yml     # Docker setup
```

## 🌐 API Endpoints

### Inbound Gate
- `POST /schedule` - Schedule a new task
- `POST /lam/message` - Receive LAM message
- `GET /health` - Health check

### Job Management
- `GET /jobs` - List jobs (paginated)
- `GET /jobs/{job_id}` - Get job status
- `DELETE /jobs/{job_id}` - Cancel job
- `POST /jobs/{job_id}/retry` - Retry failed job
- `WS /ws/jobs/{job_id}` - Live job updates (WebSocket)

### Monitoring
- `GET /metrics` - Prometheus metrics
- `GET /audit` - Query audit log

## 🔐 Security

- **Authentication**: API Key (Header: `X-API-Key`)
- **Rate Limiting**: Per IP and per API key
- **Policy Engine**: App allowlist, action blacklist, PII detection
- **Audit Trail**: Every action logged with screenshot
- **Secrets Management**: Environment variables (later: Vault integration)

## 📊 Monitoring

- **Tracing**: OpenTelemetry → Jaeger
- **Metrics**: Prometheus
- **Dashboards**: Grafana
- **Logging**: structlog (JSON format)

## 🚢 Deployment

### Railway

1. Create new project on Railway
2. Connect GitHub repository
3. Add Redis add-on
4. Set environment variables (see `.env.example`)
5. Deploy from `main` branch

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide (coming soon).

## 🛣️ Roadmap

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

See [docs/TODO.md](docs/TODO.md) for detailed task list.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run code quality checks
5. Submit a pull request

## 📝 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Playwright](https://playwright.dev/)
- [OpenAI](https://openai.com/)
- [Redis](https://redis.io/)
- [OpenTelemetry](https://opentelemetry.io/)

---

**Status**: 🚧 In Development  
**Version**: 0.1.0  
**Last Updated**: 2025-11-03

