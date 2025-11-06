"""Agent Communication for LuminaOS integration."""

from agents.desktop_rpa.agent_comm.agent_discovery import AgentDiscovery
from agents.desktop_rpa.agent_comm.agent_registry import AgentRegistry
from agents.desktop_rpa.agent_comm.models import Agent, AgentCapability

__all__ = ["AgentDiscovery", "AgentRegistry", "Agent", "AgentCapability"]

