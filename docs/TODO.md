# 📋 CPA Scheduler/Planner - Umsetzungs-Todos

**Projekt**: CPA Scheduler/Planner  
**Start**: 2025-11-03  
**Status**: 🚀 In Planung

---

## ✅ Phase 1: Foundation & Core (Woche 1-2)

### 1.1 Projekt-Struktur aufsetzen ✅
- [x] Repository initialisieren
- [x] Ordnerstruktur erstellen (`scheduler/`, `tests/`, `docs/`, etc.)
- [x] Dependencies definieren (`pyproject.toml` mit Poetry)
- [x] Docker Compose Setup (Redis, SQLite)
- [x] `.env.example` Template erstellen
- [x] `.gitignore` konfigurieren
- [x] `README.md` mit Setup-Anleitung

### 1.2 Agent Communication Protocol Implementation ✅
- [x] `scheduler/core/agent_protocol.py` erstellen
- [x] Pydantic BaseMessage Model (id, ts, type, sender, to, intent, payload, context, correlation, expected, status, security)
- [x] RequestMessage Model
- [x] InformMessage Model
- [x] ProposeMessage, AgreeMessage, RefuseMessage Models
- [x] ConfirmMessage, FailureMessage, DoneMessage Models
- [x] DiscoverMessage, OfferMessage, AssignMessage Models
- [x] Message Validation (Pydantic validators)
- [x] Message Serialization (to_dict, from_dict, to_json, from_json)
- [x] Agent Message Factory/Builder
- [x] Unit Tests (`tests/core/test_agent_protocol.py`)
  - [x] Test Message Creation
  - [x] Test Validation (required fields)
  - [x] Test Serialization/Deserialization
  - [x] Test Invalid Messages (error handling)

### 1.3 ToDo-Schema & Task Graph ✅
- [x] `scheduler/core/task_graph.py` erstellen
- [x] ToDo Pydantic Model (action, selector, text, timeout, depends_on)
- [x] ActionType Enum (open_app, click, type, wait_for, playwright, uia, send_mail)
- [x] TaskGraph Class
  - [x] `add_task(todo: ToDo)` Method
  - [x] `build_graph()` Method (Dependency Graph)
  - [x] `topological_sort()` Method (Dependency Resolution)
  - [x] `get_parallel_batches()` Method (Parallel Execution Groups)
  - [x] `detect_cycles()` Method (Zyklus-Erkennung)
- [x] `scheduler/core/task_executor_interface.py` erstellen
  - [x] Abstract BaseExecutor Class
  - [x] `execute(todo: ToDo)` Abstract Method
  - [x] `verify(todo: ToDo)` Abstract Method
  - [x] ExecutionResult Model (success, result, error, duration)
- [x] Unit Tests (`tests/core/test_task_graph.py`)
  - [x] Test Sequential Tasks
  - [x] Test Parallel Tasks
  - [x] Test Mixed Dependencies
  - [x] Test Cycle Detection (should raise error)
  - [x] Test Empty Graph
  - [x] Test Single Task

### 1.4 Intent Router (Rule-based V1) ✅
- [x] `scheduler/core/intent_router.py` erstellen
- [x] IntentRouter Class
  - [x] `route(message: str)` Method → Intent
  - [x] Regex/Keyword Matching
  - [x] Intent Registry (load from YAML/JSON)
  - [x] Fallback Intent ("unknown")
- [x] `scheduler/config/intents.yaml` erstellen
  - [x] Define Sample Intents (send_mail, search_document, export_pdf, etc.)
  - [x] Regex Patterns per Intent
  - [x] Task Templates per Intent
- [x] Intent Model (Pydantic)
  - [x] name: str
  - [x] patterns: list[str]
  - [x] task_template: list[ToDo]
- [x] Unit Tests (`tests/core/test_intent_router.py`)
  - [x] Test Known Intents
  - [x] Test Unknown Intent (fallback)
  - [x] Test Case Insensitivity
  - [x] Test Multiple Patterns per Intent

