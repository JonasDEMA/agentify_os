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

### 1.2 LAM Protocol Implementation ✅
- [x] `scheduler/core/lam_protocol.py` erstellen
- [x] Pydantic BaseMessage Model (id, ts, type, sender, to, intent, payload, context, correlation, expected, status, security)
- [x] RequestMessage Model
- [x] InformMessage Model
- [x] ProposeMessage, AgreeMessage, RefuseMessage Models
- [x] ConfirmMessage, FailureMessage, DoneMessage Models
- [x] DiscoverMessage, OfferMessage, AssignMessage Models
- [x] Message Validation (Pydantic validators)
- [x] Message Serialization (to_dict, from_dict, to_json, from_json)
- [x] LAM Message Factory/Builder
- [x] Unit Tests (`tests/core/test_lam_protocol.py`)
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

### 1.4 Intent Router (Rule-based V1)
- [ ] `scheduler/core/intent_router.py` erstellen
- [ ] IntentRouter Class
  - [ ] `route(message: str)` Method → Intent
  - [ ] Regex/Keyword Matching
  - [ ] Intent Registry (load from YAML/JSON)
  - [ ] Fallback Intent ("unknown")
- [ ] `scheduler/config/intents.yaml` erstellen
  - [ ] Define Sample Intents (send_mail, search_document, export_pdf, etc.)
  - [ ] Regex Patterns per Intent
  - [ ] Task Templates per Intent
- [ ] Intent Model (Pydantic)
  - [ ] name: str
  - [ ] patterns: list[str]
  - [ ] task_template: list[ToDo]
- [ ] Unit Tests (`tests/core/test_intent_router.py`)
  - [ ] Test Known Intents
  - [ ] Test Unknown Intent (fallback)
  - [ ] Test Case Insensitivity
  - [ ] Test Multiple Patterns per Intent

### 1.5 Job Queue (Redis)
- [ ] `scheduler/queue/job_queue.py` erstellen
- [ ] JobQueue Class
  - [ ] `__init__(redis_url: str)`
  - [ ] `enqueue(job: Job)` Method → job_id
  - [ ] `dequeue()` Method → Job | None
  - [ ] `get_status(job_id: str)` Method → JobStatus
  - [ ] `update_status(job_id: str, status: JobStatus)` Method
  - [ ] `retry(job_id: str)` Method
  - [ ] `cancel(job_id: str)` Method
- [ ] Job Model (Pydantic)
  - [ ] id: str (UUID)
  - [ ] intent: str
  - [ ] task_graph: TaskGraph
  - [ ] status: JobStatus (pending, running, done, failed)
  - [ ] created_at: datetime
  - [ ] started_at: datetime | None
  - [ ] completed_at: datetime | None
  - [ ] error: str | None
  - [ ] retry_count: int
  - [ ] max_retries: int
- [ ] JobStatus Enum (pending, running, done, failed, cancelled)
- [ ] Retry Logic (exponential backoff)
- [ ] Dead Letter Queue (failed jobs after max retries)
- [ ] Unit Tests (`tests/queue/test_job_queue.py`)
  - [ ] Test Enqueue/Dequeue
  - [ ] Test Status Updates
  - [ ] Test Retry Logic
  - [ ] Test Dead Letter Queue
  - [ ] Test Concurrent Access
- [ ] Integration Tests (with real Redis)
  - [ ] Test Redis Connection
  - [ ] Test Queue Persistence

---

## ✅ Phase 2: API & Orchestration (Woche 2-3)

### 2.1 FastAPI Application
- [ ] `scheduler/main.py` erstellen
- [ ] FastAPI App Setup
  - [ ] App Instance
  - [ ] CORS Middleware
  - [ ] Exception Handlers (Global)
  - [ ] Startup/Shutdown Events
- [ ] Health Check Endpoint (`GET /health`)
  - [ ] Check Redis Connection
  - [ ] Check Database Connection
  - [ ] Return Status (healthy, degraded, unhealthy)
- [ ] OpenAPI/Swagger Configuration
  - [ ] Title, Description, Version
  - [ ] Tags for Endpoint Groups
- [ ] Logging Setup (structlog)
  - [ ] JSON Formatter
  - [ ] Correlation ID Middleware
