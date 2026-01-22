# 🤝 Agent Communication Protocol

## Übersicht

Der **CPA Scheduler** kommuniziert mit spezialisierten Agenten über **REST API** und das **Agent Communication Protocol** (Lumina Agent Messages).

## Architektur

```
┌─────────────────────────────────────────────────────────┐
│ CPA Scheduler (Orchestrator)                            │
│ • Agent Registry                                        │
│ • Job Queue                                             │
│ • Task Graph                                            │
└─────────────┬───────────────────────────────────────────┘
              │ REST API + Agent Communication Protocol
              │
    ┌─────────┴─────────┬─────────────┬──────────────┐
    │                   │             │              │
┌───▼────────────┐  ┌───▼──────┐  ┌──▼──────┐  ┌───▼──────┐
│ Desktop-RPA    │  │ Email-   │  │ Web-    │  │ Data-    │
│ Agent          │  │ Agent    │  │ Agent   │  │ Agent    │
│ (lokal)        │  │          │  │         │  │          │
└────────────────┘  └──────────┘  └─────────┘  └──────────┘
```

## Agent Types

### 1. Desktop-RPA-Agent
**Verantwortlichkeiten:**
- Lokale Desktop-Automation (Windows)
- Vision-basierte UI-Interaktion (OCR, Screenshot Analysis)
- Feingranulare Aktionen (Click, Type, Wait, etc.)
- Generische Task-Ausführung

**Capabilities:**
- `DESKTOP_AUTOMATION`
- `VISION`
- `OCR`
- `UI_AUTOMATION`

**Technologie:**
- Python (lokal)
- Playwright (Browser-Automation)
- PyAutoGUI / pywinauto (Desktop-Automation)
- OpenCV / Tesseract (Vision/OCR)

### 2. Email-Agent
**Verantwortlichkeiten:**
- Email senden/empfangen
- Attachments verarbeiten
- Email-Suche

**Capabilities:**
- `EMAIL_SEND`
- `EMAIL_READ`
- `EMAIL_SEARCH`

**Technologie:**
- Microsoft Graph API
- MSAL (Authentication)

### 3. Web-Agent
**Verantwortlichkeiten:**
- Web Scraping
- Form Submission
- API Calls

**Capabilities:**
- `WEB_SCRAPE`
- `WEB_FORM`
- `API_CALL`

### 4. Data-Agent
**Verantwortlichkeiten:**
- Datenbank-Queries
- ETL-Operationen
- Data Transformation

**Capabilities:**
- `DATABASE_QUERY`
- `ETL`
- `DATA_TRANSFORM`

---

## Communication Flow

### 1. Agent Registration (Startup)

**Agent → Scheduler:**
```http
POST /agents/register
Content-Type: application/json

{
  "name": "Desktop-RPA-Agent-001",
  "type": "DESKTOP_RPA",
  "capabilities": ["DESKTOP_AUTOMATION", "VISION", "OCR"],
  "endpoint": "http://localhost:8001",
  "metadata": {
    "version": "1.0.0",
    "platform": "Windows 11",
    "hostname": "DESKTOP-XYZ"
  }
}
```

**Scheduler → Agent:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "agent_id": "agent-uuid-123",
  "status": "registered",
  "heartbeat_interval": 30
}
```

### 2. Heartbeat (Periodic)

**Agent → Scheduler:**
```http
POST /agents/{agent_id}/heartbeat
Content-Type: application/json

{
  "status": "online",
  "current_load": 0.3,
  "available_slots": 5
}
```

**Scheduler → Agent:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ok"
}
```

### 3. Task Assignment (Scheduler → Agent)

**Scheduler → Agent:**
```http
POST {agent_endpoint}/tasks
Content-Type: application/json

{
  "id": "msg-uuid-456",
  "ts": "2025-11-03T10:30:00Z",
  "type": "request",
  "sender": "agent://scheduler/main",
  "to": ["agent://desktop-rpa/001"],
  "intent": "document_search",
  "task": "Öffne DATEV und suche Dokument 'Rechnung-2024-001'",
  "payload": {
    "application": "DATEV",
    "search_term": "Rechnung-2024-001",
    "timeout": 60
  },
  "context": {
    "tenant": "acme",
    "user": "user@example.com",
    "locale": "de-DE"
  },
  "correlation": {
    "conversationId": "conv-123",
    "jobId": "job-789"
  },
  "expected": {
    "deadline": "2025-11-03T10:35:00Z",
    "format": "json"
  }
}
```

**Agent → Scheduler (Acknowledgement):**
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "status": "accepted",
  "task_id": "task-uuid-789",
  "estimated_duration": 45
}
```

### 4. Status Updates (Agent → Scheduler)

**Agent → Scheduler:**
```http
POST /lam/message
Content-Type: application/json

