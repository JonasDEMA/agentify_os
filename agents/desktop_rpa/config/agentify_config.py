"""Agentify configuration for agent communication."""

import os
from dataclasses import dataclass


@dataclass
class AgentifyConfig:
    """Configuration for Agentify Agent Gateway."""

    # Agent Gateway endpoint
    gateway_url: str = "https://agentify.dev/api/v1/agent-gateway"

    # API Token for authentication
    api_token: str = "e8f76097709ad01c5d563d6ab1f1a21cdb26a5bb085ec3a4d49c33827224e164"

    # Sender ID for agent messages
    sender_id: str = "cpa_agent"

    # Request timeout in seconds
    timeout: int = 30

    # Enable/disable Agentify integration
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "AgentifyConfig":
        """Create config from environment variables.

        Environment variables:
            AGENTIFY_GATEWAY_URL: Agent Gateway URL
            AGENTIFY_API_TOKEN: API token
            AGENTIFY_SENDER_ID: Sender ID
            AGENTIFY_TIMEOUT: Request timeout
            AGENTIFY_ENABLED: Enable/disable integration

        Returns:
            AgentifyConfig instance
        """
        return cls(
            gateway_url=os.getenv(
                "AGENTIFY_GATEWAY_URL",
                "https://agentify.dev/api/v1/agent-gateway",
            ),
            api_token=os.getenv(
                "AGENTIFY_API_TOKEN",
                "e8f76097709ad01c5d563d6ab1f1a21cdb26a5bb085ec3a4d49c33827224e164",
            ),
            sender_id=os.getenv("AGENTIFY_SENDER_ID", "cpa_agent"),
            timeout=int(os.getenv("AGENTIFY_TIMEOUT", "30")),
            enabled=os.getenv("AGENTIFY_ENABLED", "true").lower() == "true",
        )


# Global config instance
agentify_config = AgentifyConfig.from_env()

