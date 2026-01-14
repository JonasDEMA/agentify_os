"""Models for natural language agent communication.

This module defines the message types for human-like communication between
user and agent, including real-time status updates.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages in agent communication."""
    
    # User → Agent
    USER_COMMAND = "user_command"  # User sends natural language command
    
    # Agent → User (Status Updates)
    AGENT_THINKING = "agent_thinking"  # "Let me think about this..."
    AGENT_ACTION = "agent_action"  # "Opening Outlook now..."
    AGENT_PROGRESS = "agent_progress"  # "Checking your calendar..."
    AGENT_RESULT = "agent_result"  # "Your next appointment with Dieter is..."
    AGENT_ERROR = "agent_error"  # "Sorry, I couldn't find..."
    AGENT_QUESTION = "agent_question"  # "Which calendar should I check?"
    
    # System
    SYSTEM_STATUS = "system_status"  # Agent online/offline


class UserCommand(BaseModel):
    """User command in natural language."""
    
    message_type: MessageType = Field(default=MessageType.USER_COMMAND)
    command: str = Field(..., description="Natural language command from user")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None, description="Session ID for conversation tracking")


class AgentThinking(BaseModel):
    """Agent is thinking/analyzing."""
    
    message_type: MessageType = Field(default=MessageType.AGENT_THINKING)
    message: str = Field(..., description="Human-like thinking message")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None)
    
    # Optional: What the agent is analyzing
    analyzing: str | None = Field(default=None, description="What is being analyzed")


class AgentAction(BaseModel):
    """Agent is performing an action."""
    
    message_type: MessageType = Field(default=MessageType.AGENT_ACTION)
    message: str = Field(..., description="Human-like action message")
    action_type: str = Field(..., description="Type of action: click, type, open_app, etc.")
    target: str | None = Field(default=None, description="Target of action")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None)


class AgentProgress(BaseModel):
    """Agent progress update during task execution."""
    
    message_type: MessageType = Field(default=MessageType.AGENT_PROGRESS)
    message: str = Field(..., description="Human-like progress message")
    progress_percent: int | None = Field(default=None, ge=0, le=100, description="Progress percentage")
    current_step: int | None = Field(default=None, description="Current step number")
    total_steps: int | None = Field(default=None, description="Total number of steps")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None)


class AgentResult(BaseModel):
    """Agent final result/answer."""
    
    message_type: MessageType = Field(default=MessageType.AGENT_RESULT)
    message: str = Field(..., description="Human-like result message")
    result_data: dict[str, Any] | None = Field(default=None, description="Structured result data")
    success: bool = Field(default=True, description="Whether task was successful")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None)


class AgentError(BaseModel):
    """Agent encountered an error."""
    
    message_type: MessageType = Field(default=MessageType.AGENT_ERROR)
    message: str = Field(..., description="Human-like error message")
    error_type: str | None = Field(default=None, description="Type of error")
    error_details: str | None = Field(default=None, description="Technical error details")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None)


class AgentQuestion(BaseModel):
    """Agent asks user for clarification."""
    
    message_type: MessageType = Field(default=MessageType.AGENT_QUESTION)
    message: str = Field(..., description="Question for user")
    options: list[str] | None = Field(default=None, description="Possible answer options")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: str | None = Field(default=None)


class SystemStatus(BaseModel):
    """System status update."""
    
    message_type: MessageType = Field(default=MessageType.SYSTEM_STATUS)
    status: str = Field(..., description="online, offline, busy, error")
    agent_id: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now)


# Union type for all message types
AgentMessage = (
    UserCommand
    | AgentThinking
    | AgentAction
    | AgentProgress
    | AgentResult
    | AgentError
    | AgentQuestion
    | SystemStatus
)


class ConversationSession(BaseModel):
    """A conversation session between user and agent."""
    
    session_id: str = Field(..., description="Unique session ID")
    user_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: datetime | None = Field(default=None)
    messages: list[dict[str, Any]] = Field(default_factory=list, description="All messages in session")
    task_goal: str | None = Field(default=None, description="Original task goal")
    task_status: str = Field(default="in_progress", description="in_progress, completed, failed, cancelled")

