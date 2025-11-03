# 🏗️ CPA Scheduler/Planner - Architektur-Dokumentation

## Übersicht

Der **CPA Scheduler/Planner** ist die zentrale Orchestrierungskomponente der Cognitive Process Automation (CPA) Architektur. Er sitzt zwischen den Channels (Email, Chat, Voice) und der CPA Desktop AI und koordiniert die Ausführung von Tasks über das LAM-Protokoll (Lumina Agent Messages).

## Systemarchitektur

```
┌─────────────────────────────────────────────────┐
│ Apps & Agenten (LuminaOS Schicht 1)             │
│ → Channels (Email, Chat, Voice/Vapi)            │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ Orchestrator-Agenten (Schicht 2)                │
│ ┌─────────────────────────────────────────────┐ │
│ │ SCHEDULER/PLANNER                           │ │
│ │ • Intent Router (NLU/Rules)                 │ │
│ │ • Task Graph Builder (ToDo-Schema)          │ │
│ │ • Job Queue (Redis/NATS)                    │ │
│ │ • LAM Protocol Handler                      │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ CPA-KI Engine (Schicht 3)                       │
│ → Observe/Think/Act/Verify Loop                 │
│ → Vision, OCR, UIA (später)                     │
└──────────────────────────────────────────────────┘
```

## Technologie-Stack

### Core Framework
- **FastAPI**: Async Web Framework für REST API & WebSockets
- **Pydantic V2**: Schema Validation & Serialization
- **Python 3.11+**: Moderne Python Features (async/await, type hints)

### Queue & Messaging
- **Redis**: Job Queue, Session Storage, Pub/Sub
- **LAM Protocol**: Standardisiertes Agent-zu-Agent Messaging

### Database & Storage
- **SQLite + sqlite-vss**: Lokale Persistenz & Vector Search (V1)
- **Migration zu Supabase**: PostgreSQL + pgvector (geplant)
- **Repository Pattern**: Austauschbare DB-Layer

### LLM Integration
- **OpenAI API**: Default LLM Provider (GPT-4, GPT-3.5)
- **LLM Provider Pattern**: Austauschbare Backends (später Ollama lokal)
- **Structured Output**: JSON Mode / Function Calling

### Observability
- **structlog**: Strukturiertes Logging
- **OpenTelemetry**: Distributed Tracing & Metrics
- **Prometheus**: Metrics Collection
- **Grafana**: Dashboards & Visualization

### Testing
- **pytest**: Unit & Integration Tests
- **pytest-asyncio**: Async Test Support
- **Locust**: Load Testing

### Deployment
- **Docker**: Containerization
- **Railway**: Cloud Hosting
- **GitHub Actions**: CI/CD Pipeline

## Komponenten-Übersicht

### 1. LAM Protocol (`lam_protocol.py`)
Standardisiertes Nachrichtenprotokoll für Agent-Kommunikation.

**Message Types:**
- `request` – Anfrage an Agent
- `inform` – Information / Ergebnis
- `propose` – Vorschlag zur Abstimmung
- `agree` / `refuse` – Antwort auf Proposal
- `confirm` – Bestätigung
- `failure` – Fehler/Abbruch
- `done` – Task abgeschlossen
- `discover` – Suche nach Agenten mit Capability
- `offer` – Agent bietet Capability an
- `assign` – Task wird zugewiesen

**Minimal Fields:**
```json
{
  "id": "uuid",
  "ts": "2025-10-30T09:45:00Z",
  "type": "request",
  "sender": "agent://orchestrator/Marketing",
  "to": ["agent://worker/Analysis"],
  "intent": "analyse",
  "task": "Analysiere Q3 Churn",
  "payload": {},
  "context": {
    "tenant": "acme",
    "domain": "crm",
    "locale": "de-DE"
  },
  "correlation": {
    "conversationId": "conv-123",
    "inReplyTo": "uuid-xyz"
  }
}
```

### 2. Task Graph (`task_graph.py`)
Dependency-basierte Task-Ausführung mit paralleler/sequenzieller Orchestrierung.

