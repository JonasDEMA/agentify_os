"""Executors for Desktop RPA Agent."""

from agents.desktop_rpa.executors.base import BaseExecutor, ExecutionResult
from agents.desktop_rpa.executors.click_executor import ClickExecutor
from agents.desktop_rpa.executors.screenshot_executor import ScreenshotExecutor
from agents.desktop_rpa.executors.type_executor import TypeExecutor
from agents.desktop_rpa.executors.wait_executor import WaitExecutor

__all__ = [
    "BaseExecutor",
    "ExecutionResult",
    "ClickExecutor",
    "TypeExecutor",
    "WaitExecutor",
    "ScreenshotExecutor",
]

