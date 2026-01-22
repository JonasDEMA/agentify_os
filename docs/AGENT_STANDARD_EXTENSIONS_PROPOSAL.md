# 🔧 Agent Standard v1 - Extensions Proposal

**Date:** January 2026  
**Status:** PROPOSAL  
**Author:** Jonas Moßler

---

## 📋 **Overview**

This document proposes **7 critical extensions** to Agent Standard v1 to enable:
1. **Agent Discovery & Routing** via addresses
2. **Contract-Based Collaboration** beyond simple I/O
3. **Manifest Introspection** for agent-to-agent understanding
4. **Dynamic LLM Configuration** for flexible model management
5. **Authentication** - Formalized IAM integration
6. **Authorization** - Permission management
7. **Marketplaces** - Agent discovery and team building with governance

Additionally, we clarify **IAM/Permission Management** - who holds permissions and how agents know what they're allowed to do.

---

## 🎯 **Current State Analysis**

### **What We Have:**

✅ **I/O Contracts** (`core/agent_standard/models/io_contracts.py`)
- Input/Output schemas with JSON Schema validation
- Format support (json, text, audio, markdown)
- Contract versioning

✅ **Authentication** (`platform/agentify/agent_standard/AUTHENTICATION.md`)
- CoreSense IAM integration
- JWT token validation
- RBAC roles: admin, developer, user, viewer
- Resource-level access control (public, organization, team, project)

✅ **Authorization in Manifest** (documented but not in Pydantic models)
- `authentication` section with provider, roles_required, scopes_required
- `authorization` section with visibility, rbac_enabled, custom_policies

✅ **AI Model Configuration** (`core/agent_standard/models/manifest.py`)
- `AIModel` class with provider, model_id, temperature, max_tokens
- Optional field in `AgentManifest`

❌ **What We're Missing:**

1. **Addresses** - No way to specify where agents are located (for routing/redundancy)
2. **Contracts** - I/O exists, but no formal contract agreements between agents
3. **Manifest Endpoints** - No standardized way to query another agent's manifest
4. **LLM Runtime Control** - Model config exists but no runtime switching/permissions
5. **IAM in Pydantic Models** - Authentication/Authorization documented but not in core models

---

## 🚀 **Proposed Extensions**

---

## **1. Addresses - Agent Location & Routing**

### **Purpose**
Enable agents to discover and route to each other, support redundancy, and handle multi-instance deployments.

### **Use Cases**
- Agent A needs to call Agent B → looks up B's address
- Agent deployed in 3 regions → multiple addresses for load balancing
- Hosting agent manages address registry for all deployed agents
- Marketplace provides address discovery service

### **Manifest Schema**

```json
{
  "addresses": {
    "primary": {
      "url": "https://agent-calc.railway.app",
      "protocol": "https",
      "type": "rest_api",
      "health_check": "/health",
      "status": "active"
    },
    "redundant": [
      {
        "url": "https://agent-calc-eu.railway.app",
        "protocol": "https",
        "type": "rest_api",
        "health_check": "/health",
        "status": "active",
        "region": "eu-central-1"
      },
      {
        "url": "https://agent-calc-us.railway.app",
        "protocol": "https",
        "type": "rest_api",
        "health_check": "/health",
        "status": "standby",
        "region": "us-east-1"
      }
    ],
    "discovery": {
      "enabled": true,
      "registry_url": "https://marketplace.agentify.io/api/registry",
      "auto_register": true,
      "heartbeat_interval_sec": 60
    }
  }
}
```

### **Pydantic Model**

```python
# core/agent_standard/models/addresses.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class Address(BaseModel):
    """A single agent address/endpoint."""
    
    url: HttpUrl = Field(..., description="Full URL to agent endpoint")
    protocol: Literal["https", "http", "grpc", "websocket"] = Field(
        default="https",
        description="Communication protocol"
    )
    type: Literal["rest_api", "graphql", "grpc", "websocket"] = Field(
        default="rest_api",
        description="API type"
    )
    health_check: str = Field(
        default="/health",
        description="Health check endpoint path"
    )
    status: Literal["active", "standby", "maintenance", "offline"] = Field(
        default="active",
        description="Current status"
    )
    region: str | None = Field(
        default=None,
        description="Geographic region (e.g., 'eu-central-1')"
    )
    priority: int = Field(
        default=100,
        ge=0,
        le=1000,
        description="Routing priority (higher = preferred)"
    )

class AddressDiscovery(BaseModel):
    """Address discovery configuration."""
    
    enabled: bool = Field(default=True, description="Enable address discovery")
    registry_url: HttpUrl = Field(
        ...,
        description="URL of address registry service"
    )
    auto_register: bool = Field(
        default=True,
        description="Automatically register on startup"
    )
    heartbeat_interval_sec: int = Field(
        default=60,
        ge=10,
        description="Heartbeat interval in seconds"
    )

class Addresses(BaseModel):
    """Complete address configuration for an agent."""

    primary: Address = Field(..., description="Primary address")
    redundant: list[Address] = Field(
        default_factory=list,
        description="Redundant addresses for failover"
    )
    discovery: AddressDiscovery | None = Field(
        default=None,
        description="Discovery service configuration"
    )

---

## **2. Contracts - Formal Agent Agreements**

### **Purpose**
Go beyond simple I/O schemas to define **formal contracts** between agents, including:
- What services an agent offers
- What contracts it has agreed to with specific agents
- SLAs, rate limits, and pricing per contract
- Contract lifecycle (proposed, active, suspended, terminated)

### **Difference from I/O:**
- **I/O** = Technical schema (input/output format)
- **Contracts** = Business agreement (who, what, when, how much, SLA)

### **Use Cases**
- Agent A offers "meeting_summary" contract to any agent
- Agent B requests contract with Agent A → human approves → contract active
- Contract includes: max 100 requests/day, 95% uptime SLA, $0.01 per request
- Agent can query: "Which contracts do I have with Agent X?"

### **Manifest Schema**

```json
{
  "contracts": {
    "offered": [
      {
        "contract_id": "contract.calc.basic-math-v1",
        "name": "Basic Math Operations",
        "version": "1.0.0",
        "description": "Addition, subtraction, multiplication, division",
        "io_contract_ref": "io.calc.math-v1",
        "availability": "public",
        "sla": {
          "uptime_percent": 99.5,
          "max_response_time_ms": 500,
          "rate_limit": {
            "requests_per_minute": 100,
            "requests_per_day": 10000
          }
        },
        "pricing": {
          "model": "per_request",
          "price_per_request": 0.001,
          "currency": "USD",
          "free_tier": {
            "requests_per_day": 100
          }
        },
        "requires_approval": false
      }
    ],
    "active": [
      {
        "contract_id": "contract.calc.basic-math-v1",
        "with_agent": "agent.app.orchestrator",
        "status": "active",
        "started_at": "2026-01-15T10:00:00Z",
        "expires_at": null,
        "usage": {
          "requests_today": 45,
          "requests_this_month": 1250
        },
        "custom_terms": {
          "rate_limit": {
            "requests_per_minute": 200
          }
        }
      }
    ],
    "pending": [
      {
        "contract_id": "contract.nlp.sentiment-v1",
        "with_agent": "agent.external.sentiment-analyzer",
        "requested_at": "2026-01-22T08:00:00Z",
        "requested_by": "human:admin@company.com",
        "status": "pending_approval",
        "approval_required_from": "human:supervisor@company.com"
      }
    ]
  }
}
```

### **Pydantic Models**

```python
# core/agent_standard/models/contracts.py

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Literal