**ToDo Schema:**
```python
class ToDo(BaseModel):
    action: Literal["open_app", "click", "type", 
                    "wait_for", "playwright", "uia", 
                    "send_mail"]
    selector: str | None = None
    text: str | None = None
    timeout: float = 8.0
    depends_on: list[int] = []  # Task-Indices
```

**Features:**
- Topologische Sortierung (Dependency Resolution)
- Parallele Ausführung unabhängiger Tasks
- Zyklus-Erkennung
- Timeout-Handling

### 3. Intent Router (`intent_router.py`)
Klassifiziert User-Intent und mappt zu Task-Templates.

**V1: Rule-based**
- Regex/Keyword Matching
- Intent Registry (YAML/JSON)
- Fallback zu LLM

**V2: LLM-based**
- Few-Shot Prompting
- Structured Output (Pydantic)
- Intent Extraction

### 4. Job Queue (`job_queue.py`)
Redis-basierte Task Queue mit Retry-Logic.

**Features:**
- Enqueue/Dequeue
- Job Status Tracking (pending, running, done, failed)
- Exponential Backoff Retry
- Dead Letter Queue
- Priority Queues

### 5. Task Orchestrator (`task_orchestrator.py`)
Hauptlogik für Task-Orchestrierung.

**Flow:**
1. Receive LAM Request
2. Intent Router → Task Graph
3. Enqueue Tasks to Redis
4. Monitor Execution
5. Send LAM Inform/Failure Response

**Features:**
- Correlation ID Tracking
- Timeout Handling
- Error Recovery
- Progress Reporting (WebSocket)

### 6. Executors (`executors/`)
Ausführungslogik für verschiedene Action-Types.

**Executor Types:**
- `PlaywrightExecutor`: Web Automation (goto, click, fill, wait_for)
- `MailExecutor`: Email via Graph API (send, read, search)
- `UIAExecutor`: Windows UI Automation (später)
- `FileExecutor`: Filesystem Operations (später)

**Interface:**
```python
class BaseExecutor(ABC):
    @abstractmethod
    async def execute(self, todo: ToDo) -> ExecutionResult:
        pass
    
    @abstractmethod
    async def verify(self, todo: ToDo) -> bool:
        pass
```

### 7. LLM Provider (`llm_provider.py`)
Abstraction Layer für verschiedene LLM-Backends.

**Providers:**
- `OpenAIProvider`: GPT-4, GPT-3.5
- `OllamaProvider`: Lokale LLMs (geplant)
- `MockProvider`: Testing

**Interface:**
```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def generate_structured(
        self, 
        prompt: str, 
        schema: Type[BaseModel]
    ) -> BaseModel:
        pass
```

### 8. Repository (`repository/`)
Persistenz-Layer mit austauschbarem Backend.

**Repositories:**
- `JobRepository`: Job CRUD
- `TaskRepository`: Task CRUD
- `MessageRepository`: LAM Message History
- `AuditRepository`: Audit Trail

**Implementations:**
- `SQLiteRepository`: V1 (lokal)
- `SupabaseRepository`: V2 (geplant)

### 9. Context Memory (`context_memory.py`)
Short-term & Long-term Memory für Kontext-Management.

**Short-term (Redis):**
- UI State
- Session Data
- Temporary Variables

**Long-term (SQLite + sqlite-vss):**
- Embeddings (OpenAI)
- Semantic Search
- Knowledge Base (FAQ, How-Tos)

## API Endpoints

### Inbound Gate
```
POST   /schedule              # Schedule new task
POST   /lam/message           # Receive LAM message
GET    /health                # Health check
```

### Job Management
```
GET    /jobs                  # List jobs (paginated)
GET    /jobs/{job_id}         # Get job status
DELETE /jobs/{job_id}         # Cancel job
POST   /jobs/{job_id}/retry   # Retry failed job
WS     /ws/jobs/{job_id}      # Live job updates
```

### Audit & Monitoring
```
GET    /audit                 # Query audit log
GET    /metrics               # Prometheus metrics
```

## Migration-Strategie

### SQLite → Supabase
1. Repository Pattern ermöglicht austauschbaren DB-Layer
2. Migration Script für Datenübertragung
3. Feature Flag für schrittweise Migration
4. Backward Compatibility während Übergangsphase

### Redis → Temporal
1. Queue Interface abstrahieren
2. Temporal Workflow Definition
3. Migration Script
4. Parallel-Betrieb während Migration

