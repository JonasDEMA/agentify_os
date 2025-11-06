"""Agent Registry - Persistent storage for known agents.

This module provides:
- Persistent storage of known agents
- Caching of agent information
- Fallback handling when agents are unavailable
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.desktop_rpa.agent_comm.models import Agent, AgentCapability

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manages persistent storage of known agents."""

    def __init__(self, registry_path: str | Path = "data/agent_registry.json"):
        """Initialize Agent Registry.

        Args:
            registry_path: Path to registry file
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.agents: dict[str, Agent] = {}
        self.capability_map: dict[str, list[str]] = {}  # capability -> agent_ids

        # Load existing registry
        self._load_registry()

        logger.info(f"Agent Registry initialized (path={registry_path})")

    def _load_registry(self):
        """Load registry from file."""
        if not self.registry_path.exists():
            logger.info("No existing registry found, starting fresh")
            return

        try:
            with open(self.registry_path, "r") as f:
                data = json.load(f)

            # Parse agents
            for agent_data in data.get("agents", []):
                # Parse capabilities
                capabilities = []
                for cap_data in agent_data.get("capabilities", []):
                    capabilities.append(
                        AgentCapability(
                            name=cap_data.get("name", ""),
                            description=cap_data.get("description", ""),
                            parameters=cap_data.get("parameters", {}),
                            version=cap_data.get("version", "1.0.0"),
                        )
                    )

                # Create agent
                agent = Agent(
                    id=agent_data.get("id", ""),
                    name=agent_data.get("name", ""),
                    description=agent_data.get("description", ""),
                    capabilities=capabilities,
                    endpoint=agent_data.get("endpoint", ""),
                    status=agent_data.get("status", "available"),
                    metadata=agent_data.get("metadata", {}),
                )

                self.agents[agent.id] = agent

                # Update capability map
                for cap in agent.capabilities:
                    if cap.name not in self.capability_map:
                        self.capability_map[cap.name] = []
                    self.capability_map[cap.name].append(agent.id)

            logger.info(f"Loaded {len(self.agents)} agents from registry")

        except Exception as e:
            logger.error(f"Error loading registry: {e}")

    def _save_registry(self):
        """Save registry to file."""
        try:
            # Convert agents to dict
            agents_data = []
            for agent in self.agents.values():
                capabilities_data = []
                for cap in agent.capabilities:
                    capabilities_data.append(
                        {
                            "name": cap.name,
                            "description": cap.description,
                            "parameters": cap.parameters,
                            "version": cap.version,
                        }
                    )

                agents_data.append(
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "description": agent.description,
                        "capabilities": capabilities_data,
                        "endpoint": agent.endpoint,
                        "status": agent.status,
                        "metadata": agent.metadata,
                    }
                )

            data = {"agents": agents_data, "updated_at": datetime.now().isoformat()}

            with open(self.registry_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.agents)} agents to registry")

        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def register_agent(self, agent: Agent):
        """Register an agent.

        Args:
            agent: Agent to register
        """
        self.agents[agent.id] = agent

        # Update capability map
        for cap in agent.capabilities:
            if cap.name not in self.capability_map:
                self.capability_map[cap.name] = []
            if agent.id not in self.capability_map[cap.name]:
                self.capability_map[cap.name].append(agent.id)

        # Save to file
        self._save_registry()

        logger.info(f"Registered agent: {agent.name} (id={agent.id})")

    def get_agent(self, agent_id: str) -> Agent | None:
        """Get an agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent if found, None otherwise
        """
        return self.agents.get(agent_id)

    def get_agents_by_capability(self, capability: str) -> list[Agent]:
        """Get all agents with a specific capability.

        Args:
            capability: Capability name

        Returns:
            List of agents with the capability
        """
        agent_ids = self.capability_map.get(capability, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_preferred_agent(self, capability: str) -> Agent | None:
        """Get the preferred agent for a capability.

        Args:
            capability: Capability name

        Returns:
            Preferred agent or None
        """
        agents = self.get_agents_by_capability(capability)

        if not agents:
            return None

        # Return first available agent
        for agent in agents:
            if agent.status == "available":
                return agent

        # Fallback to first agent
        return agents[0]

    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status.

        Args:
            agent_id: Agent ID
            status: New status (available, busy, offline)
        """
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].last_seen = datetime.now()
            self._save_registry()
            logger.info(f"Updated agent {agent_id} status to: {status}")

    def remove_agent(self, agent_id: str):
        """Remove an agent from registry.

        Args:
            agent_id: Agent ID to remove
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]

            # Remove from capability map
            for cap in agent.capabilities:
                if cap.name in self.capability_map:
                    self.capability_map[cap.name] = [
                        aid
                        for aid in self.capability_map[cap.name]
                        if aid != agent_id
                    ]

            # Remove agent
            del self.agents[agent_id]
            self._save_registry()

            logger.info(f"Removed agent: {agent_id}")

    def get_summary(self) -> dict[str, Any]:
        """Get registry summary.

        Returns:
            Dictionary with registry statistics
        """
        return {
            "total_agents": len(self.agents),
            "capabilities": list(self.capability_map.keys()),
            "available_agents": sum(
                1 for a in self.agents.values() if a.status == "available"
            ),
            "agents": [
                {"id": a.id, "name": a.name, "status": a.status}
                for a in self.agents.values()
            ],
        }

