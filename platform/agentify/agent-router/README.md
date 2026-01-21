# 🔀 Agent Router

**Version:** 1.0.0  
**Status:** ✅ Implemented

---

## 🎯 Overview

The Agent Router is a service that routes messages between cloud and edge agents in the Agentify platform. It handles:
- **Message Routing** - Routes messages to agents based on location (cloud vs edge)
- **Agent Discovery** - Maintains registry of all agents across cloud and edge
- **Message Queuing** - Queues messages for offline agents
- **Retry Logic** - Automatically retries failed deliveries with exponential backoff
- **Cross-Boundary Communication** - Enables seamless communication between cloud and edge agents

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
- `DEVICE_MANAGER_URL` - Device Manager service URL

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

### Register Agent

**POST** `/api/v1/agents/register`

Register an agent with the router.

**Request:**
```json
{
  "agent_id": "agent.energy.api",
  "location": "edge",
  "address": "http://100.64.0.1:8000",
  "device_id": "raspi-001",
  "customer_id": "customer-123",
  "capabilities": ["energy-monitoring", "grid-control"],
  "status": "online",
  "metadata": {
    "version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "agent_id": "agent.energy.api",
    "location": "edge",
    "address": "http://100.64.0.1:8000",
    "status": "online",
    "last_seen": "2024-01-21T12:00:00Z"
  },
  "message": "Agent registered successfully. 2 pending messages delivered."
}
```

### Unregister Agent

**DELETE** `/api/v1/agents/:agent_id`

Unregister an agent from the router.

### Update Agent Status

**PUT** `/api/v1/agents/:agent_id/status`

Update agent status (online/offline).

**Request:**
```json
{
  "status": "online"
}
```

### Discover Agents

**POST** `/api/v1/agents/discover`

Discover agents by capabilities, location, or customer.

**Request:**
```json
{
  "capabilities": ["energy-monitoring"],
  "location": "edge",
  "customer_id": "customer-123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "agent_id": "agent.energy.api",
        "location": "edge",
        "address": "http://100.64.0.1:8000",
        "capabilities": ["energy-monitoring", "grid-control"],
        "status": "online"
      }
    ]
  }
}
```

### Get Agent

**GET** `/api/v1/agents/:agent_id`

Get agent details by ID.

### Route Message

**POST** `/api/v1/route`

Route a message to one or more agents.

**Request:**
```json
{
  "id": "msg-123",
  "ts": "2024-01-21T12:00:00Z",
  "type": "request",
  "sender": "agent.marketplace.orchestrator",
  "to": ["agent.energy.api"],
  "intent": "get_energy_data",
  "payload": {
    "start_time": "2024-01-21T00:00:00Z",
    "end_time": "2024-01-21T12:00:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "success": true,
        "delivered": true,
        "queued": false,
        "response": {
          "type": "inform",
          "sender": "agent.energy.api",
          "payload": { "data": [...] }
        }
      }
    ],
    "all_delivered": true,
    "any_queued": false
  },
  "message": "All messages delivered"
}
```

### Get Pending Messages

**GET** `/api/v1/agents/:agent_id/pending`

Get pending messages for an agent.

**Query Parameters:**
- `limit` - Maximum number of messages to return (default: 10)

### Get Statistics

**GET** `/api/v1/stats`

Get router statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_agents": 15,
    "cloud_agents": 10,
    "edge_agents": 5,
    "online_agents": 12,
    "pending_messages": 3
  }
}
```

---

## 🔄 Message Routing Flow

### Cloud-to-Cloud
```
Cloud Agent A → Agent Router → Cloud Agent B
```

### Cloud-to-Edge
```
Cloud Agent → Agent Router → Tailscale → Edge Agent (Raspberry Pi)
```

### Edge-to-Cloud
```
Edge Agent → Tailscale → Agent Router → Cloud Agent
```

### Edge-to-Edge
```
Edge Agent A → Tailscale → Agent Router → Tailscale → Edge Agent B
```

---

## 📦 Message Queuing

When an agent is offline, messages are automatically queued:

1. **Message arrives** for offline agent
2. **Router queues** message in database
3. **Agent comes online** and registers/updates status
4. **Router delivers** all pending messages
5. **Retry logic** with exponential backoff if delivery fails

**Retry Schedule:**
- Attempt 1: Immediate
- Attempt 2: +1 second
- Attempt 3: +2 seconds
- Attempt 4: +4 seconds
- Max retries: 3 (configurable)

---

## 🗄️ Database Schema

### `agent_registry` Table
```sql
CREATE TABLE agent_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT UNIQUE NOT NULL,
  location TEXT NOT NULL,
  address TEXT NOT NULL,
  device_id TEXT,
  customer_id TEXT NOT NULL,
  capabilities TEXT[] NOT NULL,
  status TEXT NOT NULL,
  metadata JSONB,
  last_seen TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `message_queue` Table
```sql
CREATE TABLE message_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message JSONB NOT NULL,
  target_agent_id TEXT NOT NULL,
  target_location TEXT NOT NULL,
  target_device_id TEXT,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  next_retry_at TIMESTAMPTZ,
  delivered BOOLEAN DEFAULT FALSE,
  delivered_at TIMESTAMPTZ,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Router                            │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Message    │         │    Agent     │                 │
│  │   Router     │◄────────┤   Registry   │                 │
│  └──────┬───────┘         └──────────────┘                 │
│         │                                                    │
│         │                 ┌──────────────┐                 │
│         └─────────────────┤   Message    │                 │
│                           │    Queue     │                 │
│                           └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
         │                           │
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  Cloud Agents   │         │  Edge Agents    │
│  (Railway)      │         │  (Tailscale)    │
└─────────────────┘         └─────────────────┘
```

---

## ✅ Implementation Status

- [x] Project structure
- [x] TypeScript configuration
- [x] Agent registry database
- [x] Message queue database
- [x] Message router with cloud/edge routing
- [x] Retry logic with exponential backoff
- [x] Agent discovery API
- [x] Message routing API
- [x] Background message processor
- [x] Statistics endpoint
- [ ] WebSocket support for real-time updates
- [ ] Redis caching for agent registry
- [ ] Load balancing for multi-instance agents
- [ ] Message encryption for edge communication

---

**Next:** Integrate with Marketplace Orchestrator and test end-to-end routing

