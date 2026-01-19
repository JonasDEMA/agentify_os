"""Security Policies - Manages access control and safety rules."""
import logging
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PolicyConfig(BaseModel):
    """Configuration for security policies."""
    allowed_apps: List[str] = ["chrome", "notepad", "excel", "outlook"]
    blocked_actions: List[str] = ["delete_file", "format_disk", "run_shell"]
    rate_limit_per_minute: int = 60

class PolicyEngine:
    """Engine for enforcing security policies."""

    def __init__(self, config: Optional[PolicyConfig] = None):
        self.config = config or PolicyConfig()

    def check_app_allowed(self, app_name: str) -> bool:
        """Check if an application is allowed to be opened."""
        is_allowed = app_name.lower() in [a.lower() for a in self.config.allowed_apps]
        if not is_allowed:
            logger.warning(f"Policy violation: App {app_name} is not allowed")
        return is_allowed

    def check_action_allowed(self, action: str) -> bool:
        """Check if an action is blocked by security policy."""
        is_blocked = action.lower() in [a.lower() for a in self.config.blocked_actions]
        if is_blocked:
            logger.warning(f"Policy violation: Action {action} is blocked")
        return not is_blocked

    def validate_task(self, action: str, target: str) -> bool:
        """Validate if a task is safe to execute."""
        if action == "open_app":
            return self.check_app_allowed(target)
        return self.check_action_allowed(action)
