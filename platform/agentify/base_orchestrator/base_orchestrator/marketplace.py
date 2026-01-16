"""Marketplace discovery implementation."""

import asyncio
from typing import Any

from .agent_protocol import AgentProtocol
from .models import Agent, MessageType


class MarketplaceDiscovery:
    """Handles marketplace discovery."""

    def __init__(self, orchestrator_id: str, marketplace_url: str):
        self.orchestrator_id = orchestrator_id
        self.marketplace_url = marketplace_url
        self.protocol = AgentProtocol(sender_id=orchestrator_id)

    async def discover_agents(
        self,
        capability: str,
        min_rating: float = 0.0,
        max_price: float = float("inf"),
    ) -> list[Agent]:
        """Discover agents by capability.

        Args:
            capability: Required capability
            min_rating: Minimum rating
            max_price: Maximum price

        Returns:
            List of discovered agents
        """
        print(f"🔍 Searching marketplace for '{capability}' agents...")

        try:
            # Send discover message to marketplace
            response = await self.protocol.discover(
                marketplace_address=self.marketplace_url,
                capability=capability,
                min_rating=min_rating,
                max_price=max_price,
            )

            # Parse agents from response
            agents_data = response.payload.get("agents", [])
            agents = [Agent(**agent_data) for agent_data in agents_data]

            print(f"✅ Found {len(agents)} agents")
            return agents

        except Exception as e:
            print(f"❌ Marketplace discovery failed: {e}")
            # Return mock agents for local testing
            return self._get_mock_agents(capability)

    def _get_mock_agents(self, capability: str) -> list[Agent]:
        """Get mock agents for local testing.

        Args:
            capability: Required capability

        Returns:
            List of mock agents
        """
        mock_agents = {
            "calculation": [
                Agent(
                    agent_id="agent.calculator.calculation",
                    name="Calculation Agent",
                    description="Performs mathematical calculations",
                    capabilities=["calculation"],
                    rating=9.5,
                    price=0.001,
                    address="http://localhost:8000",
                    status="available",
                )
            ],
            "formatting": [
                Agent(
                    agent_id="agent.calculator.formatting",
                    name="Formatting Agent",
                    description="Formats numbers for display",
                    capabilities=["formatting"],
                    rating=9.0,
                    price=0.0005,
                    address="http://localhost:8001",
                    status="available",
                )
            ],
        }

        agents = mock_agents.get(capability, [])
        print(f"⚠️  Using mock agents (marketplace not available)")
        return agents

    async def get_agent_address(
        self,
        agent_id: str,
        customer_id: str = "local-customer",
    ) -> str | None:
        """Get agent address from marketplace/hosting.

        Args:
            agent_id: Agent ID
            customer_id: Customer ID

        Returns:
            Agent address or None
        """
        try:
            # In real implementation, this would query marketplace
            # which would query hosting agent for the address
            # For now, return mock addresses
            mock_addresses = {
                "agent.calculator.calculation": "http://localhost:8000",
                "agent.calculator.formatting": "http://localhost:8001",
            }
            return mock_addresses.get(agent_id)

        except Exception as e:
            print(f"❌ Failed to get agent address: {e}")
            return None

    async def deploy_agent(
        self,
        agent_id: str,
        customer_id: str,
        co_locate: bool = False,
        co_locate_with: str | None = None,
    ) -> str | None:
        """Deploy an agent via marketplace.

        Args:
            agent_id: Agent ID to deploy
            customer_id: Customer ID
            co_locate: Whether to co-locate with another agent
            co_locate_with: Agent ID to co-locate with

        Returns:
            Agent address or None
        """
        try:
            # Send deploy message to marketplace
            response = await self.protocol.send_message(
                agent_address=self.marketplace_url,
                message_type=MessageType.REQUEST,
                intent="deploy_agent",
                payload={
                    "agent_id": agent_id,
                    "customer_id": customer_id,
                    "co_location": {
                        "required": co_locate,
                        "with_agent": co_locate_with,
                        "reason": "low_latency_required" if co_locate else None,
                    },
                },
            )

            # Extract address from response
            address = response.payload.get("address")
            return address

        except Exception as e:
            print(f"❌ Failed to deploy agent: {e}")
            # Return mock address for local testing
            return await self.get_agent_address(agent_id, customer_id)

    async def close(self):
        """Close connections."""
        await self.protocol.close()

