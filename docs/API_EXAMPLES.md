# CPA Scheduler API Examples

This document provides examples of how to interact with the CPA Scheduler REST API.

## Base URL
Default local development: `http://localhost:8000`

---

## 1. Job Management

### Schedule a Job
Create a new job with a task graph.

**Endpoint:** `POST /jobs`

**Request:**
```json
{
  "intent": "process_invoice",
  "tasks": {
    "open_portal": {
      "action": "open_app",
      "selector": "https://portal.example.com",
      "timeout": 30
    },
    "login": {
      "action": "click",
      "selector": "#login-button",
      "depends_on": ["open_portal"]
    },
    "download_pdf": {
      "action": "playwright",
      "selector": "download-btn",
      "text": "invoice_123.pdf",
      "depends_on": ["login"]
    },
    "send_mail": {
      "action": "send_mail",
      "selector": "finance@example.com",
      "text": "Please find the invoice attached.",
      "depends_on": ["download_pdf"]
    }
  },
  "max_retries": 3
}
```

**Response:**
```json
{
  "id": "job_abc123",
  "intent": "process_invoice",
  "status": "pending",
  "created_at": "2026-01-20T10:00:00Z",
  "retry_count": 0,
  "max_retries": 3,
  "task_count": 4
}
```

### Get Job Status
Check the current status of a job.

**Endpoint:** `GET /jobs/{job_id}`

**Response:**
```json
{
  "id": "job_abc123",
  "intent": "process_invoice",
  "status": "running",
  "created_at": "2026-01-20T10:00:00Z",
  "started_at": "2026-01-20T10:00:05Z",
  "retry_count": 0,
  "max_retries": 3,
  "task_count": 4
}
```

### List Jobs
Retrieve a list of all jobs.

**Endpoint:** `GET /jobs?status_filter=running&limit=10`

---

## 2. Agent Communication (LAM Protocol)

### Send Message from Agent
Agents use this endpoint to inform the scheduler about task progress or completion.

**Endpoint:** `POST /lam/message`

**Request (Task Done):**
```json
{
  "id": "msg_xyz789",
  "ts": "2026-01-20T10:05:00Z",
  "type": "done",
  "sender": "desktop_agent_01",
  "to": "scheduler",
  "intent": "task_completion",
  "payload": {
    "task_id": "download_pdf",
    "result": "File saved to /downloads/invoice_123.pdf"
  },
  "correlation": {
    "conversationId": "job_abc123"
  }
}
```

---

## 3. Observability

### Query Audit Log
Retrieve the execution history for a specific job.

**Endpoint:** `GET /api/v1/audit/{job_id}`

**Response:**
```json
[
  {
    "id": 1,
    "job_id": "job_abc123",
    "timestamp": "2026-01-20T10:00:05Z",
    "action": "open_app",
    "status": "started",
    "details": {"selector": "https://portal.example.com"}
  },
  {
    "id": 2,
    "job_id": "job_abc123",
    "timestamp": "2026-01-20T10:00:10Z",
    "action": "open_app",
    "status": "success",
    "details": {"result": "Portal opened"}
  }
]
```

### Health Check
Check system health and Redis connectivity.

**Endpoint:** `GET /health`