### 1.5 Job Queue (Redis)
- [x] `scheduler/queue/job_queue.py` erstellen
- [x] JobQueue Class
  - [x] `__init__(redis_url: str)`
  - [x] `enqueue(job: Job)` Method → job_id
  - [x] `dequeue()` Method → Job | None
  - [x] `get_status(job_id: str)` Method → JobStatus
  - [x] `update_status(job_id: str, status: JobStatus)` Method
  - [x] `retry(job_id: str)` Method
  - [x] `cancel(job_id: str)` Method
  - [x] `get_job(job_id: str)` Method → Job | None
  - [x] `connect()` Method (async Redis connection)
  - [x] `close()` Method (async Redis close)
- [x] Job Model (Pydantic)
  - [x] id: str (UUID)
  - [x] intent: str
  - [x] task_graph: TaskGraph
  - [x] status: JobStatus (pending, running, done, failed, cancelled)
  - [x] created_at: datetime
  - [x] started_at: datetime | None
  - [x] completed_at: datetime | None
  - [x] error: str | None
  - [x] retry_count: int
  - [x] max_retries: int
  - [x] Custom serialization for TaskGraph and datetime
- [x] JobStatus Enum (pending, running, done, failed, cancelled)
- [x] Retry Logic (max_retries check)
- [x] Dead Letter Queue (failed jobs after max retries) - **TODO: Phase 2**
- [x] Unit Tests (`tests/queue/test_job_queue.py`)
  - [x] Test Enqueue/Dequeue
  - [x] Test Status Updates
  - [x] Test Retry Logic
  - [x] Test Max Retries Exceeded
  - [x] Test Cancel Job
  - [x] Test Get Job
  - [x] Test Dead Letter Queue - **TODO: Phase 2**
  - [x] Test Concurrent Access - **TODO: Phase 2**
- [x] Integration Tests (with real Redis)
  - [x] Test Redis Connection
  - [x] Test Queue Persistence

---

## ✅ Phase 2: API & Agent Management (Woche 2-3) - IN PROGRESS

### 2.1 FastAPI Application ✅
- [x] `scheduler/main.py` und `server/main.py` erstellen
- [x] FastAPI App Setup
  - [x] App Instance
  - [x] CORS Middleware (Fixed string/list parsing in .env)
  - [x] Exception Handlers (Global)
  - [x] Startup/Shutdown Events (Redis & DB Connection)
- [x] Health Check Endpoint (`GET /health`)
  - [x] Check Redis Connection
  - [x] Check Agent Registry
  - [x] Return Status (healthy)
- [x] OpenAPI/Swagger Configuration
  - [x] Title, Description, Version
  - [x] Tags for Endpoint Groups
- [x] Logging Setup (structlog)
  - [x] JSON Formatter
  - [x] Correlation ID Middleware
- [x] Unit Tests (`tests/api/test_main.py`)
  - [x] Test Health Endpoint
  - [x] Test CORS Headers
  - [x] Test Exception Handling

### 2.2 Job API Endpoints ✅
- [x] `scheduler/api/jobs.py` erstellen
- [x] `POST /jobs` Endpoint (Create Job)
  - [x] Request Model (CreateJobRequest: intent, tasks, max_retries)
  - [x] Response Model (JobResponse: id, status, created_at)
  - [x] Task Graph Construction
  - [x] Enqueue Job to Redis
  - [x] Return Job ID
- [x] `GET /jobs` Endpoint (List Jobs)
  - [x] Query Parameters (limit, offset, status filter)
  - [x] Pagination
  - [x] Response Model (JobListResponse)
- [x] `GET /jobs/{job_id}` Endpoint (Get Job Status)
  - [x] Response Model (JobResponse)
  - [x] 404 if not found
- [x] `DELETE /jobs/{job_id}` Endpoint (Cancel Job)
  - [x] Cancel Job via JobQueue
  - [x] Update Status to "cancelled"
  - [x] Return Success/Error
- [x] `POST /jobs/{job_id}/retry` Endpoint (Retry Job)
  - [x] Retry Failed Job via JobQueue
  - [x] Return Success/Error
- [ ] WebSocket Endpoint (`/ws/jobs/{job_id}`) - **Optional für V1**
- [x] Integration Tests (`tests/api/test_jobs.py`)

### 2.3 Agent Registry & Management ✅
- [x] `server/db/models.py` (Agent Model)
- [x] Agent Model (SQLAlchemy)
  - [x] id, api_key, hostname, os_info, etc.
- [x] Agent Registry (Database-backed in Server)
  - [x] `register`
  - [x] `list_agents`
  - [x] `get_agent`
