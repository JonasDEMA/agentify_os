"""Agent Communication Protocol implementation."""

import httpx
from typing import Any

from .models import AgentMessage, MessageType


class AgentProtocol:
    """Handles Agent Communication Protocol."""

    def __init__(self, sender_id: str):
        self.sender_id = sender_id
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_message(
        self,
        agent_address: str,
        message_type: MessageType,
        intent: str,
        payload: dict[str, Any] | None = None,
        to: list[str] | None = None,
    ) -> AgentMessage:
        """Send a message to an agent.

        Args:
            agent_address: Agent HTTP address (e.g., http://calc:8000)
            message_type: Type of message
            intent: Intent of the message
            payload: Message payload
            to: Target agent IDs

        Returns:
            Response message from agent
        """
        message = AgentMessage(
            type=message_type,
            sender=self.sender_id,
            to=to or [],
            intent=intent,
            payload=payload or {},
        )

        # Send message via HTTP POST
        response = await self.client.post(
            f"{agent_address}/agent/message",
            json=message.model_dump(mode="json"),
        )
        response.raise_for_status()

        # Parse response
        response_data = response.json()
        return AgentMessage(**response_data)

    async def request(
        self,
        agent_address: str,
        intent: str,
        payload: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """Send a request message.

        Args:
            agent_address: Agent HTTP address
            intent: Request intent
            payload: Request payload

        Returns:
            Response message
        """
        return await self.send_message(
            agent_address=agent_address,
            message_type=MessageType.REQUEST,
            intent=intent,
            payload=payload,
        )

    async def inform(
        self,
        agent_address: str,
        intent: str,
        payload: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """Send an inform message.

        Args:
            agent_address: Agent HTTP address
            intent: Inform intent
            payload: Inform payload

        Returns:
            Response message
        """
        return await self.send_message(
            agent_address=agent_address,
            message_type=MessageType.INFORM,
            intent=intent,
            payload=payload,
        )

    async def discover(
        self,
        marketplace_address: str,
        capability: str,
        min_rating: float = 0.0,
        max_price: float = float("inf"),
    ) -> AgentMessage:
        """Discover agents on marketplace.

        Args:
            marketplace_address: Marketplace HTTP address
            capability: Required capability
            min_rating: Minimum rating
            max_price: Maximum price

        Returns:
            Response with discovered agents
        """
        return await self.send_message(
            agent_address=marketplace_address,
            message_type=MessageType.DISCOVER,
            intent="find_agents",
            payload={
                "capability": capability,
                "min_rating": min_rating,
                "max_price": max_price,
            },
        )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

