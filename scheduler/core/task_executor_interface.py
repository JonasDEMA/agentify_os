"""Task Executor Interface.

Abstract base class for task executors.
"""

from abc import ABC, abstractmethod

from scheduler.core.task_graph import ExecutionResult, ToDo


class BaseExecutor(ABC):
    """Abstract base class for task executors.

    All executors must implement the execute and verify methods.
    """

    @abstractmethod
    async def execute(self, todo: ToDo) -> ExecutionResult:
        """Execute a task.

        Args:
            todo: Task to execute

        Returns:
            Execution result

        Raises:
            Exception: If execution fails
        """
        ...

    @abstractmethod
    async def verify(self, todo: ToDo) -> bool:
        """Verify task execution.

        Args:
            todo: Task to verify

        Returns:
            True if verification successful, False otherwise
        """
        ...

    def can_execute(self, todo: ToDo) -> bool:
        """Check if this executor can execute the given task.

        Args:
            todo: Task to check

        Returns:
            True if executor can handle this task type
        """
        # Default implementation - override in subclasses
        return True

