"""Job Queue implementation using Redis.

Manages job queuing, status tracking, and retry logic.
"""

import json
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from redis.asyncio import Redis

from scheduler.core.task_graph import TaskGraph


class JobStatus(str, Enum):
    """Job status enum."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(BaseModel):
    """Job model.

    Represents a job to be executed by the scheduler.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Job ID")
    intent: str = Field(..., description="Intent name")
    task_graph: TaskGraph = Field(..., description="Task graph to execute")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Job status")
    task_status: dict[str, str] = Field(default_factory=dict, description="Status of individual tasks")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    started_at: datetime | None = Field(None, description="Start timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    error: str | None = Field(None, description="Error message if failed")
    retry_count: int = Field(default=0, description="Number of retries")
    max_retries: int = Field(default=3, description="Maximum number of retries")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Custom model dump to serialize TaskGraph.

        Returns:
            Dictionary representation
        """
        data = super().model_dump(**kwargs)
        # Serialize TaskGraph manually
        data["task_graph"] = {
            "tasks": {
                task_id: {
                    "action": task.action.value,
                    "selector": task.selector,
                    "text": task.text,
                    "timeout": task.timeout,
                    "depends_on": task.depends_on,
                }
                for task_id, task in self.task_graph.tasks.items()
            }
        }
        # Include task_status in dump
        data["task_status"] = self.task_status
        # Serialize datetime objects
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("started_at"):
            data["started_at"] = data["started_at"].isoformat()
        if data.get("completed_at"):
            data["completed_at"] = data["completed_at"].isoformat()
        return data


class JobQueue:
    """Job queue using Redis.

    Manages job queuing, dequeuing, status tracking, and retry logic.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        """Initialize job queue.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Redis | None = None
        self.queue_key = "cpa:jobs:queue"
        self.job_key_prefix = "cpa:jobs:data:"

    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = Redis.from_url(self.redis_url, decode_responses=False)
        await self.redis.ping()

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.aclose()

    def _get_job_key(self, job_id: str) -> str:
        """Get Redis key for job data.

        Args:
            job_id: Job ID

        Returns:
            Redis key
        """
        return f"{self.job_key_prefix}{job_id}"

    async def enqueue(self, job: Job) -> str:
        """Enqueue a job.

        Args:
            job: Job to enqueue

        Returns:
            Job ID

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        # Store job data
        job_key = self._get_job_key(job.id)
        job_data = json.dumps(job.model_dump())
        await self.redis.set(job_key, job_data)

        # Add job ID to queue
        await self.redis.rpush(self.queue_key, job.id)  # type: ignore[misc]

        return job.id

    async def dequeue(self) -> Job | None:
        """Dequeue a job.

        Returns:
            Job or None if queue is empty

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        # Pop job ID from queue
        job_id_bytes = await self.redis.lpop(self.queue_key)  # type: ignore[misc]
        if not job_id_bytes:
            return None

        job_id = job_id_bytes.decode() if isinstance(job_id_bytes, bytes) else job_id_bytes

        # Get job data
        job_key = self._get_job_key(job_id)
        job_data_bytes = await self.redis.get(job_key)

        if not job_data_bytes:
            return None

        job_data = job_data_bytes.decode() if isinstance(job_data_bytes, bytes) else job_data_bytes

        # Deserialize job
        job_dict = json.loads(job_data)

        # Reconstruct TaskGraph
        task_graph_data = job_dict.pop("task_graph")
        task_graph = TaskGraph()
        task_graph.tasks = {
            task_id: self._deserialize_todo(task_data)
            for task_id, task_data in task_graph_data.get("tasks", {}).items()
        }

        # Parse datetime fields
        if job_dict.get("created_at"):
            job_dict["created_at"] = datetime.fromisoformat(job_dict["created_at"])
        if job_dict.get("started_at"):
            job_dict["started_at"] = datetime.fromisoformat(job_dict["started_at"])
        if job_dict.get("completed_at"):
            job_dict["completed_at"] = datetime.fromisoformat(job_dict["completed_at"])

        # Create Job instance
        job = Job(task_graph=task_graph, **job_dict)

        return job

    def _deserialize_todo(self, task_data: dict[str, Any]) -> Any:
        """Deserialize ToDo from dict.

        Args:
            task_data: Task data dictionary

        Returns:
            ToDo instance
        """
        from scheduler.core.task_graph import ActionType, ToDo

        return ToDo(
            action=ActionType(task_data["action"]),
            selector=task_data["selector"],
            text=task_data.get("text"),
            timeout=task_data.get("timeout", 30.0),
            depends_on=task_data.get("depends_on", []),
        )

    async def get_status(self, job_id: str) -> JobStatus | None:
        """Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job status or None if not found

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        job = await self.get_job(job_id)
        return job.status if job else None

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error: str | None = None,
    ) -> None:
        """Update job status.

        Args:
            job_id: Job ID
            status: New status
            error: Error message (optional)

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        job = await self.get_job(job_id)
        if not job:
            return

        job.status = status
        if error:
            job.error = error

        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.now(UTC)
        elif status in (JobStatus.DONE, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = datetime.now(UTC)

        # Save updated job
        job_key = self._get_job_key(job_id)
        job_data = json.dumps(job.model_dump())
        await self.redis.set(job_key, job_data)

    async def update_task_status(
        self,
        job_id: str,
        task_id: str,
        status: str,
    ) -> None:
        """Update status of a specific task in a job.

        Args:
            job_id: Job ID
            task_id: Task ID
            status: New task status

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        job = await self.get_job(job_id)
        if not job:
            return

        job.task_status[task_id] = status

        # Save updated job
        job_key = self._get_job_key(job_id)
        job_data = json.dumps(job.model_dump())
        await self.redis.set(job_key, job_data)

    async def retry(self, job_id: str) -> bool:
        """Retry a failed job.

        Args:
            job_id: Job ID

        Returns:
            True if job was retried, False if max retries exceeded

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        job = await self.get_job(job_id)
        if not job:
            return False

        # Check if max retries exceeded
        if job.retry_count >= job.max_retries:
            return False

        # Increment retry count
        job.retry_count += 1
        job.status = JobStatus.PENDING
        job.error = None

        # Save updated job
        job_key = self._get_job_key(job_id)
        job_data = json.dumps(job.model_dump())
        await self.redis.set(job_key, job_data)

        # Re-enqueue job
        await self.redis.rpush(self.queue_key, job_id)  # type: ignore[misc]

        return True

    async def cancel(self, job_id: str) -> None:
        """Cancel a job.

        Args:
            job_id: Job ID

        Raises:
            RuntimeError: If not connected to Redis
        """
        await self.update_status(job_id, JobStatus.CANCELLED)

    async def get_job(self, job_id: str) -> Job | None:
        """Get a job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job or None if not found

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis:
            msg = "Not connected to Redis"
            raise RuntimeError(msg)

        job_key = self._get_job_key(job_id)
        job_data_bytes = await self.redis.get(job_key)

        if not job_data_bytes:
            return None

        job_data = job_data_bytes.decode() if isinstance(job_data_bytes, bytes) else job_data_bytes

        # Deserialize job
        job_dict = json.loads(job_data)

        # Reconstruct TaskGraph
        task_graph_data = job_dict.pop("task_graph")
        task_graph = TaskGraph()
        task_graph.tasks = {
            task_id: self._deserialize_todo(task_data)
            for task_id, task_data in task_graph_data.get("tasks", {}).items()
        }

        # Parse datetime fields
        if job_dict.get("created_at"):
            job_dict["created_at"] = datetime.fromisoformat(job_dict["created_at"])
        if job_dict.get("started_at"):
            job_dict["started_at"] = datetime.fromisoformat(job_dict["started_at"])
        if job_dict.get("completed_at"):
            job_dict["completed_at"] = datetime.fromisoformat(job_dict["completed_at"])

        # Create Job instance
        job = Job(task_graph=task_graph, **job_dict)

        return job

