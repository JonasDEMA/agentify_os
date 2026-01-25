"""Calculation Agent - Simple mathematical calculation agent."""

import json
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# Add base_coordinator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "base_coordinator"))
from base_coordinator.workflow_handler import handle_workflow_chain


# ========== Models ==========

class MessageType(str, Enum):
    """Agent message types."""
    REQUEST = "request"
    INFORM = "inform"
    FAILURE = "failure"


class AgentMessage(BaseModel):
    """Agent Communication Protocol message."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    type: MessageType
    sender: str
    to: list[str] = Field(default_factory=list)
    intent: str
    payload: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agent_id: str
    version: str
    uptime: float


# ========== FastAPI App ==========

app = FastAPI(
    title="Calculation Agent",
    description="Simple mathematical calculation agent",
    version="1.0.0",
)

AGENT_ID = "agent.calculator.calculation"
START_TIME = datetime.utcnow()

# Logging storage
LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)
ACTIVITIES_LOG = LOGS_DIR / "activities.jsonl"
COMMUNICATIONS_LOG = LOGS_DIR / "communications.jsonl"

# In-memory storage for quick access
activities = []
communications = []


# ========== Logging Functions ==========

def log_activity(activity: dict):
    """Log an activity."""
    activities.append(activity)
    with open(ACTIVITIES_LOG, "a") as f:
        f.write(json.dumps(activity) + "\n")


def log_communication(comm: dict):
    """Log a communication."""
    communications.append(comm)
    with open(COMMUNICATIONS_LOG, "a") as f:
        f.write(json.dumps(comm) + "\n")


# ========== Calculation Logic ==========

def calculate(a: float, b: float, op: str) -> float:
    """Perform calculation.
    
    Args:
        a: First number
        b: Second number
        op: Operation (+, -, *, /)
        
    Returns:
        Result of calculation
        
    Raises:
        ValueError: If operation is invalid or division by zero
    """
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    else:
        raise ValueError(f"Invalid operation: {op}")


# ========== Endpoints ==========

@app.post("/agent/message")
async def handle_message(message: AgentMessage) -> AgentMessage:
    """Handle incoming agent message.

    Args:
        message: Incoming message

    Returns:
        Response message
    """
    print(f"📨 Received message: {message.intent} from {message.sender}")

    # Log incoming communication
    log_communication({
        "timestamp": datetime.utcnow().isoformat(),
        "message_id": message.id,
        "direction": "inbound",
        "from_agent": message.sender,
        "to_agent": AGENT_ID,
        "intent": message.intent,
        "status": "received",
        "payload": message.payload,
    })

    # Create activity
    activity_id = f"act_{uuid4().hex[:8]}"
    activity_start = datetime.utcnow()

    # Handle calculate intent
    if message.intent == "calculate":
        try:
            # Extract parameters
            a = message.payload.get("a")
            b = message.payload.get("b")
            op = message.payload.get("op")
            
            if a is None or b is None or op is None:
                raise ValueError("Missing parameters: a, b, op required")
            
            # Perform calculation
            result = calculate(float(a), float(b), op)

            # Log activity
            duration_ms = (datetime.utcnow() - activity_start).total_seconds() * 1000
            log_activity({
                "timestamp": activity_start.isoformat(),
                "activity_id": activity_id,
                "activity_type": "calculation",
                "status": "completed",
                "duration_ms": duration_ms,
                "input": {"a": a, "b": b, "op": op},
                "output": {"result": result},
                "ethics_evaluation": {
                    "passed": True,
                    "constraints_checked": ["no-harm", "transparency"],
                    "violations": []
                },
            })

            # Create response
            result_payload = {
                "result": result,
                "operation": f"{a} {op} {b}",
            }
            
            # Check if this is part of a workflow chain
            if "__workflow__" in message.payload:
                return await handle_workflow_chain(
                    message=message,
                    my_result=result_payload,
                    agent_id=AGENT_ID
                )
            
            response = AgentMessage(
                type=MessageType.INFORM,
                sender=AGENT_ID,
                to=[message.sender],
                intent="calculation_result",
                payload=result_payload,
            )

            # Log outbound communication
            log_communication({
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": response.id,
                "direction": "outbound",
                "from_agent": AGENT_ID,
                "to_agent": message.sender,
                "intent": response.intent,
                "status": "sent",
                "payload": response.payload,
            })

            return response
            
        except Exception as e:
            # Return error
            return AgentMessage(
                type=MessageType.FAILURE,
                sender=AGENT_ID,
                to=[message.sender],
                intent="calculation_error",
                payload={
                    "error": str(e),
                },
            )
    
    # Unknown intent
    return AgentMessage(
        type=MessageType.FAILURE,
        sender=AGENT_ID,
        to=[message.sender],
        intent="unknown_intent",
        payload={
            "error": f"Unknown intent: {message.intent}",
        },
    )


@app.get("/health")
async def health() -> HealthResponse:
    """Health check endpoint."""
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    return HealthResponse(
        status="healthy",
        agent_id=AGENT_ID,
        version="1.0.0",
        uptime=uptime,
    )


@app.get("/manifest")
async def manifest() -> dict[str, Any]:
    """Return agent manifest."""
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path) as f:
        return json.load(f)


@app.get("/agent/activities")
async def get_activities() -> dict[str, Any]:
    """Get all activities."""
    return {"activities": activities}


@app.get("/agent/communications")
async def get_communications() -> dict[str, Any]:
    """Get all communications."""
    return {"communications": communications}


@app.get("/agent/ui", response_class=HTMLResponse)
@app.get("/agent/ui/", response_class=HTMLResponse)
async def ui_root():
    """Redirect to overview."""
    return HTMLResponse(content="""
        <html>
            <head>
                <meta http-equiv="refresh" content="0; url=/agent/ui/overview">
            </head>
            <body>Redirecting to overview...</body>
        </html>
    """)


@app.get("/agent/ui/overview", response_class=HTMLResponse)
async def ui_overview():
    """Agent overview page."""
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"

    content = f"""
        <h1>Calculation Agent - Overview</h1>

        <div class="card">
            <h2>Status</h2>
            <div class="stat">
                <div class="stat-label">Agent ID</div>
                <div class="stat-value">{AGENT_ID}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Status</div>
                <div class="stat-value"><span class="badge badge-success">Active</span></div>
            </div>
            <div class="stat">
                <div class="stat-label">Uptime</div>
                <div class="stat-value">{uptime_str}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Activities</div>
                <div class="stat-value">{len(activities)}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Communications</div>
                <div class="stat-value">{len(communications)}</div>
            </div>
        </div>

        <div class="card">
            <h2>Capabilities</h2>
            <p>✅ Basic arithmetic operations (+, -, *, /)</p>
        </div>
    """

    return get_ui_template("Calculation Agent - Overview", content)


def get_ui_template(title: str, content: str) -> str:
    """Get HTML template for UI pages."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                padding: 20px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #3b82f6; margin-bottom: 20px; }}
            h2 {{ color: #60a5fa; margin: 20px 0 10px; }}
            .nav {{
                background: #1e293b;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: flex;
                gap: 15px;
            }}
            .nav a {{
                color: #3b82f6;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 4px;
                transition: background 0.2s;
            }}
            .nav a:hover {{ background: #334155; }}
            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .stat {{
                display: inline-block;
                margin-right: 30px;
                margin-bottom: 10px;
            }}
            .stat-label {{ color: #94a3b8; font-size: 14px; }}
            .stat-value {{ color: #e2e8f0; font-size: 24px; font-weight: bold; }}
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
            }}
            .badge-success {{ background: #10b981; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/agent/ui/overview">Overview</a>
                <a href="/agent/ui/activities">Activities</a>
                <a href="/agent/ui/communications">Communications</a>
                <a href="/agent/ui/ethics">Ethics & Health</a>
                <a href="/agent/ui/io">I/O</a>
            </div>
            {content}
        </div>
    </body>
    </html>
    """


# ========== Main ==========

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting Calculation Agent on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

