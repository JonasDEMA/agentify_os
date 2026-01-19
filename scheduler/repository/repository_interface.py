"""Repository Interface - Abstract base classes for data persistence."""
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict

from scheduler.queue.job_queue import Job, JobStatus
from scheduler.core.lam_protocol import BaseMessage

class JobRepository(ABC):
    """Abstract interface for Job persistence."""

    @abstractmethod
    async def save(self, job: Job) -> None:
        """Save or update a job."""
        pass

    @abstractmethod
    async def get(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""
        pass

    @abstractmethod
    async def list(
        self, 
        limit: int = 100, 
        offset: int = 0, 
        status: Optional[JobStatus] = None
    ) -> List[Job]:
        """List jobs with filtering and pagination."""
        pass

    @abstractmethod
    async def update_status(self, job_id: str, status: JobStatus, error: Optional[str] = None) -> None:
        """Update job status."""
        pass

    @abstractmethod
    async def delete(self, job_id: str) -> None:
        """Delete a job."""
        pass


class AuditRepository(ABC):
    """Abstract interface for Audit Log persistence."""

    @abstractmethod
    async def log_action(
        self, 
        job_id: str, 
        action: str, 
        status: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an action performed during job execution."""
        pass

    @abstractmethod
    async def get_logs(self, job_id: str) -> List[Dict[str, Any]]:
        """Retrieve logs for a specific job."""
        pass


class TaskRepository(ABC):
    """Abstract interface for Task persistence."""

    @abstractmethod
    async def save_tasks(self, job_id: str, tasks: Dict[str, Any]) -> None:
        """Save tasks for a job."""
        pass

    @abstractmethod
    async def get_tasks(self, job_id: str) -> Dict[str, Any]:
        """Retrieve tasks for a job."""
        pass


class MessageRepository(ABC):
    """Abstract interface for Message persistence."""

    @abstractmethod
    async def save_message(self, message: BaseMessage) -> None:
        """Save an agent message."""
        pass

    @abstractmethod
    async def get_messages(self, job_id: Optional[str] = None) -> List[BaseMessage]:
        """Retrieve messages, optionally filtered by job_id."""
        pass
