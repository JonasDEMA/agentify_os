# 🤝 Contributing to CPA Agent Platform

Thank you for your interest in contributing to the **CPA Agent Platform**! We welcome contributions from the community.

---

## 📋 **Table of Contents**

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)

---

## 📜 **Code of Conduct**

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

---

## 🚀 **Getting Started**

### **1. Fork the Repository**

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/cpa_agent_platform.git
cd cpa_agent_platform
```

### **2. Set Up Development Environment**

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Verify installation
agent-std --version
```

### **3. Create a Branch**

```bash
# Create a feature branch
git checkout -b feature/my-feature

# Or a bugfix branch
git checkout -b fix/my-bugfix
```

---

## 🔧 **Development Workflow**

### **1. Make Changes**

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation

### **2. Run Tests**

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test
poetry run pytest tests/core/test_agent.py
```

### **3. Run Code Quality Checks**

```bash
# Linting
poetry run ruff check .

# Type checking
poetry run mypy core/

# Formatting
poetry run black .

# All checks
poetry run pre-commit run --all-files
```

### **4. Commit Changes**

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature"

# Follow conventional commits:
# - feat: new feature
# - fix: bug fix
# - docs: documentation changes
# - test: test changes
# - refactor: code refactoring
# - chore: maintenance tasks
```

### **5. Push Changes**

```bash
# Push to your fork
git push origin feature/my-feature
```

---

## 📝 **Coding Standards**

### **Python Style**

- Follow **PEP 8**
- Use **type hints** for all functions
- Write **docstrings** for all public functions/classes
- Keep functions **small and focused**
- Use **descriptive variable names**

### **Example**

```python
from typing import Optional

def greet_user(name: str, greeting: Optional[str] = None) -> str:
    """Greet a user by name.
    
    Args:
        name: User's name
        greeting: Optional custom greeting (default: "Hello")
    
    Returns:
        Greeting message
    
    Example:
        >>> greet_user("Alice")
        "Hello, Alice!"
    """
    greeting = greeting or "Hello"
    return f"{greeting}, {name}!"
```

### **Agent Standard Compliance**

All new agents MUST:
- Use `@agent_tool` decorator
- Define ethics constraints
- Define desires
- Include manifest.json
- Pass `agent-std validate`

---

## 🧪 **Testing**

### **Test Structure**

```
tests/
├── core/                  # Core component tests
├── integration/           # Integration tests
├── examples/              # Example tests
└── conftest.py            # Pytest fixtures
```

### **Writing Tests**

```python
import pytest
from core.agent_standard import Agent

def test_agent_creation():
    """Test agent creation from manifest."""
    agent = Agent.from_manifest("tests/fixtures/test_manifest.json")
    assert agent.agent_id == "agent.test.example"

@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent execution."""
    agent = Agent.from_manifest("tests/fixtures/test_manifest.json")
    result = await agent.execute({"action": "test"})
    assert result["success"] is True
```

### **Running Tests**

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/core/test_agent.py

# Specific test function
poetry run pytest tests/core/test_agent.py::test_agent_creation

# With coverage
poetry run pytest --cov=core --cov-report=html
```

---

## 📚 **Documentation**

### **Code Documentation**

- Add **docstrings** to all public functions/classes
- Use **Google-style docstrings**
- Include **examples** in docstrings

### **User Documentation**

- Update **README.md** for user-facing changes
- Update **ARCHITECTURE.md** for architectural changes
- Add **examples** to `core/agent_standard/examples/`

### **Example Documentation**

```python
def my_function(x: int, y: int) -> int:
    """Add two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    
    Example:
        >>> my_function(2, 3)
        5
    """
    return x + y
```

---

## 🔀 **Pull Request Process**

### **1. Create Pull Request**

- Go to GitHub and create a pull request from your fork
- Use a descriptive title
- Fill out the PR template

### **2. PR Checklist**

- [ ] Tests pass (`poetry run pytest`)
- [ ] Code quality checks pass (`poetry run pre-commit run --all-files`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Agent Standard compliance verified (`agent-std validate`)

### **3. Review Process**

- Maintainers will review your PR
- Address any feedback
- Once approved, your PR will be merged

---

## 🎯 **Contribution Ideas**

### **Good First Issues**

- Add new examples
- Improve documentation
- Fix typos
- Add tests

### **Advanced Contributions**

- New agent tools
- Framework adapters (LangChain, FastAPI, etc.)
- Performance improvements
- New deployment targets

---

## 📞 **Getting Help**

- **Issues**: https://github.com/JonasDEMA/cpa_agent_platform/issues
- **Discussions**: https://github.com/JonasDEMA/cpa_agent_platform/discussions
- **Email**: support@lumina-os.com

---

**Thank you for contributing! 🙏**