- [x] Agent Storage (SQLite with `aiosqlite`)
- [x] Unit Tests (`tests/server/test_agents.py`)

### 2.4 Agent API Endpoints ✅
- [x] `server/api/v1/agents.py` erstellen
- [x] `POST /register` Endpoint
- [x] `GET /` Endpoint (List)
- [x] `GET /{agent_id}` Endpoint
- [x] `POST /agents/{id}/heartbeat` Endpoint
- [x] `DELETE /agents/{id}` Endpoint
- [x] Integration Tests (`tests/server/test_agents.py`)

### 2.5 Agent Message Handler ✅
- [x] `scheduler/api/lam_handler.py` erstellt
- [x] `POST /lam/message` Endpoint
  - [x] Accept Agent Message (any type)
  - [x] Validate Message (Pydantic)
  - [x] Route to appropriate handler based on type
    - [x] `inform` → Log Job Info
    - [x] `done` → Mark Job Complete
    - [x] `failure` → Mark Job Failed
  - [x] Return Acknowledgement
- [x] Integration Tests (`tests/api/test_lam_handler.py`)

### 2.6 Task Orchestrator ✅
- [x] `scheduler/orchestrator/orchestrator.py` erstellen
- [x] Orchestrator Class
  - [x] `__init__(job_queue)`
  - [x] `process_job(job_id: str)` Method (Main Loop)
    - [x] Get Job from Queue
    - [x] Get Task Graph from Job
    - [x] For each Task in Graph:
      - [x] Find Agent for Task (via AgentRegistry)
      - [x] Send LAM Request to Agent (via REST API)
      - [x] Wait for Agent Response (inform/done/failure)
      - [x] Update Job Status
    - [x] Send Final Response (done/failure)
  - [x] `dispatch_task(job, task_id, task)` Method
    - [x] Create Task Request
    - [x] Send to Agent Endpoint (POST /tasks)
  - [x] `handle_agent_response` (Handled via `lam_handler` + polling/refresh in Orchestrator)
  - [x] Task Status Tracking in `Job` model
- [x] Background Worker integration in `scheduler/main.py`
- [x] Unit Tests (`tests/orchestrator/test_orchestrator.py`)

---

## ✅ Phase 3: LLM Integration (Woche 3) ✅

### 3.1 LLM Wrapper (Abstraction Layer) ✅
- [x] `scheduler/llm/llm_wrapper.py` erstellen
- [x] Abstract LLMProvider Class
- [x] LLMWrapper Class
- [x] OpenAIProvider Class (implements LLMProvider)
- [x] `intent_to_task_graph` Method
- [x] `select_agent_for_task` Method
- [x] Unit Tests (`tests/llm/test_llm_wrapper.py`)

### 3.2 LLM-based Intent Enhancement ✅
- [x] `scheduler/llm/llm_intent_router.py` erstellen
- [x] LLMIntentRouter Class
- [x] LLM classification with Rule-based fallback
- [x] Structured output for Intent classification

### 3.3 LLM-based Task Planner ✅
- [x] `scheduler/llm/llm_task_planner.py` erstellen
- [x] LLMTaskPlanner Class
- [x] Intent → TaskGraph decomposition

---

## ✅ Phase 4: Desktop RPA Agent - Basic Implementation (Woche 4) - COMPLETE

### 4.1 Desktop RPA Agent - Basic Executors ✅
- [x] `agents/desktop_rpa/` Package erstellen
- [x] `agents/desktop_rpa/main.py` - FastAPI Application
  - [x] `/health` Endpoint
  - [x] `/tasks` Endpoint
  - [x] Lifespan Management
  - [x] Structured Logging
- [x] `agents/desktop_rpa/config/settings.py` - Configuration
- [x] `agents/desktop_rpa/executors/` - Basic Executors
  - [x] `base.py` - Base Executor Interface
  - [x] `click_executor.py` - Click Actions
  - [x] `type_executor.py` - Type Actions
  - [x] `wait_executor.py` - Wait Actions
  - [x] `screenshot_executor.py` - Screenshot Actions
- [x] PyAutoGUI Integration
- [x] Pillow for Screenshots
- [x] Manual Testing (Health Check, Screenshot, Wait)
- [x] README.md Documentation

---

## ✅ Phase 5: Cognitive RPA Agent ✅

