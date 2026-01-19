"""LLM-based Task Planner - Decomposes intents into detailed TaskGraphs."""
import logging
from typing import Any, Dict, Optional

from scheduler.core.task_graph import TaskGraph
from scheduler.llm.llm_wrapper import LLMWrapper

logger = logging.getLogger(__name__)

class LLMTaskPlanner:
    """Planner that uses an LLM to generate a structured TaskGraph from user requests."""

    def __init__(self, llm_wrapper: LLMWrapper):
        """Initialize LLM task planner.

        Args:
            llm_wrapper: LLM wrapper instance
        """
        self.llm_wrapper = llm_wrapper

    async def plan(self, intent: str, description: str, context: Optional[Dict[str, Any]] = None) -> TaskGraph:
        """Generate a TaskGraph for a given intent and description.

        Args:
            intent: User intent
            description: User request description
            context: Additional context (e.g., historical data, user preferences)

        Returns:
            Generated TaskGraph
        """
        logger.info(f"Planning task graph for intent: {intent}")
        
        # We delegate the core logic to the LLMWrapper's specialized method
        # but we could add more logic here later (e.g., validation, multi-step planning)
        try:
            # Enrich prompt with context if available
            context_str = f"\nContext: {context}" if context else ""
            
            # For now, we just call the wrapper
            return await self.llm_wrapper.intent_to_task_graph(intent, description + context_str)
            
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            # Return empty task graph as fallback
            return TaskGraph()
