"""Learning Loop - Orchestrates the cognitive RPA cycle of execution and learning."""
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from agents.desktop_rpa.cognitive.experience_memory import Experience, ExperienceMemory
from agents.desktop_rpa.cognitive.strategy_manager import Strategy, StrategyManager
from agents.desktop_rpa.cognitive.state_graph import StateGraph
from agents.desktop_rpa.cognitive.llm_wrapper import LLMWrapper
from agents.desktop_rpa.vision.state_detector import StateDetector
from agents.desktop_rpa.planner.goal_planner import GoalPlanner

logger = logging.getLogger(__name__)

class LearningLoop:
    """The main control loop for the Cognitive RPA agent."""

    def __init__(
        self,
        llm_wrapper: LLMWrapper,
        state_detector: StateDetector,
        strategy_manager: StrategyManager,
        experience_memory: ExperienceMemory,
        goal_planner: GoalPlanner
    ):
        """Initialize the Learning Loop.

        Args:
            llm_wrapper: LLM interface
            state_detector: Component to identify current state
            strategy_manager: Component to manage playbooks
            experience_memory: Component to store execution history
            goal_planner: Component to decompose goals
        """
        self.llm = llm_wrapper
        self.state_detector = state_detector
        self.strategy_manager = strategy_manager
        self.experience_memory = experience_memory
        self.goal_planner = goal_planner

    async def run_goal(self, goal: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Execute a high-level goal and learn from the experience.

        Args:
            goal: The high-level goal to achieve
            context: Additional context for execution

        Returns:
            True if goal was achieved, False otherwise
        """
        logger.info(f"Starting cognitive loop for goal: {goal}")
        start_time = time.time()
        
        # 1. Detect initial state
        initial_state = self.state_detector.detect_state(None) # Image would be passed here
        
        # 2. Get execution plan
        plan = await self.goal_planner.plan_execution(goal, context=context)
        
        # 3. Execute actions (simplified for now)
        actions_taken = []
        success = True
        error_msg = None
        
        try:
            for step in plan.steps:
                logger.info(f"Executing step: {step.get('description', 'Unknown action')}")
                # In real implementation, we would call executors here
                actions_taken.append(step)
                # Simulate success
                time.sleep(0.5) 
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            success = False
            error_msg = str(e)

        # 4. Detect final state
        final_state = self.state_detector.detect_state(None) # Image would be passed here
        
        # 5. Record experience
        duration = time.time() - start_time
        experience = Experience(
            experience_id=str(uuid4()),
            goal=goal,
            initial_state=initial_state,
            final_state=final_state,
            actions_taken=actions_taken,
            success=success,
            duration=duration,
            strategy_id=plan.strategy_id,
            metadata={"error": error_msg} if error_msg else {}
        )
        self.experience_memory.save_experience(experience)

        # 6. Learn / Update strategy
        if success and not plan.strategy_id:
            # If we used an LLM-generated plan and it worked, save it as a new strategy
            new_strategy = Strategy(
                strategy_id=str(uuid4()),
                name=f"Strategy for {goal}",
                description=plan.reasoning or "",
                goal=goal,
                steps=actions_taken,
                success_count=1,
                learned_from="llm"
            )
            self.strategy_manager.save_strategy(new_strategy)
        elif plan.strategy_id:
            # Update existing strategy success/failure count
            strategy = self.strategy_manager.get_strategy(plan.strategy_id)
            if strategy:
                if success:
                    strategy.success_count += 1
                else:
                    strategy.failure_count += 1
                # Update average duration
                strategy.average_duration = (strategy.average_duration + duration) / 2
                self.strategy_manager.save_strategy(strategy)

        return success
