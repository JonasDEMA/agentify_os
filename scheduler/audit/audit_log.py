"""Audit Log Service - Handles logging of agent actions and screenshot storage."""
import os
import shutil
from datetime import datetime, UTC
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

from scheduler.repository.repository_interface import AuditRepository
from scheduler.config.settings import settings

class AuditEntry(BaseModel):
    """Audit log entry model."""
    id: Optional[int] = None
    job_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    action: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)

class AuditLogService:
    """Service for managing audit logs and screenshots."""

    def __init__(self, repository: AuditRepository, screenshot_dir: str = "./data/screenshots"):
        self.repository = repository
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def log_action(
        self, 
        job_id: str, 
        action: str, 
        status: str, 
        details: Optional[Dict[str, Any]] = None,
        screenshot_path: Optional[str] = None
    ) -> None:
        """Log an action and optionally save a screenshot.
        
        Args:
            job_id: Job ID
            action: Action name
            status: Action status (success/failure)
            details: Additional details
            screenshot_path: Path to temporary screenshot file to be moved to storage
        """
        final_details = details or {}
        
        if screenshot_path and os.path.exists(screenshot_path):
            # Create job-specific screenshot directory
            job_dir = os.path.join(self.screenshot_dir, job_id)
            os.makedirs(job_dir, exist_ok=True)
            
            # Generate unique filename for screenshot
            timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{action}_{timestamp_str}.png"
            dest_path = os.path.join(job_dir, filename)
            
            # Move screenshot to storage
            shutil.copy2(screenshot_path, dest_path)
            final_details["screenshot_url"] = f"/api/v1/audit/screenshots/{job_id}/{filename}"
            final_details["screenshot_path"] = dest_path

        await self.repository.log_action(job_id, action, status, final_details)

    async def get_job_logs(self, job_id: str) -> List[AuditEntry]:
        """Retrieve all audit logs for a specific job."""
        logs = await self.repository.get_logs(job_id)
        return [
            AuditEntry(
                id=log["id"],
                job_id=log["job_id"],
                timestamp=datetime.fromisoformat(log["timestamp"]),
                action=log["action"],
                status=log["status"],
                details=log["details"]
            )
            for log in logs
        ]
