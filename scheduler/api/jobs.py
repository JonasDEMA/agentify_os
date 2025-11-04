"""Job API endpoints.

REST API for job management (create, list, get, cancel, retry).
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from scheduler.core.task_graph import ActionType, TaskGraph, ToDo
from scheduler.queue.job_queue import Job, JobQueue, JobStatus

logger = structlog.get_logger()

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# This will be set by main.py
def get_job_queue() -> JobQueue:
    """Get JobQueue instance (to be overridden by main.py)."""
    raise NotImplementedError("get_job_queue dependency not configured")


class TaskRequest(BaseModel):
    """Task request model for API."""

    action: ActionType = Field(..., description="Action type")
    selector: str = Field(..., description="Element selector or target")
    text: str | None = Field(None, description="Text to type or email body")
    timeout: float = Field(30.0, description="Timeout in seconds")
    depends_on: list[str] = Field(default_factory=list, description="Task IDs this task depends on")


class JobCreateRequest(BaseModel):
    """Job creation request model."""

    intent: str = Field(..., description="Intent name", min_length=1)
    tasks: dict[str, TaskRequest] = Field(..., description="Task graph (task_id -> task)")
    max_retries: int = Field(default=3, description="Maximum number of retries", ge=0, le=10)


class JobResponse(BaseModel):
    """Job response model."""

    id: str = Field(..., description="Job ID")
    intent: str = Field(..., description="Intent name")
    status: JobStatus = Field(..., description="Job status")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    started_at: str | None = Field(None, description="Start timestamp (ISO format)")
    completed_at: str | None = Field(None, description="Completion timestamp (ISO format)")
    error: str | None = Field(None, description="Error message if failed")
    retry_count: int = Field(..., description="Number of retries")
    max_retries: int = Field(..., description="Maximum number of retries")
    task_count: int = Field(..., description="Number of tasks in the job")


class JobListResponse(BaseModel):
    """Job list response model."""

    jobs: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")


def _job_to_response(job: Job) -> JobResponse:
    """Convert Job to JobResponse.

    Args:
        job: Job instance

    Returns:
        JobResponse instance
    """
    return JobResponse(
        id=job.id,
        intent=job.intent,
        status=job.status,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error=job.error,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        task_count=len(job.task_graph.tasks),
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> JobResponse:
    """Create a new job.

    Args:
        request: Job creation request
        job_queue: JobQueue instance (injected)

    Returns:
        Created job

    Raises:
        HTTPException: If job creation fails
    """
    try:
        # Build TaskGraph from request
        # We need to manually build the task graph with task IDs
        task_graph = TaskGraph()
        task_id_map: dict[str, str] = {}  # Map request task_id to generated task_id

        # First pass: add tasks without dependencies
        for req_task_id, task_req in request.tasks.items():
            if not task_req.depends_on:
                todo = ToDo(
                    action=task_req.action,
                    selector=task_req.selector,
                    text=task_req.text,
                    timeout=task_req.timeout,
                    depends_on=[],
                )
                generated_id = task_graph.add_task(todo)
                task_id_map[req_task_id] = generated_id

        # Second pass: add tasks with dependencies
        remaining_tasks = {
            req_task_id: task_req
            for req_task_id, task_req in request.tasks.items()
            if task_req.depends_on
        }

        while remaining_tasks:
            added_any = False
            for req_task_id, task_req in list(remaining_tasks.items()):
                # Check if all dependencies are satisfied
                if all(dep_id in task_id_map for dep_id in task_req.depends_on):
                    # Map dependency IDs
                    mapped_deps = [task_id_map[dep_id] for dep_id in task_req.depends_on]
                    todo = ToDo(
                        action=task_req.action,
                        selector=task_req.selector,
                        text=task_req.text,
                        timeout=task_req.timeout,
                        depends_on=mapped_deps,
                    )
                    generated_id = task_graph.add_task(todo)
                    task_id_map[req_task_id] = generated_id
                    del remaining_tasks[req_task_id]
                    added_any = True

            if not added_any and remaining_tasks:
                # Circular dependency or missing dependency
                raise ValueError("Circular dependency or missing dependency detected")

        # Create Job
        job = Job(
            intent=request.intent,
            task_graph=task_graph,
            max_retries=request.max_retries,
        )

        # Enqueue job
        await job_queue.enqueue(job)

        logger.info("job_created", job_id=job.id, intent=job.intent, task_count=len(task_graph.tasks))

        return _job_to_response(job)

    except ValueError as e:
        logger.error("job_creation_failed", error=str(e), intent=request.intent)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task graph: {e}",
        ) from e
    except Exception as e:
        logger.error("job_creation_failed", error=str(e), intent=request.intent, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job",
        ) from e


@router.get("", response_model=JobListResponse)
async def list_jobs(
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
    status_filter: JobStatus | None = Query(None, description="Filter by job status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
) -> JobListResponse:
    """List all jobs.

    Args:
        job_queue: JobQueue instance (injected)
        status_filter: Optional status filter
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip

    Returns:
        List of jobs
    """
    try:
        # Get all job IDs from Redis
        # For now, we'll use a simple pattern match
        # In production, you'd want to use a sorted set or index
        if not job_queue.redis:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis not connected",
            )

        # Get all job keys
        job_keys = await job_queue.redis.keys("job:*")
        jobs: list[Job] = []

        for key in job_keys:
            job_data = await job_queue.redis.get(key)
            if job_data:
                job_dict = Job.model_validate_json(job_data)
                jobs.append(job_dict)

        # Filter by status if provided
        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]

        # Sort by created_at (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        # Apply pagination
        total = len(jobs)
        jobs = jobs[offset : offset + limit]

        logger.info("jobs_listed", total=total, returned=len(jobs), status_filter=status_filter)

        return JobListResponse(
            jobs=[_job_to_response(job) for job in jobs],
            total=total,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_list_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list jobs",
        ) from e


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> JobResponse:
    """Get job by ID.

    Args:
        job_id: Job ID
        job_queue: JobQueue instance (injected)

    Returns:
        Job details

    Raises:
        HTTPException: If job not found
    """
    try:
        job = await job_queue.get_job(job_id)

        if not job:
            logger.warning("job_not_found", job_id=job_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        logger.info("job_retrieved", job_id=job_id, status=job.status)

        return _job_to_response(job)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_get_failed", job_id=job_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job",
        ) from e


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(
    job_id: str,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> None:
    """Cancel a job.

    Args:
        job_id: Job ID
        job_queue: JobQueue instance (injected)

    Raises:
        HTTPException: If job not found or already completed
    """
    try:
        # Get job first to check status
        job = await job_queue.get_job(job_id)

        if not job:
            logger.warning("job_not_found", job_id=job_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        # Check if job can be cancelled
        if job.status in [JobStatus.DONE, JobStatus.CANCELLED]:
            logger.warning("job_already_completed", job_id=job_id, status=job.status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} is already {job.status.value}",
            )

        # Cancel job
        await job_queue.cancel(job_id)

        logger.info("job_cancelled", job_id=job_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_cancel_failed", job_id=job_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel job",
        ) from e


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: str,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> JobResponse:
    """Retry a failed job.

    Args:
        job_id: Job ID
        job_queue: JobQueue instance (injected)

    Returns:
        Updated job

    Raises:
        HTTPException: If job not found, not failed, or max retries exceeded
    """
    try:
        # Get job first to check status
        job = await job_queue.get_job(job_id)

        if not job:
            logger.warning("job_not_found", job_id=job_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        # Check if job can be retried
        if job.status != JobStatus.FAILED:
            logger.warning("job_not_failed", job_id=job_id, status=job.status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} is not in failed state (current: {job.status.value})",
            )

        # Retry job
        success = await job_queue.retry(job_id)

        if not success:
            logger.warning("job_retry_failed_max_retries", job_id=job_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} has exceeded maximum retries",
            )

        # Get updated job
        updated_job = await job_queue.get_job(job_id)
        if not updated_job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated job",
            )

        logger.info("job_retried", job_id=job_id, retry_count=updated_job.retry_count)

        return _job_to_response(updated_job)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_retry_failed", job_id=job_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry job",
        ) from e

