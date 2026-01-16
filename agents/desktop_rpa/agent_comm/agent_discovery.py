"""Agent Discovery - Find and communicate with Agentify agents via Agent Gateway.

This module provides:
- Discovery of available agents in Agentify
- Querying agents by capability
- Communication with selected agents via LAM protocol
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

from agents.desktop_rpa.agent_comm.models import (
    Agent,
    AgentCapability,
    AgentRequest,
    AgentResponse,
)

logger = logging.getLogger(__name__)


class AgentDiscovery:
    """Discovers and communicates with Agentify agents via Agent Gateway."""

    def __init__(
        self,
        api_token: str | None = None,
        gateway_url: str | None = None,
        sender_id: str = "cpa_agent",
        timeout: int = 30,
    ):
        """Initialize Agent Discovery.

        Args:
            api_token: Agentify API token for X-API-Token header (defaults to agentify_config)
            gateway_url: Agent Gateway URL (defaults to agentify_config)
            sender_id: Sender identifier for agent messages
            timeout: Request timeout in seconds
        """
        # Import here to avoid circular dependency
        from agents.desktop_rpa.config.agentify_config import agentify_config

        self.gateway_url = gateway_url or agentify_config.gateway_url
        self.api_token = api_token or agentify_config.api_token
        self.sender_id = sender_id
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
        }

        if self.api_token:
            self.headers["X-API-Token"] = self.api_token

        logger.info(f"Agent Discovery initialized (gateway={self.gateway_url}, sender={sender_id})")

    def _create_lam_message(
        self,
        message_type: str,
        payload: dict[str, Any],
        to: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a LAM-compliant message.

        Args:
            message_type: agent message type (discovery, request, inform, etc.)
            payload: Message payload
            to: Optional list of recipient agent URIs

        Returns:
            agent message dictionary
        """
        message = {
            "message_id": str(uuid.uuid4()),
            "message_type": message_type,
            "sender": self.sender_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        if to:
            message["to"] = to

        return message

    async def discover_agents(
        self, capabilities_needed: list[str] | None = None
    ) -> list[Agent]:
        """Discover available agents via Agent Gateway.

        Args:
            capabilities_needed: Optional list of capabilities (e.g., ["sms", "email"])

        Returns:
            List of available agents
        """
        try:
            # Create LAM discovery message
            payload = {}
            if capabilities_needed:
                payload["capabilities_needed"] = capabilities_needed

            lam_message = self._create_lam_message("discovery", payload)

            logger.info(
                f"Sending discovery request"
                + (f" for capabilities: {capabilities_needed}" if capabilities_needed else "")
            )

            # Send to Agent Gateway
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.gateway_url,
                    headers=self.headers,
                    json=lam_message,
                )
                response.raise_for_status()

                data = response.json()
                agents = []

                # Parse response
                # Expected format: LAM offer message with available_agents
                agents_data = []

                if data.get("message_type") == "offer":
                    # LAM offer response
                    agents_data = data.get("payload", {}).get("available_agents", [])
                elif data.get("message_type") == "inform":
                    # LAM inform response
                    agents_data = data.get("payload", {}).get("agents", [])
                else:
                    # Fallback: try direct agents array
                    agents_data = data.get("agents", [])

                for agent_data in agents_data:
                    # Parse capabilities
                    capabilities = []
                    caps_raw = agent_data.get("capabilities", "")

                    # Capabilities can be a string or array
                    if isinstance(caps_raw, str):
                        # Single capability as string description
                        # Try to extract capability name from description
                        cap_name = "unknown"
                        if "sms" in caps_raw.lower():
                            cap_name = "sms"
                        elif "email" in caps_raw.lower():
                            cap_name = "email"
                        elif "orchestrat" in caps_raw.lower():
                            cap_name = "orchestration"

                        capabilities.append(
                            AgentCapability(
                                name=cap_name,
                                description=caps_raw,
                                parameters={},
                                version="1.0.0",
                            )
                        )
                    elif isinstance(caps_raw, list):
                        # Array of capability names
                        for cap_name in caps_raw:
                            capabilities.append(
                                AgentCapability(
                                    name=cap_name,
                                    description="",
                                    parameters={},
                                    version="1.0.0",
                                )
                            )

                    # Create agent
                    agent = Agent(
                        id=agent_data.get("agent_key", agent_data.get("id", agent_data.get("agent_id", ""))),
                        name=agent_data.get("agent_name", agent_data.get("name", "")),
                        description=agent_data.get("capabilities", ""),
                        capabilities=capabilities,
                        endpoint=agent_data.get("endpoint", ""),
                        status=agent_data.get("status", "available"),
                        metadata=agent_data.get("metadata", {}),
                    )
                    agents.append(agent)

                logger.info(f"Discovered {len(agents)} agents")
                return agents

        except httpx.HTTPError as e:
            logger.error(f"HTTP error discovering agents: {e}")
            return []
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            return []

    async def find_agent_by_capability(
        self, capability: str
    ) -> Agent | None:
        """Find the best agent for a specific capability.

        Args:
            capability: Capability name (e.g., "sms", "email")

        Returns:
            Best matching agent or None
        """
        agents = await self.discover_agents(capabilities_needed=[capability])

        if not agents:
            logger.warning(f"No agents found with capability: {capability}")
            return None

        # Filter agents that have the requested capability
        matching_agents = []
        for agent in agents:
            if agent.has_capability(capability):
                matching_agents.append(agent)

        if matching_agents:
            # Return first matching available agent
            for agent in matching_agents:
                if agent.status == "available":
                    logger.info(
                        f"Selected agent '{agent.name}' for capability '{capability}'"
                    )
                    return agent

            # Fallback to first matching agent
            logger.warning(
                f"No available matching agents, using first: {matching_agents[0].name}"
            )
            return matching_agents[0]

        # No exact match, return first available agent
        logger.warning(f"No exact match for capability '{capability}', using first available agent")
        for agent in agents:
            if agent.status == "available":
                logger.info(
                    f"Selected agent '{agent.name}' for capability '{capability}'"
                )
                return agent

        # Fallback to first agent
        logger.warning(
            f"No available agents, using first agent: {agents[0].name}"
        )
        return agents[0]

    async def send_request(
        self, agent: Agent, request: AgentRequest
    ) -> AgentResponse:
        """Send a request to an agent via Agent Gateway.

        Args:
            agent: Target agent
            request: Request to send

        Returns:
            Agent response
        """
        try:
            # Create LAM request message
            # Use receiver field instead of to array
            lam_message = {
                "message_id": str(uuid.uuid4()),
                "message_type": "request",
                "sender": self.sender_id,
                "receiver": agent.id,  # Direct agent ID, not agent://
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": request.parameters,  # Send parameters directly
            }

            logger.info(f"Sending request to agent '{agent.name}' (capability: {request.capability})")
            logger.debug(f"agent message: {lam_message}")

            # Send via Agent Gateway
            async with httpx.AsyncClient(timeout=request.timeout) as client:
                response = await client.post(
                    self.gateway_url,
                    headers=self.headers,
                    json=lam_message,
                )
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response body: {response.text}")
                response.raise_for_status()

                data = response.json()

                # Parse LAM response
                if data.get("message_type") == "inform":
                    return AgentResponse(
                        success=True,
                        data=data.get("payload", {}),
                        agent_id=agent.id,
                    )
                elif data.get("message_type") == "failure":
                    return AgentResponse(
                        success=False,
                        error=data.get("payload", {}).get("reason", "Unknown error"),
                        agent_id=agent.id,
                    )
                else:
                    # Fallback: treat as success if no error
                    return AgentResponse(
                        success=data.get("success", True),
                        data=data.get("payload", data),
                        error=data.get("error"),
                        agent_id=agent.id,
                    )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending request to agent: {e}")
            return AgentResponse(
                success=False,
                error=f"HTTP error: {str(e)}",
                agent_id=agent.id,
            )
        except Exception as e:
            logger.error(f"Error sending request to agent: {e}")
            return AgentResponse(
                success=False, error=str(e), agent_id=agent.id
            )

    async def send_sms(
        self, phone_number: str, message: str
    ) -> AgentResponse:
        """Send SMS via SMS agent.

        Args:
            phone_number: Phone number to send to
            message: Message content

        Returns:
            Agent response
        """
        # Find SMS agent
        agent = await self.find_agent_by_capability("sms")
        if not agent:
            return AgentResponse(
                success=False, error="No SMS agent available"
            )

        # Create request with correct parameter names
        request = AgentRequest(
            capability="sms",
            parameters={
                "recipient_number": phone_number,  # Use recipient_number
                "message_text": message,  # Use message_text
            },
            priority="high",
        )

        # Send request
        return await self.send_request(agent, request)

    async def send_email(
        self, to: str, subject: str, body: str
    ) -> AgentResponse:
        """Send email via email agent.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            Agent response
        """
        # Find email agent
        agent = await self.find_agent_by_capability("email")
        if not agent:
            return AgentResponse(
                success=False, error="No email agent available"
            )

        # Create request
        request = AgentRequest(
            capability="email",
            parameters={"to": to, "subject": subject, "body": body},
            priority="normal",
        )

        # Send request
        return await self.send_request(agent, request)

