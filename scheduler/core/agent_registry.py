"""Agent Registry - Manages available agents and their capabilities."""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Agent(BaseModel):
    """Agent model."""

    name: str = Field(..., description="Agent name")
    endpoint: str = Field(..., description="Agent HTTP endpoint")
    capabilities: list[str] = Field(default_factory=list, description="Agent capabilities")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentRegistry:
    """Registry for managing agents."""

    def __init__(self, config_path: str | Path | None = None):
        """Initialize agent registry.

        Args:
            config_path: Path to agents.yaml config file
        """
        self.agents: list[Agent] = []
        self.config_path = config_path

        if config_path:
            self.load_agents(config_path)

    def load_agents(self, config_path: str | Path) -> None:
        """Load agents from YAML configuration.

        Args:
            config_path: Path to agents.yaml file
        """
        config_path = Path(config_path)

        if not config_path.exists():
            logger.warning(f"Agent config file not found: {config_path}")
            return

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)

            if not config or "agents" not in config:
                logger.warning(f"No agents found in config: {config_path}")
                return

            self.agents = [Agent(**agent_data) for agent_data in config["agents"]]
            logger.info(f"Loaded {len(self.agents)} agents from {config_path}")

        except Exception as e:
            logger.error(f"Failed to load agents from {config_path}: {e}", exc_info=True)
            raise

    def get_agent_by_name(self, name: str) -> Agent | None:
        """Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent if found, None otherwise
        """
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_agent_by_capability(self, capability: str) -> Agent | None:
        """Get first agent with specified capability.

        Args:
            capability: Capability name

        Returns:
            Agent if found, None otherwise
        """
        for agent in self.agents:
            if capability in agent.capabilities:
                return agent
        return None

    def get_agents_by_capability(self, capability: str) -> list[Agent]:
        """Get all agents with specified capability.

        Args:
            capability: Capability name

        Returns:
            List of agents with the capability
        """
        return [agent for agent in self.agents if capability in agent.capabilities]

    def register_agent(self, agent: Agent) -> None:
        """Register a new agent.

        Args:
            agent: Agent to register
        """
        # Remove existing agent with same name
        self.agents = [a for a in self.agents if a.name != agent.name]
        self.agents.append(agent)
        logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, name: str) -> bool:
        """Unregister an agent.

        Args:
            name: Agent name

        Returns:
            True if agent was removed, False if not found
        """
        original_count = len(self.agents)
        self.agents = [a for a in self.agents if a.name != name]

        if len(self.agents) < original_count:
            logger.info(f"Unregistered agent: {name}")
            return True

        return False

    def list_agents(self) -> list[Agent]:
        """List all registered agents.

        Returns:
            List of all agents
        """
        return self.agents.copy()

