# Cognitive Layer - Desktop RPA Agent

## 🧠 Overview

The Cognitive Layer provides LLM-powered intelligence to the Desktop RPA Agent, enabling it to:
- **Understand goals** and break them down into actionable steps
- **Analyze screenshots** using GPT-4 Vision to understand the current state
- **Suggest next actions** based on context and previous experiences
- **Create strategies** for complex multi-step tasks
- **Learn from experiences** and improve over time

## 📦 Components

### 1. **LLM Wrapper** (`llm_wrapper.py`)
Main interface to OpenAI's GPT-4o/GPT-4 Vision API.

**Key Features:**
- Async API calls with retry logic
- Screenshot encoding and optimization (max 2048x2048)
- Structured JSON responses with Pydantic validation
- Two main methods:
  - `ask_for_next_action()` - Get next action suggestion
  - `ask_for_strategy()` - Create multi-step strategy

### 2. **Data Models** (`models.py`)
Pydantic models for type-safe LLM interactions:
- `LLMRequest` - Request for next action
- `LLMResponse` - Response with action suggestion
- `ActionSuggestion` - Suggested action with confidence
- `StrategyRequest` - Request for strategy creation
- `StrategyResponse` - Strategy with steps and preconditions

## 🚀 Quick Start

### Installation

The required dependencies are already installed:
```bash
poetry install
```

### Configuration

Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
ENABLE_VISION=true
```

### Basic Usage

```python
from agents.desktop_rpa.cognitive import LLMWrapper, LLMRequest

# Initialize wrapper
llm = LLMWrapper()

# Ask for next action
request = LLMRequest(
    goal="Open Outlook and compose a new email",
    current_state="desktop_visible",
    context={"visible_applications": ["Chrome", "File Explorer"]},
)

response = await llm.ask_for_next_action(request)

print(f"Suggested Action: {response.suggestion.action_type}")
print(f"Selector: {response.suggestion.selector}")
print(f"Reasoning: {response.suggestion.reasoning}")
print(f"Confidence: {response.suggestion.confidence}")
```

### With Screenshot (Vision)

```python
from agents.desktop_rpa.cognitive import LLMWrapper, LLMRequest

# Take screenshot
screenshot_base64 = LLMWrapper.encode_screenshot("screenshot.png")

# Ask for next action with vision
request = LLMRequest(
    goal="Find and click the Start button",
    current_state="desktop_visible",
    screenshot_base64=screenshot_base64,
)

response = await llm.ask_for_next_action(request)

# LLM can now see the screen and suggest precise coordinates
print(f"Click at: {response.suggestion.selector}")  # e.g., "20,1050"
```

### Strategy Creation

```python
from agents.desktop_rpa.cognitive import LLMWrapper, StrategyRequest

# Ask for strategy
request = StrategyRequest(
    goal="Send an email via Outlook with an attachment",
    known_states=["desktop_visible", "outlook_open", "outlook_compose_email"],
    known_transitions=[
        {"from": "desktop_visible", "to": "outlook_open", "action": "click Start menu"},
    ],
)

response = await llm.ask_for_strategy(request)

print(f"Strategy: {response.strategy_name}")
print(f"Steps: {len(response.steps)}")
for i, step in enumerate(response.steps, 1):
    print(f"  {i}. {step}")
```

## 🧪 Testing

Run the test suite:
```bash
poetry run python -m agents.desktop_rpa.cognitive.test_llm
```

This will run 4 tests:
1. **Ask for Next Action** (no screenshot)
2. **Ask for Next Action with Screenshot** (vision)
3. **Ask for Strategy** (multi-step planning)
4. **Iterative Conversation** (multi-turn dialogue)

## 📊 Test Results

```
✅ Test 1: Ask for Next Action
   - Goal: "Open Outlook and compose a new email"
   - State: "desktop_visible"
   - Result: Suggested clicking taskbar Outlook icon (confidence: 0.80)
   - Tokens: 557

✅ Test 2: Ask for Next Action with Screenshot
   - Goal: "Find and click the Start button"
   - State: "desktop_visible"
   - Result: Suggested clicking at (20, 1050) - Start button (confidence: 0.95)
   - Tokens: 1635 (includes vision)

✅ Test 3: Ask for Strategy
   - Goal: "Send an email via Outlook with an attachment"
   - Result: Created 12-step strategy (confidence: 0.95)
   - Steps: Open Outlook → Compose → Attach → Send

✅ Test 4: Iterative Conversation
   - Goal: "Open Outlook and send an email"
   - Result: 3-step conversation with state tracking
