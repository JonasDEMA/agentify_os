"""Cognitive layer for Desktop RPA Agent."""

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor
from agents.desktop_rpa.cognitive.llm_wrapper import LLMWrapper
from agents.desktop_rpa.cognitive.models import (
    ActionSuggestion,
    LLMRequest,
    LLMResponse,
    StrategyRequest,
    StrategyResponse,
)

__all__ = [
    "CognitiveExecutor",
    "LLMWrapper",
    "LLMRequest",
    "LLMResponse",
    "ActionSuggestion",
    "StrategyRequest",
    "StrategyResponse",
]