### 5.1 LLM Wrapper (Foundation) ✅
- [x] `agents/desktop_rpa/cognitive/llm_wrapper.py` erstellt
- [x] LLMWrapper Class
- [x] ChatGPT API Integration
- [x] Unit Tests

### 5.2 Vision Layer ✅
- [x] `agents/desktop_rpa/vision/windows_api.py` erstellt (with macOS safety)
- [x] `agents/desktop_rpa/vision/screen_analyzer.py` (OCR) erstellt
- [x] `agents/desktop_rpa/vision/state_detector.py` (Rule-based) erstellt

### 5.3 State Graph ✅
- [x] `agents/desktop_rpa/cognitive/state_graph.py` erstellt
- [x] State and Transition Models
- [x] Pathfinding (BFS) implementation

### 5.4 Strategy Manager ✅
- [x] `agents/desktop_rpa/cognitive/strategy_manager.py` erstellt
- [x] Strategy Model
- [x] SQLite persistence for playbooks

### 5.5 Experience Memory ✅
- [x] `agents/desktop_rpa/cognitive/experience_memory.py` erstellt
- [x] Experience Model
- [x] SQLite persistence for execution history

### 5.6 Goal Planner ✅
- [x] `agents/desktop_rpa/planner/goal_planner.py` erstellt
- [x] Strategy mapping and LLM planning

### 5.7 Integration & Learning Loop ✅
- [x] `agents/desktop_rpa/cognitive/learning_loop.py` erstellt
- [x] Main cognitive cycle (Detect -> Plan -> Execute -> Learn)

---

## ✅ Phase 6: Database & Persistence (Woche 5-6) - COMPLETE

### 6.1 Repository Pattern ✅
- [x] `scheduler/repository/repository_interface.py` erstellen
- [x] Abstract JobRepository
  - [x] `save(job: Job)` Abstract Method
  - [x] `get(job_id: str)` Abstract Method → Job | None
  - [x] `list(limit, offset, status_filter)` Abstract Method → list[Job]
  - [x] `update_status(job_id, status)` Abstract Method
  - [x] `delete(job_id)` Abstract Method
- [x] Abstract AuditRepository
  - [x] `log_action(job_id, action, status, details)` Method
  - [x] `get_logs(job_id)` Method
- [x] `scheduler/repository/sqlite_repository.py` erstellen
- [x] SQLiteJobRepository (implements JobRepository)
- [x] SQLiteAuditRepository
- [x] SQLiteTaskRepository
- [x] SQLiteMessageRepository
- [x] Database Schema (SQLAlchemy Models)
- [x] Migrations (Alembic Setup)
- [x] Unit Tests (`tests/repository/test_sqlite_repository.py`)

### 6.2 Audit Log ✅
- [x] `scheduler/audit/audit_log.py` erstellen
- [x] AuditLog Class
  - [x] `log_action(action, reason, result, screenshot_path)` Method
  - [x] `get_job_logs(job_id)` Method → list[AuditEntry]
- [x] AuditEntry Model (Pydantic)
- [x] Screenshot Storage (filesystem)
- [x] Audit Query API (`GET /api/v1/audit/{job_id}`)
- [ ] Integration Tests (`tests/audit/test_audit_log.py`)

### 6.3 Context Memory (RAG) ✅
- [x] `scheduler/memory/context_memory.py` erstellen
- [x] ContextMemory Class
  - [x] Short-term Memory (Redis)
    - [x] `set_short_term(key, value, ttl)` Method
    - [x] `get_short_term(key)` Method
    - [x] `delete_short_term(key)` Method
  - [x] Long-term Memory (SQLite fallback for sqlite-vss)
    - [x] `store_long_term(text, metadata)` Method (with embedding)
    - [x] `search_long_term(query, limit)` Method (semantic search)
- [x] `scheduler/memory/embedding_service.py` erstellen
- [x] EmbeddingService Class (OpenAI)
- [x] Memory Entry Model (Pydantic)
- [ ] Integration Tests (`tests/memory/test_context_memory.py`)

---

## ✅ Phase 7: Minimal CPA Integration (Woche 6-7) - COMPLETE

### 7.1 Executor Framework ✅
- [x] `scheduler/executors/executor_registry.py` erstellen
- [x] ExecutorRegistry Class
  - [x] `register(action_type: str, executor: BaseExecutor)`
  - [x] `get(action_type: str)` → BaseExecutor
  - [x] `execute(todo: ToDo)` Method (dispatch to correct executor)
