# Desktop RPA Agent

A specialized agent for local desktop automation using PyAutoGUI.

## Features

- ✅ **Click Actions**: Click at coordinates or screen center
- ✅ **Type Actions**: Type text at current cursor position
- ✅ **Wait Actions**: Wait for specified duration
- ✅ **Screenshot Actions**: Capture screenshots with auto-naming

## Installation

The agent is part of the CPA Scheduler project. Dependencies are managed via Poetry:

```bash
poetry install
```

## Running the Agent

### Standalone Mode

```bash
poetry run python -m agents.desktop_rpa.main
```

The agent will start on `http://127.0.0.1:8001` by default.

### Configuration

Create a `.env` file or set environment variables:

```env
# Agent Info
AGENT_ID=desktop-rpa-001
AGENT_NAME=Desktop RPA Agent
AGENT_VERSION=0.1.0

# API Settings
HOST=127.0.0.1
PORT=8001
LOG_LEVEL=INFO

# Scheduler Settings (for registration)
SCHEDULER_URL=http://localhost:8000
REGISTER_ON_STARTUP=false
HEARTBEAT_INTERVAL=30

# Execution Settings
DEFAULT_TIMEOUT=30.0
SCREENSHOT_DIR=./data/screenshots
MAX_RETRIES=3

# PyAutoGUI Settings
PYAUTOGUI_PAUSE=0.5
PYAUTOGUI_FAILSAFE=true
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "agent_id": "desktop-rpa-001",
  "agent_name": "Desktop RPA Agent",
  "version": "0.1.0",
  "capabilities": ["click", "type", "wait_for", "screenshot"]
}
```

### Execute Task

```bash
POST /tasks
```

Request Body:
```json
{
  "task_id": "task-001",
  "action": "screenshot",
  "selector": "test_screenshot",
  "text": null,
  "timeout": 30.0,
  "metadata": {}
}
```

Response:
```json
{
  "task_id": "task-001",
  "success": true,
  "message": "Screenshot saved to data/screenshots/test_screenshot.png",
  "data": {
    "filepath": "data/screenshots/test_screenshot.png",
    "filename": "test_screenshot.png",
    "size": [1920, 1080]
  },
  "error": null
}
```

## Supported Actions

### 1. Click (`action: "click"`)

Click at specified coordinates or screen center.

**Selector Formats:**
- `"x,y"` - Click at coordinates (e.g., `"500,300"`)
- `"center"` - Click at screen center

**Example:**
```json
{
  "task_id": "click-001",
  "action": "click",
  "selector": "500,300",
  "timeout": 30.0
}
```

### 2. Type (`action: "type"`)

Type text at current cursor position.

**Example:**
```json
{
  "task_id": "type-001",
  "action": "type",
  "selector": "",
  "text": "Hello World!",
  "timeout": 30.0
}
```

### 3. Wait (`action: "wait_for"`)

Wait for specified duration in seconds.

**Selector Format:**
- `"5"` - Wait for 5 seconds

**Example:**
```json
{
  "task_id": "wait-001",
  "action": "wait_for",
  "selector": "2",
  "timeout": 30.0
}
```

### 4. Screenshot (`action: "screenshot"`)

Capture a screenshot and save to file.

**Selector Formats:**
- `"filename"` - Save as `filename.png`
- `"auto"` - Auto-generate filename with timestamp

**Example:**
```json
{
  "task_id": "screenshot-001",
  "action": "screenshot",
  "selector": "my_screenshot",
  "timeout": 30.0
}
```

## Testing

### Manual Testing with curl/Invoke-WebRequest

**Health Check:**
```powershell
Invoke-WebRequest -Uri http://localhost:8001/health
```

**Screenshot:**
```powershell
Invoke-WebRequest -Uri http://localhost:8001/tasks `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"task_id":"test-001","action":"screenshot","selector":"test","timeout":30.0}'
```

**Wait:**
```powershell
Invoke-WebRequest -Uri http://localhost:8001/tasks `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"task_id":"test-002","action":"wait_for","selector":"2","timeout":30.0}'
```

## Architecture

```
agents/desktop_rpa/
├── __init__.py
├── main.py                    # FastAPI application
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration
└── executors/
    ├── __init__.py
    ├── base.py                # Base executor interface
    ├── click_executor.py      # Click actions
    ├── type_executor.py       # Type actions
    ├── wait_executor.py       # Wait actions
    └── screenshot_executor.py # Screenshot actions
```

## Future Enhancements

- [ ] OCR/Vision for element-based clicking
- [ ] Element-based waiting (wait for element to appear)
- [ ] Keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)
- [ ] Mouse drag & drop
- [ ] Window management (focus, minimize, maximize)
- [ ] Multi-monitor support
- [ ] Registration with CPA Scheduler
- [ ] Heartbeat & health reporting

## License

Part of the LuminaOS CPA Platform.

