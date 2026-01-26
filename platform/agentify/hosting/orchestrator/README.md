# 🏠 Hosting Orchestrator

**Agent ID:** `agent.agentify.hosting-orchestrator`  
**Version:** 1.0.0  
**Status:** ✅ Implemented (Railway deployment)

---

## 🎯 Overview

The Hosting Orchestrator is an Agentify agent that manages deployments of other agents to:
- **Railway** (cloud platform) ✅ Implemented
- **Edge devices** (Raspberry Pi) 🚧 Coming in Phase 1.2

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
- `RAILWAY_API_KEY` - Your Railway API key (for cloud deployments)

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

## 📡 Agent Communication Protocol

### Deploy to Railway

**Request:**
```json
{
  "type": "request",
  "sender": "agent.marketplace.orchestrator",
  "to": ["agent.agentify.hosting-orchestrator"],
  "intent": "deploy_to_railway",
  "payload": {
    "agent_id": "agent.calculator.calculation",
    "customer_id": "customer-123",
    "image": "ghcr.io/agentify/calculation-agent:1.0.0",
    "env": {
      "PORT": "8000",
      "API_KEY": "secret"
    },
    "resources": {
      "cpu": "0.5",
      "memory": "512Mi"
    }
  }
}
```

**Response:**
```json
{
  "type": "inform",
  "sender": "agent.agentify.hosting-orchestrator",
  "to": ["agent.marketplace.orchestrator"],
  "intent": "deploy_to_railway_complete",
  "payload": {
    "deployment_id": "dep-abc123",
    "container_id": "svc-xyz789",
    "address": "https://calculation-customer-123.railway.app",
    "health_url": "https://calculation-customer-123.railway.app/health",
    "status": "deploying"
  }
}
```

### Get Agent Address

**Request:**
```json
{
  "type": "request",
  "sender": "agent.app.orchestrator",
  "to": ["agent.agentify.hosting-orchestrator"],
  "intent": "get_address",
  "payload": {
    "agent_id": "agent.calculator.calculation",
    "customer_id": "customer-123"
  }
}
```

**Response:**
```json
{
  "type": "inform",
  "sender": "agent.agentify.hosting-orchestrator",
  "to": ["agent.app.orchestrator"],
  "intent": "get_address_complete",
  "payload": {
    "address": "https://calculation-customer-123.railway.app",
    "health": "healthy",
    "uptime": 3600
  }
}
```

### Health Check

**Request:**
```json
{
  "type": "request",
  "sender": "agent.monitoring.health",
  "to": ["agent.agentify.hosting-orchestrator"],
  "intent": "health_check",
  "payload": {
    "container_id": "svc-xyz789"
  }
}
```

**Response:**
```json
{
  "type": "inform",
  "sender": "agent.agentify.hosting-orchestrator",
  "to": ["agent.monitoring.health"],
  "intent": "health_check_complete",
  "payload": {
    "container_id": "svc-xyz789",
    "health": "healthy",
    "response_time": 45
  }
}
```

---

## 🗄️ Database Schema

The orchestrator uses Supabase (PostgreSQL) with the following tables:

### `containers`
```sql
CREATE TABLE containers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  container_id TEXT UNIQUE NOT NULL,
  agent_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  image TEXT NOT NULL,
  address TEXT NOT NULL,
  health_url TEXT NOT NULL,
  status TEXT NOT NULL,
  health TEXT NOT NULL,
  cpu_usage FLOAT,
  memory_usage FLOAT,
  disk_usage FLOAT,
  load FLOAT,
  uptime INTEGER,
  target_type TEXT NOT NULL,
  target_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `health_checks`
```sql
CREATE TABLE health_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  container_id TEXT NOT NULL,
  status TEXT NOT NULL,
  response_time INTEGER,
  load FLOAT,
  error_message TEXT,
  checked_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

---

## 📦 Deployment

### Deploy to Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Set environment variables in Railway dashboard
4. Deploy!

---

## ✅ Implementation Status

- [x] Project structure
- [x] TypeScript configuration
- [x] Agent manifest
- [x] Railway deployer
- [x] Database client
- [x] Agent protocol handlers
- [x] Health check system
- [x] Logging
- [ ] Edge deployer (Phase 1.2)
- [ ] UI dashboard (Phase 1.2)
- [ ] Auto-scaling (Phase 1.2)

---

**Next:** Implement Edge Deployment (Phase 1.2)