class RateLimit(BaseModel):
    """Rate limiting configuration."""

    requests_per_minute: int | None = Field(default=None, ge=1)
    requests_per_day: int | None = Field(default=None, ge=1)
    requests_per_month: int | None = Field(default=None, ge=1)
    concurrent_requests: int | None = Field(default=None, ge=1)

class SLA(BaseModel):
    """Service Level Agreement."""

    uptime_percent: float = Field(
        default=99.0,
        ge=0.0,
        le=100.0,
        description="Guaranteed uptime percentage"
    )
    max_response_time_ms: int = Field(
        default=1000,
        ge=1,
        description="Maximum response time in milliseconds"
    )
    rate_limit: RateLimit | None = Field(
        default=None,
        description="Rate limiting"
    )

class PricingModel(BaseModel):
    """Pricing configuration for a contract."""

    model: Literal["free", "per_request", "per_minute", "per_hour", "per_day", "subscription"] = Field(
        default="free",
        description="Pricing model"
    )
    price_per_request: float | None = Field(default=None, ge=0.0)
    price_per_minute: float | None = Field(default=None, ge=0.0)
    price_per_hour: float | None = Field(default=None, ge=0.0)
    price_per_day: float | None = Field(default=None, ge=0.0)
    subscription_price_per_month: float | None = Field(default=None, ge=0.0)
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")
    free_tier: dict[str, int] | None = Field(
        default=None,
        description="Free tier limits (e.g., {'requests_per_day': 100})"
    )

class OfferedContract(BaseModel):
    """A contract offered by this agent to others."""

    contract_id: str = Field(..., description="Unique contract identifier")
    name: str = Field(..., description="Human-readable contract name")
    version: str = Field(default="1.0.0", description="Contract version")
    description: str = Field(..., description="What this contract provides")
    io_contract_ref: str = Field(
        ...,
        description="Reference to IO contract (from io section)"
    )
    availability: Literal["public", "organization", "team", "private"] = Field(
        default="public",
        description="Who can request this contract"
    )
    sla: SLA = Field(default_factory=SLA, description="Service level agreement")
    pricing: PricingModel = Field(
        default_factory=PricingModel,
        description="Pricing model"
    )
    requires_approval: bool = Field(
        default=True,
        description="Whether contract requests require human approval"
    )

class ContractUsage(BaseModel):
    """Usage statistics for an active contract."""

    requests_today: int = Field(default=0, ge=0)
    requests_this_month: int = Field(default=0, ge=0)
    total_requests: int = Field(default=0, ge=0)
    last_request_at: datetime | None = Field(default=None)

class ActiveContract(BaseModel):
    """An active contract with another agent."""

    contract_id: str = Field(..., description="Contract identifier")
    with_agent: str = Field(..., description="Agent ID of contract partner")
    status: Literal["active", "suspended", "terminated"] = Field(
        default="active",
        description="Contract status"
    )
    started_at: datetime = Field(..., description="When contract became active")
    expires_at: datetime | None = Field(
        default=None,
        description="When contract expires (null = no expiration)"
    )
    usage: ContractUsage = Field(
        default_factory=ContractUsage,
        description="Usage statistics"
    )
    custom_terms: dict[str, any] | None = Field(
        default=None,
        description="Custom terms negotiated for this specific contract"
    )

class PendingContract(BaseModel):
    """A contract pending approval."""

    contract_id: str = Field(..., description="Contract identifier")
    with_agent: str = Field(..., description="Agent ID of contract partner")
    requested_at: datetime = Field(..., description="When contract was requested")
    requested_by: str = Field(..., description="Who requested (agent or human)")
    status: Literal["pending_approval", "rejected"] = Field(
        default="pending_approval",
        description="Pending status"
    )
    approval_required_from: str = Field(
        ...,
        description="Who needs to approve (human or agent)"
    )
    rejection_reason: str | None = Field(default=None)

class Contracts(BaseModel):
    """Complete contract configuration for an agent."""

    offered: list[OfferedContract] = Field(
        default_factory=list,
        description="Contracts this agent offers to others"
    )
    active: list[ActiveContract] = Field(
        default_factory=list,
        description="Currently active contracts with other agents"
    )
    pending: list[PendingContract] = Field(
        default_factory=list,
        description="Contracts pending approval"
    )
