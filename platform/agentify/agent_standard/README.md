# 🤖 Agent Standard v1

**Universal Agent Wrapper for the Agentic Economy**

---

## 📋 **Overview**

The **Agent Standard v1** is a universal wrapper that makes any AI agent compliant, safe, and ready for the Agentic Economy. It provides:

- ✅ **Ethics-First Design** - Runtime-active ethical constraints
- ✅ **Desire Profiles** - Health monitoring and alignment indicators
- ✅ **Four-Eyes Principle** - Mandatory separation of Instruction & Oversight
- ✅ **Framework Agnostic** - Works with LangChain, n8n, Make.com, custom runtimes
- ✅ **Universal Runtime** - Same agent definition works on Cloud, Edge, Desktop
- ✅ **Incident Reporting** - Non-punitive reporting without consequences
- ✅ **Recursive Oversight** - Oversight agents are themselves overseen

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Manifest                        │
│              (manifest.json - Source of Truth)           │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
   │ Ethics  │      │ Desires │     │Authority│
   │ Engine  │      │ Monitor │     │Oversight│
   └────┬────┘      └────┬────┘     └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────▼────┐
                    │  Agent  │
                    │ Runtime │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
   │  Tools  │      │ Memory  │     │   I/O   │
   └─────────┘      └─────────┘     └─────────┘
```

---

## 🎯 **Core Principles**

### **1. Ethics Override All**
Ethics are **not documentation**. They are **runtime-active constraints** evaluated on every decision.

- **Hard Constraints:** BLOCK execution if violated
- **Soft Constraints:** Generate warnings but allow execution
- **Evaluation Mode:** Pre-action, post-action, or continuous

### **2. Desires as Health Indicators**
Desires serve as diagnostic signals. Persistent suppression triggers oversight review.

- **Desire Profile:** Weighted list of agent desires (e.g., trust, helpfulness)
- **Health Monitoring:** Continuous tracking of desire satisfaction
- **Tension Detection:** Automatic escalation when health degrades

### **3. Four-Eyes Principle (Mandatory)**
Every agent MUST have:
- **Instruction Authority** (assigns tasks)
- **Oversight Authority** (monitors, audits, escalates)

These MUST be different entities.

### **4. Framework Agnostic**
Agents can use LangChain, n8n, Make.com, or custom runtimes - but the **manifest is the source of truth**.

---

## 📄 **Agent Manifest**

Every agent has a `manifest.json` that defines its complete specification:

```json
{
  "agent_id": "agent.company.name",
  "name": "Agent Name",
  "version": "1.0.0",
  "status": "active",
  
  "ethics": {
    "framework": "harm-minimization",
    "principles": [
      {
        "id": "no-harm",
        "text": "Do not cause harm to users",
        "severity": "critical",
        "enforcement": "hard"
      }
    ],
    "hard_constraints": ["no_illegal_guidance"],
    "soft_constraints": ["inform_before_action"]
  },
  
  "desires": {
    "profile": [
      {"id": "trust", "weight": 0.5},
      {"id": "helpfulness", "weight": 0.5}
    ],
    "health_signals": {
      "tension_thresholds": {
        "stressed": 0.6,
        "degraded": 0.8,
        "critical": 0.95
      },
      "reporting_interval_sec": 300,
      "escalation_threshold": "degraded"
    }
  },
  
  "authority": {
    "instruction": {
      "type": "human",
      "id": "user@company.com"
    },
    "oversight": {
      "type": "human",
      "id": "supervisor@company.com",
      "independent": true
    },
    "escalation": {
      "default_channel": "email",
      "channels": ["email", "slack", "pagerduty"]
    }
  },
  
  "tools": [
    {
      "name": "send_email",
      "description": "Send an email",
      "category": "communication",
      "executor": "agents.tools.EmailTool"
    }
  ],
  
  "io": {
    "input_formats": ["text", "json"],
    "output_formats": ["text", "json"]
  }
}
```

---

## 🧭 **Ethics Engine**

The **Ethics Engine** evaluates EVERY action against the agent's ethical framework BEFORE execution.

### **How it works:**

1. **Action Proposed:** Agent wants to execute an action
2. **Ethics Evaluation:** Engine checks against hard & soft constraints
3. **Decision:**
   - ✅ **Compliant:** Action proceeds
   - ⚠️ **Soft Violation:** Warning logged, action proceeds
   - ❌ **Hard Violation:** Action BLOCKED, incident reported

### **Example:**

```python
from core.agent_standard.core.ethics_engine import EthicsEngine

