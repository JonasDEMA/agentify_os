"""Data models for Agent Communication."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentCapability:
    """Represents an agent capability."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"


@dataclass
class Agent:
    """Represents an agent in the Agentify ecosystem."""

    id: str
    name: str
    description: str
    capabilities: list[AgentCapability]
    endpoint: str
    status: str = "available"  # available, busy, offline
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability.

        Args:
            capability_name: Name of the capability to check

        Returns:
            True if agent has the capability, False otherwise
        """
        return any(cap.name == capability_name for cap in self.capabilities)

    def get_capability(self, capability_name: str) -> AgentCapability | None:
        """Get a specific capability.

        Args:
            capability_name: Name of the capability to get

        Returns:
            AgentCapability if found, None otherwise
        """
        for cap in self.capabilities:
            if cap.name == capability_name:
                return cap
        return None


@dataclass
class AgentRequest:
    """Represents a request to an agent."""

    capability: str
    parameters: dict[str, Any]
    requester_id: str = "cpa_agent"
    priority: str = "normal"  # low, normal, high, urgent
    timeout: int = 30  # seconds


@dataclass
class AgentResponse:
    """Represents a response from an agent."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    agent_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

