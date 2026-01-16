# 🤝 Agent Communication Protocol

**Standardized protocol for agent-to-agent communication**

**Version:** 1.0.0
**Status:** ✅ Active
**Based on:** Lumina Agent Messages (LAM)

---

## 🎯 **Purpose**

The Agent Communication Protocol defines how agents communicate with each other in the Agentify platform:

- 🔄 **Standardized Messages** - All agents use the same message format
- 🎯 **Intent-Based** - Messages express intent, not just data
- 📡 **Transport Agnostic** - Works over HTTP, WebSocket, Message Queue
- 🔐 **Secure** - Built-in authentication and encryption
- 📊 **Traceable** - Correlation IDs for debugging

---

## 📋 **Message Types**

### **Standard Messages**

- **`request`** - Request an action from another agent
- **`inform`** - Provide information or result
- **`propose`** - Propose a solution or action
- **`agree`** - Agree to a proposal
- **`refuse`** - Refuse a proposal
- **`confirm`** - Confirm an action
- **`failure`** - Report an error or failure
- **`done`** - Report task completion

### **Discovery Messages**

- **`discover`** - Search for agents with specific capabilities
- **`offer`** - Offer capabilities to other agents
- **`assign`** - Assign a task to an agent

---

## 📦 **Message Structure**

### **Base Message**

```typescript
{
  "id": "msg-uuid-123",                    // Unique message ID
  "ts": "2026-01-16T10:30:00Z",            // ISO-8601 timestamp
  "type": "request",                       // Message type
  "sender": "agent.calculator.orchestrator", // Sender agent ID
  "to": ["agent.calculator.calculation"],  // Target agent(s)
  "intent": "calculate",                   // Task intent
  "task": "Calculate 5 + 3",               // Natural language description
  "payload": {                             // Message data
    "a": 5,
    "b": 3,
    "op": "+"
  },
  "context": {                             // Context metadata
    "customer_id": "customer-123",
    "session_id": "session-456"
  },
  "correlation": {                         // Conversation tracking
    "conversation_id": "conv-789",
    "reply_to": "msg-uuid-000"
  },
  "expected": {                            // Expected response
    "type": "inform",
    "timeout": 5000
  },
  "status": {                              // Progress tracking
    "state": "pending",
    "progress": 0.0
  },
  "security": {                            // Auth & permissions
    "token": "jwt-token-here",
    "permissions": ["calculate"]
  }
}
```

---

## 🔄 **Communication Flows**

### **1. Simple Request-Response**

```
App Orchestrator → Calculation Agent
┌─────────────────────────────────────────┐
│ REQUEST                                 │
│ {                                       │
│   "type": "request",                    │
│   "sender": "agent.app.orchestrator",   │
│   "to": ["agent.calculator.calculation"],│
│   "intent": "calculate",                │
│   "payload": { "a": 5, "b": 3, "op": "+" }│
│ }                                       │
└─────────────────────────────────────────┘
                  ↓
Calculation Agent → App Orchestrator
┌─────────────────────────────────────────┐
│ INFORM                                  │
│ {                                       │
│   "type": "inform",                     │
│   "sender": "agent.calculator.calculation",│
│   "to": ["agent.app.orchestrator"],    │
│   "intent": "result",                   │
│   "payload": { "result": 8 }            │
│ }                                       │
└─────────────────────────────────────────┘
```

### **2. Discovery Flow**

```
App Orchestrator → Marketplace Orchestrator
┌─────────────────────────────────────────┐
│ DISCOVER                                │
│ {                                       │
│   "type": "discover",                   │
│   "sender": "agent.app.orchestrator",   │
│   "to": ["agent.marketplace.orchestrator"],│
│   "intent": "find_agent",               │
│   "payload": {                          │
│     "capability": "calculation",        │
│     "customer_id": "customer-123"       │
│   }                                     │
│ }                                       │
└─────────────────────────────────────────┘
                  ↓
Marketplace Orchestrator → App Orchestrator
┌─────────────────────────────────────────┐
│ OFFER                                   │
│ {                                       │
│   "type": "offer",                      │
│   "sender": "agent.marketplace.orchestrator",│
│   "to": ["agent.app.orchestrator"],    │
│   "intent": "agent_found",              │
│   "payload": {                          │
│     "agent_id": "agent.calculator.calculation",│
│     "address": "http://calc-cust-123:8000",│
│     "capabilities": ["calculation"]     │
│   }                                     │
│ }                                       │
└─────────────────────────────────────────┘
```


### **4. Usage Tracking Flow**

