# 🔄 Agent Standard Integration Proposal

**Date:** 2026-01-20  
**Status:** PROPOSAL  
**Goal:** Integrate CPA Scheduler, Team Discovery, and RAG into Agent Standard v1

---

## 🎯 **Executive Summary**

This proposal outlines how to integrate three critical capabilities into every agent:

1. **Schedule** - Built-in CPA scheduler for task orchestration
2. **Team** - Marketplace-based team discovery with human-in-the-loop approval
3. **Knowledge** - RAG hooks provided by hosting agents

**Key Principle:** These are **runtime capabilities** provided by the platform, not implementation requirements. Agents describe what they need, the platform provides it.

---

## 📊 **Current State vs. Proposed State**

| Area | Current State | Proposed State |
|------|---------------|----------------|
| **Schedule** | Dict in manifest, no runtime | CPA Scheduler integrated into every agent runtime |
| **Team** | Dict in manifest, no runtime | Marketplace discovery + human approval workflow |
| **Knowledge** | Dict in manifest, no runtime | RAG hook provided by hosting agent |

---

## 1️⃣ **Schedule Integration - Built-in CPA Scheduler**

### **Problem**
- Agents have `schedule` field in manifest (cron jobs)
- No runtime implementation
- CPA Scheduler exists but is separate component

### **Solution: Embed CPA Scheduler in Agent Runtime**

Every agent gets a built-in scheduler that:
- ✅ Reads `schedule.jobs` from manifest
- ✅ Executes tasks via CPA TaskGraph
- ✅ Supports cron expressions, dependencies, parallel execution
- ✅ Integrates with ethics engine and oversight

### **Architecture**

```
Agent Runtime
├── Ethics Engine ✅ (existing)
├── Desire Monitor ✅ (existing)
├── Oversight Controller ✅ (existing)
└── CPA Scheduler ⭐ (NEW)
    ├── Job Queue (Redis)
    ├── Task Graph Builder
    ├── Cron Parser
    └── Task Executor
```

### **Manifest Example**

```json
{
  "schedule": {
    "jobs": [
      {
        "id": "daily_health_check",
        "name": "Daily Health Check",
        "cron": "0 9 * * *",
        "timezone": "UTC",
        "action": {
          "type": "tool_call",
          "tool": "health_check",
          "params": {}
        },
        "enabled": true
      }
    ]
  }
}
```

### **Runtime Behavior**

1. Agent starts → Scheduler reads `schedule.jobs`
2. Scheduler registers cron jobs
3. At trigger time → Creates TaskGraph → Executes via CPA Scheduler
4. Ethics + Oversight applied to every scheduled task
5. Results logged to activities queue

### **Implementation Plan**

- [ ] Create `core/agent_standard/core/scheduler.py`
- [ ] Integrate CPA `TaskGraph` and `JobQueue`
- [ ] Add scheduler to `AgentRuntime.start()`
- [ ] Create `Schedule` Pydantic model
- [ ] Add tests for scheduled task execution

---

## 2️⃣ **Team Integration - Marketplace Discovery + Human Approval**

### **Problem**
- Agents have `team` field in manifest
- No runtime logic for team composition
- No marketplace integration

### **Solution: Marketplace-Based Team Discovery with Human-in-the-Loop**

Every agent can request team members from marketplace(s) with mandatory human approval.

### **Architecture**

```
Agent needs team member
    ↓
1. Query Marketplace(s) for capability
    ↓
2. Marketplace returns candidate agents
    ↓
3. Human-in-the-Loop approval (via Oversight)
    ↓
4. Approved agents added to team
    ↓
5. Team collaboration begins
```

### **Manifest Example**

```json
{
  "team": {
    "discovery": {
      "enabled": true,
      "marketplaces": [
        "marketplace://default",
        "marketplace://energy-sector"
      ],
      "approval_required": true
    },
    "members": [
      {
        "agent_id": "agent.acme.data-analyst",
        "role": "data_analysis",
        "trust_level": 0.9,
        "status": "active"
      }
    ]
  }
}
```

### **Runtime Behavior**

1. Agent needs capability (e.g., "data_analysis")
2. Runtime queries configured marketplaces
3. Marketplace returns candidates with pricing
4. **Human approval required** (via Oversight escalation)
5. Human approves/rejects candidates
6. Approved agents added to `team.members`
7. Agent can now delegate tasks to team

### **Implementation Plan**

- [ ] Create `core/agent_standard/core/team_manager.py`
- [ ] Integrate marketplace discovery protocol
- [ ] Add human approval workflow via `OversightController`
- [ ] Create `Team` Pydantic model with discovery config
- [ ] Add team member trust level tracking

---

## 3️⃣ **Knowledge Integration - RAG Hook from Hosting Agent**

### **Problem**
- Agents have `knowledge` field in manifest
- No RAG implementation
- Every agent would need to implement RAG separately

### **Solution: Hosting Agent Provides RAG as Default Service**

The **hosting agent** (Railway, AWS, Edge) provides RAG infrastructure as a default service. Agents just hook into it.

### **Architecture**

```
Hosting Agent (Railway/AWS/Edge)
├── Container Management
├── Network Configuration
└── Default Services ⭐
    ├── RAG Service (Vector DB + Embeddings)
    ├── Memory Service (Redis/PostgreSQL)
    └── Observability Service (Logs/Metrics)

Agent Runtime
└── Knowledge Manager
    └── Connects to Hosting Agent's RAG Service
```

### **Manifest Example**