```

## 🎯 Action Types

The LLM can suggest the following action types:

| Action Type | Description | Selector Example | Value Example |
|------------|-------------|------------------|---------------|
| `click` | Click at coordinates or element | `"20,1050"` or `"center"` | - |
| `type` | Type text | - | `"Hello World"` |
| `wait_for` | Wait for duration | `"5.0"` (seconds) | - |
| `screenshot` | Take screenshot | `"filename.png"` | - |

## 📈 Response Structure

### LLMResponse

```json
{
  "suggestion": {
    "action_type": "click",
    "selector": "20,1050",
    "value": null,
    "reasoning": "The Start button is located at bottom-left corner",
    "confidence": 0.95,
    "metadata": {}
  },
  "state_assessment": "Desktop is visible with taskbar at bottom",
  "next_state_prediction": "Start menu will open",
  "warnings": [],
  "timestamp": "2025-11-04T18:10:39",
  "model_used": "gpt-4o",
  "tokens_used": 1635
}
```

### StrategyResponse

```json
{
  "strategy_name": "Outlook Email With Attachment Strategy",
  "goal": "Send an email via Outlook with an attachment",
  "preconditions": ["desktop_visible", "Outlook installed"],
  "steps": [
    {"action_type": "click", "selector": "Start menu", "value": "search for Outlook"},
    {"action_type": "wait_for_state", "selector": "Outlook", "value": "outlook_open"},
    ...
  ],
  "expected_states": ["outlook_open", "outlook_compose_email", "email_sent"],
  "confidence": 0.95,
  "reasoning": "This strategy uses known transitions...",
  "timestamp": "2025-11-04T18:10:49",
  "model_used": "gpt-4o"
}
```

## 🔧 Configuration

### Settings (in `.env`)

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required** - Your OpenAI API key |
| `LLM_MODEL` | `gpt-4o` | Model to use (gpt-4o, gpt-4-vision-preview) |
| `LLM_TEMPERATURE` | `0.7` | Temperature (0.0 = deterministic, 2.0 = creative) |
| `LLM_MAX_TOKENS` | `1000` | Max tokens for response |
| `LLM_TIMEOUT` | `30.0` | Request timeout in seconds |
| `LLM_MAX_RETRIES` | `3` | Max retries for failed requests |
| `ENABLE_VISION` | `true` | Enable vision capabilities (send screenshots) |

### Prompt Engineering

The system prompts are defined in `llm_wrapper.py`:
- `SYSTEM_PROMPT_ACTION` - For next action suggestions
- `SYSTEM_PROMPT_STRATEGY` - For strategy creation

You can customize these prompts to change the LLM's behavior.

## 🎓 Best Practices

### 1. **Always provide context**
```python
request = LLMRequest(
    goal="Open Outlook",
    current_state="desktop_visible",
    context={
        "visible_applications": ["Chrome", "File Explorer"],
        "screen_resolution": "1920x1080",
    },
    previous_actions=[...],  # Include previous actions
    obstacles=[...],  # Include obstacles encountered
)
```

### 2. **Use vision when uncertain**
If the agent is uncertain about the current state, take a screenshot and send it to the LLM:
```python
screenshot_base64 = LLMWrapper.encode_screenshot("current_state.png")
request.screenshot_base64 = screenshot_base64
```

### 3. **Track confidence levels**
```python
if response.suggestion.confidence < 0.7:
    # Low confidence - take screenshot or ask for clarification
    logger.warning(f"Low confidence: {response.suggestion.confidence}")
```

### 4. **Handle warnings**
```python
if response.warnings:
    for warning in response.warnings:
        logger.warning(f"LLM Warning: {warning}")
```

### 5. **Optimize token usage**
- Only send screenshots when necessary (vision uses more tokens)
- Limit context size (previous_actions, obstacles)
- Use lower max_tokens for simple queries

## 🔮 Future Enhancements

- [ ] **State Graph Integration** - Use learned state graphs to guide LLM
- [ ] **Experience Memory** - Learn from past successes/failures
- [ ] **Strategy Manager** - Store and reuse successful strategies
- [ ] **Local LLM Support** - Add Ollama/Llama integration
- [ ] **Multi-modal Input** - Support audio, video, etc.
- [ ] **Fine-tuning** - Fine-tune on domain-specific tasks

## 📚 Related Documentation

- [Cognitive RPA Requirements](../../../docs/COGNITIVE_RPA_REQUIREMENTS.md)
- [Desktop RPA Agent README](../README.md)
- [Architecture Overview](../../../docs/ARCHITECTURE.md)

## 🤝 Contributing

See the main project README for contribution guidelines.

## 📄 License

See the main project LICENSE file.

