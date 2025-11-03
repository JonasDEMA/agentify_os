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
- [ ] Dead Letter Queue (failed jobs after max retries) - **TODO: Phase 2**
- [x] Unit Tests (`tests/queue/test_job_queue.py`)
  - [x] Test Enqueue/Dequeue
  - [x] Test Status Updates
  - [x] Test Retry Logic
  - [x] Test Max Retries Exceeded
  - [x] Test Cancel Job
  - [x] Test Get Job
  - [ ] Test Dead Letter Queue - **TODO: Phase 2**
  - [ ] Test Concurrent Access - **TODO: Phase 2**
- [ ] Integration Tests (with real Redis)
  - [ ] Test Redis Connection
  - [ ] Test Queue Persistence

---

## ✅ Phase 2: API & Agent Management (Woche 2-3)

### 2.1 FastAPI Application
- [ ] `scheduler/main.py` erstellen
- [ ] FastAPI App Setup
  - [ ] App Instance
  - [ ] CORS Middleware
  - [ ] Exception Handlers (Global)
  - [ ] Startup/Shutdown Events (Redis Connection)
- [ ] Health Check Endpoint (`GET /health`)
  - [ ] Check Redis Connection
  - [ ] Check Agent Registry
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

### 2.2 Job API Endpoints
- [ ] `scheduler/api/jobs.py` erstellen
- [ ] `POST /jobs` Endpoint (Create Job)
  - [ ] Request Model (CreateJobRequest: intent, description, context)
  - [ ] Response Model (JobResponse: job_id, status, created_at)
  - [ ] Intent Router → Task Graph
  - [ ] Enqueue Job to Redis
  - [ ] Return Job ID
- [ ] `GET /jobs` Endpoint (List Jobs)
  - [ ] Query Parameters (limit, offset, status filter)
  - [ ] Pagination
  - [ ] Response Model (JobListResponse: jobs, total, page, page_size)
- [ ] `GET /jobs/{job_id}` Endpoint (Get Job Status)
  - [ ] Response Model (JobDetailResponse: job, status, tasks)
  - [ ] 404 if not found
- [ ] `DELETE /jobs/{job_id}` Endpoint (Cancel Job)
  - [ ] Cancel Job via JobQueue
  - [ ] Update Status to "cancelled"
  - [ ] Return Success/Error
- [ ] `POST /jobs/{job_id}/retry` Endpoint (Retry Job)
  - [ ] Retry Failed Job via JobQueue
  - [ ] Return Success/Error
- [ ] WebSocket Endpoint (`/ws/jobs/{job_id}`) - **Optional für V1**
  - [ ] Connect to Job Updates
  - [ ] Send Status Updates (real-time)
  - [ ] Disconnect on Job Completion
- [ ] Integration Tests (`tests/api/test_jobs.py`)
  - [ ] Test Create Job
  - [ ] Test List Jobs
  - [ ] Test Get Job (existing/non-existing)
  - [ ] Test Cancel Job
  - [ ] Test Retry Job

### 2.3 Agent Registry & Management
- [ ] `scheduler/agents/agent_registry.py` erstellen
- [ ] Agent Model (Pydantic)
  - [ ] id: str (UUID)
  - [ ] name: str
  - [ ] type: AgentType (DESKTOP_RPA, EMAIL, WEB, DATA)
  - [ ] capabilities: list[ActionType]
  - [ ] endpoint: str (REST API URL)
  - [ ] status: AgentStatus (online, offline, busy)
  - [ ] last_heartbeat: datetime
  - [ ] metadata: dict (version, platform, etc.)
- [ ] AgentRegistry Class
  - [ ] `register(agent: Agent)` Method
  - [ ] `unregister(agent_id: str)` Method
  - [ ] `get_agent(agent_id: str)` Method
  - [ ] `list_agents(capability: ActionType | None)` Method
  - [ ] `update_heartbeat(agent_id: str)` Method
  - [ ] `find_agent_for_task(action_type: ActionType)` Method
- [ ] Agent Storage (Redis)
  - [ ] Store agent data in Redis (key: `cpa:agents:{agent_id}`)
  - [ ] TTL for heartbeat expiration
- [ ] Unit Tests (`tests/agents/test_agent_registry.py`)
  - [ ] Test Register Agent
  - [ ] Test Unregister Agent
  - [ ] Test List Agents
  - [ ] Test Find Agent for Task
  - [ ] Test Heartbeat Expiration

