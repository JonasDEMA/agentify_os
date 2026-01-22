# 🚀 Agentify Developer Guide

**The Complete Guide to Building Agents & Apps on Agentify**

> 🎯 **This is THE starting point for all developers building on Agentify.**
>
> Whether you're using Lovable, n8n, Make.com, Python, JavaScript, or any other tool - start here!

> 📊 **For Business/Research Overview:** See [Capabilities Overview](../../docs/AGENTIFY_CAPABILITIES_OVERVIEW.md) and [Executive Summary](../../docs/AGENTIFY_EXECUTIVE_SUMMARY.md)

---

## 📋 **Table of Contents**

1. [Platform Architecture](#-platform-architecture)
2. [Understanding the Two Layers](#-understanding-the-two-layers)
3. [Quick Start - Create Your First Agent](#-quick-start---create-your-first-agent)
4. [The Agent Standard v1](#-agent-standard-v1)
5. [Runtime Libraries](#️-runtime-libraries)
6. [Templates & Examples](#-templates--examples)
7. [AI Prompt for Development](#-ai-prompt-for-development)
8. [Deployment & Registration](#-deployment--registration)

---

## 🏗️ **Platform Architecture**

**How Apps, Orchestrators, Marketplaces, and Hosting work together**

The Agentify Platform follows a **modular, marketplace-driven architecture**:

```
🎯 App Layer (Blue)
    ↓
🏪 Marketplace Layer (Orange) - 3 Marketplaces in parallel
    ↓
🚀 Hosting Layer (Green) - Container Management
    ↓
⚙️ Runtime Environment (Purple) - 3 Containers with Agents
    ↓
🔄 Direct Communication + Dynamic Expansion
```

**📖 Full Architecture Documentation:** [PLATFORM_ARCHITECTURE.md](PLATFORM_ARCHITECTURE.md)

**Key Concepts:**
- **Apps contain Orchestrator Agents** that coordinate workflows
- **Marketplaces provide agent teams** with billing and licensing
- **Hosting Agents deploy containers** (Railway, AWS, GCP, etc.)
- **Agents communicate directly** peer-to-peer within containers
- **Dynamic capability expansion** - agents request new capabilities on-demand

---

## 🧠 **Understanding the Meta-Standard Architecture**

Agentify is a **meta-standard** - it does NOT prescribe how you build your agents. Instead, it provides a universal description layer that makes agents from different frameworks interoperable.

**Think of it as "USB for AI Agents":**
- Different devices (keyboard, mouse, camera) use different internal technologies
- But they all plug into the same USB port
- Similarly: Different agents (Python, n8n, Make.com, Lovable) use different implementations
- But they all use the same JSON manifest to describe themselves

---

### **Layer 1: JSON Manifest (Description Layer)** 📝

**What it is:**
- A JSON file that **describes** your agent (not HOW it's built, but WHAT it does)
- The **single source of truth** for agent capabilities
- **Implementation-agnostic** - works with ANY framework

**Key Principle: Separation of Description and Implementation**
- **Description (JSON)**: What the agent does, its ethics, tools, I/O contracts
- **Implementation (Your Choice)**: Python, JavaScript, n8n, Make.com, Lovable, custom code

**What it contains:**
- Agent identity, capabilities, ethics, tools, etc.
- All 14 core sections of Agent Standard v1
- NO implementation details - just the "contract"

**Who creates it:**
- You (manually)
- Lovable (AI-powered app builder)
- n8n (workflow automation)
- Make.com (integration platform)
- Any tool that can generate JSON

**Example:**
```json
{
  "agent_id": "agent.mycompany.myagent",
  "name": "My Agent",
  "version": "1.0.0",
  "status": "active",
  "ethics": { ... },
  "tools": [ ... ],
  "io": { ... }
}
```

**This manifest works with:**
- ✅ Python implementation
- ✅ JavaScript implementation
- ✅ n8n workflow
- ✅ Make.com scenario
- ✅ Lovable app
- ✅ Your custom framework

---

### **Layer 2: Runtime Library (Execution Layer)** ⚙️

**What it is:**
- **Optional** libraries that help you implement agents
- Reads the JSON manifest
- Implements ethics engine, oversight, health monitoring, etc.

**Important: You don't HAVE to use our runtime libraries!**
- Build your agent however you want (Python, JS, n8n, Make.com, etc.)
- Just provide a JSON manifest that describes it
- The manifest makes it interoperable with other agents

**What the runtime libraries do (if you use them):**
- Loads the JSON manifest
- Validates ethics before actions
- Monitors agent health
- Enforces Four-Eyes Principle
- Executes tools and workflows

**Who uses it:**
- Your Python/JavaScript code
- Agentify platform (automatically)
- Desktop agents (via Agentify Desktop)

**Example:**
```python
from core.agent_standard.core.agent import Agent

# Load agent from JSON manifest
agent = Agent.from_json_file("my_agent.json")

# Execute with runtime ethics & oversight
result = agent.execute("Analyze this data")
```

---

## 🎯 **The Key Insight**

```
┌─────────────────────────────────────────────────────────┐
│                    JSON Manifest                         │
│              (WHAT the agent is and does)                │
│                                                          │
│  Created by: Lovable, n8n, Make.com, you, etc.         │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ Loaded by
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Runtime Library                         │
│              (HOW the agent executes)                    │
│                                                          │
│  - Ethics Engine                                        │
│  - Desire Monitor                                       │
│  - Oversight Controller                                 │
│  - Tool Executor                                        │
└─────────────────────────────────────────────────────────┘
```

**You create the JSON. The runtime library executes it.**

---

## 🚀 **Quick Start - Create Your First Agent**

### **Step 1: Choose Your Approach**

#### **Option A: Pure JSON (No Code)** ⚡

Perfect for: Lovable, n8n, Make.com, quick prototyping

```bash
# Copy minimal template
cp core/agent_standard/templates/minimal_agent_template.json my_agent.json

# Edit placeholders
# Replace <YOUR_COMPANY>, <YOUR_AGENT_NAME>, etc.

# Validate
python -m core.agent_standard.validation.manifest_validator my_agent.json

# Done! Upload to Agentify marketplace
```

**📖 See:** [Minimal Template](../../core/agent_standard/templates/minimal_agent_template.json)

---

#### **Option B: Python Code** 🐍

Perfect for: Custom agents, complex logic, full control

```python
from core.agent_standard.models.manifest import AgentManifest
from core.agent_standard.models.ethics import EthicsFramework, EthicsPrinciple
from core.agent_standard.models.authority import Authority, AuthorityEntity

# Create manifest programmatically
manifest = AgentManifest(
    agent_id="agent.mycompany.myagent",
    name="My Agent",
    version="1.0.0",
    status="active",
    
    ethics=EthicsFramework(
        framework="harm-minimization",
        principles=[
            EthicsPrinciple(
                id="no-harm",
                text="Do not cause harm",
                severity="critical",
                enforcement="hard"
            )
        ],
        hard_constraints=["no_illegal_guidance"]
    ),
    
    authority=Authority(
        instruction=AuthorityEntity(type="human", id="user@example.com"),
        oversight=AuthorityEntity(type="human", id="supervisor@example.com", independent=True)
    ),
    
    io={"input_formats": ["text"], "output_formats": ["text"]}
)

# Save to JSON
manifest.to_json_file("my_agent.json")
```

**📖 See:** [Quick Start Guide](../../core/agent_standard/QUICKSTART_COMPLETE.md)

---

#### **Option C: Using Runtime Library** ⚙️

Perfect for: Running agents, implementing custom behavior

```python
from core.agent_standard.core.agent import Agent

# Load agent from JSON
agent = Agent.from_json_file("my_agent.json")

# Execute with full runtime support
# - Ethics are checked automatically
# - Health is monitored
# - Oversight is enforced
result = agent.execute(
    input_data="Analyze this sales data",
    context={"user_id": "user123"}
)

print(result)
```

**📖 See:** [Runtime Documentation](../../core/agent_standard/README.md)

---

## 📚 **Agent Standard v1**

Every agent MUST follow the Agent Standard v1, which defines **14 core areas**:

| # | Section | Required | Description |
|---|---------|----------|-------------|
| 1 | Overview | ✅ | Agent identity & capabilities |
| 2 | Ethics & Desires | ✅ | Ethics framework & health monitoring |
| 3 | Pricing | ⚠️ Optional | Pricing model & revenue share |
| 4 | Tools | ⚠️ Optional | Available tools & connections |
| 5 | Memory | ⚠️ Optional | State persistence |
| 6 | Schedule | ⚠️ Optional | Automated execution |
| 7 | Activities | ⚠️ Optional | Execution queue |
| 8 | Prompt / Guardrails | ⚠️ Optional | LLM config & safety |
| 9 | Team | ⚠️ Optional | Multi-agent collaboration |
| 10 | Customers | ⚠️ Optional | Customer assignments |
| 11 | Knowledge | ⚠️ Optional | RAG & data access |
| 12 | IO | ✅ | Input/output formats |
| 13 | Revisions | ✅ | Version control |
| 14 | Authority & Oversight | ✅ | Four-Eyes Principle |

**📖 Complete Reference:** [Agent Anatomy](agent_standard/AGENT_ANATOMY.md)

---

## ⚙️ **Runtime Libraries**

### **Python Library**

**Installation:**

```bash
# Option 1: Install from source (current method)
git clone https://github.com/JonasDEMA/agentify_os.git
cd agentify_os
pip install -e .

# Option 2: Install from GitHub
pip install git+https://github.com/JonasDEMA/agentify_os.git

# Option 3: Install from PyPI (coming soon)
# pip install agentify-sdk
```

**📖 See:** [INSTALLATION.md](../../INSTALLATION.md) for detailed installation instructions

**Usage:**
```python
from core.agent_standard.core.agent import Agent

# Load agent
agent = Agent.from_json_file("my_agent.json")

# Execute
result = agent.execute("Do something")
```

**Features:**
- ✅ Ethics Engine (runtime-active)
- ✅ Desire Monitor (health tracking)
- ✅ Oversight Controller (Four-Eyes Principle)
- ✅ Tool Executor
- ✅ Memory Management
- ✅ Schedule Execution

**📖 Documentation:** [core/agent_standard/](../../core/agent_standard/)

---

### **JavaScript Library** (Coming Soon)

```javascript
import { Agent } from '@agentify/sdk';

// Load agent
const agent = await Agent.fromJsonFile('my_agent.json');

// Execute
const result = await agent.execute('Do something');
```

---

## 📝 **Templates & Examples**

### **Templates**

| Template | Use Case | Link |
|----------|----------|------|
| **Minimal** | Quick start, prototyping | [minimal_agent_template.json](../../core/agent_standard/templates/minimal_agent_template.json) |
| **Complete** | Full features, production | [agent_manifest_template.json](../../core/agent_standard/templates/agent_manifest_template.json) |

**📖 Template Guide:** [templates/README.md](../../core/agent_standard/templates/README.md)

---

### **Examples**

| Example | Description | Link |
|---------|-------------|------|
| **Complete Agent** | All 14 sections | [complete_agent_example.json](../../core/agent_standard/examples/complete_agent_example.json) |
| **Meeting Assistant** | Real-world example | [meeting_assistant.json](../../core/agent_standard/examples/meeting_assistant.json) |
| **Desktop Automation** | Desktop agent | [desktop_automation_agent.json](../../core/agent_standard/examples/desktop_automation_agent.json) |

---

## 🤖 **AI Prompt for Development**

Use this prompt with your AI assistant (Claude, GPT-4, etc.) to build agents:

```
I want to create an agent for Agentify platform.

Context:
- Agentify uses Agent Standard v1 with 14 core sections
- Agents are described via JSON manifest (single source of truth)
- Runtime library executes the JSON with ethics, oversight, health monitoring

Requirements:
1. Create a JSON manifest following Agent Standard v1
2. Include all required sections: overview, ethics, desires, authority, io, revisions
3. Follow Four-Eyes Principle (instruction ≠ oversight)
4. Use templates from: core/agent_standard/templates/

My agent should:
[DESCRIBE YOUR AGENT HERE]

Please:
1. Use minimal_agent_template.json as starting point
2. Fill in all placeholders
3. Validate against Agent Standard v1
4. Provide the complete JSON manifest

References:
- Quick Start: core/agent_standard/QUICKSTART_COMPLETE.md
- Agent Anatomy: platform/agentify/agent_standard/AGENT_ANATOMY.md
- Templates: core/agent_standard/templates/
- Examples: core/agent_standard/examples/
```

**📖 More Details:** [QUICKSTART_COMPLETE.md](../../core/agent_standard/QUICKSTART_COMPLETE.md)

---

## 🚀 **Deployment & Registration**

### **Step 1: Validate Your Agent**

```python
from core.agent_standard.validation.manifest_validator import ManifestValidator

validator = ManifestValidator()
result = validator.validate_file("my_agent.json")

if result.is_valid:
    print("✅ Valid!")
else:
    for error in result.errors:
        print(f"❌ {error}")
```

### **Step 2: Register in Marketplace**

```python
from platform.agentify.register_agents import register_agent

# Register agent
register_agent("my_agent.json")
```

### **Step 3: Deploy**

```bash
# Deploy to Agentify Cloud
agentify deploy my_agent.json

# Or run locally
python -m core.agent_standard.core.runtime my_agent.json
```

**📖 Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md) (Coming Soon)

---

## 📖 **Complete Documentation Structure**

```
Agentify Documentation
│
├── 🚀 DEVELOPER_GUIDE.md ← YOU ARE HERE (Start here!)
│
├── Agent Standard v1
│   ├── QUICKSTART_COMPLETE.md ← Quick start guide
│   ├── AGENT_ANATOMY.md ← Reference for all 14 sections
│   ├── IMPLEMENTATION_STATUS.md ← Current progress
│   └── README.md ← Full specification
│
├── Templates
│   ├── minimal_agent_template.json ← Quick start
│   ├── agent_manifest_template.json ← Complete
│   └── README.md ← Template guide
│
├── Examples
│   ├── complete_agent_example.json ← All 14 sections
│   ├── meeting_assistant.json ← Real-world
│   └── desktop_automation_agent.json ← Desktop
│
└── Runtime
    ├── core/agent_standard/ ← Python implementation
    └── SDK documentation ← API reference
```

---

## 🎯 **Summary**

**To build an agent on Agentify:**

1. **Create JSON manifest** (describes WHAT)
   - Use templates: `minimal_agent_template.json` or `agent_manifest_template.json`
   - Follow Agent Standard v1 (14 sections)
   - Validate with `ManifestValidator`

2. **Use runtime library** (executes HOW)
   - Python: `from agentify import Agent`
   - Load JSON: `Agent.from_json_file("my_agent.json")`
   - Execute: `agent.execute("Do something")`

3. **Deploy**
   - Register in marketplace
   - Deploy to cloud or run locally

**The JSON is the agent. The runtime executes it.**

---

## 🆘 **Need Help?**

- **Quick Start:** [QUICKSTART_COMPLETE.md](../../core/agent_standard/QUICKSTART_COMPLETE.md)
- **Templates:** [templates/](../../core/agent_standard/templates/)
- **Examples:** [examples/](../../core/agent_standard/examples/)
- **Full Spec:** [Agent Standard v1](agent_standard/README.md)

---

**Ready to build? Start with the [Quick Start Guide](../../core/agent_standard/QUICKSTART_COMPLETE.md)!** 🚀

