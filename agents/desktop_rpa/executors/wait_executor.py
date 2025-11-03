"""Wait executor for Desktop RPA Agent."""

import asyncio
import logging

from agents.desktop_rpa.executors.base import BaseExecutor, ExecutionResult

logger = logging.getLogger(__name__)


class WaitExecutor(BaseExecutor):
    """Executor for wait actions."""

    @property
    def action_type(self) -> str:
        """Return the action type."""
        return "wait_for"

    async def execute(
        self,
        selector: str,
        text: str | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Execute a wait action.

        Args:
            selector: Wait duration in seconds or element to wait for
            text: Not used for wait actions
            timeout: Maximum wait time (overrides selector if selector is element)

        Returns:
            ExecutionResult with success status
        """
        try:
            # Parse wait duration from selector
            # Format: "5" (seconds) or "element_name" (wait for element)
            try:
                wait_seconds = float(selector)
                logger.info(f"Waiting for {wait_seconds} seconds")

                await asyncio.sleep(wait_seconds)

                return ExecutionResult(
                    success=True,
                    message=f"Waited for {wait_seconds} seconds",
                    data={"wait_seconds": wait_seconds},
                )

            except ValueError:
                # Element-based waiting - would need OCR/Vision (not implemented yet)
                return ExecutionResult(
                    success=False,
                    message=f"Element-based waiting not yet implemented: {selector}",
                    error="NOT_IMPLEMENTED",
                )

        except Exception as e:
            logger.error(f"Wait action failed: {e}")
            return ExecutionResult(
                success=False,
                message=f"Wait action failed: {e}",
                error=str(e),
            )

