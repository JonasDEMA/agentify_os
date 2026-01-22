# 📝 Logging Agent

**Version:** 1.0.0  
**Status:** ✅ Implemented

---

## 🎯 Overview

The Logging Agent is an infrastructure agent that provides centralized log collection, search, and streaming for cloud and edge agents. It transforms logging into a first-class agent capability that can be discovered and orchestrated by AI.

**Key Features:**
- **Log Collection** - Collect logs from containers and devices
- **Log Search** - Search logs with complex filters
- **Real-time Streaming** - Stream logs via WebSocket
- **Log Export** - Export logs to various formats
- **Retention Policies** - Automatic log cleanup
- **Agent Communication Protocol** - Full integration with Agentify platform

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key

### 3. Run Development Server

```bash
npm run dev
```

### 4. Build for Production

```bash
npm run build
npm start
```

---

## 📡 API Endpoints

### Agent Communication Protocol

**POST** `/agent/message`

Handle agent messages with the following intents:
- `collect_logs` - Collect logs from source
- `search_logs` - Search logs with filters
- `stream_logs` - Get streaming info
- `export_logs` - Export logs
- `get_stats` - Get statistics

**Example Request:**
```json
{
  "id": "msg-123",
  "ts": "2026-01-22T12:00:00Z",
  "type": "request",
  "sender": "agent.marketplace.orchestrator",
  "to": ["agent.agentify.logging"],
  "intent": "collect_logs",
  "payload": {
    "source_type": "container",
    "source_id": "container-abc123",
    "customer_id": "customer-123",
    "tail": 100
  }
}
```

**Example Response:**
```json
{
  "id": "msg-124",
  "ts": "2026-01-22T12:00:01Z",
  "type": "inform",
  "sender": "agent.agentify.logging",
  "to": ["agent.marketplace.orchestrator"],
  "intent": "collect_logs",
  "payload": {
    "logs": [...],
    "count": 100
  }
}
```

### REST API Endpoints

#### Collect Logs
**POST** `/api/v1/logs/collect`

```json
{
  "source_type": "container",
  "source_id": "container-abc123",
  "customer_id": "customer-123",
  "tail": 100
}
```

#### Search Logs
**POST** `/api/v1/logs/search`

```json
{
  "customer_id": "customer-123",
  "query": "error",
  "level": "error",
  "start_time": "2026-01-22T00:00:00Z",
  "end_time": "2026-01-22T23:59:59Z",
  "limit": 100
}
```

#### Stream Logs (WebSocket)
**WS** `/api/v1/logs/stream`

Connect via WebSocket and send:
```json
{
  "source_type": "container",
  "source_id": "container-abc123",
  "customer_id": "customer-123",
  "level": "error"
}
```

#### Export Logs
**POST** `/api/v1/logs/export`

```json
{
  "search": {
    "customer_id": "customer-123",
    "level": "error"
  },
  "format": "json",
  "destination": "local"
}
```

#### Get Export Job
**GET** `/api/v1/logs/export/:job_id`

#### Get Retention Policy
**GET** `/api/v1/retention-policies/:customer_id`

#### Create Retention Policy
**POST** `/api/v1/retention-policies`

```json
{
  "customer_id": "customer-123",
  "retention_days": 30,
  "compression_enabled": true
}
```

#### Get Statistics
**GET** `/api/v1/stats/:customer_id`

#### Health Check
**GET** `/health`

---

## 🔍 Log Collection

### From Containers

The Logging Agent uses Dockerode to collect logs from Docker containers:

```typescript
// Collect last 100 lines
POST /api/v1/logs/collect
{
  "source_type": "container",
  "source_id": "container-abc123",
  "customer_id": "customer-123",
  "tail": 100
}

// Collect logs since timestamp
{
  "source_type": "container",
  "source_id": "container-abc123",
  "customer_id": "customer-123",
  "since": "2026-01-22T12:00:00Z"
}
```

### From Devices

Collect logs from edge devices via HTTP:

```typescript
POST /api/v1/logs/collect
{
  "source_type": "device",
  "source_id": "raspi-001",
  "customer_id": "customer-123",
  "tail": 100
}
```

---

## 🔎 Log Search

Search logs with powerful filters:

```typescript
POST /api/v1/logs/search
{
  "customer_id": "customer-123",
  "query": "database connection",
  "level": "error",
  "source_type": "container",
  "source_id": "api-container",
  "start_time": "2026-01-22T00:00:00Z",
  "end_time": "2026-01-22T23:59:59Z",
  "tags": ["production"],
  "limit": 100,
  "offset": 0
}
```

Response:
```json
{
  "success": true,
  "data": {
    "logs": [...],
    "count": 42,
    "has_more": false,
    "total": 42
  }
}
```

---

## 📊 Real-time Streaming

Stream logs in real-time via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:3004/api/v1/logs/stream');

ws.on('open', () => {
  ws.send(JSON.stringify({
    source_type: 'container',
    source_id: 'container-abc123',
    customer_id: 'customer-123',
    level: 'error'
  }));
});

ws.on('message', (data) => {
  const log = JSON.parse(data);
  console.log(log);
});
```

---

## 🗄️ Database Schema

### `logs` Table
```sql
CREATE TABLE logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ NOT NULL,
  level TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  message TEXT NOT NULL,
  metadata JSONB,
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_logs_customer ON logs(customer_id);
CREATE INDEX idx_logs_source ON logs(source_id);
CREATE INDEX idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX idx_logs_level ON logs(level);
```

### `retention_policies` Table
```sql
CREATE TABLE retention_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL UNIQUE,
  source_type TEXT,
  level TEXT,
  retention_days INTEGER NOT NULL,
  compression_enabled BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `export_jobs` Table
```sql
CREATE TABLE export_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  status TEXT NOT NULL,
  format TEXT NOT NULL,
  destination TEXT NOT NULL,
  log_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  error TEXT,
  download_url TEXT
);
```

---

## 🎯 Agent Capabilities

The Logging Agent exposes the following capabilities:

- `log_collection` (expert) - Collect logs from containers and agents
- `log_forwarding` (high) - Forward logs to external systems
- `log_search` (expert) - Search and filter logs
- `log_streaming` (high) - Real-time log streaming
- `log_retention` (high) - Manage log retention policies

---

## ✅ Implementation Status

- [x] Project structure
- [x] Agent manifest with capabilities
- [x] TypeScript configuration
- [x] Type definitions
- [x] Database client
- [x] Log collector (containers + devices)
- [x] Log search engine
- [x] Agent Communication Protocol
- [x] REST API endpoints
- [x] WebSocket streaming
- [x] Background cleanup job
- [x] Export functionality
- [x] Retention policies

---

**Next:** Deploy to production and integrate with Marketplace Orchestrator

