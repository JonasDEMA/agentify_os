# CPA Server API Documentation

## 🚀 Übersicht

Der CPA Server ist die zentrale Monitoring- und Management-Plattform für LuminaOS CPA Agents.

**Features:**
- ✅ Agent-Registrierung mit automatischer ID-Vergabe
- ✅ Token-basierte Authentifizierung (API Keys)
- ✅ Real-time Log Streaming
- ✅ Screenshot Upload & Management
- ✅ Agent Status Monitoring
- ✅ REST API mit FastAPI
- ✅ Automatische OpenAPI Dokumentation

---

## 📦 Installation & Start

### Server starten:

```bash
# Mit Poetry
poetry run python -m server.main

# Oder direkt mit uvicorn
poetry run uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

### Server läuft auf:
- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Authentifizierung

### 1. Agent Registrierung

**Endpoint:** `POST /api/v1/agents/register`

**Request:**
```json
{
  "agent_info": {
    "os_name": "Windows",
    "os_version": "11",
    "os_build": "22621.2715",
    "os_locale": "de-DE",
    "hostname": "DESKTOP-ABC123",
    "cpu_count": 8,
    "memory_total_gb": 16.0,
    "screen_resolution": "1920x1080",
    "dpi_scaling": 1.0,
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "python_version": "3.12.0",
    "agent_version": "0.1.0",
    "has_vision": true,
    "has_ocr": true,
    "has_ui_automation": true
  },
  "phone_number": "+4915143233730"
}
```

**Response:**
```json
{
  "agent_id": "agent_a1b2c3d4e5f6...",
  "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "server_url": "http://localhost:8000",
  "websocket_url": "ws://localhost:8000/ws",
  "registered_at": "2025-11-08T10:30:00Z"
}
```

**Wichtig:** 
- Der `api_key` wird nur einmal zurückgegeben!
- Agent speichert ihn lokal in `.agent_credentials.json`
- Für alle weiteren Requests im Header: `Authorization: Bearer <api_key>`

---

## 📡 API Endpoints

### Agents

#### `GET /api/v1/agents/`
Liste aller registrierten Agents

**Query Parameters:**
- `skip` (int): Anzahl zu überspringen (default: 0)
- `limit` (int): Max. Anzahl (default: 100)

**Response:**
```json
[
  {
    "id": "agent_abc123",
    "hostname": "DESKTOP-ABC123",
    "os_name": "Windows",
    "os_version": "11",
    "ip_address": "192.168.1.100",
    "registered_at": "2025-11-08T10:30:00Z",
    "last_seen_at": "2025-11-08T10:35:00Z",
    "is_active": true,
    "current_task": "Open Calculator"
  }
]
```

#### `GET /api/v1/agents/{agent_id}`
Details zu einem Agent

**Response:**
```json
{
  "id": "agent_abc123",
  "hostname": "DESKTOP-ABC123",
  "os_name": "Windows",
  "os_version": "11",
  "os_build": "22621.2715",
  "cpu_count": 8,
  "memory_total_gb": 16.0,
  "screen_resolution": "1920x1080",
  "ip_address": "192.168.1.100",
  "mac_address": "00:11:22:33:44:55",
  "python_version": "3.12.0",
  "agent_version": "0.1.0",
  "has_vision": true,
  "has_ocr": true,
  "has_ui_automation": true,
  "phone_number": "+4915143233730",
  "registered_at": "2025-11-08T10:30:00Z",
  "last_seen_at": "2025-11-08T10:35:00Z",
  "is_active": true,
  "current_task": "Open Calculator"
}
```

---

### Logs

#### `POST /api/v1/logs/`
Log-Eintrag erstellen (benötigt API Key)

**Headers:**
```
Authorization: Bearer <api_key>
```

**Request:**
```json
{
  "agent_id": "agent_abc123",
  "timestamp": "2025-11-08T10:35:00Z",
  "level": "info",
  "message": "Starting task: Open Calculator",
  "task_goal": "Open Calculator",
  "metadata": {
    "step": 1,
    "action": "click"
  }
}
```

**Response:**
```json
{
  "id": 123,
  "status": "created"
}
```

**Log Levels:**
- `info` - Normale Informationen
- `success` - Erfolgreiche Aktionen
- `warning` - Warnungen
- `error` - Fehler
- `thinking` - LLM Thinking

#### `GET /api/v1/logs/`
Liste aller Logs

**Query Parameters:**
- `agent_id` (str): Filter nach Agent
- `level` (str): Filter nach Level
- `skip` (int): Anzahl zu überspringen
- `limit` (int): Max. Anzahl

**Response:**
```json
[
  {
    "id": 123,
    "agent_id": "agent_abc123",
    "timestamp": "2025-11-08T10:35:00Z",
    "level": "info",
    "message": "Starting task: Open Calculator",
    "task_goal": "Open Calculator",
    "metadata": {"step": 1}
  }
]
```

#### `GET /api/v1/logs/{agent_id}/stream`
Stream neue Logs seit einer ID

**Query Parameters:**
- `since_id` (int): Nur Logs mit ID > since_id

**Response:**
```json
[
  {
    "id": 124,
    "timestamp": "2025-11-08T10:35:01Z",
    "level": "success",
    "message": "Calculator opened",
    "task_goal": "Open Calculator",
    "metadata": {}
  }
]
```

---

### Screenshots

#### `POST /api/v1/screenshots/`
Screenshot hochladen (benötigt API Key)

**Headers:**
```
Authorization: Bearer <api_key>
```

**Form Data:**
- `file` (file): PNG Screenshot
- `metadata` (JSON string):
```json
{
  "agent_id": "agent_abc123",
  "timestamp": "2025-11-08T10:35:00Z",
  "action_type": "before_click",
  "mouse_x": 100,
  "mouse_y": 200,
  "task_goal": "Open Calculator",
  "filename": "screenshot_before_click_20251108_103500.png",
  "file_size_bytes": 123456
}
```

**Response:**
```json
{
  "id": 456,
  "status": "uploaded",
  "url": "/screenshots/agent_abc123/screenshot_before_click_20251108_103500.png"
}
```

#### `GET /api/v1/screenshots/`
Liste aller Screenshots

**Query Parameters:**
- `agent_id` (str): Filter nach Agent
- `action_type` (str): Filter nach Action Type
- `skip` (int): Anzahl zu überspringen
- `limit` (int): Max. Anzahl

**Response:**
```json
[
  {
    "id": 456,
    "agent_id": "agent_abc123",
    "timestamp": "2025-11-08T10:35:00Z",
    "action_type": "before_click",
    "mouse_x": 100,
    "mouse_y": 200,
    "task_goal": "Open Calculator",
    "filename": "screenshot_before_click_20251108_103500.png",
    "file_size_bytes": 123456,
    "url": "/screenshots/agent_abc123/screenshot_before_click_20251108_103500.png"
  }
]
```

#### `GET /api/v1/screenshots/{agent_id}/latest`
Neueste Screenshots eines Agents

**Query Parameters:**
- `limit` (int): Max. Anzahl (default: 10)

---

## 🔒 Sicherheit

### API Key Authentifizierung

Alle geschützten Endpoints benötigen einen API Key im Header:

```
Authorization: Bearer <api_key>
```

**Geschützte Endpoints:**
- `POST /api/v1/logs/`
- `POST /api/v1/screenshots/`

**Öffentliche Endpoints:**
- `POST /api/v1/agents/register` (nur für Registrierung)
- `GET /api/v1/agents/` (Liste)
- `GET /api/v1/agents/{agent_id}` (Details)
- `GET /api/v1/logs/` (Liste)
- `GET /api/v1/screenshots/` (Liste)

### API Key Generierung

API Keys werden automatisch bei der Registrierung generiert:
- 64 Bytes URL-safe random token
- Gespeichert in Datenbank (hashed)
- Nur einmal zurückgegeben

---

## 📊 Datenbank

**SQLite** mit SQLAlchemy (async)

**Tabellen:**
- `agents` - Registrierte Agents
- `log_entries` - Log-Einträge
- `screenshots` - Screenshot-Metadaten

**Datei:** `cpa_server.db`

---

## 🎯 Für Lovable UI

### Wichtige Endpoints für UI:

1. **Agent Liste:** `GET /api/v1/agents/`
2. **Agent Details:** `GET /api/v1/agents/{agent_id}`
3. **Log Stream:** `GET /api/v1/logs/{agent_id}/stream?since_id=0`
4. **Screenshots:** `GET /api/v1/screenshots/{agent_id}/latest?limit=10`

### Polling-Strategie:

```javascript
// Alle 2 Sekunden neue Logs abrufen
setInterval(async () => {
  const logs = await fetch(`/api/v1/logs/${agentId}/stream?since_id=${lastLogId}`);
  // Update UI
}, 2000);
```

### Screenshot Anzeige:

```html
<img src="/screenshots/agent_abc123/screenshot_before_click_20251108_103500.png" />
```

---

## 🚀 Deployment (Railway)

### Environment Variables:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
DATABASE_URL=postgresql://...
SECRET_KEY=<random-secret-key>
CORS_ORIGINS=["https://your-lovable-ui.com"]
```

### Procfile:

```
web: uvicorn server.main:app --host 0.0.0.0 --port $PORT
```

