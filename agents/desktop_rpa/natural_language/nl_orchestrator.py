"""Natural Language Orchestrator for CPA Agent.

This orchestrator:
1. Receives natural language commands from user
2. Parses intent and extracts parameters using LLM
3. Routes to appropriate CPA task execution
4. Sends human-like status updates during execution
5. Returns final result in natural language
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable
from pathlib import Path

from agents.desktop_rpa.natural_language.models import (
    UserCommand,
    AgentThinking,
    AgentAction,
    AgentProgress,
    AgentResult,
    AgentError,
    AgentQuestion,
    ConversationSession,
    MessageType,
)
from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor
from agents.desktop_rpa.cognitive.llm_wrapper import LLMWrapper
from agents.desktop_rpa.cognitive.models import LLMRequest
import structlog

logger = structlog.get_logger()


class NaturalLanguageOrchestrator:
    """Orchestrates natural language commands to CPA task execution."""
    
    def __init__(
        self,
        message_callback: Callable[[dict[str, Any]], None] | None = None,
        use_vision: bool = True,
        use_window_manager: bool = True,
    ):
        """Initialize orchestrator.
        
        Args:
            message_callback: Callback for sending messages to user (UI/WebSocket)
            use_vision: Enable vision layer
            use_window_manager: Enable window manager
        """
        self.message_callback = message_callback
        self.use_vision = use_vision
        self.use_window_manager = use_window_manager
        
        # LLM for intent parsing
        self.llm = LLMWrapper()
        
        # Current session
        self.current_session: ConversationSession | None = None
        
        logger.info("NaturalLanguageOrchestrator initialized")
    
    def _send_message(self, message: dict[str, Any]):
        """Send message to user via callback."""
        if self.message_callback:
            self.message_callback(message)
        
        # Also add to session
        if self.current_session:
            self.current_session.messages.append(message)
    
    async def process_command(self, command: str, user_id: str | None = None) -> ConversationSession:
        """Process a natural language command.
        
        Args:
            command: Natural language command from user
            user_id: Optional user ID
            
        Returns:
            ConversationSession with all messages and result
        """
        # Create new session
        session_id = str(uuid.uuid4())
        self.current_session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            task_goal=command,
            task_status="in_progress",
        )
        
        logger.info(f"Processing command: {command}", session_id=session_id)
        
        # Send user command
        user_cmd = UserCommand(command=command, session_id=session_id)
        self._send_message(user_cmd.model_dump(mode="json"))
        
        try:
            # Step 1: Parse intent
            await self._send_thinking("Let me understand what you need...")
            intent = await self._parse_intent(command)
            
            logger.info(f"Parsed intent: {intent}", session_id=session_id)
            
            # Step 2: Execute task
            result = await self._execute_task(intent, session_id)
            
            # Step 3: Send final result
            self.current_session.task_status = "completed"
            return self.current_session
            
        except Exception as e:
            logger.error(f"Error processing command: {e}", session_id=session_id)
            
            # Send error message
            error_msg = AgentError(
                message=f"Sorry, I encountered an error: {str(e)}",
                error_type=type(e).__name__,
                error_details=str(e),
                session_id=session_id,
            )
            self._send_message(error_msg.model_dump(mode="json"))
            
            self.current_session.task_status = "failed"
            return self.current_session
    
    async def _parse_intent(self, command: str) -> dict[str, Any]:
        """Parse user intent from natural language command.
        
        Uses LLM to extract:
        - Task goal (what user wants to achieve)
        - Application (if mentioned)
        - Parameters (dates, names, etc.)
        
        Args:
            command: Natural language command
            
        Returns:
            Parsed intent dictionary
        """
        # Use LLM to parse intent
        prompt = f"""Parse this user command and extract the task goal and parameters:

User command: "{command}"

Extract:
1. Task goal (what the user wants to achieve)
2. Application (if mentioned, e.g., Outlook, Word, Excel)
3. Parameters (dates, names, search terms, etc.)

Return as JSON:
{{
    "task_goal": "...",
    "application": "..." or null,
    "parameters": {{...}}
}}

