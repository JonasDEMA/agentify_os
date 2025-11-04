"""LLM Wrapper for Desktop RPA Agent."""

import base64
import json
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI, OpenAIError
from PIL import Image

from agents.desktop_rpa.cognitive.models import (
    ActionSuggestion,
    LLMRequest,
    LLMResponse,
    StrategyRequest,
    StrategyResponse,
)
from agents.desktop_rpa.config.settings import settings

logger = logging.getLogger(__name__)


# System prompts for different use cases
SYSTEM_PROMPT_ACTION = """You are a Desktop RPA Agent assistant. Your role is to help the agent 
navigate Windows desktop applications to achieve goals.

You will receive:
- A goal (e.g., "Send email via Outlook")
- Current state (e.g., "outlook_closed")
- A screenshot of the current screen (base64 encoded) - if available
- Context (previous actions, obstacles, etc.)

You should respond with:
- The next action to take (click, type, wait_for, screenshot)
- The reasoning behind the action
- Confidence level (0.0 - 1.0)
- Assessment of the current state
- Prediction of the next state after the action

Available action types:
- click: Click at coordinates or element (selector: "x,y" or "center")
- type: Type text (value: text to type)
- wait_for: Wait for condition (selector: duration in seconds)
- screenshot: Take a screenshot (selector: filename)

Be precise, conservative, and explain your reasoning clearly.
If you're uncertain, suggest taking a screenshot first to gather more information.
"""

SYSTEM_PROMPT_STRATEGY = """You are a Desktop RPA Strategy Planner. Your role is to create 
step-by-step strategies for achieving goals in Windows desktop applications.

You will receive:
- A goal (e.g., "Send email via Outlook with attachment")
- Context (known states, transitions, etc.)

You should respond with:
- A strategy name
- Preconditions (what must be true before starting)
- Steps to execute (ordered list of actions)
- Expected states during execution
- Confidence level
- Reasoning

Create strategies that are:
- Robust (handle common obstacles)
- Efficient (minimal steps)
- Clear (easy to understand and debug)
- Reusable (can be applied in similar situations)
"""