- [ ] Unit Tests (`tests/api/test_main.py`)
  - [ ] Test Health Endpoint
  - [ ] Test CORS Headers
  - [ ] Test Exception Handling

### 2.2 Inbound Gate (Webhooks)
- [ ] `scheduler/api/inbound_gate.py` erstellen
- [ ] `POST /schedule` Endpoint
  - [ ] Request Model (ScheduleRequest: intent, task, context)
  - [ ] Response Model (ScheduleResponse: job_id, status)
  - [ ] Validation (Pydantic)
  - [ ] Enqueue Job to Redis
  - [ ] Return Job ID
- [ ] `POST /lam/message` Endpoint
  - [ ] Accept LAM Message (any type)
  - [ ] Validate Message (Pydantic)
  - [ ] Route to appropriate handler
  - [ ] Return Acknowledgement
- [ ] Authentication Middleware
  - [ ] API Key Validation (Header: `X-API-Key`)
  - [ ] JWT Validation (später)
- [ ] Rate Limiting (slowapi)
  - [ ] Per IP: 100 req/min
  - [ ] Per API Key: 1000 req/min
- [ ] Integration Tests (`tests/api/test_inbound_gate.py`)
  - [ ] Test Schedule Endpoint (valid request)
  - [ ] Test Schedule Endpoint (invalid request)
  - [ ] Test LAM Message Endpoint
  - [ ] Test Authentication (valid/invalid API key)
  - [ ] Test Rate Limiting

### 2.3 Scheduler API
- [ ] `scheduler/api/scheduler_api.py` erstellen
- [ ] `GET /jobs` Endpoint
  - [ ] Query Parameters (limit, offset, status filter)
  - [ ] Pagination
  - [ ] Response Model (JobListResponse: jobs, total, page, page_size)
- [ ] `GET /jobs/{job_id}` Endpoint
  - [ ] Response Model (JobDetailResponse: job, tasks, messages)
  - [ ] 404 if not found
- [ ] `DELETE /jobs/{job_id}` Endpoint
  - [ ] Cancel Job
  - [ ] Update Status to "cancelled"
  - [ ] Return Success/Error
- [ ] `POST /jobs/{job_id}/retry` Endpoint
  - [ ] Retry Failed Job
  - [ ] Reset Status to "pending"
  - [ ] Increment retry_count
  - [ ] Re-enqueue
- [ ] WebSocket Endpoint (`/ws/jobs/{job_id}`)
  - [ ] Connect to Job Updates
  - [ ] Send Status Updates (real-time)
  - [ ] Send Task Progress
  - [ ] Disconnect on Job Completion
- [ ] Integration Tests (`tests/api/test_scheduler_api.py`)
  - [ ] Test List Jobs
  - [ ] Test Get Job (existing/non-existing)
  - [ ] Test Cancel Job
  - [ ] Test Retry Job
  - [ ] Test WebSocket Connection
  - [ ] Test WebSocket Updates

### 2.4 Task Orchestrator
- [ ] `scheduler/orchestrator/task_orchestrator.py` erstellen
- [ ] TaskOrchestrator Class
  - [ ] `__init__(job_queue, executor_registry, message_bus)`
  - [ ] `process_job(job_id: str)` Method (Main Loop)
    - [ ] Dequeue Job
    - [ ] Build Task Graph
    - [ ] Execute Tasks (parallel/sequential)
    - [ ] Update Job Status
    - [ ] Send LAM Response (inform/failure)
  - [ ] `execute_task_batch(tasks: list[ToDo])` Method (Parallel Execution)
  - [ ] `handle_task_failure(task, error)` Method (Error Recovery)
  - [ ] `send_progress_update(job_id, progress)` Method (WebSocket)
- [ ] Correlation ID Tracking
  - [ ] Store conversationId in Job
  - [ ] Include in all LAM Messages
- [ ] Timeout Handling
  - [ ] Respect `expected.deadline` from LAM Message
  - [ ] Cancel Job if deadline exceeded
- [ ] Background Worker
  - [ ] Continuously poll Redis Queue
  - [ ] Process Jobs asynchronously
  - [ ] Graceful Shutdown