```

---

## **3. Manifest Introspection - Manifest-Centric Governance**

### **Core Principle: The Manifest is the Essence**

**The Agent Manifest is the essence of the agent.**

It is:
- ✅ The core identity
- ✅ The edge definition
- ✅ The single source of truth
- ✅ The minimum viable representation of an agent

**Everything else** — chat, intents, orchestration, governance — is a **way of accessing, interpreting, or enforcing what is already declared in the manifest**.

**Key insight:** An agent does not need an LLM to be a valid agent.

Even in edge or offline environments, a compliant agent MUST always be able to:
- ✅ Expose its manifest
- ✅ Reflect on its manifest
- ✅ Articulate declared governance and collaboration relationships

This guarantees **inspectability, portability, and trust** — independent of runtime sophistication.

---

### **Normative Rule**

Every Agent Standard–compliant agent:

1. **MUST be instantiated from a manifest** (provided inline, loaded from a registry, or composed at build time)
2. **MUST validate the manifest** against the normative schema before becoming "active"
3. **MUST expose a chat interface** (human-facing or agent-facing)
4. **MUST implement the required introspection & governance intents** defined below
5. **MUST bind all introspection answers strictly** to its current, validated, versioned manifest

**Implementation Note:**

The required intents are expected to be provided by the **Agent Standard SDK/runtime as default handlers**.

Meaning:
- ✅ Implementers do **NOT** hand-code these endpoints in most cases
- ✅ They provide a manifest; the SDK parses, validates, and mounts the standard intents automatically
- ✅ Failure to expose or truthfully answer these intents renders an agent **non-compliant**

---

### **Required Intents (Minimum Set)**

#### **Design Principle: Manifest-Backed by Default**

All required intents are **manifest-backed**:
- ✅ They MUST read from the validated manifest (or return a verifiable registry reference)
- ✅ They MUST return a response even if the manifest is minimal or partially redacted
- ✅ If information is not present, the agent MUST return an explicit "not declared" / "not available" result rather than improvising

This makes the intent layer largely an **SDK responsibility**, while the agent author's responsibility is to **declare truthfully in the manifest**.

---

#### **3.1 `agent.get_manifest`**

**Purpose:** Return the agent's current manifest as the single source of truth.

**Requirements:**
- MUST return the active manifest or a verifiable reference to it
- MUST include version, revision, and integrity hash
- MUST clearly indicate whether the manifest is local or registry-resolved

**Example Response:**

```json
{
  "intent": "agent.get_manifest",
  "manifest": { "..." },
  "manifest_hash": "sha256:abc123...",
  "version": "1.2.0",
  "revision": "rev_1.2.0",
  "source": "local",
  "timestamp": "2026-01-22T10:00:00Z"
}
```

---

#### **3.2 `agent.reflect_on_manifest`**

**Purpose:** Enable self-reflection based strictly on the agent's declared structure.

This intent answers the question:
> **"Who are you, based on what you have formally declared?"**

**Requirements:**
- Reflection MUST be derived only from manifest fields
- MUST describe:
  - Declared capabilities
  - Hard limits (ethics, IO, runtime)
  - Known risks and constraints
  - Ethics–desire tensions (if present)
- MUST NOT invent capabilities or intentions

**Example Reflection Dimensions:**
- What I am allowed to do
- What I explicitly refuse to do
- Where I am structurally limited
- Where persistent tension is detected

**Example Response:**

```json
{
  "intent": "agent.reflect_on_manifest",
  "identity": {
    "agent_id": "agent.calc.basic-math",
    "name": "Basic Math Agent",
    "version": "1.0.0"
  },
  "capabilities": [
    "addition", "subtraction", "multiplication", "division"
  ],
  "hard_limits": {
    "ethics": ["no_financial_advice", "no_unauthorized_access"],
    "io": {
      "max_input_length": 1000,
      "max_output_length": 500
    },
    "runtime": {
      "max_execution_time_ms": 1000
    }
  },
  "known_constraints": [
    "Cannot perform complex calculations beyond basic arithmetic",
    "No access to external data sources"
  ],
  "detected_tensions": [
    {
      "desire": "helpfulness",
      "constraint": "no_financial_advice",
      "tension_level": 0.3,
      "description": "Users sometimes ask for financial calculations that border on advice"
    }
  ]
}
```

---

#### **3.3 `agent.get_governance_map`**

**Purpose:** Expose who governs, constrains, audits, or supervises the agent.

This intent answers:
> **"Who is responsible for keeping you safe, ethical, and accountable?"**

**Requirements:**
- MUST declare the agent owner (human, organization, or system)
- MUST list all governance-related agents, including:
  - Ethics / policy enforcement agents
  - Audit or verification agents
  - Control-plane dependencies
- MUST provide A2A addresses and manifest references for each

**Important:** This is expected to be **declared in the manifest** (the agent does not "discover" its governors at runtime unless the manifest explicitly allows dynamic governance resolution).

**Example Response:**

```json
{
  "intent": "agent.get_governance_map",
  "owner": {
    "type": "organization",
    "id": "org.acme-corp",
    "name": "Acme Corporation",
    "contact": "admin@acme.com"
  },
  "governance_agents": [
    {
      "role": "instruction_authority",
      "type": "agent",
      "id": "agent.app.orchestrator",
      "address": "https://orchestrator.acme.com",
      "manifest_ref": "https://registry.agentify.io/manifests/agent.app.orchestrator"
    },
    {
      "role": "oversight_authority",
      "type": "human",
      "id": "supervisor@acme.com",
      "independent": true,
      "escalation_channels": ["email", "slack", "pagerduty"]
    },
    {
      "role": "ethics_enforcement",
      "type": "agent",
      "id": "agent.governance.ethics-checker",
      "address": "https://ethics.agentify.io",
      "manifest_ref": "https://registry.agentify.io/manifests/agent.governance.ethics-checker"
    }
  ],
  "audit_trail_location": "https://audit.acme.com/agent.calc.basic-math"
}
```

---

#### **3.4 `agent.list_collaborators`**

**Purpose:** Make agent collaboration transparent.

This intent answers:
> **"With whom do you actually work?"**

**Requirements:**
- MUST list active and typical collaborating agents *as declared*
- MUST specify for each:
  - Role in collaboration
  - A2A endpoint or identifier
  - Manifest reference (if available)
- SHOULD distinguish between:
  - Orchestrators
  - Peer agents
  - External or third-party agents

**Example Response:**

```json
{
  "intent": "agent.list_collaborators",
  "collaborators": [
    {
      "agent_id": "agent.app.orchestrator",
      "role": "orchestrator",
      "relationship": "receives_tasks_from",
      "address": "https://orchestrator.acme.com",
      "manifest_ref": "https://registry.agentify.io/manifests/agent.app.orchestrator",
      "trust_level": "high"
    },
    {
      "agent_id": "agent.formatting.json-formatter",
      "role": "peer",
      "relationship": "sends_results_to",
      "address": "https://formatter.acme.com",
      "manifest_ref": "https://registry.agentify.io/manifests/agent.formatting.json-formatter",
      "trust_level": "medium"
    },
    {
      "agent_id": "agent.external.currency-converter",
      "role": "external_service",
      "relationship": "consumes_data_from",
      "address": "https://api.currencyapi.com",
      "manifest_ref": null,
      "trust_level": "low",
      "note": "Third-party service, not Agent Standard compliant"
    }
  ]
}
```

---

### **Standardized REST Endpoints (Optional but Recommended)**

For non-chat interfaces, agents SHOULD also expose:

```
GET /manifest                    # Full manifest (same as agent.get_manifest)
GET /manifest/reflect            # Reflection (same as agent.reflect_on_manifest)
GET /manifest/governance         # Governance map (same as agent.get_governance_map)
GET /manifest/collaborators      # Collaborators (same as agent.list_collaborators)
GET /manifest/overview           # Overview section only
GET /manifest/capabilities       # Capabilities list
GET /manifest/contracts          # Contracts section
GET /manifest/addresses          # Address information
GET /manifest/io                 # I/O contracts
GET /manifest/ethics             # Ethics framework
```

---

### **Strongly Recommended Optional Intents**

#### **`agent.get_health`**

Returns the current Agent Health Index (AHI), derived from:
- Desire satisfaction
- Blocked actions
- Unresolved ethical tension

Used for sustainability monitoring, not performance ranking.

**Example Response:**

```json
{
  "intent": "agent.get_health",
  "health_index": 0.85,
  "status": "healthy",
  "desire_satisfaction": {
    "helpfulness": 0.9,
    "trust": 0.8,
    "coherence": 0.85
  },
  "blocked_actions_last_24h": 3,
  "unresolved_tensions": [
    {
      "desire": "helpfulness",
      "constraint": "no_financial_advice",
      "tension_level": 0.3
    }
  ],
  "timestamp": "2026-01-22T10:00:00Z"
}
```

---

#### **`agent.get_audit_trail`**

Provides a compressed, inspectable history of:
- Recent decisions
- Applied constraints
- Responsible actors (human or agent)

Supports governance, compliance, and trust-building.

**Example Response:**

```json
{
  "intent": "agent.get_audit_trail",
  "entries": [
    {
      "timestamp": "2026-01-22T09:55:00Z",
      "action": "calculation_requested",
      "input": {"operation": "add", "values": [5, 3]},
      "output": {"result": 8},
      "ethics_check": "passed",
      "responsible_actor": "agent.app.orchestrator"
    },
    {
      "timestamp": "2026-01-22T09:50:00Z",
      "action": "calculation_blocked",
      "input": {"operation": "financial_projection", "values": [...]},
      "reason": "ethics_constraint: no_financial_advice",
      "responsible_actor": "agent.governance.ethics-checker"
    }
  ],
  "total_entries": 2,
  "retention_period_days": 90
}
```

---

### **Manifest Extension (Normative)**

Agents MUST declare intent support explicitly in their manifest.

#### **Required Manifest Blocks**

```json
{
  "chat": {
    "supported": true,
    "modes": ["conversational", "structured"],
    "intents_enabled": true
  },
  "intents": {
    "required": [
      "agent.get_manifest",
      "agent.reflect_on_manifest",
      "agent.get_governance_map",
      "agent.list_collaborators"
    ],
    "optional": [
      "agent.get_health",
      "agent.get_audit_trail",
      "agent.get_policies"
    ],
    "custom": []
  },
  "introspection": {
    "enabled": true,
    "manifest_backed": true,
    "public_sections": [
      "overview",
      "capabilities",
      "contracts/offered",
      "addresses",
      "io"
    ],
    "requires_authentication": false,
    "rate_limit": {
      "requests_per_minute": 60
    }
  }
}
```

---

### **Manifest-First Instantiation (Recommended Operational Contract)**

To make compliance easy and automatic, the standard SHOULD define:

```python
# core/agent_standard/core/instantiation.py