class LLMWrapper:
    """Wrapper for LLM interactions."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ):
        """Initialize LLM wrapper.

        Args:
            api_key: OpenAI API key (defaults to settings.openai_api_key)
            model: Model to use (defaults to settings.llm_model)
            temperature: Temperature (defaults to settings.llm_temperature)
            max_tokens: Max tokens (defaults to settings.llm_max_tokens)
            timeout: Timeout (defaults to settings.llm_timeout)
            max_retries: Max retries (defaults to settings.llm_max_retries)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.llm_model
        self.temperature = temperature or settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.timeout = timeout or settings.llm_timeout
        self.max_retries = max_retries or settings.llm_max_retries

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        logger.info(
            f"LLM Wrapper initialized with model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}"
        )

    async def ask_for_next_action(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """Ask LLM for the next action to take.

        Args:
            request: LLM request with goal, state, screenshot, context

        Returns:
            LLM response with action suggestion

        Raises:
            OpenAIError: If LLM request fails
        """
        logger.info(f"Asking LLM for next action: goal={request.goal}, state={request.current_state}")

        # Build messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_ACTION},
        ]

        # Build user message
        user_content = self._build_action_user_message(request)
        messages.append({"role": "user", "content": user_content})

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            response_data = json.loads(content)
            llm_response = self._parse_action_response(response_data, response)

            logger.info(
                f"LLM suggested action: {llm_response.suggestion.action_type} "
                f"(confidence={llm_response.suggestion.confidence:.2f})"
            )

            return llm_response

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise

    async def ask_for_strategy(
        self,
        request: StrategyRequest,
    ) -> StrategyResponse:
        """Ask LLM to create a strategy for achieving a goal.

        Args:
            request: Strategy request with goal and context

        Returns:
            Strategy response with steps

        Raises:
            OpenAIError: If LLM request fails
        """
        logger.info(f"Asking LLM for strategy: goal={request.goal}")

        # Build messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_STRATEGY},
        ]

        # Build user message
        user_content = self._build_strategy_user_message(request)
        messages.append({"role": "user", "content": user_content})

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            response_data = json.loads(content)
            strategy_response = self._parse_strategy_response(response_data, response)

            logger.info(
                f"LLM created strategy: {strategy_response.strategy_name} "
                f"with {len(strategy_response.steps)} steps"
            )

            return strategy_response

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise

    def _build_action_user_message(self, request: LLMRequest) -> list[dict[str, Any]]:
        """Build user message for action request.

        Args:
            request: LLM request

        Returns:
            User message content (text + optional image)
        """
        # Build text content
        text_parts = [
            f"**Goal**: {request.goal}",
            f"**Current State**: {request.current_state}",
        ]

        if request.previous_actions:
            text_parts.append(f"**Previous Actions**: {json.dumps(request.previous_actions, indent=2)}")

        if request.obstacles:
            text_parts.append(f"**Obstacles**: {json.dumps(request.obstacles, indent=2)}")

        if request.context:
            text_parts.append(f"**Context**: {json.dumps(request.context, indent=2)}")

        text_parts.append(
            "\n**Please respond in JSON format with the following structure**:\n"
            "```json\n"
            "{\n"
            '  "suggestion": {\n'
            '    "action_type": "click|type|wait_for|screenshot",\n'
            '    "selector": "coordinates or element identifier",\n'
            '    "value": "value for the action (optional)",\n'
            '    "reasoning": "why this action",\n'
            '    "confidence": 0.0-1.0,\n'
            '    "metadata": {}\n'
            "  },\n"
            '  "state_assessment": "assessment of current state",\n'
            '  "next_state_prediction": "predicted next state",\n'
            '  "warnings": ["warning1", "warning2"]\n'
            "}\n"
            "```"
        )

        text_content = "\n\n".join(text_parts)

        # If screenshot is provided and vision is enabled, include it
        if request.screenshot_base64 and settings.enable_vision:
            return [
                {"type": "text", "text": text_content},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{request.screenshot_base64}",
                    },
                },
            ]
        else:
            return [{"type": "text", "text": text_content}]

    def _build_strategy_user_message(self, request: StrategyRequest) -> str:
        """Build user message for strategy request."""
        parts = [
            f"**Goal**: {request.goal}",
        ]

        if request.known_states:
            parts.append(f"**Known States**: {', '.join(request.known_states)}")

        if request.known_transitions:
            parts.append(f"**Known Transitions**: {json.dumps(request.known_transitions, indent=2)}")

        if request.context:
            parts.append(f"**Context**: {json.dumps(request.context, indent=2)}")

        parts.append(
            "\n**Please respond in JSON format with the following structure**:\n"
            "```json\n"
            "{\n"
            '  "strategy_name": "name of the strategy",\n'
            '  "goal": "goal of the strategy",\n'
            '  "preconditions": ["condition1", "condition2"],\n'
            '  "steps": [{"action_type": "...", "selector": "...", "value": "..."}],\n'
            '  "expected_states": ["state1", "state2"],\n'
            '  "confidence": 0.0-1.0,\n'
            '  "reasoning": "why this strategy"\n'
            "}\n"
            "```"
        )

        return "\n\n".join(parts)

    def _parse_action_response(self, data: dict[str, Any], raw_response: Any) -> LLMResponse:
        """Parse action response from LLM."""
        suggestion_data = data.get("suggestion", {})
        suggestion = ActionSuggestion(
            action_type=suggestion_data.get("action_type", "screenshot"),
            selector=suggestion_data.get("selector"),
            value=suggestion_data.get("value"),
            reasoning=suggestion_data.get("reasoning", "No reasoning provided"),
            confidence=suggestion_data.get("confidence", 0.5),
            metadata=suggestion_data.get("metadata", {}),
        )

        return LLMResponse(
            suggestion=suggestion,
            state_assessment=data.get("state_assessment", "Unknown state"),
            next_state_prediction=data.get("next_state_prediction"),
            warnings=data.get("warnings", []),
            timestamp=datetime.now(),
            model_used=self.model,
            tokens_used=raw_response.usage.total_tokens if raw_response.usage else None,
        )

    def _parse_strategy_response(self, data: dict[str, Any], raw_response: Any) -> StrategyResponse:
        """Parse strategy response from LLM."""
        return StrategyResponse(
            strategy_name=data.get("strategy_name", "Unnamed Strategy"),
            goal=data.get("goal", ""),
            preconditions=data.get("preconditions", []),
            steps=data.get("steps", []),
            expected_states=data.get("expected_states", []),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", "No reasoning provided"),
            timestamp=datetime.now(),
            model_used=self.model,
        )

    @staticmethod
    def encode_screenshot(screenshot_path: str | Path) -> str:
        """Encode screenshot to base64.

        Args:
            screenshot_path: Path to screenshot file

        Returns:
            Base64 encoded screenshot
        """
        with Image.open(screenshot_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too large (max 2048x2048 for GPT-4 Vision)
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Encode to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @staticmethod
    def encode_screenshot_from_bytes(screenshot_bytes: bytes) -> str:
        """Encode screenshot bytes to base64.

        Args:
            screenshot_bytes: Screenshot as bytes

        Returns:
            Base64 encoded screenshot
        """
        with Image.open(BytesIO(screenshot_bytes)) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too large
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Encode to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