### 2.4 Agent API Endpoints
- [ ] `scheduler/api/agents.py` erstellen
- [ ] `POST /agents/register` Endpoint
  - [ ] Request Model (RegisterAgentRequest: name, type, capabilities, endpoint)
  - [ ] Response Model (AgentResponse: agent_id, status)
  - [ ] Register Agent in AgentRegistry
  - [ ] Return Agent ID
- [ ] `POST /agents/{id}/heartbeat` Endpoint
  - [ ] Update last_heartbeat timestamp
  - [ ] Return Success
- [ ] `GET /agents` Endpoint
  - [ ] Query Parameters (type, capability, status)
  - [ ] Response Model (AgentListResponse: agents, total)
- [ ] `GET /agents/{id}` Endpoint
  - [ ] Response Model (AgentDetailResponse: agent details)
  - [ ] 404 if not found
- [ ] `DELETE /agents/{id}` Endpoint
  - [ ] Unregister Agent
  - [ ] Return Success
- [ ] Integration Tests (`tests/api/test_agents.py`)
  - [ ] Test Register Agent
  - [ ] Test Heartbeat
  - [ ] Test List Agents
  - [ ] Test Get Agent
  - [ ] Test Unregister Agent

### 2.5 LAM Message Handler
- [ ] `scheduler/api/lam_handler.py` erstellen
- [ ] `POST /lam/message` Endpoint
  - [ ] Accept LAM Message (any type)
  - [ ] Validate Message (Pydantic)
  - [ ] Route to appropriate handler based on type
    - [ ] `inform` → Update Job Status
    - [ ] `done` → Mark Task Complete
    - [ ] `failure` → Mark Task Failed
    - [ ] `offer` → Register Agent Capability
  - [ ] Return Acknowledgement
- [ ] Integration Tests (`tests/api/test_lam_handler.py`)
  - [ ] Test Inform Message
  - [ ] Test Done Message
  - [ ] Test Failure Message
  - [ ] Test Offer Message

### 2.6 Task Orchestrator
- [ ] `scheduler/orchestrator/orchestrator.py` erstellen
- [ ] Orchestrator Class
  - [ ] `__init__(job_queue, agent_registry, llm_wrapper)`
  - [ ] `process_job(job_id: str)` Method (Main Loop)
    - [ ] Get Job from Queue
    - [ ] Get Task Graph from Job
    - [ ] For each Task in Graph:
      - [ ] Find Agent for Task (via AgentRegistry)
      - [ ] Send LAM Request to Agent (via REST API)
      - [ ] Wait for Agent Response (inform/done/failure)
      - [ ] Update Job Status
    - [ ] Send Final Response (done/failure)
  - [ ] `assign_task_to_agent(task: ToDo, agent: Agent)` Method
    - [ ] Create LAM Request Message
    - [ ] Send to Agent Endpoint (POST /tasks)
    - [ ] Return correlation_id
  - [ ] `handle_agent_response(message: LAMMessage)` Method
    - [ ] Update Task Status
    - [ ] Update Job Status
    - [ ] Continue with next Task
  - [ ] `handle_task_failure(task, error)` Method (Error Recovery)
    - [ ] Retry Logic
    - [ ] Fallback to different Agent
- [ ] Correlation ID Tracking
  - [ ] Store conversationId in Job
  - [ ] Include in all LAM Messages
- [ ] Timeout Handling
  - [ ] Task-level timeout
  - [ ] Job-level timeout
  - [ ] Cancel Job if deadline exceeded
- [ ] Background Worker
  - [ ] Continuously poll Redis Queue
  - [ ] Process Jobs asynchronously
  - [ ] Graceful Shutdown
- [ ] Integration Tests (`tests/orchestrator/test_orchestrator.py`)
  - [ ] Test Simple Job (single task)
  - [ ] Test Complex Job (multiple tasks with dependencies)
  - [ ] Test Agent Assignment
  - [ ] Test Agent Response Handling
  - [ ] Test Task Failure (retry)
  - [ ] Test Job Timeout
  - [ ] Test Correlation ID Tracking

---

## ✅ Phase 3: LLM Integration (Woche 3)

### 3.1 LLM Wrapper (Abstraction Layer)
- [ ] `scheduler/llm/llm_wrapper.py` erstellen
- [ ] Abstract LLMProvider Class
  - [ ] `generate(prompt: str, **kwargs)` Abstract Method → str
  - [ ] `generate_structured(prompt: str, schema: Type[BaseModel])` Abstract Method → BaseModel
  - [ ] `get_embedding(text: str)` Abstract Method → list[float] (optional)
- [ ] LLMWrapper Class
  - [ ] `__init__(provider: LLMProvider)`
  - [ ] `intent_to_task_graph(intent: str, description: str)` Method → TaskGraph
  - [ ] `select_agent_for_task(task: ToDo, agents: list[Agent])` Method → Agent
  - [ ] `analyze_error(error: str, context: dict)` Method → str (recovery suggestion)