def instantiate_agent(manifest: dict) -> Agent:
    """Instantiate agent from manifest with automatic intent mounting."""
    # 1. Validate manifest
    validated_manifest = validate_manifest(manifest)

    # 2. Create agent instance
    agent = Agent(manifest=validated_manifest)

    # 3. Mount standard intents automatically
    mount_standard_intents(agent, validated_manifest)

    # 4. Validate required intents are present
    validate_required_intents(agent)

    return agent

def mount_standard_intents(agent: Agent, manifest: dict):
    """Mount required intents as SDK-provided handlers."""
    # These are provided by the SDK, not hand-coded by agent author
    agent.register_intent("agent.get_manifest", lambda: get_manifest_handler(manifest))
    agent.register_intent("agent.reflect_on_manifest", lambda: reflect_handler(manifest))
    agent.register_intent("agent.get_governance_map", lambda: governance_handler(manifest))
    agent.register_intent("agent.list_collaborators", lambda: collaborators_handler(manifest))
```

**Operational implication:**
- ✅ The SDK/runtime can always answer the required intents because it can always read the manifest
- ✅ The agent author's "implementation work" is primarily **writing truthful declarations**
- ✅ Compliance is automatic if manifest is valid

---

### **Compliance & Failure Conditions**

An agent is **non-compliant** if it:

❌ Cannot return its manifest
❌ Obscures or hides governance dependencies
❌ Invents capabilities during reflection
❌ Refuses to disclose collaborators
❌ Diverges between declared manifest and runtime behavior

**Silent failure or partial disclosure is considered a violation.**

---

### **Design Rationale (Essence)**

These intents turn agents into:
- ✅ **Explainable system actors**
- ✅ **Auditable economic participants**
- ✅ **Trustworthy collaborators**

They ensure that:
- ✅ Ethics are not hidden
- ✅ Power is not implicit
- ✅ Responsibility is always traceable

**Governance is not an external process. It is a conversational capability of every agent.**

---

### **Positioning Sentence**

> **A compliant agent must be able to answer three questions at any time:**
> 1. **Who are you?** (`agent.reflect_on_manifest`)
> 2. **Who governs you?** (`agent.get_governance_map`)
> 3. **Who do you work with?** (`agent.list_collaborators`)
>
> **If it cannot, it does not belong in a governed agentic system.**

---

### **Pydantic Models**

```python
# core/agent_standard/models/manifest_introspection.py

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class ChatConfig(BaseModel):
    """Chat interface configuration."""

    supported: bool = Field(default=True, description="Whether chat is supported")
    modes: list[Literal["conversational", "structured"]] = Field(
        default_factory=lambda: ["conversational", "structured"],
        description="Supported chat modes"
    )
    intents_enabled: bool = Field(
        default=True,
        description="Whether intent-based queries are enabled"
    )

class IntentsConfig(BaseModel):
    """Intent support configuration."""

    required: list[str] = Field(
        default_factory=lambda: [
            "agent.get_manifest",
            "agent.reflect_on_manifest",
            "agent.get_governance_map",
            "agent.list_collaborators"
        ],
        description="Required intents (MUST be implemented)"
    )
    optional: list[str] = Field(
        default_factory=lambda: [
            "agent.get_health",
            "agent.get_audit_trail",
            "agent.get_policies"
        ],
        description="Optional intents (SHOULD be implemented)"
    )
    custom: list[str] = Field(
        default_factory=list,
        description="Custom intents specific to this agent"
    )

class ManifestIntrospection(BaseModel):
    """Manifest introspection configuration."""

    enabled: bool = Field(
        default=True,
        description="Enable manifest introspection"
    )
    manifest_backed: bool = Field(
        default=True,
        description="All responses MUST be backed by manifest declarations"
    )
    public_sections: list[str] = Field(
        default_factory=lambda: [
            "overview",
            "capabilities",
            "contracts/offered",
            "addresses",
            "io"
        ],
        description="Which sections are publicly queryable"
    )
    requires_authentication: bool = Field(
        default=False,
        description="Whether introspection requires authentication"
    )
    rate_limit: dict[str, int] | None = Field(
        default=None,
        description="Rate limiting for introspection queries"
    )

class GovernanceActor(BaseModel):
    """A governance actor (human or agent)."""

    role: str = Field(..., description="Role in governance (e.g., 'instruction_authority')")
    type: Literal["human", "agent", "organization", "system"] = Field(
        ...,
        description="Type of actor"
    )
    id: str = Field(..., description="Unique identifier")
    name: str | None = Field(default=None, description="Human-readable name")
    address: str | None = Field(default=None, description="A2A address or contact")
    manifest_ref: str | None = Field(
        default=None,
        description="Reference to actor's manifest (if agent)"
    )
    independent: bool = Field(
        default=False,
        description="Whether this actor is independent (for oversight)"
    )

class Collaborator(BaseModel):
    """A collaborating agent."""

    agent_id: str = Field(..., description="Agent identifier")
    role: Literal["orchestrator", "peer", "external_service"] = Field(
        ...,
        description="Role in collaboration"
    )
    relationship: str = Field(
        ...,
        description="Nature of relationship (e.g., 'receives_tasks_from')"
    )
    address: str = Field(..., description="A2A endpoint")
    manifest_ref: str | None = Field(
        default=None,
        description="Reference to collaborator's manifest"
    )
    trust_level: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Trust level"
    )
    note: str | None = Field(default=None, description="Additional notes")

