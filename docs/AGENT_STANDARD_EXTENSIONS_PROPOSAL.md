# 🔧 Agent Standard v1 - Extensions Proposal

**Date:** January 2026  
**Status:** PROPOSAL  
**Author:** Jonas Moßler

---

## 📋 **Overview**

This document proposes **4 critical extensions** to Agent Standard v1 to enable:
1. **Agent Discovery & Routing** via addresses
2. **Contract-Based Collaboration** beyond simple I/O
3. **Manifest Introspection** for agent-to-agent understanding
4. **Dynamic LLM Configuration** for flexible model management

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

## **3. Manifest Introspection - Agent-to-Agent Understanding**

### **Purpose**
Enable agents to query each other's manifests **without requiring an LLM**, while also supporting LLM-based chat queries.

### **Use Cases**
- Agent A wants to know: "What capabilities does Agent B have?"
- Agent A queries: `GET /manifest/capabilities` → structured JSON response
- Agent A with LLM asks: "Can you summarize meetings?" → Agent B responds via chat
- Marketplace queries all agents: `GET /manifest/overview` for discovery

### **Standardized Endpoints**

Every agent MUST expose these endpoints:

```
GET /manifest                    # Full manifest
GET /manifest/overview           # Overview section only
GET /manifest/capabilities       # Capabilities list
GET /manifest/contracts          # Contracts section
GET /manifest/contracts/offered  # Only offered contracts
GET /manifest/addresses          # Address information
GET /manifest/io                 # I/O contracts
GET /manifest/ethics             # Ethics framework
GET /manifest/pricing            # Pricing information
```

### **Alternative: Intent-Based Query (LLM)**

If agent has LLM capability, it can also respond to natural language:

```json
POST /manifest/query
{
  "query": "Can you help me analyze customer sentiment?",
  "format": "natural_language"
}

Response:
{
  "answer": "Yes, I can analyze customer sentiment. I offer a sentiment analysis contract that processes text and returns positive/negative/neutral scores with confidence levels.",
  "relevant_contracts": ["contract.nlp.sentiment-v1"],
  "relevant_capabilities": ["sentiment_analysis", "text_processing"]
}
```

### **Pydantic Models**

```python
# core/agent_standard/models/manifest_introspection.py

from pydantic import BaseModel, Field
from typing import Literal

class ManifestQuery(BaseModel):
    """A query for manifest information."""

    query: str = Field(..., description="Natural language query")
    format: Literal["natural_language", "structured"] = Field(
        default="structured",
        description="Response format"
    )
    sections: list[str] | None = Field(
        default=None,
        description="Specific manifest sections to query (null = all relevant)"
    )

class ManifestQueryResponse(BaseModel):
    """Response to a manifest query."""

    answer: str | None = Field(
        default=None,
        description="Natural language answer (if format=natural_language)"
    )
    data: dict[str, any] | None = Field(
        default=None,
        description="Structured data (if format=structured)"
    )
    relevant_contracts: list[str] = Field(
        default_factory=list,
        description="Contract IDs relevant to the query"
    )
    relevant_capabilities: list[str] = Field(
        default_factory=list,
        description="Capability names relevant to the query"
    )

class ManifestIntrospection(BaseModel):
    """Manifest introspection configuration."""

    enabled: bool = Field(
        default=True,
        description="Enable manifest introspection endpoints"
    )
    public_sections: list[str] = Field(
        default_factory=lambda: ["overview", "capabilities", "contracts/offered", "addresses", "io"],
        description="Which sections are publicly queryable"
    )
    requires_authentication: bool = Field(
        default=False,
        description="Whether introspection requires authentication"
    )
    llm_query_enabled: bool = Field(
        default=False,
        description="Whether natural language queries are supported"
    )
    rate_limit: dict[str, int] | None = Field(
        default=None,
        description="Rate limiting for introspection queries"
    )
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

## **5. IAM / Permission Management - Clarification**

### **Current State**

✅ **We HAVE IAM, but it's not in Pydantic models:**
- Documented in `platform/agentify/agent_standard/AUTHENTICATION.md`
- CoreSense IAM as default provider
- RBAC with roles: admin, developer, user, viewer
- Resource-level access control
- JWT token validation

❌ **What's Missing:**
- `authentication` and `authorization` sections not in `AgentManifest` Pydantic model
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
| 3 | **Manifest Introspection** | NEW | `ManifestIntrospection` | `introspection` | ○ Optional |
| 4 | **LLM Models** | ENHANCED | `LLMModels` | `llm_models` | ○ Optional |
| 5 | **Authentication** | FORMALIZED | `Authentication` | `authentication` | ✅ Yes |
| 6 | **Authorization** | FORMALIZED | `Authorization` | `authorization` | ✅ Yes |

---

## **🚀 Implementation Plan**

### **Phase 1: Core Models (Week 1)**
- [ ] Create `core/agent_standard/models/addresses.py`
- [ ] Create `core/agent_standard/models/contracts.py`
- [ ] Create `core/agent_standard/models/manifest_introspection.py`
- [ ] Create `core/agent_standard/models/llm_models.py`
- [ ] Create `core/agent_standard/models/authentication.py`
- [ ] Update `core/agent_standard/models/manifest.py` to include new fields

### **Phase 2: Runtime Support (Week 2)**
- [ ] Create `core/agent_standard/core/permissions.py` (PermissionChecker)
- [ ] Create `core/agent_standard/core/address_registry.py` (Address discovery)
- [ ] Create `core/agent_standard/core/contract_manager.py` (Contract lifecycle)
- [ ] Update `core/agent_standard/core/agent.py` to support new features

### **Phase 3: API Endpoints (Week 3)**
- [ ] Implement manifest introspection endpoints (`GET /manifest/*`)
- [ ] Implement contract management endpoints (`POST /contracts/request`, etc.)
- [ ] Implement LLM model switching endpoint (`PUT /llm/model`)
- [ ] Implement address registration endpoint (`POST /addresses/register`)

### **Phase 4: Documentation & Examples (Week 4)**
- [ ] Update Agent Standard documentation
- [ ] Create example manifests with all new sections
- [ ] Update Developer Guide
- [ ] Create migration guide for existing agents

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