- [ ] Integration Tests (`tests/orchestrator/test_task_orchestrator.py`)
  - [ ] Test Simple Job (single task)
  - [ ] Test Complex Job (multiple tasks with dependencies)
  - [ ] Test Parallel Execution
  - [ ] Test Task Failure (retry)
  - [ ] Test Job Timeout
  - [ ] Test Correlation ID Tracking

---

## ✅ Phase 3: LLM Integration (Woche 3)

### 3.1 LLM Provider Abstraction
- [ ] `scheduler/llm/llm_provider.py` erstellen
- [ ] Abstract LLMProvider Class
  - [ ] `generate(prompt: str, **kwargs)` Abstract Method → str
  - [ ] `generate_structured(prompt: str, schema: Type[BaseModel])` Abstract Method → BaseModel
  - [ ] `get_embedding(text: str)` Abstract Method → list[float]
- [ ] LLMProviderRegistry Class
  - [ ] `register(name: str, provider: LLMProvider)`
  - [ ] `get(name: str)` → LLMProvider
  - [ ] Default Provider
- [ ] `scheduler/llm/openai_provider.py` erstellen
- [ ] OpenAIProvider Class (implements LLMProvider)
  - [ ] `__init__(api_key: str, model: str)`
  - [ ] `generate()` using Chat Completion API
  - [ ] `generate_structured()` using JSON Mode / Function Calling
  - [ ] `get_embedding()` using Embeddings API
  - [ ] Error Handling (rate limit, timeout, invalid response)
  - [ ] Retry Logic (exponential backoff)
- [ ] `scheduler/llm/mock_provider.py` erstellen (for testing)
- [ ] MockProvider Class
  - [ ] Predefined Responses
  - [ ] No API Calls
- [ ] Unit Tests (`tests/llm/test_llm_provider.py`)
  - [ ] Test OpenAI Provider (with mocked API)
  - [ ] Test Structured Output
  - [ ] Test Error Handling
  - [ ] Test Retry Logic
  - [ ] Test Mock Provider

### 3.2 LLM-based Intent Router
- [ ] `scheduler/llm/llm_intent_router.py` erstellen
- [ ] LLMIntentRouter Class
  - [ ] `__init__(llm_provider: LLMProvider, fallback_router: IntentRouter)`
  - [ ] `route(message: str)` Method → Intent
  - [ ] Prompt Engineering (Few-Shot Examples)
  - [ ] Structured Output (Intent Model)
  - [ ] Fallback to Rule-based Router (on error)
- [ ] `scheduler/prompts/intent_classification.jinja2` erstellen
  - [ ] System Prompt
  - [ ] Few-Shot Examples
  - [ ] User Message Template
- [ ] Prompt Templates (Jinja2)
  - [ ] Load from File
  - [ ] Variable Substitution
- [ ] Integration Tests (`tests/llm/test_llm_intent_router.py`)
  - [ ] Test Known Intents (with Mock LLM)
  - [ ] Test Unknown Intent (fallback)
  - [ ] Test LLM Error (fallback to rule-based)

### 3.3 LLM-based Task Planner
- [ ] `scheduler/llm/llm_task_planner.py` erstellen
- [ ] LLMTaskPlanner Class
  - [ ] `__init__(llm_provider: LLMProvider)`
  - [ ] `plan(intent: Intent, context: dict)` Method → TaskGraph
  - [ ] Natural Language → ToDo List
  - [ ] Dependency Inference
  - [ ] Selector Generation (Playwright, UIA)
  - [ ] Validation (Task Graph must be valid)
- [ ] `scheduler/prompts/task_planning.jinja2` erstellen
  - [ ] System Prompt (explain available actions)
  - [ ] Few-Shot Examples (sample workflows)
  - [ ] User Message Template
- [ ] TaskPlan Model (Pydantic)
  - [ ] tasks: list[ToDo]
  - [ ] reasoning: str (why this plan?)
- [ ] Integration Tests (`tests/llm/test_llm_task_planner.py`)
  - [ ] Test Simple Task (single action)
  - [ ] Test Complex Task (multiple actions with dependencies)
  - [ ] Test Invalid Plan (validation error)
  - [ ] Test Selector Generation

---

## ✅ Phase 4: Database & Persistence (Woche 4)

