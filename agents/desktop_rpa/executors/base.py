"""Base executor interface for Desktop RPA Agent."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Result of an executor action."""

    success: bool = Field(..., description="Whether the action succeeded")
    message: str = Field(default="", description="Result message")
    data: dict[str, Any] = Field(default_factory=dict, description="Result data")
    error: str | None = Field(None, description="Error message if failed")


class BaseExecutor(ABC):
    """Base class for all executors.

    Each executor implements a specific action type (click, type, wait, etc.).
    """

    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize executor.

        Args:
            timeout: Default timeout in seconds
        """
        self.timeout = timeout

    @abstractmethod
    async def execute(
        self,
        selector: str,
        text: str | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Execute the action.

        Args:
            selector: Element selector or target
            text: Text to type (for type actions)
            timeout: Timeout in seconds (overrides default)

        Returns:
            ExecutionResult with success status and data
        """
        pass

    @property
    @abstractmethod
    def action_type(self) -> str:
        """Return the action type this executor handles."""
        pass

