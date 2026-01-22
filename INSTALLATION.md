# 📦 Agentify SDK - Installation Guide

**How to install and use the Agentify SDK**

---

## 🚀 **Quick Install**

### **Option 1: Install from PyPI** (Coming Soon)

```bash
pip install agentify-sdk
```

**Status:** ⚠️ Package will be published to PyPI soon

---

### **Option 2: Install from Source** (Current Method)

```bash
# Clone repository
git clone https://github.com/JonasDEMA/agentify_os.git
cd agentify_os

# Install in development mode
pip install -e .

# Or install with extras
pip install -e ".[dev,langchain,openai,anthropic]"
```

---

### **Option 3: Install from GitHub**

```bash
pip install git+https://github.com/JonasDEMA/agentify_os.git
```

---

## 📚 **Usage**

### **Import the SDK**

```python
# Import core components
from core.agent_standard.models.manifest import AgentManifest
from core.agent_standard.core.agent import Agent
from core.agent_standard.models.ethics import EthicsFramework
from core.agent_standard.models.authority import Authority

# Or use the convenience imports (coming soon)
# from agentify import Agent, AgentManifest
```

### **Load an Agent**

```python
from core.agent_standard.core.agent import Agent

# Load from JSON file
agent = Agent.from_json_file("my_agent.json")

# Execute
result = agent.execute("Analyze this data")
print(result)
```

### **Create an Agent Programmatically**

```python
from core.agent_standard.models.manifest import AgentManifest
from core.agent_standard.models.ethics import EthicsFramework, EthicsPrinciple
from core.agent_standard.models.authority import Authority, AuthorityEntity

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

---

## 🔧 **Dependencies**

### **Required**

- Python >= 3.9
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- typing-extensions >= 4.0.0

### **Optional**

- **LangChain Integration:** `pip install agentify-sdk[langchain]`
- **OpenAI Support:** `pip install agentify-sdk[openai]`
- **Anthropic Support:** `pip install agentify-sdk[anthropic]`
- **All Extras:** `pip install agentify-sdk[all]`
- **Development:** `pip install agentify-sdk[dev]`

---

## 🧪 **Verify Installation**

```python
# Test import
from core.agent_standard.models.manifest import AgentManifest
print("✅ Agentify SDK installed successfully!")

# Load example agent
from core.agent_standard.core.agent import Agent
agent = Agent.from_json_file("core/agent_standard/examples/complete_agent_example.json")
print(f"✅ Loaded agent: {agent.manifest.name}")
```

---

## 📖 **Next Steps**

1. **Read the Quick Start Guide:** [core/agent_standard/QUICKSTART_COMPLETE.md](core/agent_standard/QUICKSTART_COMPLETE.md)
2. **Explore Templates:** [core/agent_standard/templates/](core/agent_standard/templates/)
3. **Check Examples:** [core/agent_standard/examples/](core/agent_standard/examples/)
4. **Read Developer Guide:** [platform/agentify/DEVELOPER_GUIDE.md](platform/agentify/DEVELOPER_GUIDE.md)

---

## 🆘 **Troubleshooting**

### **Import Error**

```python
# If you get import errors, make sure you're in the project root
import sys
sys.path.insert(0, '/path/to/agentify_os')

from core.agent_standard.models.manifest import AgentManifest
```

### **Missing Dependencies**

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install with Poetry
poetry install
```

---

## 🚀 **Publishing to PyPI** (For Maintainers)

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Or use Poetry
poetry build
poetry publish
```

---

## 📝 **Current Status**

- ✅ **Source Installation:** Working
- ✅ **GitHub Installation:** Working
- ⚠️ **PyPI Installation:** Coming soon

**To use now:** Install from source or GitHub (see Option 2 or 3 above)

---

**Need help?** See the [Developer Guide](platform/agentify/DEVELOPER_GUIDE.md) or [Quick Start](core/agent_standard/QUICKSTART_COMPLETE.md)

