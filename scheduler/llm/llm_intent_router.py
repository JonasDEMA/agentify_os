"""LLM-based Intent Router - Enhances rule-based routing with LLM classification."""
import logging
from typing import Optional, List

from pydantic import BaseModel, Field
from scheduler.core.intent_router import IntentRouter, Intent
from scheduler.llm.llm_wrapper import LLMWrapper

logger = logging.getLogger(__name__)

class IntentClassification(BaseModel):
    """Model for LLM intent classification response."""
    intent: str = Field(..., description="The classified intent name")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Reasoning for this classification")

class LLMIntentRouter:
    """Intent router that uses an LLM for classification with a rule-based fallback."""

    def __init__(self, llm_wrapper: LLMWrapper, fallback_router: Optional[IntentRouter] = None):
        """Initialize LLM intent router.

        Args:
            llm_wrapper: LLM wrapper instance
            fallback_router: Optional rule-based router for fallback
        """
        self.llm_wrapper = llm_wrapper
        self.fallback_router = fallback_router

    async def route(self, message: str) -> str:
        """Route a message to an intent using LLM and optional fallback.

        Args:
            message: User message

        Returns:
            Intent name or "unknown"
        """
        if not message:
            return "unknown"

        # 1. Try LLM classification
        try:
            # Get list of known intents for the prompt if fallback_router is available
            known_intents = []
            if self.fallback_router:
                known_intents = list(self.fallback_router.intents.keys())
            
            intents_str = ", ".join(known_intents) if known_intents else "any appropriate intent"
            
            system_prompt = f"""You are an Intent Classifier for a Cognitive Process Automation system.
            Your goal is to classify the user's message into one of the following known intents: {intents_str}.
            If the message doesn't fit any known intent, you can suggest a new appropriate intent name or return 'unknown'.
            Provide a confidence score and your reasoning.
            """
            
            result = await self.llm_wrapper.generate_structured(
                prompt=f"Message to classify: {message}",
                response_model=IntentClassification,
                system_prompt=system_prompt
            )
            
            if result.confidence > 0.6:
                logger.info(f"LLM classified intent: {result.intent} (conf: {result.confidence})")
                return result.intent
                
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")

        # 2. Fallback to rule-based routing
        if self.fallback_router:
            logger.info("Falling back to rule-based intent router")
            return self.fallback_router.route(message)

        return "unknown"