- [ ] `scheduler/llm/openai_provider.py` erstellen
- [ ] OpenAIProvider Class (implements LLMProvider)
  - [ ] `__init__(api_key: str, model: str = "gpt-4")`
  - [ ] `generate()` using Chat Completion API
  - [ ] `generate_structured()` using JSON Mode / Function Calling
  - [ ] `get_embedding()` using Embeddings API (optional)
  - [ ] Error Handling (rate limit, timeout, invalid response)
  - [ ] Retry Logic (exponential backoff)
- [ ] `scheduler/llm/ollama_provider.py` erstellen (optional für V1)
- [ ] OllamaProvider Class (implements LLMProvider)
  - [ ] `__init__(base_url: str, model: str = "llama2")`
  - [ ] `generate()` using Ollama API
  - [ ] `generate_structured()` using JSON Mode
- [ ] `scheduler/llm/mock_provider.py` erstellen (for testing)
- [ ] MockProvider Class
  - [ ] Predefined Responses
  - [ ] No API Calls
- [ ] Unit Tests (`tests/llm/test_llm_wrapper.py`)
  - [ ] Test OpenAI Provider (with mocked API)
  - [ ] Test Structured Output
  - [ ] Test Error Handling
  - [ ] Test Retry Logic
  - [ ] Test Mock Provider
  - [ ] Test Intent → Task Graph Conversion
  - [ ] Test Agent Selection

### 3.2 LLM-based Intent Enhancement
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

## ⏳ Phase 5: Cognitive RPA Agent 🆕 **CORE CPA CAPABILITY**

**See**: `docs/COGNITIVE_RPA_REQUIREMENTS.md` for detailed requirements and architecture

### 5.1 LLM Wrapper (Foundation) ⏳ **NEXT**
- [ ] `agents/desktop_rpa/cognitive/llm_wrapper.py` erstellen
- [ ] LLMWrapper Class
  - [ ] `ask_for_next_action(goal, state, screenshot, context)` Method
  - [ ] `ask_for_strategy(goal, context)` Method
  - [ ] ChatGPT API Integration (GPT-4o/GPT-4 Vision)
  - [ ] Screenshot → Base64 encoding
  - [ ] Prompt engineering for Desktop RPA
  - [ ] Response parsing and validation
  - [ ] Error handling and retries
- [ ] LLMRequest and LLMResponse Models (Pydantic)
- [ ] Configuration (API key, model, temperature, etc.)
- [ ] Unit Tests (`tests/cognitive/test_llm_wrapper.py`)
  - [ ] Test with mock LLM
  - [ ] Test screenshot encoding
  - [ ] Test prompt generation
  - [ ] Test response parsing
  - [ ] Test error handling

### 5.2 Vision Layer ⏳
- [ ] `agents/desktop_rpa/vision/windows_api.py` erstellen
  - [ ] Windows UI Automation integration (`pywinauto` or `uiautomation`)
  - [ ] Detect windows and titles
  - [ ] Find GUI elements (buttons, text fields, etc.)
  - [ ] Get element properties (text, position, state)
- [ ] `agents/desktop_rpa/vision/screen_analyzer.py` erstellen
  - [ ] OCR integration (pytesseract)
  - [ ] Text extraction from screenshots
  - [ ] Fallback when UI Automation fails
- [ ] `agents/desktop_rpa/vision/state_detector.py` erstellen
  - [ ] Rule-based state detection
  - [ ] Window title matching
  - [ ] Element presence checking
  - [ ] State detection rules (JSON/YAML)
- [ ] Unit Tests (`tests/vision/test_*.py`)
  - [ ] Test Windows API integration
  - [ ] Test OCR
  - [ ] Test state detection

### 5.3 State Graph ⏳
- [ ] `agents/desktop_rpa/cognitive/state_graph.py` erstellen
- [ ] State and Transition Models (Pydantic)
- [ ] StateGraph Class
  - [ ] `add_state(state: State)` Method
  - [ ] `add_transition(transition: Transition)` Method
  - [ ] `find_path(from_state, to_state)` Method (A* or Dijkstra)
  - [ ] `get_current_state()` Method
  - [ ] `execute_transition(transition)` Method
- [ ] SQLite Schema for State Graphs
  - [ ] `state_graphs` table
  - [ ] `states` table
  - [ ] `transitions` table
  - [ ] Graph versioning (revision history)
- [ ] Graph Visualization Export
  - [ ] Export to GraphViz DOT format
  - [ ] Export to Mermaid format