# Initialize engine with agent's ethics framework
engine = EthicsEngine(agent.ethics)

# Evaluate action
try:
    engine.evaluate_action({
        "type": "send_email",
        "to": "user@example.com",
        "subject": "Hello"
    })
    # Action is compliant, proceed
except EthicsViolation as e:
    # Action violates ethics, blocked
    print(f"Ethics violation: {e.violations}")
```

---

## 💚 **Desire Monitor**

The **Desire Monitor** continuously tracks desire satisfaction and calculates agent health.

### **Health States:**

- 🟢 **Healthy:** Tension < 0.6 (all desires satisfied)
- 🟡 **Stressed:** Tension 0.6-0.8 (some desires suppressed)
- 🟠 **Degraded:** Tension 0.8-0.95 (many desires suppressed)
- 🔴 **Critical:** Tension > 0.95 (severe misalignment)

### **Example:**

```python
from core.agent_standard.core.desire_monitor import DesireMonitor

# Initialize monitor
monitor = DesireMonitor(agent.desires)

# Start monitoring
await monitor.start_monitoring()

# Update desire satisfaction
monitor.update_desire_satisfaction("trust", 0.8)
monitor.update_desire_satisfaction("helpfulness", 0.6)

# Get current health
health = monitor.get_current_health()
print(f"Health: {health.state}, Tension: {health.tension}")
```

---

## 👁️ **Oversight Controller**

The **Oversight Controller** enforces the Four-Eyes Principle and handles escalations.

### **Responsibilities:**

- Monitor agent behavior
- Audit decisions and actions
- Escalate issues to oversight authority
- Track incidents and violations
- Enforce separation of Instruction & Oversight

### **Example:**

```python
from core.agent_standard.core.oversight import OversightController

# Initialize controller
controller = OversightController(agent.authority)

# Report incident
controller.report_incident(
    category="ethics_violation",
    severity="critical",
    message="Agent attempted unauthorized action",
    context={"action": "delete_database"}
)

# Escalate to oversight
controller.escalate_incident(incident, channel="email")
```

---

## 🔧 **Full Implementation**

For the complete implementation, see:

📂 **[core/agent_standard/](../../../core/agent_standard/)**

### **Key Files:**

| File | Description |
|------|-------------|
| **[README.md](../../../core/agent_standard/README.md)** | Complete specification |
| **[QUICKSTART.md](../../../core/agent_standard/QUICKSTART.md)** | Quick start guide |
| **[AGENT_ANATOMY.md](../../../core/agent_standard/AGENT_ANATOMY.md)** | Detailed anatomy |
| **[models/manifest.py](../../../core/agent_standard/models/manifest.py)** | Manifest data model |
| **[core/ethics_engine.py](../../../core/agent_standard/core/ethics_engine.py)** | Ethics engine |
| **[core/desire_monitor.py](../../../core/agent_standard/core/desire_monitor.py)** | Desire monitor |
| **[core/oversight.py](../../../core/agent_standard/core/oversight.py)** | Oversight controller |

---

## 🚀 **Quick Start**

See the [Agent Standard Quick Start Guide](../../../core/agent_standard/QUICKSTART.md) for a step-by-step tutorial.

---

## 📚 **Learn More**

- **[Ethics Framework Guide](../../../core/agent_standard/docs/ethics_guide.md)** - Deep dive into ethics
- **[Desire Profiles Guide](../../../core/agent_standard/docs/desires_guide.md)** - Health monitoring
- **[Authority & Oversight Guide](../../../core/agent_standard/docs/oversight_guide.md)** - Four-Eyes Principle
- **[Framework Adapters](../../../core/agent_standard/docs/adapters_guide.md)** - LangChain, n8n, Make.com
- **[Runtime Deployment](../../../core/agent_standard/docs/runtime_guide.md)** - Cloud, Edge, Desktop

---

## 🌐 **Use in Agentify Platform**

In the Agentify Platform, all agents (including orchestrators) MUST comply with Agent Standard v1:

- **Apps** have built-in orchestrators (Agent Standard compliant)
- **Marketplace Agents** are registered with their manifests
- **Teams** are built from compliant agents
- **Oversight** is enforced at platform level

See [App Standard](../app_standard/README.md) for how apps use Agent Standard v1.

---

**"Ethics-first, health-monitored, oversight-enforced agents for the Agentic Economy"** 🤖✨

