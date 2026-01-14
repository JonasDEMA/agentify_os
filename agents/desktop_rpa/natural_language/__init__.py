"""Natural language communication module for CPA agent."""

from agents.desktop_rpa.natural_language.models import (
    MessageType,
    UserCommand,
    AgentThinking,
    AgentAction,
    AgentProgress,
    AgentResult,
    AgentError,
    AgentQuestion,
    SystemStatus,
    AgentMessage,
    ConversationSession,
)

__all__ = [
    "MessageType",
    "UserCommand",
    "AgentThinking",
    "AgentAction",
    "AgentProgress",
    "AgentResult",
    "AgentError",
    "AgentQuestion",
    "SystemStatus",
    "AgentMessage",
    "ConversationSession",
]

