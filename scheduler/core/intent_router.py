"""Intent Router for rule-based intent classification.

Routes user messages to intents based on regex patterns.
"""

import re
from typing import Any

from pydantic import BaseModel, Field


class Intent(BaseModel):
    """Intent definition model."""

    name: str = Field(..., description="Intent name")
    patterns: list[str] = Field(..., description="Regex patterns for matching")
    description: str = Field(..., description="Intent description")


class IntentRouter:
    """Intent router for rule-based intent classification.

    Routes user messages to intents based on regex pattern matching.
    """

    def __init__(self) -> None:
        """Initialize intent router."""
        self.intents: dict[str, Intent] = {}

    def register_intent(self, intent: Intent) -> None:
        """Register an intent.

        Args:
            intent: Intent to register
        """
        self.intents[intent.name] = intent

    def get_intent(self, name: str) -> Intent | None:
        """Get an intent by name.

        Args:
            name: Intent name

        Returns:
            Intent or None if not found
        """
        return self.intents.get(name)

    def route(self, message: str) -> str:
        """Route a message to an intent.

        Args:
            message: User message

        Returns:
            Intent name or "unknown" if no match
        """
        if not message:
            return "unknown"

        # Normalize message (lowercase)
        normalized_message = message.lower()

        # Try to match against all registered intents
        for intent in self.intents.values():
            for pattern in intent.patterns:
                # Compile regex pattern (case insensitive)
                try:
                    regex = re.compile(pattern, re.IGNORECASE)
                    if regex.search(normalized_message):
                        return intent.name
                except re.error:
                    # If regex compilation fails, try exact match
                    if pattern.lower() in normalized_message:
                        return intent.name

        # No match found
        return "unknown"

    def load_from_dict(self, intents_data: list[dict[str, Any]]) -> None:
        """Load intents from dictionary.

        Args:
            intents_data: List of intent dictionaries
        """
        for intent_dict in intents_data:
            intent = Intent(**intent_dict)
            self.register_intent(intent)

