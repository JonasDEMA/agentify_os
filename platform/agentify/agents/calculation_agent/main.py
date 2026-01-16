"""Calculation Agent - Simple mathematical calculation agent."""

import os
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn


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
            
            # Return result
            return AgentMessage(
                type=MessageType.INFORM,
                sender=AGENT_ID,
                to=[message.sender],
                intent="calculation_result",
                payload={
                    "result": result,
                    "operation": f"{a} {op} {b}",
                },
            )
            
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
    return {
        "agent_id": AGENT_ID,
        "name": "Calculation Agent",
        "version": "1.0.0",
        "status": "active",
        "capabilities": ["calculation"],
    }


# ========== Main ==========

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting Calculation Agent on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