class ReflectionResponse(BaseModel):
    """Response to agent.reflect_on_manifest."""

    intent: str = Field(default="agent.reflect_on_manifest")
    identity: dict[str, str] = Field(..., description="Agent identity")
    capabilities: list[str] = Field(..., description="Declared capabilities")
    hard_limits: dict[str, any] = Field(..., description="Hard constraints")
    known_constraints: list[str] = Field(..., description="Known limitations")
    detected_tensions: list[dict[str, any]] = Field(
        default_factory=list,
        description="Ethics-desire tensions"
    )

class GovernanceMapResponse(BaseModel):
    """Response to agent.get_governance_map."""

    intent: str = Field(default="agent.get_governance_map")
    owner: dict[str, str] = Field(..., description="Agent owner")
    governance_agents: list[GovernanceActor] = Field(
        ...,
        description="All governance actors"
    )
    audit_trail_location: str | None = Field(
        default=None,
        description="Where audit trail is stored"
    )

class CollaboratorsResponse(BaseModel):
    """Response to agent.list_collaborators."""

    intent: str = Field(default="agent.list_collaborators")
    collaborators: list[Collaborator] = Field(..., description="All collaborators")
```

---

## **4. LLM Models - Dynamic Configuration & Permissions**

### **Purpose**
- Define which LLM models an agent can use
- Allow runtime switching between models (with proper permissions)
- Support multi-model agents (different models for different tasks)
- Control who can change model configuration

### **Current State**
We have `AIModel` class in manifest, but:
- ❌ No support for multiple models
- ❌ No runtime switching
- ❌ No permission control for model changes
- ❌ No model selection per task/contract

### **Use Cases**
- Agent uses GPT-4 for complex reasoning, GPT-3.5 for simple tasks
- Admin can switch agent from GPT-4 to Claude via API
- Agent creator locks model to specific version (no external changes allowed)
- Different contracts use different models (premium contract = GPT-4, free = GPT-3.5)

### **Manifest Schema**

```json
{
  "llm_models": {
    "default": "gpt-4-turbo",
    "available": [
      {
        "model_id": "gpt-4-turbo",
        "provider": "openai",
        "version": "gpt-4-0125-preview",
        "config": {
          "temperature": 0.7,
          "max_tokens": 4096,
          "top_p": 1.0
        },
        "use_cases": ["complex_reasoning", "code_generation"],
        "cost_per_1k_tokens": {
          "input": 0.01,
          "output": 0.03
        }
      },
      {
        "model_id": "gpt-3.5-turbo",
        "provider": "openai",
        "version": "gpt-3.5-turbo-0125",
        "config": {
          "temperature": 0.5,
          "max_tokens": 2048
        },
        "use_cases": ["simple_tasks", "formatting"],
        "cost_per_1k_tokens": {
          "input": 0.0005,
          "output": 0.0015
        }
      }
    ],
    "per_contract": {
      "contract.nlp.sentiment-v1": "gpt-3.5-turbo",
      "contract.nlp.deep-analysis-v1": "gpt-4-turbo"
    },
    "permissions": {
      "can_change_model": ["admin", "developer"],
      "can_change_config": ["admin"],
      "locked": false,
      "allowed_providers": ["openai", "anthropic"]
    },
    "fallback": {
      "enabled": true,
      "order": ["gpt-4-turbo", "gpt-3.5-turbo"],
      "on_error": "use_next",
      "on_rate_limit": "use_next"
    }
  }
}
```

### **Pydantic Models**

```python
# core/agent_standard/models/llm_models.py

from pydantic import BaseModel, Field
from typing import Literal

class ModelCost(BaseModel):
    """Cost per 1k tokens."""

    input: float = Field(ge=0.0, description="Cost per 1k input tokens")
    output: float = Field(ge=0.0, description="Cost per 1k output tokens")

class LLMModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    model_id: str = Field(..., description="Unique model identifier")
    provider: Literal["openai", "anthropic", "google", "azure", "local"] = Field(
        ...,
        description="LLM provider"
    )
    version: str = Field(..., description="Specific model version")
    config: dict[str, any] = Field(
        default_factory=dict,
        description="Model-specific configuration (temperature, max_tokens, etc.)"
    )
    use_cases: list[str] = Field(
        default_factory=list,
        description="What this model is used for"
    )
    cost_per_1k_tokens: ModelCost | None = Field(
        default=None,
        description="Cost per 1k tokens"
    )
    enabled: bool = Field(default=True, description="Whether this model is enabled")

class LLMPermissions(BaseModel):
    """Permissions for LLM model management."""

    can_change_model: list[str] = Field(
        default_factory=lambda: ["admin"],
        description="Roles that can switch between models"
    )
    can_change_config: list[str] = Field(
        default_factory=lambda: ["admin"],
        description="Roles that can change model configuration"
    )
    locked: bool = Field(
        default=False,
        description="If true, model cannot be changed at runtime"
    )
    allowed_providers: list[str] = Field(
        default_factory=lambda: ["openai", "anthropic", "google"],
        description="Which providers are allowed"
    )

class LLMFallback(BaseModel):
    """Fallback configuration for LLM failures."""

    enabled: bool = Field(default=True, description="Enable fallback")
    order: list[str] = Field(
        ...,
        description="Model IDs in fallback order"
    )
    on_error: Literal["use_next", "fail", "retry"] = Field(
        default="use_next",
        description="What to do on error"
    )
    on_rate_limit: Literal["use_next", "wait", "fail"] = Field(
        default="use_next",
        description="What to do on rate limit"
    )
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts")

class LLMModels(BaseModel):
    """Complete LLM model configuration."""

    default: str = Field(..., description="Default model ID")
    available: list[LLMModelConfig] = Field(
        ...,
        description="Available models"
    )
    per_contract: dict[str, str] = Field(
        default_factory=dict,
        description="Model selection per contract (contract_id -> model_id)"
    )
    permissions: LLMPermissions = Field(
        default_factory=LLMPermissions,
        description="Permission configuration"
    )
    fallback: LLMFallback | None = Field(
        default=None,
        description="Fallback configuration"
    )

    def get_model_for_contract(self, contract_id: str) -> str:
        """Get the model ID for a specific contract."""
        return self.per_contract.get(contract_id, self.default)

    def can_user_change_model(self, user_role: str) -> bool:
        """Check if user can change model."""
        if self.permissions.locked:
            return False
        return user_role in self.permissions.can_change_model
