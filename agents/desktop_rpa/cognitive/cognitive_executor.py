"""Cognitive Executor - LLM-guided task execution."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pyautogui

from agents.desktop_rpa.cognitive.llm_wrapper import LLMWrapper
from agents.desktop_rpa.cognitive.models import LLMRequest
from agents.desktop_rpa.config.settings import settings

logger = logging.getLogger(__name__)


class CognitiveExecutor:
    """Executor that uses LLM to guide task execution.

    This executor:
    1. Receives a high-level goal
    2. Takes screenshots to understand current state
    3. Asks LLM for next action
    4. Executes the suggested action
    5. Repeats until goal is achieved
    """

    def __init__(self, llm_wrapper: LLMWrapper | None = None, callback=None):
        """Initialize cognitive executor.

        Args:
            llm_wrapper: LLM wrapper instance (creates new one if None)
            callback: Optional callback function for UI updates (receives event dict)
        """
        self.llm = llm_wrapper or LLMWrapper()
        self.screenshot_dir = Path(settings.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.callback = callback

        # Execution state
        self.current_state = "unknown"
        self.current_step = 0
        self.previous_actions: list[dict[str, Any]] = []
        self.obstacles: list[dict[str, Any]] = []
        self.max_steps = 20  # Prevent infinite loops

        logger.info("Cognitive Executor initialized")

    async def execute(self, todo: dict[str, Any]) -> dict[str, Any]:
        """Execute a task using LLM guidance.
        
        Args:
            todo: Task to execute with 'goal' field
            
        Returns:
            Execution result
        """
        goal = todo.get("goal")
        if not goal:
            raise ValueError("Task must have 'goal' field")
        
        logger.info(f"Starting cognitive execution: goal='{goal}'")
        print(f"\n🤖 Starting cognitive execution...")
        print(f"🎯 Goal: {goal}\n")

        # Notify UI
        self._notify("start", {"goal": goal})

        # Reset state
        self.current_state = "desktop_visible"
        self.previous_actions = []
        self.obstacles = []

        # Execution loop
        for step in range(1, self.max_steps + 1):
            self.current_step = step
            logger.info(f"Step {step}/{self.max_steps}: state={self.current_state}")

            print(f"\n{'─' * 60}")
            print(f"📍 Step {step}/{self.max_steps}")
            print(f"🔍 Current state: {self.current_state}")

            # Notify UI
            self._notify("step", {"step": step, "max_steps": self.max_steps, "state": self.current_state})
            
            try:
                # Take screenshot
                screenshot_path = await self._take_screenshot(f"step_{step}")
                screenshot_base64 = LLMWrapper.encode_screenshot(screenshot_path)
                print(f"📸 Screenshot taken: {screenshot_path.name}")
                self._notify("screenshot", {"path": str(screenshot_path)})

                # Ask LLM for next action
                request = LLMRequest(
                    goal=goal,
                    current_state=self.current_state,
                    screenshot_base64=screenshot_base64,
                    context={
                        "step": step,
                        "max_steps": self.max_steps,
                    },
                    previous_actions=self.previous_actions[-5:],  # Last 5 actions
                    obstacles=self.obstacles,
                )

                print(f"🧠 Asking LLM for next action...")
                self._notify("thinking", {"message": "Analyzing screenshot and deciding next action..."})
                response = await self.llm.ask_for_next_action(request)

                logger.info(
                    f"LLM suggested: {response.suggestion.action_type} "
                    f"(confidence={response.suggestion.confidence:.2f})"
                )
                logger.info(f"Reasoning: {response.suggestion.reasoning}")

                confidence_emoji = "🟢" if response.suggestion.confidence >= 0.8 else "🟡" if response.suggestion.confidence >= 0.6 else "🔴"
                print(f"{confidence_emoji} LLM suggests: {response.suggestion.action_type.upper()}")
                print(f"   💭 Reasoning: {response.suggestion.reasoning}")
                print(f"   📊 Confidence: {response.suggestion.confidence:.2f}")
                if response.suggestion.selector:
                    print(f"   🎯 Selector: {response.suggestion.selector}")
                if response.suggestion.value:
                    print(f"   ✍️  Value: {response.suggestion.value}")

                # Notify UI
                self._notify("action_suggested", {
                    "action": response.suggestion.action_type,
                    "reasoning": response.suggestion.reasoning,
                    "confidence": response.suggestion.confidence,
                    "selector": response.suggestion.selector,
                    "value": response.suggestion.value,
                })
                
                # Check for warnings
                if response.warnings:
                    for warning in response.warnings:
                        logger.warning(f"LLM Warning: {warning}")
                        print(f"⚠️  Warning: {warning}")

                # Execute suggested action
                print(f"⚙️  Executing action...")
                self._notify("executing", {"action": response.suggestion.action_type})
                action_result = await self._execute_action(response.suggestion)
                print(f"✅ Action completed: {action_result.get('status', 'unknown')}")
                self._notify("action_completed", {"result": action_result})
                
                # Record action
                self.previous_actions.append({
                    "step": step,
                    "action_type": response.suggestion.action_type,
                    "selector": response.suggestion.selector,
                    "value": response.suggestion.value,
                    "reasoning": response.suggestion.reasoning,
                    "confidence": response.suggestion.confidence,
                    "result": action_result.get("status"),
                    "timestamp": datetime.now().isoformat(),
                })
                
                # Update state
                if response.next_state_prediction:
                    self.current_state = response.next_state_prediction
                    print(f"🔄 State updated to: {self.current_state}")

                # Check if goal is achieved
                if self._is_goal_achieved(response, action_result):
                    logger.info(f"Goal achieved in {step} steps!")
                    print(f"\n🎉 Goal achieved in {step} steps!")
                    result = {
                        "status": "success",
                        "steps": step,
                        "final_state": self.current_state,
                        "actions": self.previous_actions,
                    }
                    self._notify("completed", result)
                    return result
                
                # Wait before next step
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in step {step}: {e}", exc_info=True)
                print(f"❌ Error in step {step}: {e}")

                # Record obstacle
                self.obstacles.append({
                    "step": step,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })

                # Continue to next step (LLM might suggest recovery)
                continue

        # Max steps reached
        logger.warning(f"Max steps ({self.max_steps}) reached without achieving goal")
        print(f"\n⚠️  Max steps ({self.max_steps}) reached without achieving goal")
        return {
            "status": "incomplete",
            "steps": self.max_steps,
            "final_state": self.current_state,
            "actions": self.previous_actions,
            "obstacles": self.obstacles,
        }



    def _notify(self, event_type: str, data: dict[str, Any] | None = None):
        """Notify callback about event.

        Args:
            event_type: Type of event (start, step, thinking, executing, completed, etc.)
            data: Event data
        """
        if self.callback:
            try:
                self.callback({
                    "type": event_type,
                    "data": data or {},
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                logger.warning(f"Callback error: {e}")

    async def _take_screenshot(self, name: str) -> Path:
        """Take a screenshot.
        
        Args:
            name: Screenshot name
            
        Returns:
            Path to screenshot
        """
        screenshot_path = self.screenshot_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Take screenshot in thread pool
        screenshot = await asyncio.to_thread(pyautogui.screenshot)
        await asyncio.to_thread(screenshot.save, screenshot_path)
        
        logger.debug(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

    async def _execute_action(self, suggestion: Any) -> dict[str, Any]:
        """Execute suggested action.
        
        Args:
            suggestion: Action suggestion from LLM
            
        Returns:
            Execution result
        """
        action_type = suggestion.action_type
        selector = suggestion.selector
        value = suggestion.value
        
        logger.info(f"Executing: {action_type} (selector={selector}, value={value})")
        
        try:
            if action_type == "click":
                return await self._execute_click(selector)
            elif action_type == "type":
                return await self._execute_type(value)
            elif action_type == "wait_for":
                return await self._execute_wait(selector)
            elif action_type == "screenshot":
                # Already taken screenshot, just return success
                return {"status": "success", "action": "screenshot"}
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return {"status": "unknown_action", "action": action_type}
                
        except Exception as e:
            logger.error(f"Error executing {action_type}: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_click(self, selector: str | None) -> dict[str, Any]:
        """Execute click action.
        
        Args:
            selector: Click target (coordinates or "center")
            
        Returns:
            Execution result
        """
        if not selector:
            return {"status": "error", "error": "No selector provided"}
        
        if selector == "center":
            # Click center of screen
            screen_width, screen_height = await asyncio.to_thread(pyautogui.size)
            x, y = screen_width // 2, screen_height // 2
        elif "," in selector:
            # Parse coordinates
            try:
                x, y = map(int, selector.split(","))
            except ValueError:
                return {"status": "error", "error": f"Invalid coordinates: {selector}"}
        else:
            return {"status": "error", "error": f"Invalid selector: {selector}"}
        
        # Move mouse slowly to position (so user can see it)
        await asyncio.to_thread(pyautogui.moveTo, x, y, duration=1.0)

        # Click
        await asyncio.to_thread(pyautogui.click)
        logger.info(f"Clicked at ({x}, {y})")

        return {"status": "success", "action": "click", "x": x, "y": y}

    async def _execute_type(self, text: str | None) -> dict[str, Any]:
        """Execute type action.
        
        Args:
            text: Text to type
            
        Returns:
            Execution result
        """
        if not text:
            return {"status": "error", "error": "No text provided"}
        
        # Type text
        await asyncio.to_thread(pyautogui.write, text, interval=0.05)
        logger.info(f"Typed: {text}")
        
        return {"status": "success", "action": "type", "text": text}

    async def _execute_wait(self, duration_str: str | None) -> dict[str, Any]:
        """Execute wait action.
        
        Args:
            duration_str: Duration in seconds
            
        Returns:
            Execution result
        """
        if not duration_str:
            duration = 1.0
        else:
            try:
                duration = float(duration_str)
            except ValueError:
                return {"status": "error", "error": f"Invalid duration: {duration_str}"}
        
        # Wait
        await asyncio.sleep(duration)
        logger.info(f"Waited {duration} seconds")
        
        return {"status": "success", "action": "wait", "duration": duration}

    def _is_goal_achieved(self, response: Any, action_result: dict[str, Any]) -> bool:
        """Check if goal is achieved.
        
        Args:
            response: LLM response
            action_result: Action execution result
            
        Returns:
            True if goal is achieved
        """
        # Simple heuristic: if LLM predicts a "done" or "complete" state
        if response.next_state_prediction:
            prediction = response.next_state_prediction.lower()
            if any(keyword in prediction for keyword in ["done", "complete", "success", "sent", "saved"]):
                return True
        
        # Check if LLM has high confidence and suggests no more actions
        if response.suggestion.action_type == "screenshot" and response.suggestion.confidence > 0.9:
            # LLM is just observing, might be done
            return False
        
        return False