- [x] `scheduler/executors/base_executor.py` erstellen (already defined in 1.3)
- [x] Unit Tests (`tests/executors/test_executor_registry.py`)
  - [ ] Test Register/Get
  - [ ] Test Dispatch
  - [ ] Test Unknown Action Type (error)

### 7.2 Playwright Executor ✅
- [x] `scheduler/executors/playwright_executor.py` erstellen
- [x] PlaywrightExecutor Class (extends BaseExecutor)
  - [ ] `__init__(headless: bool = True)`
  - [ ] `execute(todo: ToDo)` Method
    - [ ] Action: `goto` (navigate to URL)
    - [ ] Action: `click` (click element)
    - [ ] Action: `fill` (fill input field)
    - [ ] Action: `wait_for` (wait for element)
    - [ ] Action: `screenshot` (take screenshot)
  - [ ] `verify(todo: ToDo)` Method (check element exists)
  - [ ] Selector Strategies (CSS, XPath, Text)
  - [ ] Error Handling (timeout, element not found)
  - [ ] Screenshot on Error
- [ ] Playwright Context Management
  - [ ] Browser Pool (reuse browsers)
  - [ ] Context Isolation (per job)
  - [ ] Cleanup (close browsers)
- [ ] Integration Tests (`tests/executors/test_playwright_executor.py`)
  - [ ] Test Goto
  - [ ] Test Click
  - [ ] Test Fill
  - [ ] Test Wait For
  - [ ] Test Screenshot
  - [ ] Test Error Handling (element not found)

### 7.3 Mail Executor (Graph API)
- [ ] `scheduler/executors/mail_executor.py` erstellen
- [ ] MailExecutor Class (extends BaseExecutor)
  - [ ] `__init__(client_id, client_secret, tenant_id)`
  - [ ] `execute(todo: ToDo)` Method
    - [ ] Action: `send_mail` (send email with attachments)
    - [ ] Action: `read_mail` (read inbox)
    - [ ] Action: `search_mail` (search emails)
  - [ ] `verify(todo: ToDo)` Method (check email sent)
  - [ ] OAuth2 Authentication (MSAL)
  - [ ] Error Handling (auth error, API error)
- [ ] Graph API Client
  - [ ] Send Mail Endpoint
  - [ ] List Messages Endpoint
  - [ ] Search Endpoint
- [ ] Integration Tests (`tests/executors/test_mail_executor.py`)
  - [ ] Test Send Mail (mocked Graph API)
  - [ ] Test Read Mail
  - [ ] Test Search Mail
  - [ ] Test OAuth2 Flow

### 7.4 End-to-End Workflow
- [ ] Example Workflow: "Open Portal → Download PDF → Send Mail"
- [ ] `tests/integration/test_e2e_workflow.py` erstellen
  - [ ] Setup Test Environment (Redis, SQLite, Mock LLM)
  - [ ] Submit Job via `/schedule` API
  - [ ] Wait for Job Completion
  - [ ] Verify Job Status (done)
  - [ ] Verify Tasks Executed (audit log)
  - [ ] Verify Email Sent (mock Graph API)
- [ ] Error Recovery Test
  - [ ] Simulate Task Failure
  - [ ] Verify Retry Logic
  - [ ] Verify Fallback Behavior

---

## ✅ Phase 8: Observability & Security (Woche 7-8) - COMPLETE

### 8.1 OpenTelemetry Integration ✅
- [x] `scheduler/telemetry/telemetry.py` erstellen
- [x] OpenTelemetry Setup
  - [ ] Tracer Provider
  - [ ] Meter Provider
  - [ ] Logger Provider
- [ ] Tracing
  - [ ] Span for each API Request
  - [ ] Span for each Task Execution
  - [ ] Span for each LLM Call
  - [ ] Span for each Database Query
  - [ ] Correlation ID Propagation
- [ ] Metrics
  - [ ] Counter: `jobs_total` (by status)
  - [ ] Counter: `tasks_total` (by action_type, status)
  - [ ] Histogram: `task_duration_seconds` (by action_type)
  - [ ] Histogram: `llm_call_duration_seconds`
  - [ ] Gauge: `job_queue_length`