{
  "id": "msg-uuid-457",
  "ts": "2025-11-03T10:30:15Z",
  "type": "inform",
  "sender": "agent://desktop-rpa/001",
  "to": ["agent://scheduler/main"],
  "intent": "document_search",
  "task": "Öffne DATEV und suche Dokument 'Rechnung-2024-001'",
  "payload": {
    "status": "in_progress",
    "progress": 0.5,
    "message": "DATEV geöffnet, suche läuft..."
  },
  "correlation": {
    "conversationId": "conv-123",
    "jobId": "job-789",
    "inReplyTo": "msg-uuid-456"
  }
}
```

### 5. Task Completion (Agent → Scheduler)

**Agent → Scheduler (Success):**
```http
POST /lam/message
Content-Type: application/json

{
  "id": "msg-uuid-458",
  "ts": "2025-11-03T10:31:00Z",
  "type": "done",
  "sender": "agent://desktop-rpa/001",
  "to": ["agent://scheduler/main"],
  "intent": "document_search",
  "task": "Öffne DATEV und suche Dokument 'Rechnung-2024-001'",
  "payload": {
    "result": {
      "found": true,
      "document_id": "DOC-2024-001",
      "path": "C:\\DATEV\\Dokumente\\Rechnung-2024-001.pdf",
      "metadata": {
        "size": 245678,
        "created": "2024-01-15T09:00:00Z"
      }
    },
    "execution_time": 45.2,
    "screenshot": "base64-encoded-image"
  },
  "correlation": {
    "conversationId": "conv-123",
    "jobId": "job-789",
    "inReplyTo": "msg-uuid-456"
  },
  "status": {
    "code": "success",
    "message": "Dokument erfolgreich gefunden"
  }
}
```

**Agent → Scheduler (Failure):**
```http
POST /lam/message
Content-Type: application/json

{
  "id": "msg-uuid-459",
  "ts": "2025-11-03T10:31:00Z",
  "type": "failure",
  "sender": "agent://desktop-rpa/001",
  "to": ["agent://scheduler/main"],
  "intent": "document_search",
  "task": "Öffne DATEV und suche Dokument 'Rechnung-2024-001'",
  "payload": {
    "error": "DocumentNotFound",
    "message": "Dokument 'Rechnung-2024-001' nicht gefunden",
    "details": {
      "search_term": "Rechnung-2024-001",
      "search_location": "C:\\DATEV\\Dokumente",
      "files_scanned": 1234
    },
    "screenshot": "base64-encoded-image"
  },
  "correlation": {
    "conversationId": "conv-123",
    "jobId": "job-789",
    "inReplyTo": "msg-uuid-456"
  },
  "status": {
    "code": "error",
    "message": "Dokument nicht gefunden"
  }
}
```

---

## Agent Discovery

### Capability-based Discovery

**Scheduler fragt:** "Wer kann DESKTOP_AUTOMATION?"

```python
# Scheduler Code
agents = agent_registry.list_agents(capability="DESKTOP_AUTOMATION")
# Returns: [Desktop-RPA-Agent-001, Desktop-RPA-Agent-002]

# Select best agent (e.g. lowest load)
agent = min(agents, key=lambda a: a.current_load)
```

### On-Demand Registration

Wenn kein Agent verfügbar ist:
1. Scheduler wartet auf Agent-Registration
2. Agent startet und registriert sich
3. Scheduler assigned Task

---

## Error Handling

### Agent Timeout
- Scheduler wartet max. `task.timeout` Sekunden
- Bei Timeout: Task als `failed` markieren
- Retry mit anderem Agent oder später

### Agent Offline
- Heartbeat fehlt → Agent als `offline` markieren
- Laufende Tasks als `failed` markieren
- Retry mit anderem Agent

### Task Failure
- Agent sendet `failure` Message
- Scheduler entscheidet: Retry oder Abbruch
- Max. 3 Retries (konfigurierbar)

---

## Security

### Authentication
- **Agent → Scheduler**: API Key im Header (`X-API-Key`)
- **Scheduler → Agent**: API Key im Header (`X-API-Key`)

### Authorization
- Agents dürfen nur ihre eigenen Tasks abrufen
- Agents dürfen nur ihre eigenen Status-Updates senden

### Encryption
- HTTPS für alle Kommunikation (Production)
- HTTP für lokale Entwicklung

---

## Implementation Notes

### Desktop-RPA-Agent (separate Komponente)
- Läuft lokal auf Windows
- Eigene FastAPI-Anwendung
- Registriert sich beim Scheduler
- Implementiert `/tasks` Endpoint
- Sendet Status-Updates via `/lam/message`

**Beispiel-Struktur:**
```
desktop-rpa-agent/
├── main.py              # FastAPI App
├── agent.py             # Agent Logic
├── executors/
│   ├── vision.py        # Vision/OCR
│   ├── ui_automation.py # Click/Type/etc.
│   └── playwright.py    # Browser Automation
├── config.py            # Configuration
└── tests/
```

**Wird später implementiert!** (Phase 4+)

