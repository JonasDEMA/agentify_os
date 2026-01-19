"""LuminaOS configuration for agent communication."""

import os
from dataclasses import dataclass


@dataclass
class LuminaOSConfig:
    """Configuration for LuminaOS LAM Gateway."""

    # LAM Gateway endpoint
    gateway_url: str = "https://luminaos-three.vercel.app/api/v1/lam-gateway"

    # API Token for authentication
    api_token: str = "e8f76097709ad01c5d563d6ab1f1a21cdb26a5bb085ec3a4d49c33827224e164"

    # Sender ID for LAM messages
    sender_id: str = "cpa_agent"

    # Request timeout in seconds
    timeout: int = 30

    # Enable/disable LuminaOS integration
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "LuminaOSConfig":
        """Create config from environment variables.

        Environment variables:
            LUMINAOS_GATEWAY_URL: LAM Gateway URL
            LUMINAOS_API_TOKEN: API token
            LUMINAOS_SENDER_ID: Sender ID
            LUMINAOS_TIMEOUT: Request timeout
            LUMINAOS_ENABLED: Enable/disable integration

        Returns:
            LuminaOSConfig instance
        """
        return cls(
            gateway_url=os.getenv(
                "LUMINAOS_GATEWAY_URL",
                "https://luminaos-three.vercel.app/api/v1/lam-gateway",
            ),
            api_token=os.getenv(
                "LUMINAOS_API_TOKEN",
                "e8f76097709ad01c5d563d6ab1f1a21cdb26a5bb085ec3a4d49c33827224e164",
            ),
            sender_id=os.getenv("LUMINAOS_SENDER_ID", "cpa_agent"),
            timeout=int(os.getenv("LUMINAOS_TIMEOUT", "30")),
            enabled=os.getenv("LUMINAOS_ENABLED", "true").lower() == "true",
        )


# Global config instance
luminaos_config = LuminaOSConfig.from_env()