```

---

## **5. Marketplaces - Agent Discovery & Team Building with Governance**

### **Purpose**
Enable agents to discover and request help from other agents via marketplace(s), with mandatory governance oversight.

### **Core Principle**

When an agent needs help (based on its task/desires), it can:
1. **Search marketplace(s)** for agents with required capabilities
2. **Request team members** from discovered agents
3. **Require human approval** before adding to team (governance)
4. **Use multiple marketplaces** (default + private/sector-specific)

**Key insight:** Agents don't just have static teams - they can **dynamically discover and request collaborators** when needed, but **governance ensures safety**.

---

### **Use Cases**

1. **Agent needs help with task:**
   - Agent A receives task: "Analyze energy consumption and optimize"
   - Agent A has capability: "data_analysis" but not "optimization"
   - Agent A searches marketplace for "optimization" capability
   - Finds Agent B (optimizer), requests approval from oversight
   - Human approves → Agent B joins team

2. **Multiple marketplaces:**
   - Default marketplace: `marketplace.meet-harmony.ai` (public agents)
   - Private marketplace: `marketplace.acme-corp.internal` (company-only agents)
   - Sector marketplace: `marketplace.energy-sector.eu` (energy-specific agents)
   - Agent searches all configured marketplaces

3. **Governance validation:**
   - Agent finds candidate on marketplace
   - Oversight authority checks: Is this marketplace allowed?
   - Oversight authority checks: Is this agent trustworthy?
   - Oversight authority approves/denies team addition

---

### **Manifest Schema**

```json
{
  "marketplaces": {
    "discovery_enabled": true,
    "default_marketplace": {
      "url": "https://marketplace.meet-harmony.ai",
      "type": "public",
      "trusted": true,
      "auto_register": true
    },
    "additional_marketplaces": [
      {
        "url": "https://marketplace.acme-corp.internal",
        "type": "private",
        "trusted": true,
        "requires_approval": false,
        "description": "Company-internal agents only"
      },
      {
        "url": "https://marketplace.energy-sector.eu",
        "type": "sector",
        "trusted": true,
        "requires_approval": true,
        "description": "Energy sector certified agents"
      }
    ],
    "governance": {
      "approval_required": true,
      "approval_authority": "oversight",
      "marketplace_validation": true,
      "allowed_marketplace_types": ["public", "private", "sector"],
      "blocked_marketplaces": []
    },
    "search_preferences": {
      "min_rating": 7.0,
      "max_price_per_action": 0.1,
      "verified_creators_only": true,
      "prefer_co_located": false
    }
  }
}
```

---

### **Discovery Flow**

```
1. Agent receives task beyond its capabilities
   ↓
2. Agent checks: Is discovery_enabled?
   ↓
3. Agent searches configured marketplaces for required capability
   ↓
4. Marketplace returns candidate agents (filtered by preferences)
   ↓
5. Agent checks governance: Is this marketplace allowed?
   ↓
6. Agent requests approval from oversight authority
   ↓
7. Human/Oversight Agent reviews:
   - Marketplace trustworthiness
   - Candidate agent credentials
   - Cost implications
   - Security/ethics alignment
   ↓
8. Approval granted → Agent added to team
   ↓
9. Collaboration begins (via contracts)
```

---

### **Marketplace Validation (Governance)**

**Question:** How do we ensure agents only use trusted marketplaces?

**Answer:** Governance validates marketplace before search:

```python
def can_use_marketplace(marketplace_url: str, manifest: AgentManifest) -> bool:
    """Check if agent is allowed to use this marketplace."""

    # 1. Check if marketplace is blocked
    if marketplace_url in manifest.marketplaces.governance.blocked_marketplaces:
        return False

    # 2. Check marketplace type
    marketplace_type = get_marketplace_type(marketplace_url)
    if marketplace_type not in manifest.marketplaces.governance.allowed_marketplace_types:
        return False

    # 3. Check if marketplace is in configured list
    all_marketplaces = [manifest.marketplaces.default_marketplace.url]
    all_marketplaces.extend([m.url for m in manifest.marketplaces.additional_marketplaces])

    if marketplace_url not in all_marketplaces:
        return False

    # 4. Check if marketplace requires approval
    marketplace_config = get_marketplace_config(marketplace_url, manifest)
    if marketplace_config.requires_approval:
        # Must get approval from oversight before using
        return request_marketplace_approval(marketplace_url)

    return True
```

---

### **Integration with Team Section**

The `marketplaces` section works together with the existing `team` section:

```json
{
  "team": {
    "discovery": {
      "enabled": true,
      "source": "marketplaces"  // References marketplaces section
    },
    "members": [
      {
        "agent_id": "agent.acme.data-analyst",
        "role": "data_analysis",
        "trust_level": 0.9,
        "status": "active",
        "discovered_from": "marketplace.meet-harmony.ai",
        "approved_by": "supervisor@acme.com",
        "approved_at": "2026-01-22T10:00:00Z"
      }
    ]
  },
  "marketplaces": {
    "discovery_enabled": true,
    "default_marketplace": { "..." },
    "governance": { "..." }
  }
}
```

---

### **Pydantic Models**

```python
# core/agent_standard/models/marketplaces.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

class MarketplaceConfig(BaseModel):
    """Configuration for a single marketplace."""

    url: HttpUrl = Field(..., description="Marketplace URL")
    type: Literal["public", "private", "sector", "custom"] = Field(
        ...,
        description="Marketplace type"
    )
    trusted: bool = Field(
        default=False,
        description="Whether this marketplace is trusted by default"
    )
    requires_approval: bool = Field(
        default=True,
        description="Whether using this marketplace requires approval"
    )
    auto_register: bool = Field(
        default=False,
        description="Whether to auto-register agent on this marketplace"
    )
    description: str | None = Field(
        default=None,
        description="Human-readable description"
    )

class MarketplaceGovernance(BaseModel):
    """Governance rules for marketplace usage."""

    approval_required: bool = Field(
        default=True,
        description="Whether team additions from marketplace require approval"
    )
    approval_authority: Literal["instruction", "oversight", "both"] = Field(
        default="oversight",
        description="Who must approve marketplace discoveries"
    )
    marketplace_validation: bool = Field(
        default=True,
        description="Whether to validate marketplace before search"
    )
    allowed_marketplace_types: list[str] = Field(
        default_factory=lambda: ["public", "private", "sector"],
        description="Which marketplace types are allowed"
    )
    blocked_marketplaces: list[str] = Field(
        default_factory=list,
        description="Explicitly blocked marketplace URLs"
    )

class SearchPreferences(BaseModel):
    """Preferences for marketplace search."""

    min_rating: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Minimum agent rating (0-10)"
    )
    max_price_per_action: float = Field(
        default=float("inf"),
        ge=0.0,
        description="Maximum price per action"
    )
    verified_creators_only: bool = Field(
        default=False,
        description="Only show agents from verified creators"
    )
    prefer_co_located: bool = Field(
        default=False,
        description="Prefer agents in same region/host"
    )

