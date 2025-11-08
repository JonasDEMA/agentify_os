"""Server Communication - Agent registration, log streaming, screenshot upload."""
from agents.desktop_rpa.server_comm.agent_client import AgentClient
from agents.desktop_rpa.server_comm.models import (
    AgentInfo,
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    LogEntry,
    ScreenshotUpload,
)

__all__ = [
    "AgentClient",
    "AgentInfo",
    "AgentRegistrationRequest",
    "AgentRegistrationResponse",
    "LogEntry",
    "ScreenshotUpload",
]