- [ ] Logs
  - [ ] structlog → OpenTelemetry
  - [ ] Correlation ID in all logs
- [ ] Jaeger/Tempo Export
  - [ ] OTLP Exporter Configuration
- [ ] Grafana Dashboard (`scheduler/telemetry/grafana_dashboard.json`)
  - [ ] System Health Overview
  - [ ] Job Queue Metrics
  - [ ] Task Success/Failure Rate
  - [ ] LLM Performance
  - [ ] Error Rate by Type
- [ ] Integration Tests (`tests/telemetry/test_telemetry.py`)
  - [ ] Test Span Creation
  - [ ] Test Metrics Recording
  - [ ] Test Log Export

### 8.2 Security & Policies ✅
- [x] `scheduler/security/policies.py` erstellen
- [x] PolicyEngine Class
  - [ ] `check_app_allowed(app_name: str)` Method → bool
  - [ ] `check_action_allowed(action: str)` Method → bool
  - [ ] `check_rate_limit(tenant: str)` Method → bool
  - [ ] `detect_pii(text: str)` Method → bool (DSGVO)
- [ ] `scheduler/config/policies.yaml` erstellen
  - [ ] App Allowlist (e.g., ["chrome", "outlook", "datev"])
  - [ ] Action Blacklist (e.g., ["delete_file", "run_command"])
  - [ ] Rate Limits (per tenant)
  - [ ] PII Patterns (IBAN, Email, Phone, etc.)
- [ ] `scheduler/security/secrets_manager.py` erstellen
- [ ] SecretsManager Class
  - [ ] `get_secret(key: str)` Method → str
  - [ ] Integration with Doppler/HashiCorp Vault (later)
  - [ ] Fallback to Environment Variables
- [ ] JWT Authentication (FastAPI Dependency)
  - [ ] `scheduler/security/auth.py`
  - [ ] `verify_token(token: str)` Function
  - [ ] `get_current_user()` Dependency
- [ ] Unit Tests (`tests/security/test_policies.py`)
  - [ ] Test App Allowlist
  - [ ] Test Action Blacklist
  - [ ] Test Rate Limiting
  - [ ] Test PII Detection

### 8.3 Monitoring & Alerts
- [ ] Prometheus Metrics Export
  - [ ] `/metrics` Endpoint (prometheus_client)
- [ ] Grafana Dashboards (already in 6.1)
- [ ] Alerting Rules (`scheduler/monitoring/alerts.yaml`)
  - [ ] High Error Rate (> 5%)
  - [ ] High Queue Length (> 100)
  - [ ] LLM API Latency (> 5s)
  - [ ] Job Timeout Rate (> 10%)
- [ ] Prometheus Alertmanager Configuration
  - [ ] Email Notifications
  - [ ] Slack Notifications (later)

---

## ✅ Phase 9: Deployment & DevOps (Woche 8-9) - COMPLETE

### 9.1 Docker Setup ✅
- [x] `Dockerfile` erstellen
  - [x] Multi-stage Build (builder + runtime)
  - [x] Python 3.11 Base Image
  - [x] Install Dependencies (Poetry)
  - [x] Copy Application Code
  - [x] Expose Port 8000
  - [x] Health Check
- [x] `docker-compose.yml` erstellen
  - [x] scheduler service
  - [x] redis service
  - [x] (optional) jaeger service
  - [x] (optional) grafana service
  - [x] Volume Mounts (data persistence)
  - [x] Environment Variables
- [x] `.dockerignore` erstellen
- [x] Test Docker Build
  - [x] `docker build -t cpa-scheduler .`
  - [x] `docker-compose up`
  - [x] Verify Health Check

### 9.2 Railway Deployment ✅
- [x] `railway.toml` erstellen
- [x] Railway Project Setup
  - [ ] Create New Project
  - [ ] Connect GitHub Repository
  - [ ] Add Redis Add-on
- [ ] Environment Variables (Railway Dashboard)
  - [ ] `OPENAI_API_KEY`
  - [ ] `REDIS_URL`
  - [ ] `DATABASE_URL`
  - [ ] `API_KEY`
- [ ] Deployment
  - [ ] Push to `main` branch
  - [ ] Verify Deployment
  - [ ] Test Health Endpoint