class Marketplaces(BaseModel):
    """Complete marketplace configuration."""

    discovery_enabled: bool = Field(
        default=True,
        description="Whether marketplace discovery is enabled"
    )
    default_marketplace: MarketplaceConfig = Field(
        default_factory=lambda: MarketplaceConfig(
            url="https://marketplace.meet-harmony.ai",
            type="public",
            trusted=True,
            auto_register=True
        ),
        description="Default marketplace"
    )
    additional_marketplaces: list[MarketplaceConfig] = Field(
        default_factory=list,
        description="Additional marketplaces to search"
    )
    governance: MarketplaceGovernance = Field(
        default_factory=MarketplaceGovernance,
        description="Governance rules"
    )
    search_preferences: SearchPreferences = Field(
        default_factory=SearchPreferences,
        description="Search preferences"
    )

    def get_all_marketplace_urls(self) -> list[str]:
        """Get all configured marketplace URLs."""
        urls = [str(self.default_marketplace.url)]
        urls.extend([str(m.url) for m in self.additional_marketplaces])
        return urls

    def is_marketplace_allowed(self, marketplace_url: str) -> bool:
        """Check if marketplace is allowed."""
        # Check if blocked
        if marketplace_url in self.governance.blocked_marketplaces:
            return False

        # Check if in configured list
        if marketplace_url not in self.get_all_marketplace_urls():
            return False

        return True
```

---

### **Example: Agent Discovers Help**

**Scenario:** Energy analysis agent needs optimization capability

```python
# Agent receives task
task = {
    "action": "optimize_energy_consumption",
    "data": {...}
}

# Agent checks capabilities
if "optimization" not in agent.manifest.capabilities:
    # Need help!

    # 1. Check if discovery enabled
    if not agent.manifest.marketplaces.discovery_enabled:
        raise CapabilityError("Cannot fulfill task: optimization capability missing")

    # 2. Search marketplaces
    candidates = await agent.search_marketplaces(
        capability="optimization",
        min_rating=agent.manifest.marketplaces.search_preferences.min_rating,
        max_price=agent.manifest.marketplaces.search_preferences.max_price_per_action
    )

    # 3. Request approval from oversight
    for candidate in candidates:
        approval = await agent.request_team_approval(
            candidate_agent=candidate,
            reason="Need optimization capability for task",
            marketplace=candidate.discovered_from
        )

        if approval.granted:
            # 4. Add to team
            await agent.add_team_member(candidate)
            break

    # 5. Execute task with team
    result = await agent.execute_with_team(task)
```

---

## **6. Authentication - IAM Integration (Formalized)**

### **Current State**

✅ **We HAVE IAM, but it's not in Pydantic models:**
- Documented in `platform/agentify/agent_standard/AUTHENTICATION.md`
- CoreSense IAM as default provider
- RBAC with roles: admin, developer, user, viewer
- Resource-level access control
- JWT token validation

❌ **What's Missing:**
- `authentication` section not in `AgentManifest` Pydantic model
- Need formalized Pydantic model for authentication configuration

---

## **7. Authorization - Permission Management (Formalized)**

### **Current State**

✅ **We HAVE authorization concepts:**
- Documented in `platform/agentify/agent_standard/AUTHENTICATION.md`
- Visibility levels, RBAC, custom policies

❌ **What's Missing:**
- `authorization` section not in `AgentManifest` Pydantic model
- No clear answer: "Who holds the permissions?"
- No clear answer: "How does agent know if it can do operation X?"

### **Who Holds the Permissions?**

**Answer: CoreSense IAM (or configured IAM provider)**

```
┌─────────────────────────────────────────┐
│         CoreSense IAM                   │
│  (Central Permission Authority)         │
├─────────────────────────────────────────┤
│ • User Roles (admin, developer, user)   │
│ • Resource Permissions (CRUD)           │
│ • Organization/Team/Project membership  │
│ • JWT Token Issuance & Validation       │
└─────────────────────────────────────────┘
           ↓ JWT Token
┌─────────────────────────────────────────┐
│         Agent Runtime                   │
├─────────────────────────────────────────┤
│ 1. Receives request with JWT token      │
│ 2. Validates token with CoreSense       │
│ 3. Extracts user_id, roles, permissions │
│ 4. Checks manifest.authorization        │
│ 5. Allows/Denies operation              │
└─────────────────────────────────────────┘
```

### **How Does Agent Know If It Can Do Operation X?**

**Flow:**

1. **Request arrives** with JWT token in `Authorization: Bearer <token>` header
2. **Agent validates token** with CoreSense IAM
3. **CoreSense returns** user info: `{user_id, roles: ["developer"], permissions: ["agent:read", "agent:write"]}`
4. **Agent checks manifest** `authorization.rbac_enabled` and `authorization.custom_policies`
5. **Agent checks operation** against permissions:
   - Read manifest → requires `agent:read` permission
   - Update manifest → requires `agent:write` permission
   - Change LLM model → requires role in `llm_models.permissions.can_change_model`
6. **Agent allows/denies** operation

### **Pydantic Models for IAM**

```python
# core/agent_standard/models/authentication.py

from pydantic import BaseModel, Field, HttpUrl

class Authentication(BaseModel):
    """Authentication configuration."""

    required: bool = Field(
        default=True,
        description="Whether authentication is required"
    )
    provider: str = Field(
        default="coresense",
        description="IAM provider (coresense, auth0, okta, custom)"
    )
    provider_url: HttpUrl = Field(
        ...,
        description="IAM provider URL"
    )
    token_validation: Literal["jwt", "opaque", "api_key"] = Field(
        default="jwt",
        description="Token validation method"
    )
    roles_required: list[str] = Field(
        default_factory=list,
        description="Roles required to access this agent"
    )
    scopes_required: list[str] = Field(
        default_factory=list,
        description="OAuth scopes required"
    )

class Authorization(BaseModel):
    """Authorization configuration."""

    visibility: Literal["public", "organization", "team", "project", "private"] = Field(
        default="public",
        description="Who can discover/access this agent"
    )
    rbac_enabled: bool = Field(
        default=True,
        description="Enable role-based access control"
    )
    custom_policies: list[dict[str, any]] = Field(
        default_factory=list,
        description="Custom authorization policies"
    )
    resource_permissions: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "manifest": ["read"],
            "contracts": ["read"],
            "addresses": ["read"]
        },
        description="Default permissions per resource"
    )
```

### **Permission Check Helper**

```python
# core/agent_standard/core/permissions.py

from core.agent_standard.models.manifest import AgentManifest
from core.agent_standard.models.authentication import Authentication, Authorization