### OpenAI → Lokales LLM
1. LLM Provider Pattern
2. Ollama Integration
3. Performance-Benchmarks
4. Fallback zu Cloud-LLM bei Bedarf

## Security & Compliance

### Authentication
- API Key (Header: `X-API-Key`)
- JWT Tokens (später)
- OAuth2 für Graph API

### Authorization
- Tenant Isolation
- Role-based Access Control (RBAC)
- Row Level Security (RLS) in Supabase

### Policies
- App Allowlist
- Action Blacklist
- Rate Limiting per Tenant
- DSGVO Compliance (PII Detection)

### Audit Trail
- Jede Aktion wird geloggt
- Screenshot + Grund + Resultat
- Immutable Audit Log
- Retention Policy

## Performance-Ziele

### Latency
- Intent Routing: < 100ms
- Task Graph Building: < 200ms
- LLM Call: < 2s (OpenAI)
- Playwright Action: < 500ms
- End-to-End Workflow: < 10s (einfacher Task)

### Throughput
- 100 concurrent jobs
- 1000 tasks/minute
- 10k messages/minute

### Availability
- 99.9% Uptime
- Graceful Degradation
- Circuit Breaker für externe Services

## Monitoring & Observability

### Metrics (Prometheus)
- Job Queue Length
- Task Success/Failure Rate
- LLM API Latency
- Executor Duration by Type
- Error Rate by Type

### Tracing (OpenTelemetry)
- Request → Response Flow
- Task Execution Spans
- LLM Call Traces
- Database Query Traces

### Logging (structlog)
- Structured JSON Logs
- Correlation IDs
- Log Levels (DEBUG, INFO, WARN, ERROR)
- Log Aggregation (Grafana Loki)

### Dashboards (Grafana)
- System Health Overview
- Job Queue Metrics
- Error Rate & Types
- LLM Performance
- Executor Performance

## Deployment

### Docker Compose (Local)
```yaml
services:
  scheduler:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=sqlite:///data/scheduler.db
    volumes:
      - ./data:/app/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Railway (Production)
- Auto-deploy from GitHub
- Redis Add-on
- Environment Variables (Secrets)
- Health Checks
- Auto-scaling

## Control Loop (Observe → Think/Plan → Act → Verify)

Der CPA-Agent folgt einem kognitiven Control-Loop:

1. **Observe**: Bildschirm & UI-Tree erfassen (Screen, OCR, Accessibility, DOM)
2. **Think/Plan**: Ziel → Schrittplan mit Tools/Selektoren (LLM-basiert)
3. **Act**: Maus/Tastatur/UI-APIs ausführen
4. **Verify**: Zustand/Erfolg prüfen, ggf. replannen

Der Scheduler orchestriert diesen Loop und koordiniert die einzelnen Phasen.

## Beispiel-Workflow

**Szenario**: Am Telefon: "Finde in DATEV letzte Rechnung für Firma X, exportiere PDF, sende per Mail an anna@kunde.de"

**Plan (vom LLM generiert):**
1. Login → DATEV Portal (Playwright)
2. Suche Kunde "Firma X" (UIA/Playwright)
3. Navigiere zu Rechnungen (Click)
4. Filter "letzte Rechnung" (Click + Wait)
5. Export PDF (Click + Download)
6. Compose Mail via Graph API
7. Anhang hinzufügen
8. Senden
9. Verifizieren ("Gesendet" + Rechnungsnummer-Match)

**Executor**: Playwright für Web, Graph API für Mail, Verifier checkt Erfolg.

## Risiken & Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|--------|---------------|
| Flaky UI | Selektoren > Vision; Wait-for-State statt Sleep |
| Scaling/DPI | Standardwerte erzwingen |
| Compliance | Freigabe-Policies, vollständiges Audit |
| App-Updates | Canary-Runs, visuelle Diffs |
| Audio-Latenz | GPU-ASR, Chunking, VAD |
| LLM Hallucination | Structured Output, Validation, Retry |
| Network Failures | Circuit Breaker, Exponential Backoff |

## Nächste Schritte

Siehe `docs/TODO.md` für detaillierte Umsetzungs-Todos.

