"""Executor Registry - Manages and dispatches tasks to specific executors."""
import logging
from typing import Dict, Optional, Type

from scheduler.core.task_executor_interface import BaseExecutor
from scheduler.core.task_graph import ActionType, ToDo, ExecutionResult

logger = logging.getLogger(__name__)

class ExecutorRegistry:
    """Registry for task executors."""

    def __init__(self):
        self._executors: Dict[ActionType, BaseExecutor] = {}

    def register(self, action_type: ActionType, executor: BaseExecutor) -> None:
        """Register an executor for a specific action type.
        
        Args:
            action_type: Type of action handled by the executor
            executor: Executor instance
        """
        self._executors[action_type] = executor
        logger.info(f"Registered executor for action: {action_type}")

    def get_executor(self, action_type: ActionType) -> Optional[BaseExecutor]:
        """Get the executor for a specific action type."""
        return self._executors.get(action_type)

    async def execute(self, todo: ToDo) -> ExecutionResult:
        """Execute a task using the registered executor.
        
        Args:
            todo: Task to execute
            
        Returns:
            Execution result
            
        Raises:
            ValueError: If no executor is registered for the action type
        """
        executor = self.get_executor(todo.action)
        if not executor:
            msg = f"No executor registered for action type: {todo.action}"
            logger.error(msg)
            raise ValueError(msg)
        
        return await executor.execute(todo)