Examples:
- "Check my next appointment with Dieter" → {{"task_goal": "Find next appointment with Dieter", "application": "Outlook", "parameters": {{"contact_name": "Dieter"}}}}
- "Open Outlook and check my calendar" → {{"task_goal": "Open Outlook and view calendar", "application": "Outlook", "parameters": {{}}}}
"""
        
        # For now, simple heuristic parsing (can be replaced with LLM call)
        # TODO: Use LLM for better intent parsing
        
        task_goal = command
        application = None
        parameters = {}
        
        # Detect application mentions
        command_lower = command.lower()
        if "outlook" in command_lower:
            application = "Outlook"
        elif "word" in command_lower:
            application = "Word"
        elif "excel" in command_lower:
            application = "Excel"
        elif "chrome" in command_lower or "browser" in command_lower:
            application = "Chrome"
        
        # Detect calendar/appointment queries
        if "appointment" in command_lower or "meeting" in command_lower or "calendar" in command_lower:
            # Extract contact name if mentioned
            words = command.split()
            for i, word in enumerate(words):
                if word.lower() in ["with", "from", "to"] and i + 1 < len(words):
                    parameters["contact_name"] = words[i + 1]
                    break
        
        return {
            "task_goal": task_goal,
            "application": application,
            "parameters": parameters,
        }

    async def _execute_task(self, intent: dict[str, Any], session_id: str) -> dict[str, Any]:
        """Execute task based on parsed intent.

        Args:
            intent: Parsed intent from _parse_intent
            session_id: Session ID

        Returns:
            Execution result
        """
        task_goal = intent["task_goal"]
        application = intent.get("application")
        parameters = intent.get("parameters", {})

        # Send action message
        if application:
            await self._send_action(f"Alright, let me work with {application} for you...")
        else:
            await self._send_action(f"Okay, I'll help you with that...")

        # Create executor with callback for progress updates
        def executor_callback(event: dict[str, Any]):
            """Handle events from cognitive executor."""
            event_type = event.get("type")
            data = event.get("data", {})

            if event_type == "thinking":
                message = data.get("message", "Thinking...")
                asyncio.create_task(self._send_thinking(message))

            elif event_type == "step":
                step = data.get("step", 0)
                max_steps = data.get("max_steps", 0)
                state = data.get("state", "")
                asyncio.create_task(self._send_progress(
                    f"Step {step}/{max_steps}: {state}",
                    current_step=step,
                    total_steps=max_steps,
                ))

            elif event_type == "action":
                action_type = data.get("action_type", "")
                target = data.get("target", "")
                if target:
                    asyncio.create_task(self._send_action(
                        f"I'm {action_type}ing {target}...",
                        action_type=action_type,
                        target=target,
                    ))
                else:
                    asyncio.create_task(self._send_action(
                        f"Performing {action_type}...",
                        action_type=action_type,
                    ))

        # Execute with CognitiveExecutor
        executor = CognitiveExecutor(
            callback=executor_callback,
            use_vision=self.use_vision,
            use_window_manager=self.use_window_manager,
        )

        # Execute task
        result = await executor.execute({"goal": task_goal})

        # Send result
        if result["status"] == "success":
            final_state = result.get("final_state", "")
            await self._send_result(
                f"Done! {final_state}",
                result_data=result,
                success=True,
            )
        else:
            await self._send_result(
                f"I couldn't complete the task. Final state: {result.get('final_state', 'unknown')}",
                result_data=result,
                success=False,
            )

        return result

    async def _send_thinking(self, message: str):
        """Send thinking message."""
        msg = AgentThinking(
            message=message,
            session_id=self.current_session.session_id if self.current_session else None,
        )
        self._send_message(msg.model_dump(mode="json"))
        await asyncio.sleep(0.1)  # Small delay for natural feel

    async def _send_action(self, message: str, action_type: str = "action", target: str | None = None):
        """Send action message."""
        msg = AgentAction(
            message=message,
            action_type=action_type,
            target=target,
            session_id=self.current_session.session_id if self.current_session else None,
        )
        self._send_message(msg.model_dump(mode="json"))
        await asyncio.sleep(0.1)

    async def _send_progress(self, message: str, current_step: int | None = None, total_steps: int | None = None):
        """Send progress message."""
        progress_percent = None
        if current_step and total_steps:
            progress_percent = int((current_step / total_steps) * 100)

        msg = AgentProgress(
            message=message,
            progress_percent=progress_percent,
            current_step=current_step,
            total_steps=total_steps,
            session_id=self.current_session.session_id if self.current_session else None,
        )
        self._send_message(msg.model_dump(mode="json"))
        await asyncio.sleep(0.1)

    async def _send_result(self, message: str, result_data: dict[str, Any] | None = None, success: bool = True):
        """Send final result message."""
        msg = AgentResult(
            message=message,
            result_data=result_data,
            success=success,
            session_id=self.current_session.session_id if self.current_session else None,
        )
        self._send_message(msg.model_dump(mode="json"))

    async def _send_question(self, message: str, options: list[str] | None = None):
        """Send question to user."""
        msg = AgentQuestion(
            message=message,
            options=options,
            session_id=self.current_session.session_id if self.current_session else None,
        )
        self._send_message(msg.model_dump(mode="json"))

