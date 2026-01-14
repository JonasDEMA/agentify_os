# 🤖 Natural Language Agent Communication

This module enables **natural language communication** with the CPA Agent, with **real-time status updates** in human-like language.

## 🎯 Features

- **Natural Language Commands**: Tell the agent what to do in plain English/German
- **Real-time Updates**: Agent sends human-like progress updates during execution
- **Human-like Communication**: "Let me check your calendar...", "Opening Outlook now...", etc.
- **WebSocket-based**: Real-time bidirectional communication
- **Local Testing**: Simulates cloud service locally for offline testing

## 📦 Components

### 1. **Message Protocol** (`models.py`)

Defines message types for communication:

- `UserCommand`: User sends natural language command
- `AgentThinking`: "Let me think about this..."
- `AgentAction`: "Opening Outlook now..."
- `AgentProgress`: "Checking your calendar... (50%)"
- `AgentResult`: "Your next appointment with Dieter is on Friday at 2 PM"
- `AgentError`: "Sorry, I couldn't find..."
- `AgentQuestion`: "Which calendar should I check?"

### 2. **Natural Language Orchestrator** (`nl_orchestrator.py`)

Orchestrates the entire flow:

1. Receives natural language command
2. Parses intent using LLM
3. Routes to appropriate CPA task
4. Sends real-time status updates
5. Returns final result

### 3. **WebSocket Server** (`websocket_server.py`)

WebSocket server for real-time communication:

- Accepts connections from UI
- Forwards commands to orchestrator
- Streams updates back to UI

### 4. **Test UI** (`test_ui.html` + `test_ui.js`)

Beautiful web interface for testing:

- Send natural language commands
- See real-time agent responses
- Progress bars for long tasks
- Color-coded message types

## 🚀 Quick Start

### 1. Start the WebSocket Server

```bash
# Option 1: Use the batch file
cd agents/desktop_rpa/natural_language
start_test_server.bat

# Option 2: Run directly
poetry run python -m agents.desktop_rpa.natural_language.websocket_server
```

### 2. Open the Test UI

Open `test_ui.html` in your browser (Chrome, Firefox, Edge)

### 3. Send Commands

Try these example commands:

- "Check my next appointment with Dieter"
- "Open Outlook and check my calendar"
- "Find all emails from John"
- "Create a new Word document"
- "Activate Ransomware Protection in Windows"

## 📊 Message Flow Example

```
User: "Check my next appointment with Dieter"
  ↓
Agent: 💭 "Let me understand what you need..."
  ↓
Agent: ⚡ "Alright, let me work with Outlook for you..."
  ↓
Agent: 📊 "Step 1/5: Opening Outlook..." (20%)
  ↓
Agent: 📊 "Step 2/5: Navigating to calendar..." (40%)
  ↓
Agent: 📊 "Step 3/5: Searching for appointments with Dieter..." (60%)
  ↓
Agent: 📊 "Step 4/5: Found appointment..." (80%)
  ↓
Agent: ✅ "Your next appointment with Dieter is on Friday, December 15 at 2:00 PM"
```

## 🔧 Architecture

```
┌─────────────┐
│   Browser   │
│  (Test UI)  │
└──────┬──────┘
       │ WebSocket
       │ ws://localhost:8765
       ↓
┌──────────────────────┐
│  WebSocket Server    │
│  (websocket_server)  │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────────┐
│  NL Orchestrator         │
│  (nl_orchestrator)       │
│  - Parse intent          │
│  - Route to task         │
│  - Send updates          │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│  Cognitive Executor      │
│  (cognitive_executor)    │
│  - Execute task          │
│  - Vision Layer          │
│  - Window Manager        │
└──────────────────────────┘
```

## 🌐 Cloud Service Integration

This module is designed to work both **locally** (for testing) and with a **cloud service** (for production):

### Local Mode (Current)
- WebSocket server runs locally
- UI connects to `ws://localhost:8765`
- Agent executes tasks on local machine

### Cloud Mode (Future)
- WebSocket server runs on Railway/AWS
- UI connects to `wss://your-domain.com`
- Multiple agents can connect
- Agents share learnings via cloud database

## 📝 Example Commands

### Calendar & Appointments
- "Check my next appointment with [Name]"
- "Show me my calendar for today"
- "Find all meetings this week"

### Email
- "Find all emails from [Name]"
- "Check my unread emails"
- "Send an email to [Name]"

### Applications
- "Open Outlook"
- "Open Word and create a new document"
- "Open Excel and load [filename]"

### System Tasks
- "Activate Ransomware Protection"
- "Check Windows Defender status"
- "Take a screenshot"

## 🔒 Security

- **Local Testing**: No data leaves your machine
- **Cloud Mode**: All communication encrypted (WSS)
- **Authentication**: API keys for cloud connections
- **Privacy**: User data ownership and control

## 🚧 Future Enhancements

- [ ] Better intent parsing with LLM
- [ ] Multi-turn conversations
- [ ] Context awareness across sessions
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Agent learning from user feedback

## 📞 Support

For questions or issues, check the main CPA documentation or create an issue on GitHub.

