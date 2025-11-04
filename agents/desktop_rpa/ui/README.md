# 🤖 CPA Agent Monitor

**Windows UI for monitoring and controlling the Cognitive RPA Agent**

## Features

### 📊 Live Monitoring
- **Real-time task execution** - See what the agent is doing right now
- **Step-by-step progress** - Track each step of the execution
- **State visualization** - Current state of the desktop/application
- **Activity log** - Detailed log with color-coded messages

### 🎮 Control Panel
- **Template Tasks** - Pre-defined tasks you can run with one click
- **Custom Prompts** - Write your own task descriptions
- **Start/Stop Controls** - Full control over task execution
- **Status Indicator** - Visual feedback on agent status

### 🎓 Learning History
- **Track learned strategies** - See what the agent has learned
- **Confidence scores** - How confident the agent is in each strategy
- **Revision history** - Track improvements over time
- **Timestamp tracking** - When each strategy was learned

### 🧠 Agent Intelligence
The monitor shows you exactly what the agent is thinking:
- 📸 **Taking screenshots** - Capturing current state
- 🧠 **Analyzing** - LLM is processing the screenshot
- 💭 **Reasoning** - Why the agent chose this action
- 📊 **Confidence** - How sure the agent is (🟢 high, 🟡 medium, 🔴 low)
- ⚙️ **Executing** - Performing the action
- ✅ **Completed** - Action finished

## Usage

### Running the Monitor

**Option 1: Python Script**
```bash
poetry run python agents/desktop_rpa/ui/run_monitor.py
```

**Option 2: Executable (after building)**
```bash
dist\CPA_Monitor.exe
```

### Building the Executable

```bash
# Windows
build_executable.bat

# Or manually
poetry add --group dev pyinstaller
poetry run pyinstaller build_monitor.spec --clean
```

The executable will be created in `dist\CPA_Monitor.exe`.

## Template Tasks

The monitor comes with pre-defined tasks:

1. **Open Start Menu** - Click the Windows Start button
2. **Open Notepad** - Launch Notepad from Start Menu
3. **Open Calculator** - Find and open Calculator
4. **Open File Explorer** - Launch Windows Explorer
5. **Search in Start Menu** - Search for Control Panel
6. **Type in Notepad** - Open Notepad and type text
7. **Take Screenshot** - Capture desktop screenshot
8. **Open Browser** - Launch default web browser

## Custom Tasks

You can write your own task descriptions in natural language:

**Examples:**
- "Open Outlook and create a new email"
- "Find the invoice.pdf file in Documents folder"
- "Open Excel and create a new spreadsheet"
- "Search for 'Python' in the Start Menu"

## UI Components

### Control Panel (Left)
- **Task Templates Dropdown** - Select pre-defined tasks
- **Custom Task Text Area** - Write your own task
- **▶️ Start Task Button** - Begin execution
- **⏹️ Stop Button** - Cancel current task
- **Status Label** - Current agent status

### Monitor Panel (Right Top)
- **Current Goal** - What the agent is trying to achieve
- **Step Counter** - Current step / Total steps
- **State** - Current desktop/application state
- **Activity Log** - Real-time execution log with colors:
  - 🔵 Blue = Info
  - 🟢 Green = Success
  - 🟠 Orange = Warning
  - 🔴 Red = Error
  - 🟣 Purple = Thinking/Analyzing

### Learning History (Right Bottom)
- **Timestamp** - When the strategy was learned
- **Task** - What task was performed
- **Strategy** - How many steps it took
- **Confidence** - Success confidence score

## Event Types

The monitor tracks these events:

| Event | Icon | Description |
|-------|------|-------------|
| `start` | 🚀 | Task execution started |
| `step` | 📍 | New step begun |
| `screenshot` | 📸 | Screenshot captured |
| `thinking` | 🧠 | LLM analyzing screenshot |
| `action_suggested` | 💭 | LLM suggested next action |
| `executing` | ⚙️ | Performing action |
| `action_completed` | ✅ | Action finished |
| `completed` | 🎉 | Task completed successfully |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CPA Monitor UI                        │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │   Control    │  │      Live Monitoring             │ │
│  │   Panel      │  │  ┌────────────────────────────┐  │ │
│  │              │  │  │  Goal, Step, State         │  │ │
│  │ Templates    │  │  └────────────────────────────┘  │ │
│  │ Custom Task  │  │  ┌────────────────────────────┐  │ │
│  │ Start/Stop   │  │  │  Activity Log              │  │ │
│  │              │  │  │  [Colored messages]        │  │ │
│  └──────────────┘  │  └────────────────────────────┘  │ │
│                    └──────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Learning History                        │   │
│  │  [Timestamp | Task | Strategy | Confidence]      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Cognitive Executor   │
              │  (with callback)      │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │    LLM Wrapper        │
              │    (GPT-4o)           │
              └───────────────────────┘
```

## Callback System

The executor sends events to the UI via callback:

```python
def _on_executor_event(self, event: dict):
    event_type = event.get("type")
    data = event.get("data", {})
    
    if event_type == "thinking":
        self._log("🧠 Analyzing screenshot...", "thinking")
    elif event_type == "executing":
        self._log(f"⚙️ Executing: {data['action']}", "info")
    # ... etc
```

## Future Enhancements

- 📊 **Graph Visualization** - Visual state graphs
- 🎨 **Dark Mode** - Theme support
- 💾 **Save/Load Strategies** - Export learned knowledge
- 📈 **Statistics Dashboard** - Success rates, timing, etc.
- 🔔 **Notifications** - Desktop notifications on completion
- 🎥 **Screen Recording** - Record agent execution
- 🌐 **Web UI** - Browser-based interface

## Troubleshooting

**UI doesn't start:**
- Make sure all dependencies are installed: `poetry install`
- Check that Python 3.12+ is installed
- Verify `.env` file exists with `OPENAI_API_KEY`

**Task execution fails:**
- Check OpenAI API key is valid
- Ensure PyAutoGUI can control mouse/keyboard
- Check screenshots directory is writable

**Executable doesn't work:**
- Rebuild with `build_executable.bat`
- Check that `.env` file is in same directory as executable
- Run from command line to see error messages

## License

Part of LuminaOS - CPA Agent Platform