```
Calculation Agent → Marketplace Orchestrator
┌─────────────────────────────────────────┐
│ INFORM                                  │
│ {                                       │
│   "type": "inform",                     │
│   "sender": "agent.calculator.calculation",│
│   "to": ["agent.marketplace.orchestrator"],│
│   "intent": "track_usage",              │
│   "payload": {                          │
│     "agent_id": "agent.calculator.calculation",│
│     "customer_id": "customer-123",      │
│     "action": "calculate",              │
│     "duration": 50,                     │
│     "timestamp": "2026-01-16T10:30:00Z" │
│   }                                     │
│ }                                       │
└─────────────────────────────────────────┘
```

---

## 🛠️ **Implementation**

### **HTTP Transport**

**Request:**
```http
POST /agent/message
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "type": "request",
  "sender": "agent.app.orchestrator",
  "to": ["agent.calculator.calculation"],
  "intent": "calculate",
  "payload": { "a": 5, "b": 3, "op": "+" }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "type": "inform",
  "sender": "agent.calculator.calculation",
  "to": ["agent.app.orchestrator"],
  "intent": "result",
  "payload": { "result": 8 }
}
```

### **WebSocket Transport**

**Client → Server:**
```json
{
  "type": "request",
  "sender": "agent.app.orchestrator",
  "to": ["agent.calculator.calculation"],
  "intent": "calculate",
  "payload": { "a": 5, "b": 3, "op": "+" }
}
```

**Server → Client:**
```json
{
  "type": "inform",
  "sender": "agent.calculator.calculation",
  "to": ["agent.app.orchestrator"],
  "intent": "result",
  "payload": { "result": 8 }
}
```

---

## 🔐 **Security**

### **Authentication**

All messages MUST include authentication:

**Option A - JWT Token (Recommended):**
```json
{
  "security": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "provider": "coresense"
  }
}
```

**Option B - API Key:**
```json
{
  "security": {
    "api_key": "sk-1234567890abcdef",
    "provider": "custom"
  }
}
```

### **Authorization**

Agents MUST verify permissions before executing actions:

```typescript
// Check if sender has permission to execute action
if (!hasPermission(message.sender, message.intent)) {
  return {
    type: "refuse",
    sender: "agent.calculator.calculation",
    to: [message.sender],
    intent: "permission_denied",
    payload: {
      error: "Insufficient permissions",
      required: ["calculate"]
    }
  };
}
```

### **Encryption**

- **Transport:** TLS 1.3 (HTTPS, WSS)
- **End-to-End:** Optional AES-256-GCM for sensitive payloads

---

## 📊 **Error Handling**

### **Failure Message**

```json
{
  "type": "failure",
  "sender": "agent.calculator.calculation",
  "to": ["agent.app.orchestrator"],
  "intent": "calculation_failed",
  "payload": {
    "error": "Division by zero",
    "code": "MATH_ERROR",
    "details": {
      "a": 5,
      "b": 0,
      "op": "/"
    }
  }
}
```

### **Timeout Handling**

If no response within `expected.timeout`:

```json
{
  "type": "failure",
  "sender": "agent.app.orchestrator",
  "to": ["agent.calculator.calculation"],
  "intent": "timeout",
  "payload": {
    "error": "Request timeout",
    "timeout": 5000,
    "original_message_id": "msg-uuid-123"
  }
}
```

---

## 🎯 **Best Practices**

### **1. Always Include Intent**

```json
// ✅ Good
{
  "type": "request",
  "intent": "calculate",
  "payload": { "a": 5, "b": 3, "op": "+" }
}

// ❌ Bad
{
  "type": "request",
  "payload": { "a": 5, "b": 3, "op": "+" }
}
```

### **2. Use Correlation IDs**

```json
{
  "correlation": {
    "conversation_id": "conv-789",
    "reply_to": "msg-uuid-000"
  }
}
```

### **3. Include Context**

```json
{
  "context": {
    "customer_id": "customer-123",
    "session_id": "session-456",
    "trace_id": "trace-789"
  }
}
```

### **4. Set Timeouts**

```json
{
  "expected": {
    "type": "inform",
    "timeout": 5000  // 5 seconds
  }
}
```

### **5. Track Progress**

```json
{
  "status": {
    "state": "in_progress",
    "progress": 0.5,  // 50%
    "message": "Processing data..."
  }
}
```

---

## 📚 **Reference Implementation**

See `scheduler/core/lam_protocol.py` for complete Python implementation:

- `BaseMessage` - Base message model
- `RequestMessage`, `InformMessage`, etc. - Specific message types
- `MessageFactory` - Factory for creating messages
- `MessageType` - Enum of all message types

---

## 🔗 **Related Documentation**

- **Agent Standard**: `README.md` - Agent Standard v1
- **Authentication**: `AUTHENTICATION.md` - Authentication & IAM
- **App Standard**: `../app_standard/README.md` - App Standard v1
- **Marketplace**: `../marketplace/README.md` - Marketplace

---

**Status:** ✅ Active
**Version:** 1.0.0
**Date:** 2026-01-16


