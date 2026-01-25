"""Agent Communication Protocol Protocol.

A standardized protocol for structured communication between AI agents.
"""

import json
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    """agent message types."""

    # Standard messages
    REQUEST = "request"  # Anfrage an Agent
    INFORM = "inform"  # Information / Ergebnis
    PROPOSE = "propose"  # Vorschlag zur Abstimmung
    AGREE = "agree"  # Zustimmung zu Proposal
    REFUSE = "refuse"  # Ablehnung von Proposal
    CONFIRM = "confirm"  # Bestätigung
    FAILURE = "failure"  # Fehler/Abbruch
    DONE = "done"  # Task abgeschlossen
    ROUTE = "route"  # Routing-Info vom Coordinator

    # Discovery messages
    DISCOVER = "discover"  # Suche nach Agenten mit Capability
    OFFER = "offer"  # Agent bietet Capability an
    ASSIGN = "assign"  # Task wird zugewiesen


class BaseMessage(BaseModel):
    """Base agent message model.

    All agent messages inherit from this base class.
    """

    # Required fields
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique message ID")
    ts: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp ISO-8601",
    )
    type: MessageType = Field(..., description="Message type")
    sender: str = Field(..., description="Agent URI (e.g., agent://coordinator/Marketing)")
    intent: str = Field(..., description="Task intent")

    # Optional fields
    to: list[str] = Field(default_factory=list, description="Target agent(s) URI")
    task: str | None = Field(None, description="Natural language task description")
    payload: dict[str, Any] = Field(default_factory=dict, description="Message data")
    context: dict[str, Any] = Field(default_factory=dict, description="Context metadata")
    correlation: dict[str, Any] = Field(default_factory=dict, description="Conversation tracking")
    expected: dict[str, Any] = Field(default_factory=dict, description="Expected response")
    status: dict[str, Any] = Field(default_factory=dict, description="Progress tracking")
    security: dict[str, Any] = Field(default_factory=dict, description="Auth & permissions")

    @field_validator("ts", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Any) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            # Try parsing ISO format
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                return datetime.fromisoformat(v)
        if isinstance(v, datetime):
            return v
        msg = f"Invalid timestamp type: {type(v)}"
        raise TypeError(msg)

    def to_dict(self) -> dict[str, Any]:
        """Serialize message to dictionary."""
        data = self.model_dump(mode="json", exclude_none=False)
        # Convert enum to string
        if isinstance(data.get("type"), MessageType):
            data["type"] = data["type"].value
        return data

    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseMessage":
        """Deserialize message from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseMessage":
        """Deserialize message from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    class Config:
        """Pydantic config."""

        use_enum_values = True


class RequestMessage(BaseMessage):
    """Request message - Anfrage an Agent."""

    type: MessageType = Field(default=MessageType.REQUEST, frozen=True)


class InformMessage(BaseMessage):
    """Inform message - Information / Ergebnis."""

    type: MessageType = Field(default=MessageType.INFORM, frozen=True)


class ProposeMessage(BaseMessage):
    """Propose message - Vorschlag zur Abstimmung."""

    type: MessageType = Field(default=MessageType.PROPOSE, frozen=True)


class AgreeMessage(BaseMessage):
    """Agree message - Zustimmung zu Proposal."""

    type: MessageType = Field(default=MessageType.AGREE, frozen=True)


class RefuseMessage(BaseMessage):
    """Refuse message - Ablehnung von Proposal."""

    type: MessageType = Field(default=MessageType.REFUSE, frozen=True)


class ConfirmMessage(BaseMessage):
    """Confirm message - Bestätigung."""

    type: MessageType = Field(default=MessageType.CONFIRM, frozen=True)


class FailureMessage(BaseMessage):
    """Failure message - Fehler/Abbruch."""

    type: MessageType = Field(default=MessageType.FAILURE, frozen=True)


class DoneMessage(BaseMessage):
    """Done message - Task abgeschlossen."""

    type: MessageType = Field(default=MessageType.DONE, frozen=True)


class RouteMessage(BaseMessage):
    """Route message - Routing-Info vom Coordinator."""

    type: MessageType = Field(default=MessageType.ROUTE, frozen=True)


class DiscoverMessage(BaseMessage):
    """Discover message - Suche nach Agenten mit Capability."""

    type: MessageType = Field(default=MessageType.DISCOVER, frozen=True)


class OfferMessage(BaseMessage):
    """Offer message - Agent bietet Capability an."""

    type: MessageType = Field(default=MessageType.OFFER, frozen=True)


class AssignMessage(BaseMessage):
    """Assign message - Task wird zugewiesen."""

    type: MessageType = Field(default=MessageType.ASSIGN, frozen=True)


# Message type mapping
MESSAGE_TYPE_MAP: dict[MessageType, type[BaseMessage]] = {
    MessageType.REQUEST: RequestMessage,
    MessageType.INFORM: InformMessage,
    MessageType.PROPOSE: ProposeMessage,
    MessageType.AGREE: AgreeMessage,
    MessageType.REFUSE: RefuseMessage,
    MessageType.CONFIRM: ConfirmMessage,
    MessageType.FAILURE: FailureMessage,
    MessageType.DONE: DoneMessage,
    MessageType.ROUTE: RouteMessage,
    MessageType.DISCOVER: DiscoverMessage,
    MessageType.OFFER: OfferMessage,
    MessageType.ASSIGN: AssignMessage,
}


class MessageFactory:
    """Factory for creating agent messages."""

    @staticmethod
    def create(message_type: MessageType | str, **kwargs: Any) -> BaseMessage:
        """Create a message of the specified type.

        Args:
            message_type: Type of message to create
            **kwargs: Message fields

        Returns:
            Message instance

        Raises:
            ValueError: If message type is unknown
        """
        # Convert string to enum if needed
        if isinstance(message_type, str):
            try:
                message_type = MessageType(message_type)
            except ValueError as err:
                msg = f"Unknown message type: {message_type}"
                raise ValueError(msg) from err

        # Get message class
        message_class = MESSAGE_TYPE_MAP.get(message_type)
        if not message_class:
            raise ValueError(f"Unknown message type: {message_type}")

        # Create message
        return message_class(**kwargs)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BaseMessage:
        """Create a message from dictionary.

        Args:
            data: Message data

        Returns:
            Message instance

        Raises:
            ValueError: If message type is unknown or missing
        """
        message_type = data.get("type")
        if not message_type:
            raise ValueError("Message type is required")

        return MessageFactory.create(message_type, **data)

    @staticmethod
    def from_json(json_str: str) -> BaseMessage:
        """Create a message from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Message instance

        Raises:
            ValueError: If message type is unknown or missing
        """
        data = json.loads(json_str)
        return MessageFactory.from_dict(data)

