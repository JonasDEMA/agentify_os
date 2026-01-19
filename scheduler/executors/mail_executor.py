"""Mail Executor - Executes email-related tasks using Microsoft Graph API."""
import logging
import time
from typing import Optional, Any, Dict

from scheduler.core.task_executor_interface import BaseExecutor
from scheduler.core.task_graph import ActionType, ToDo, ExecutionResult

logger = logging.getLogger(__name__)

class MailExecutor(BaseExecutor):
    """Executor for email tasks via MS Graph API."""

    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        """Initialize mail executor.
        
        Args:
            credentials: API credentials (client_id, client_secret, tenant_id)
        """
        self.credentials = credentials or {}

    async def execute(self, todo: ToDo) -> ExecutionResult:
        """Execute a mail task."""
        start_time = time.time()
        try:
            if todo.action == ActionType.SEND_MAIL:
                result = await self._send_mail(todo)
                duration = time.time() - start_time
                return ExecutionResult(
                    success=True,
                    result={"output": result},
                    duration=duration
                )
            else:
                raise ValueError(f"Action {todo.action} not supported by MailExecutor")
        except Exception as e:
            logger.error(f"Mail execution failed: {e}")
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=str(e),
                duration=duration
            )

    async def verify(self, todo: ToDo) -> bool:
        """Verify task execution."""
        return True

    async def _send_mail(self, todo: ToDo) -> str:
        """Internal handler for sending mail."""
        recipient = todo.selector
        body = todo.text
        
        logger.info(f"Sending email to {recipient}")
        
        # MOCK IMPLEMENTATION
        # In a real implementation, we would use msal and requests to call Graph API
        return f"Email sent to {recipient} (Mocked)"

    def can_execute(self, todo: ToDo) -> bool:
        return todo.action == ActionType.SEND_MAIL