### 4.1 Repository Pattern
- [ ] `scheduler/repository/repository_interface.py` erstellen
- [ ] Abstract JobRepository
  - [ ] `save(job: Job)` Abstract Method
  - [ ] `get(job_id: str)` Abstract Method → Job | None
  - [ ] `list(limit, offset, status_filter)` Abstract Method → list[Job]
  - [ ] `update_status(job_id, status)` Abstract Method
  - [ ] `delete(job_id)` Abstract Method
- [ ] Abstract TaskRepository (similar structure)
- [ ] Abstract MessageRepository (similar structure)
- [ ] Abstract AuditRepository (similar structure)
- [ ] `scheduler/repository/sqlite_repository.py` erstellen
- [ ] SQLiteJobRepository (implements JobRepository)
  - [ ] Schema Definition (SQL)
  - [ ] CRUD Operations (using sqlite3 or SQLAlchemy)
  - [ ] Migrations (Alembic)
- [ ] SQLiteTaskRepository
- [ ] SQLiteMessageRepository
- [ ] SQLiteAuditRepository
- [ ] Database Schema (`scheduler/repository/schema.sql`)
  - [ ] jobs table
  - [ ] tasks table
  - [ ] messages table
  - [ ] audit_log table
- [ ] Alembic Setup
  - [ ] `alembic init`
  - [ ] Initial Migration
- [ ] Unit Tests (`tests/repository/test_sqlite_repository.py`)
  - [ ] Test CRUD Operations (in-memory SQLite)
  - [ ] Test Pagination
  - [ ] Test Filtering
  - [ ] Test Transactions

### 4.2 Audit Log
- [ ] `scheduler/audit/audit_log.py` erstellen
- [ ] AuditLog Class
  - [ ] `log_action(action, reason, result, screenshot_path)` Method
  - [ ] `query(filters)` Method → list[AuditEntry]
- [ ] AuditEntry Model (Pydantic)
  - [ ] id: str
  - [ ] timestamp: datetime
  - [ ] job_id: str
  - [ ] task_id: str | None
  - [ ] action: str
  - [ ] reason: str
  - [ ] result: str (success/failure)
  - [ ] screenshot_path: str | None
  - [ ] metadata: dict
- [ ] Screenshot Storage (filesystem)
  - [ ] Save to `data/screenshots/{job_id}/{task_id}.png`
- [ ] Audit Query API (`GET /audit`)
  - [ ] Query Parameters (job_id, start_date, end_date, action_type)
  - [ ] Pagination
  - [ ] Response Model (AuditListResponse)
- [ ] Integration Tests (`tests/audit/test_audit_log.py`)
  - [ ] Test Log Action
  - [ ] Test Query (with filters)
  - [ ] Test Screenshot Storage

### 4.3 Context Memory (RAG)
- [ ] `scheduler/memory/context_memory.py` erstellen
- [ ] ContextMemory Class
  - [ ] Short-term Memory (Redis)
    - [ ] `set(key, value, ttl)` Method
    - [ ] `get(key)` Method
    - [ ] `delete(key)` Method
  - [ ] Long-term Memory (SQLite + sqlite-vss)
    - [ ] `store(text, metadata)` Method (with embedding)
    - [ ] `search(query, limit)` Method (semantic search)
    - [ ] `get_by_id(id)` Method
- [ ] `scheduler/memory/embedding_service.py` erstellen
- [ ] EmbeddingService Class
  - [ ] `__init__(llm_provider: LLMProvider)`
  - [ ] `embed(text: str)` Method → list[float]
  - [ ] Batch Embedding
- [ ] Memory Entry Model (Pydantic)
  - [ ] id: str
  - [ ] text: str
  - [ ] embedding: list[float]
  - [ ] metadata: dict
  - [ ] created_at: datetime
- [ ] sqlite-vss Setup
  - [ ] Install extension
  - [ ] Create vector index
- [ ] Integration Tests (`tests/memory/test_context_memory.py`)
  - [ ] Test Short-term Memory (Redis)
  - [ ] Test Long-term Memory (SQLite)
  - [ ] Test Semantic Search
  - [ ] Test Embedding Service

---

## 🔄 Phase 5: Minimal CPA Integration (Woche 4-5)

