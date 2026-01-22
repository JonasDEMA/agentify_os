"""Pydantic models for Base Orchestrator."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Agent message types."""

    REQUEST = "request"
    INFORM = "inform"
    PROPOSE = "propose"
    AGREE = "agree"
    REFUSE = "refuse"
    CONFIRM = "confirm"
    FAILURE = "failure"
    DONE = "done"
    DISCOVER = "discover"
    OFFER = "offer"
    ASSIGN = "assign"


class AgentMessage(BaseModel):
    """Agent Communication Protocol message."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    type: MessageType
    sender: str
    to: list[str] = Field(default_factory=list)
    intent: str
    task: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    correlation: dict[str, Any] = Field(default_factory=dict)
    expected: dict[str, Any] = Field(default_factory=dict)
    status: dict[str, Any] = Field(default_factory=dict)
    security: dict[str, Any] = Field(default_factory=dict)


class Agent(BaseModel):
    """Agent metadata from marketplace."""

    agent_id: str
    name: str
    description: str
    capabilities: list[str]
    rating: float = 0.0
    price: float = 0.0
    address: str | None = None
    status: str = "unknown"  # unknown, available, busy, offline


class Team(BaseModel):
    """Agent team."""

    team_id: str = Field(default_factory=lambda: str(uuid4()))
    app_id: str
    agents: list[Agent]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed: bool = False


class TaskRequest(BaseModel):
    """Task request to an agent."""

    capability: str
    action: str
    params: dict[str, Any] = Field(default_factory=dict)
    timeout: int = 5000  # milliseconds


class TaskResponse(BaseModel):
    """Task response from an agent."""

    success: bool
    result: Any = None
    error: str | None = None
    duration: int = 0  # milliseconds

