"""Type executor for Desktop RPA Agent."""

import asyncio
import logging

import pyautogui

from agents.desktop_rpa.executors.base import BaseExecutor, ExecutionResult

logger = logging.getLogger(__name__)


class TypeExecutor(BaseExecutor):
    """Executor for typing text using PyAutoGUI."""

    @property
    def action_type(self) -> str:
        """Return the action type."""
        return "type"

    async def execute(
        self,
        selector: str,
        text: str | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Execute a type action.

        Args:
            selector: Target element (not used for now, types at current cursor position)
            text: Text to type
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with success status
        """
        if not text:
            return ExecutionResult(
                success=False,
                message="No text provided for type action",
                error="MISSING_TEXT",
            )

        try:
            logger.info(f"Typing text: {text[:50]}...")  # Log first 50 chars

            # Run in thread pool to avoid blocking
            await asyncio.to_thread(pyautogui.write, text)

            return ExecutionResult(
                success=True,
                message=f"Typed {len(text)} characters",
                data={"text_length": len(text), "text_preview": text[:50]},
            )

        except Exception as e:
            logger.error(f"Type action failed: {e}")
            return ExecutionResult(
                success=False,
                message=f"Type action failed: {e}",
                error=str(e),
            )

