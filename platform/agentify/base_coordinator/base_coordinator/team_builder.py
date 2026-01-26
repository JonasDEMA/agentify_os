"""Team building implementation."""

from typing import Any

from .marketplace import MarketplaceDiscovery
from .models import Agent, Team


class TeamBuilder:
    """Handles team building."""

    def __init__(self, app_id: str, marketplace: MarketplaceDiscovery):
        self.app_id = app_id
        self.marketplace = marketplace
        self.current_team: Team | None = None

    async def discover_and_build_team(
        self,
        required_capabilities: list[str],
        min_rating: float = 0.0,
        max_price: float = float("inf"),
    ) -> Team:
        """Discover agents and build a team.

        Args:
            required_capabilities: List of required capabilities
            min_rating: Minimum rating for agents
            max_price: Maximum price per agent

        Returns:
            Proposed team
        """
        print(f"\n🔍 Building team for capabilities: {required_capabilities}")

        # Discover agents for each capability
        all_agents: list[Agent] = []
        for capability in required_capabilities:
            agents = await self.marketplace.discover_agents(
                capability=capability,
                min_rating=min_rating,
                max_price=max_price,
            )

            if not agents:
                print(f"⚠️  No agents found for capability: {capability}")
                continue

            # Pick best agent (highest rating)
            best_agent = max(agents, key=lambda a: a.rating)
            all_agents.append(best_agent)
            print(f"  ✅ Selected: {best_agent.name} (rating: {best_agent.rating})")

        # Create team
        team = Team(
            app_id=self.app_id,
            agents=all_agents,
            confirmed=False,
        )

        self.current_team = team
        return team

    def confirm_team(self, team: Team) -> None:
        """Confirm a team.

        Args:
            team: Team to confirm
        """
        team.confirmed = True
        self.current_team = team
        print(f"✅ Team confirmed with {len(team.agents)} agents")

    async def deploy_team(
        self,
        team: Team,
        customer_id: str,
        co_locate: bool = True,
    ) -> dict[str, str]:
        """Deploy team agents.

        Args:
            team: Team to deploy
            customer_id: Customer ID
            co_locate: Whether to co-locate agents

        Returns:
            Dict mapping agent_id to address
        """
        print(f"\n🚀 Deploying team...")

        addresses: dict[str, str] = {}

        for agent in team.agents:
            print(f"  📦 Deploying {agent.name}...")

            # Request deployment via marketplace
            address = await self.marketplace.deploy_agent(
                agent_id=agent.agent_id,
                customer_id=customer_id,
                co_locate=co_locate,
                co_locate_with=self.app_id if co_locate else None,
            )

            if address:
                addresses[agent.agent_id] = address
                print(f"    ✅ Deployed at {address}")
            else:
                print(f"    ❌ Deployment failed")

        return addresses

    def get_agent_by_capability(self, capability: str) -> Agent | None:
        """Get agent from team by capability.

        Args:
            capability: Required capability

        Returns:
            Agent or None
        """
        if not self.current_team or not self.current_team.confirmed:
            return None

        for agent in self.current_team.agents:
            if capability in agent.capabilities:
                return agent

        return None

    def get_team(self) -> Team | None:
        """Get current team.

        Returns:
            Current team or None
        """
        return self.current_team