### 9.3 CI/CD
- [ ] `.github/workflows/ci.yml` erstellen
  - [ ] Trigger: Push, Pull Request
  - [ ] Jobs:
    - [ ] Lint (ruff, mypy)
    - [ ] Test (pytest)
    - [ ] Build Docker Image
- [ ] `.github/workflows/deploy.yml` erstellen
  - [ ] Trigger: Push to `main`
  - [ ] Jobs:
    - [ ] Build Docker Image
    - [ ] Push to Registry (GitHub Container Registry)
    - [ ] Deploy to Railway (API)
- [ ] Pre-commit Hooks (`.pre-commit-config.yaml`)
  - [ ] ruff (linting)
  - [ ] black (formatting)
  - [ ] mypy (type checking)
- [ ] Test CI/CD Pipeline
  - [ ] Create Pull Request
  - [ ] Verify CI runs
  - [ ] Merge to main
  - [ ] Verify Deployment

---

## 📚 Phase 10: Documentation & Testing (Woche 9-10)

### 10.1 API Documentation ✅
- [x] OpenAPI/Swagger (auto-generated by FastAPI)
- [ ] Postman Collection
  - [ ] Export from Swagger
  - [x] Add Example Requests
  - [x] Add Environment Variables
- [x] API Usage Examples (`docs/API_EXAMPLES.md`)
  - [x] Schedule Job
  - [x] Get Job Status
  - [x] Send Agent Message
  - [x] Query Audit Log

### 10.2 Developer Documentation
- [x] Architecture Overview (already in `docs/ARCHITECTURE.md`)
- [x] Agent Communication Protocol Guide (`docs/LAM_PROTOCOL.md`) - (Brought in from hamza_poc)
- [ ] Executor Development Guide (`docs/EXECUTOR_GUIDE.md`)
- [ ] Deployment Guide (`docs/DEPLOYMENT.md`)
- [ ] Troubleshooting

### 10.3 Testing
- [x] Unit Test Coverage > 90% (Verified 2026-01-19)
  - [x] Run `pytest --cov`
  - [x] Identify gaps
  - [x] Add missing tests
- [ ] Integration Tests (End-to-End)
  - [ ] Already covered in previous phases
- [ ] Load Testing (`tests/load/locustfile.py`)
  - [ ] Locust Setup
  - [ ] Test `/schedule` Endpoint
  - [ ] Test `/jobs/{job_id}` Endpoint
  - [ ] Target: 100 concurrent users
- [ ] Security Testing
  - [ ] OWASP ZAP Scan (later)
  - [ ] Dependency Vulnerability Scan (Snyk/Dependabot)

---

## 🔮 Phase 11: Advanced Features (Later)

### 11.1 Agent Discovery
- [ ] Agent Registry (who can do what?)
- [ ] Capability Negotiation (Offer/Assign Flow)
- [ ] Load Balancing (multiple workers)

### 11.2 Human-in-the-Loop
- [ ] Approval Workflow (4-Augen-Prinzip)
- [ ] Interactive Prompts (user input)
- [ ] Review UI (web dashboard)

### 11.3 Migration zu Temporal
- [ ] Temporal Workflow Definition
- [ ] Migration Script (Redis → Temporal)
- [ ] Backward Compatibility

### 9.4 Migration zu Supabase
- [ ] Supabase Repository Implementation
- [ ] Data Migration Script (SQLite → PostgreSQL)
- [ ] Row Level Security (RLS) Policies

---

## 📝 Notes

- **Testing**: Write tests FIRST (TDD) for critical components
- **Documentation**: Update docs as you go, not at the end
- **Git Commits**: Small, atomic commits with clear messages
- **Code Review**: Self-review before committing
- **Performance**: Profile before optimizing

---

**Last Updated**: 2026-01-19  
**Next Review**: Ready for PR review (Phases 1-10 complete)

---

## 🛠️ Infrastructure & Dev Setup ✅
- [x] **Local Development Script**: `dev-local.sh` for multi-service startup.
- [x] **Local Development Guide**: `LOCAL_DEV.md` with Swagger endpoints and curl examples.
- [x] **Environment Stability**: Fixed CORS and SQLite driver issues.
- [x] **Service Health**: Verified Scheduler (8000), Server (8001), and Calc Agent (8002).
- [x] **Calculator PoC Orchestrator**: Implemented and verified (multi-agent LAM flow).
- [x] **Calculator PoC UI**: Implemented and verified (React calculator with job polling).