### 5.1 Executor Framework
- [ ] `scheduler/executors/executor_registry.py` erstellen
- [ ] ExecutorRegistry Class
  - [ ] `register(action_type: str, executor: BaseExecutor)`
  - [ ] `get(action_type: str)` → BaseExecutor
  - [ ] `execute(todo: ToDo)` Method (dispatch to correct executor)
- [ ] `scheduler/executors/base_executor.py` erstellen (already defined in 1.3)
- [ ] Unit Tests (`tests/executors/test_executor_registry.py`)
  - [ ] Test Register/Get
  - [ ] Test Dispatch
  - [ ] Test Unknown Action Type (error)

### 5.2 Playwright Executor
- [ ] `scheduler/executors/playwright_executor.py` erstellen
- [ ] PlaywrightExecutor Class (extends BaseExecutor)
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

### 5.3 Mail Executor (Graph API)
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

### 5.4 End-to-End Workflow
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

## 📊 Phase 6: Observability & Security (Woche 5-6)

### 6.1 OpenTelemetry Integration
- [ ] `scheduler/telemetry/telemetry.py` erstellen
- [ ] OpenTelemetry Setup
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

### 6.2 Security & Policies
- [ ] `scheduler/security/policies.py` erstellen
- [ ] PolicyEngine Class
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

### 6.3 Monitoring & Alerts
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

## 🚀 Phase 7: Deployment & DevOps (Woche 6)

### 7.1 Docker Setup
- [ ] `Dockerfile` erstellen
  - [ ] Multi-stage Build (builder + runtime)
  - [ ] Python 3.11 Base Image
  - [ ] Install Dependencies (Poetry)
  - [ ] Copy Application Code
  - [ ] Expose Port 8000
  - [ ] Health Check
- [ ] `docker-compose.yml` erstellen
  - [ ] scheduler service
  - [ ] redis service
  - [ ] (optional) jaeger service
  - [ ] (optional) grafana service
  - [ ] Volume Mounts (data persistence)
  - [ ] Environment Variables
- [ ] `.dockerignore` erstellen
- [ ] Test Docker Build
  - [ ] `docker build -t cpa-scheduler .`
  - [ ] `docker-compose up`
  - [ ] Verify Health Check

### 7.2 Railway Deployment
- [ ] `railway.toml` erstellen (if needed)
- [ ] Railway Project Setup
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

### 7.3 CI/CD
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

## 📚 Phase 8: Documentation & Testing (Woche 7)

### 8.1 API Documentation
- [ ] OpenAPI/Swagger (auto-generated by FastAPI)
- [ ] Postman Collection
  - [ ] Export from Swagger
  - [ ] Add Example Requests
  - [ ] Add Environment Variables
- [ ] API Usage Examples (`docs/API_EXAMPLES.md`)
  - [ ] Schedule Job
  - [ ] Get Job Status
  - [ ] Send LAM Message
  - [ ] Query Audit Log

### 8.2 Developer Documentation
- [ ] Architecture Overview (already in `docs/ARCHITECTURE.md`)
- [ ] LAM Protocol Guide (`docs/LAM_PROTOCOL.md`)
  - [ ] Message Types
  - [ ] Examples
  - [ ] Best Practices
- [ ] Executor Development Guide (`docs/EXECUTOR_GUIDE.md`)
  - [ ] How to create custom executor
  - [ ] Interface specification
  - [ ] Testing guidelines
- [ ] Deployment Guide (`docs/DEPLOYMENT.md`)
  - [ ] Local Setup (Docker Compose)
  - [ ] Railway Deployment
  - [ ] Environment Variables
  - [ ] Troubleshooting

### 8.3 Testing
- [ ] Unit Test Coverage > 80%
  - [ ] Run `pytest --cov`
  - [ ] Identify gaps
  - [ ] Add missing tests
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

## 🔮 Phase 9: Advanced Features (Later)

### 9.1 Agent Discovery
- [ ] Agent Registry (who can do what?)
- [ ] Capability Negotiation (Offer/Assign Flow)
- [ ] Load Balancing (multiple workers)

### 9.2 Human-in-the-Loop
- [ ] Approval Workflow (4-Augen-Prinzip)
- [ ] Interactive Prompts (user input)
- [ ] Review UI (web dashboard)

### 9.3 Migration zu Temporal
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

**Last Updated**: 2025-11-03  
**Next Review**: After Phase 1 completion

