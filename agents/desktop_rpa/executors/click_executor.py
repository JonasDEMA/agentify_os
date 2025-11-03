"""Click executor for Desktop RPA Agent."""

import asyncio
import logging

import pyautogui

from agents.desktop_rpa.executors.base import BaseExecutor, ExecutionResult

logger = logging.getLogger(__name__)


class ClickExecutor(BaseExecutor):
    """Executor for click actions using PyAutoGUI."""

    @property
    def action_type(self) -> str:
        """Return the action type."""
        return "click"

    async def execute(
        self,
        selector: str,
        text: str | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Execute a click action.

        Args:
            selector: Coordinates in format "x,y" or element description
            text: Not used for click actions
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with success status
        """
        try:
            # Parse coordinates from selector
            # Format: "x,y" or "center" or "element_name"
            if "," in selector:
                # Direct coordinates
                x, y = map(int, selector.split(","))
                logger.info(f"Clicking at coordinates ({x}, {y})")

                # Run in thread pool to avoid blocking
                await asyncio.to_thread(pyautogui.click, x, y)

                return ExecutionResult(
                    success=True,
                    message=f"Clicked at ({x}, {y})",
                    data={"x": x, "y": y},
                )

            elif selector.lower() == "center":
                # Click at screen center
                screen_width, screen_height = pyautogui.size()
                x = screen_width // 2
                y = screen_height // 2
                logger.info(f"Clicking at screen center ({x}, {y})")

                await asyncio.to_thread(pyautogui.click, x, y)

                return ExecutionResult(
                    success=True,
                    message=f"Clicked at screen center ({x}, {y})",
                    data={"x": x, "y": y},
                )

            else:
                # Element name - would need OCR/Vision (not implemented yet)
                return ExecutionResult(
                    success=False,
                    message=f"Element-based clicking not yet implemented: {selector}",
                    error="NOT_IMPLEMENTED",
                )

        except ValueError as e:
            logger.error(f"Invalid coordinates format: {selector}")
            return ExecutionResult(
                success=False,
                message=f"Invalid coordinates format: {selector}",
                error=str(e),
            )
        except Exception as e:
            logger.error(f"Click action failed: {e}")
            return ExecutionResult(
                success=False,
                message=f"Click action failed: {e}",
                error=str(e),
            )