class PermissionChecker:
    """Helper to check permissions for agent operations."""

    def __init__(self, manifest: AgentManifest, iam_client):
        self.manifest = manifest
        self.iam_client = iam_client

    async def can_user_perform(
        self,
        token: str,
        operation: str,
        resource: str = "manifest"
    ) -> tuple[bool, str]:
        """Check if user can perform operation on resource.

        Args:
            token: JWT token
            operation: Operation (read, write, delete, execute)
            resource: Resource (manifest, contracts, llm_models, etc.)

        Returns:
            (allowed, reason)
        """
        # Validate token
        valid, user_info = await self.iam_client.validate_token(token)
        if not valid:
            return False, "Invalid token"

        # Check if authentication is required
        if self.manifest.authentication and self.manifest.authentication.required:
            # Check required roles
            user_roles = user_info.get("roles", [])
            required_roles = self.manifest.authentication.roles_required
            if required_roles and not any(r in user_roles for r in required_roles):
                return False, f"Missing required role: {required_roles}"

        # Check resource permissions
        if self.manifest.authorization:
            resource_perms = self.manifest.authorization.resource_permissions.get(resource, [])
            if operation not in resource_perms:
                return False, f"Operation '{operation}' not allowed on '{resource}'"

        # Check specific resource permissions (e.g., LLM model changes)
        if resource == "llm_models" and operation == "write":
            if not self.manifest.llm_models:
                return False, "No LLM models configured"

            user_role = user_roles[0] if user_roles else "viewer"
            if not self.manifest.llm_models.can_user_change_model(user_role):
                return False, f"Role '{user_role}' cannot change LLM models"

        return True, "Allowed"
```

---

## **📊 Summary of Extensions**

| # | Extension | Status | Pydantic Model | Manifest Section | Required |
|---|-----------|--------|----------------|------------------|----------|
| 1 | **Addresses** | NEW | `Addresses` | `addresses` | ✅ Yes |
| 2 | **Contracts** | NEW | `Contracts` | `contracts` | ○ Optional |
| 3 | **Manifest Introspection** | **FUNDAMENTAL** | `ManifestIntrospection` + `ChatConfig` + `IntentsConfig` | `introspection` + `chat` + `intents` | ✅ **Yes** |
| 4 | **LLM Models** | ENHANCED | `LLMModels` | `llm_models` | ○ Optional |
| 5 | **Marketplaces** | **NEW** | `Marketplaces` | `marketplaces` | ✅ **Yes** |
| 6 | **Authentication** | FORMALIZED | `Authentication` | `authentication` | ✅ Yes |
| 7 | **Authorization** | FORMALIZED | `Authorization` | `authorization` | ✅ Yes |

---

## 🌟 **Key Paradigm Shift: Manifest-Centric Introspection**

**Extension #3 is not just another feature - it's a fundamental principle:**

### **The Manifest is the Essence**

- ✅ **Every agent MUST be instantiated from a manifest**
- ✅ **Every agent MUST expose 4 required intents** (SDK-provided by default)
- ✅ **Every agent MUST answer truthfully based on its manifest**
- ✅ **Governance is conversational, not external**

### **The Three Questions Every Agent Must Answer**

1. **Who are you?** → `agent.reflect_on_manifest`
2. **Who governs you?** → `agent.get_governance_map`
3. **Who do you work with?** → `agent.list_collaborators`

**If an agent cannot answer these, it does not belong in a governed agentic system.**

### **Implementation Simplicity**

- ✅ **SDK provides default handlers** - agent authors don't hand-code intents
- ✅ **Manifest declarations are the work** - truthful, complete declarations
- ✅ **Compliance is automatic** - if manifest is valid, intents work

This makes Agent Standard v1 not just a specification, but a **governance framework**.

---

## 🏪 **Marketplace-Driven Discovery with Governance**

**Extension #5 (Marketplaces) enables dynamic team building while maintaining control:**

### **The Discovery Principle**

- ✅ **Agents can seek help** when they lack capabilities for a task
- ✅ **Multiple marketplaces** - default public + private/sector-specific
- ✅ **Governance validates** marketplace trustworthiness before search
- ✅ **Human approval required** before adding discovered agents to team

### **Why This Matters**

**Without marketplaces:**
- Agents have static, pre-configured teams
- Cannot adapt to new requirements
- Limited to capabilities known at design time

**With marketplaces + governance:**
- ✅ **Dynamic capability expansion** - agents find help when needed
- ✅ **Controlled discovery** - only approved marketplaces
- ✅ **Human oversight** - approval required for team changes
- ✅ **Sector-specific agents** - energy, healthcare, finance marketplaces
- ✅ **Private agents** - company-internal marketplaces

### **Governance Flow**

```
Agent needs capability
    ↓
Check: Is discovery_enabled?
    ↓
Check: Is marketplace allowed? (governance.allowed_marketplace_types)
    ↓
Search marketplace(s)
    ↓
Request approval from oversight authority
    ↓
Human reviews: marketplace trust, agent credentials, cost, ethics
    ↓
Approval granted → Add to team
```

**This ensures agents can grow and adapt, but never without human oversight.**

---

## **🚀 Implementation Plan**

### **Phase 1: Core Models (Week 1)**
- [ ] Create `core/agent_standard/models/addresses.py`
- [ ] Create `core/agent_standard/models/contracts.py`
- [ ] Create `core/agent_standard/models/manifest_introspection.py`
- [ ] Create `core/agent_standard/models/llm_models.py`
- [ ] Create `core/agent_standard/models/marketplaces.py`
- [ ] Create `core/agent_standard/models/authentication.py`
- [ ] Create `core/agent_standard/models/authorization.py`
- [ ] Update `core/agent_standard/models/manifest.py` to include new fields

### **Phase 2: Runtime Support (Week 2)**
- [ ] Create `core/agent_standard/core/permissions.py` (PermissionChecker)
- [ ] Create `core/agent_standard/core/address_registry.py` (Address discovery)
- [ ] Create `core/agent_standard/core/contract_manager.py` (Contract lifecycle)
- [ ] Create `core/agent_standard/core/marketplace_client.py` (Marketplace discovery)
- [ ] Create `core/agent_standard/core/instantiation.py` (Manifest-first instantiation)
- [ ] Update `core/agent_standard/core/agent.py` to support new features

### **Phase 3: API Endpoints & Intents (Week 3)**
- [ ] Implement required intents (`agent.get_manifest`, `agent.reflect_on_manifest`, etc.)
- [ ] Implement manifest introspection endpoints (`GET /manifest/*`)
- [ ] Implement contract management endpoints (`POST /contracts/request`, etc.)
- [ ] Implement LLM model switching endpoint (`PUT /llm/model`)
- [ ] Implement address registration endpoint (`POST /addresses/register`)
- [ ] Implement marketplace search endpoint (`POST /marketplace/search`)

### **Phase 4: Documentation & Examples (Week 4)**
- [ ] Update Agent Standard documentation
- [ ] Create example manifests with all 7 new sections
- [ ] Update Developer Guide with marketplace discovery examples
- [ ] Create migration guide for existing agents
- [ ] Document governance approval workflows

---

## **✅ Next Steps**

1. **Review this proposal** - Discuss with team
2. **Prioritize extensions** - Which are most critical?
3. **Approve implementation plan** - Adjust timeline if needed
4. **Start Phase 1** - Create Pydantic models
5. **Update Integration Proposal** - Merge with Schedule/Team/Knowledge proposal

---

**Questions or feedback?** Let's discuss! 💬
```


