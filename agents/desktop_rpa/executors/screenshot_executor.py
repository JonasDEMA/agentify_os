"""Screenshot executor for Desktop RPA Agent."""

import asyncio
import logging
from datetime import UTC, datetime
from pathlib import Path

import pyautogui

from agents.desktop_rpa.executors.base import BaseExecutor, ExecutionResult

logger = logging.getLogger(__name__)


class ScreenshotExecutor(BaseExecutor):
    """Executor for taking screenshots using PyAutoGUI."""

    def __init__(self, timeout: float = 30.0, screenshot_dir: str = "./data/screenshots") -> None:
        """Initialize screenshot executor.

        Args:
            timeout: Default timeout in seconds
            screenshot_dir: Directory to save screenshots
        """
        super().__init__(timeout)
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    @property
    def action_type(self) -> str:
        """Return the action type."""
        return "screenshot"

    async def execute(
        self,
        selector: str,
        text: str | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Execute a screenshot action.

        Args:
            selector: Filename or "auto" for auto-generated name
            text: Not used for screenshot actions
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with success status and screenshot path
        """
        try:
            # Generate filename
            if selector.lower() == "auto" or not selector:
                timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            else:
                filename = selector if selector.endswith(".png") else f"{selector}.png"

            filepath = self.screenshot_dir / filename
            logger.info(f"Taking screenshot: {filepath}")

            # Take screenshot in thread pool
            screenshot = await asyncio.to_thread(pyautogui.screenshot)
            await asyncio.to_thread(screenshot.save, str(filepath))

            return ExecutionResult(
                success=True,
                message=f"Screenshot saved to {filepath}",
                data={
                    "filepath": str(filepath),
                    "filename": filename,
                    "size": screenshot.size,
                },
            )

        except Exception as e:
            logger.error(f"Screenshot action failed: {e}")
            return ExecutionResult(
                success=False,
                message=f"Screenshot action failed: {e}",
                error=str(e),
            )