- [ ] Unit Tests (`tests/cognitive/test_state_graph.py`)
  - [ ] Test graph building
  - [ ] Test path finding
  - [ ] Test state detection
  - [ ] Test SQLite storage

### 5.4 Strategy Manager ⏳
- [ ] `agents/desktop_rpa/cognitive/strategy_manager.py` erstellen
- [ ] Strategy Model (Pydantic)
- [ ] StrategyManager Class
  - [ ] `create_strategy(strategy: Strategy)` Method
  - [ ] `get_strategy(strategy_id)` Method
  - [ ] `list_strategies(filters)` Method
  - [ ] `execute_strategy(strategy_id, context)` Method
  - [ ] `update_success_rate(strategy_id, success)` Method
- [ ] JSON Strategy Format Specification
- [ ] SQLite Schema for Strategies
  - [ ] `strategies` table
  - [ ] Strategy versioning
- [ ] Unit Tests (`tests/cognitive/test_strategy_manager.py`)
  - [ ] Test CRUD operations
  - [ ] Test strategy execution
  - [ ] Test success tracking
  - [ ] Test SQLite storage

### 5.5 Experience Memory ⏳
- [ ] `agents/desktop_rpa/cognitive/experience_memory.py` erstellen
- [ ] Experience Model (Pydantic)
- [ ] ExperienceMemory Class
  - [ ] `save_experience(experience: Experience)` Method
  - [ ] `get_experience(experience_id)` Method
  - [ ] `find_similar_experiences(goal, state)` Method
  - [ ] `analyze_patterns()` Method (success patterns, common obstacles)
- [ ] SQLite Schema for Experiences
  - [ ] `experiences` table
  - [ ] `obstacles` table
  - [ ] `obstacle_solutions` table
- [ ] Unit Tests (`tests/cognitive/test_experience_memory.py`)
  - [ ] Test experience storage
  - [ ] Test experience retrieval
  - [ ] Test pattern analysis
  - [ ] Test SQLite storage

### 5.6 Goal Planner ⏳
- [ ] `agents/desktop_rpa/planner/goal_planner.py` erstellen
- [ ] GoalPlanner Class
  - [ ] `decompose_goal(goal)` Method → list[sub_goals]
  - [ ] `map_goal_to_strategy(goal)` Method → Strategy | None
  - [ ] `plan_execution(goal)` Method → ExecutionPlan
- [ ] `agents/desktop_rpa/planner/action_planner.py` erstellen
- [ ] ActionPlanner Class
  - [ ] `plan_actions(strategy, context)` Method → list[actions]
  - [ ] `check_preconditions(strategy)` Method → bool
  - [ ] `sequence_actions(actions)` Method → ordered list
- [ ] Integration with LLM, State Graph, Strategy Manager
- [ ] Unit Tests (`tests/planner/test_*.py`)
  - [ ] Test goal decomposition
  - [ ] Test strategy mapping
  - [ ] Test action planning
  - [ ] Test precondition checking

### 5.7 Integration & Learning Loop ⏳
- [ ] Integrate all cognitive components
- [ ] Implement main learning loop
  - [ ] Receive goal
  - [ ] Check for existing strategy
  - [ ] Execute strategy or ask LLM
  - [ ] Handle obstacles
  - [ ] Learn from experience
  - [ ] Update state graph
  - [ ] Save strategy
- [ ] End-to-End Testing with real scenarios
  - [ ] Test: "Open Outlook and send email"
  - [ ] Test: "Find file in folder and send via email"
  - [ ] Test: "Handle pop-up and continue"
- [ ] Performance Optimization
- [ ] Documentation
  - [ ] User guide for cognitive features
  - [ ] API documentation
  - [ ] Example strategies

---

## ⏳ Phase 6: Database & Persistence (Woche 5-6)

### 6.1 Repository Pattern
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

### 6.2 Audit Log
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

### 6.3 Context Memory (RAG)
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

## 🔄 Phase 7: Minimal CPA Integration (Woche 6-7)

### 7.1 Executor Framework
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

### 7.2 Playwright Executor
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

## 📊 Phase 8: Observability & Security (Woche 7-8)

### 8.1 OpenTelemetry Integration
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

### 8.2 Security & Policies
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

## 🚀 Phase 9: Deployment & DevOps (Woche 8-9)

### 9.1 Docker Setup
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

### 9.2 Railway Deployment
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

### 10.1 API Documentation
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

### 10.2 Developer Documentation
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

### 10.3 Testing
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

**Last Updated**: 2025-11-03  
**Next Review**: After Phase 1 completion