```json
{
  "knowledge": {
    "rag": {
      "enabled": true,
      "provider": "hosting_agent_default",
      "collections": [
        {
          "name": "product_docs",
          "description": "Product documentation",
          "embedding_model": "text-embedding-3-small",
          "chunk_size": 512,
          "retrieval_policy": {
            "top_k": 5,
            "min_similarity": 0.7
          }
        }
      ]
    },
    "data_permissions": {
      "allowed_sources": ["internal_docs", "public_web"],
      "pii_handling": "redact"
    }
  }
}
```

### **Runtime Behavior**

1. **Hosting Agent Startup:**
   - Deploys agent container
   - Provisions RAG service (Vector DB + Embeddings API)
   - Injects RAG endpoint into agent environment

2. **Agent Startup:**
   - Reads `knowledge.rag` from manifest
   - Connects to hosting agent's RAG service
   - Creates/loads collections

3. **Agent Execution:**
   - Agent queries RAG via `knowledge_manager.query("What is X?")`
   - RAG service returns relevant chunks
   - Agent uses chunks in LLM context

### **Hosting Agent Responsibilities**

| Hosting Agent | RAG Implementation |
|---------------|-------------------|
| **Railway** | Supabase pgvector + OpenAI embeddings |
| **AWS** | Amazon Bedrock Knowledge Bases |
| **GCP** | Vertex AI Vector Search |
| **Edge** | Local ChromaDB + local embeddings (Ollama) |

**Key Insight:** Agent doesn't care HOW RAG is implemented - it just uses the hook.

### **Implementation Plan**

- [ ] Create `core/agent_standard/core/knowledge_manager.py`
- [ ] Define RAG service interface (query, add, delete)
- [ ] Create `Knowledge` Pydantic model with RAG config
- [ ] Add hosting agent RAG provisioning spec
- [ ] Implement reference RAG service (Supabase)

---

## 🏗️ **Unified Architecture**

### **Agent Runtime Components (After Integration)**

```
AgentRuntime
├── 1. Ethics Engine ✅ (existing)
├── 2. Desire Monitor ✅ (existing)
├── 3. Oversight Controller ✅ (existing)
├── 4. CPA Scheduler ⭐ (NEW)
│   ├── Job Queue (Redis)
│   ├── Task Graph Builder
│   └── Cron Parser
├── 5. Team Manager ⭐ (NEW)
│   ├── Marketplace Discovery
│   ├── Human Approval Workflow
│   └── Trust Level Tracking
└── 6. Knowledge Manager ⭐ (NEW)
    ├── RAG Service Client
    ├── Collection Management
    └── Query Interface
```

### **Hosting Agent Responsibilities**

```
Hosting Agent (Railway/AWS/Edge)
├── Container Deployment
├── Network Configuration
├── Default Services
│   ├── RAG Service (Vector DB + Embeddings)
│   ├── Memory Service (Redis/PostgreSQL)
│   └── Observability (Logs/Metrics)
└── Environment Injection
    ├── RAG_ENDPOINT=https://...
    ├── MEMORY_ENDPOINT=redis://...
    └── METRICS_ENDPOINT=https://...
```

---

## 📋 **Implementation Roadmap**

### **Phase 1: Schedule Integration (Week 1-2)**
- [ ] Create `Schedule` Pydantic model
- [ ] Create `core/agent_standard/core/scheduler.py`
- [ ] Integrate CPA `TaskGraph` and `JobQueue`
- [ ] Add scheduler to `AgentRuntime.start()`
- [ ] Write tests for scheduled task execution
- [ ] Update documentation

### **Phase 2: Team Integration (Week 3-4)**
- [ ] Create `Team` Pydantic model with discovery config
- [ ] Create `core/agent_standard/core/team_manager.py`
- [ ] Implement marketplace discovery protocol
- [ ] Add human approval workflow via `OversightController`
- [ ] Add team member trust level tracking
- [ ] Write tests for team discovery and approval
- [ ] Update documentation

### **Phase 3: Knowledge Integration (Week 5-6)**
- [ ] Create `Knowledge` Pydantic model with RAG config
- [ ] Create `core/agent_standard/core/knowledge_manager.py`
- [ ] Define RAG service interface
- [ ] Implement reference RAG service (Supabase)
- [ ] Add hosting agent RAG provisioning spec
- [ ] Write tests for RAG integration
- [ ] Update documentation

### **Phase 4: Integration Testing (Week 7)**
- [ ] End-to-end tests with all 3 components
- [ ] Performance testing
- [ ] Security audit
- [ ] Documentation review

---

## 🎯 **Success Criteria**

### **Schedule**
- ✅ Every agent can define cron jobs in manifest
- ✅ Jobs execute automatically via CPA Scheduler
- ✅ Ethics + Oversight applied to scheduled tasks
- ✅ Task dependencies and parallel execution work

### **Team**
- ✅ Agents can query marketplace(s) for capabilities
- ✅ Human approval required before adding team members
- ✅ Trust levels tracked and enforced
- ✅ Team collaboration works across agents

### **Knowledge**
- ✅ Hosting agents provide RAG as default service
- ✅ Agents can query RAG without implementing it
- ✅ Multiple collections supported
- ✅ Data permissions enforced

---

## 🚀 **Next Steps**

1. **Review this proposal** with team
2. **Prioritize phases** based on business needs
3. **Assign owners** for each phase
4. **Create detailed technical specs** for each component
5. **Start Phase 1** (Schedule Integration)

---

## 📚 **References**

- **CPA Scheduler:** `scheduler/` directory
- **Agent Standard:** `core/agent_standard/`
- **Platform Architecture:** `platform/agentify/PLATFORM_ARCHITECTURE.md`
- **Implementation Status:** `platform/agentify/agent_standard/IMPLEMENTATION_STATUS.md`

---

**Questions? Feedback?** Let's discuss! 💬


