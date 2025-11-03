# 🏗️ CPA Scheduler/Planner - Architektur-Dokumentation

## Übersicht

Der **CPA Scheduler/Planner** ist die zentrale Orchestrierungskomponente der Cognitive Process Automation (CPA) Architektur. Er koordiniert die Ausführung von Tasks durch **Delegation an spezialisierte Agenten** über das LAM-Protokoll (Lumina Agent Messages).

**Wichtig**: Der Scheduler führt **keine** feingranularen UI-Aktionen (Click, Type, etc.) selbst aus. Er delegiert high-level Tasks an spezialisierte Agenten (z.B. Desktop-RPA-Agent), die diese dann generisch umsetzen.

## Systemarchitektur

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Apps & Channels                                    │
│ → Email, Chat, Voice/Vapi                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ (User Requests)
┌─────────────────▼───────────────────────────────────────────┐
│ Layer 2: CPA SCHEDULER/PLANNER (diese Komponente)           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Intent Router (NLU/Rules)                             │ │
│ │ • Task Graph Builder (high-level Tasks)                 │ │
│ │ • Job Queue (Redis)                                     │ │
│ │ • Agent Registry & Discovery                            │ │
│ │ • LAM Protocol Handler                                  │ │
│ │ • LLM Wrapper (OpenAI/Ollama)                           │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────┘
                  │ (Task Delegation via LAM Protocol)
                  │
        ┌─────────┴─────────┬─────────────┬──────────────┐
        │                   │             │              │
┌───────▼────────┐  ┌───────▼──────┐  ┌──▼──────┐  ┌───▼──────┐
│ Desktop-RPA    │  │ Email-Agent  │  │ Web-    │  │ Data-    │
│ Agent          │  │              │  │ Agent   │  │ Agent    │
│ (lokal)        │  │ (MS Graph)   │  │         │  │          │
│                │  │              │  │         │  │          │
│ • Vision/OCR   │  │ • Send/Read  │  │ • Scrape│  │ • Query  │
│ • UI Automation│  │ • Attachments│  │ • Forms │  │ • ETL    │
│ • Click/Type   │  │              │  │         │  │          │
└────────────────┘  └──────────────┘  └─────────┘  └──────────┘
```

## Kommunikationsfluss

```
1. User Request → Scheduler (via Channel)
2. Scheduler: Intent Recognition → Task Graph Creation
3. Scheduler: Agent Discovery ("Wer kann Desktop-Automation?")
4. Agent: Registration/Offer ("Ich kann Desktop-Automation!")
5. Scheduler: Task Assignment (via LAM Protocol)
6. Agent: Task Execution (feingranular, generisch)
7. Agent: Status Updates → Scheduler
8. Scheduler: Result Aggregation → User
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
- **LLM Wrapper**: Abstraction Layer für verschiedene LLM Backends
- **OpenAI API**: Default Provider (GPT-4, GPT-3.5-turbo)
- **Ollama**: Lokale LLM Option (geplant)
- **Structured Output**: JSON Mode / Function Calling für Intent → Task Graph

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

**ToDo Schema (High-Level Tasks):**
```python
class ToDo(BaseModel):
    action: ActionType  # Enum: DESKTOP_AUTOMATION, EMAIL, WEB, DATA, etc.
    selector: str | None = None  # Agent-spezifische Details
    text: str | None = None      # Task-Beschreibung
    timeout: float = 8.0
    depends_on: list[int] = []   # Task-Indices
```

**Wichtig**: Tasks sind **high-level** (z.B. "DATEV öffnen und Dokument suchen"), nicht feingranular (z.B. "Click Button X"). Die feingranulare Ausführung übernimmt der zuständige Agent.

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
Redis-basierte Job Queue mit Retry-Logic.

**Features:**
- Enqueue/Dequeue
- Job Status Tracking (pending, running, done, failed, cancelled)
- Retry Logic mit max_retries
- Dead Letter Queue (geplant)
- Priority Queues (geplant)

### 5. Agent Registry (`agent_registry.py`)
Verwaltung und Discovery von spezialisierten Agenten.

**Agent Types:**
- `Desktop-RPA-Agent`: Lokale Desktop-Automation (Vision, OCR, UI Automation)
- `Email-Agent`: Email-Operationen via Microsoft Graph API
- `Web-Agent`: Web Scraping & Automation
- `Data-Agent`: Datenbank-Queries & ETL

**Agent Registration:**
- **Startup-Registration**: Agent registriert sich beim Start
- **On-Demand**: Agent registriert sich bei erster Anfrage
- **Health Checks**: Periodische Heartbeats
- **Capabilities**: Agent gibt an, welche ActionTypes er unterstützt

**Communication:**
- **REST API**: Agent ↔ Scheduler Kommunikation
- **LAM Protocol**: Standardisierte Nachrichten (request, inform, done, failure)

### 6. Task Orchestrator (`orchestrator.py`)
Hauptlogik für Task-Orchestrierung und Agent-Delegation.

**Flow:**
1. Receive User Request (via API)
2. Intent Router → Task Graph (high-level)
3. Agent Discovery ("Wer kann DESKTOP_AUTOMATION?")
4. Task Assignment (via LAM Protocol)
5. Monitor Execution (Status Updates von Agenten)
6. Result Aggregation
7. Send Response to User

**Features:**
- Correlation ID Tracking
- Timeout Handling
- Error Recovery
- Progress Reporting (WebSocket)
- Multi-Agent Coordination

### 7. LLM Wrapper (`llm_wrapper.py`)
Abstraction Layer für verschiedene LLM-Backends (lokal oder API).

**Providers:**
- `OpenAIProvider`: GPT-4, GPT-3.5-turbo (Default)
- `OllamaProvider`: Lokale LLMs (Llama, Mistral, etc.)
- `MockProvider`: Testing

**Use Cases:**
- Intent → Task Graph Conversion
- Task Description → Agent Selection
- Error Analysis & Recovery Suggestions

**Interface:**
```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel]
    ) -> BaseModel:
        """Generate structured output (JSON Mode)."""
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
POST   /jobs                  # Create new job (User Request)
POST   /lam/message           # Receive LAM message (Agent Communication)
GET    /health                # Health check
```

### Job Management
```
GET    /jobs                  # List jobs (paginated)
GET    /jobs/{job_id}         # Get job status
DELETE /jobs/{job_id}         # Cancel job
POST   /jobs/{job_id}/retry   # Retry failed job
WS     /ws/jobs/{job_id}      # Live job updates (WebSocket)
```

### Agent Management
```
POST   /agents/register       # Agent registration
POST   /agents/{id}/heartbeat # Agent heartbeat
GET    /agents                # List registered agents
GET    /agents/{id}           # Get agent details
DELETE /agents/{id}           # Unregister agent
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

