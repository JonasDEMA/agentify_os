"""Calculator API endpoints.

REST API for calculator operations.
"""

import sys
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# Add parent directory to path to support both local and Docker execution
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Try importing with scheduler prefix (local), fall back to direct import (Docker)
try:
    from scheduler.core.task_graph import TaskGraph
    from scheduler.job_queue.job_queue import Job, JobQueue
except ImportError:
    from core.task_graph import TaskGraph
    from job_queue.job_queue import Job, JobQueue

logger = structlog.get_logger()

router = APIRouter(prefix="/api/calculate", tags=["Calculator"])


# This will be set by main.py
def get_job_queue() -> JobQueue:
    """Get JobQueue instance (to be overridden by main.py)."""
    raise NotImplementedError("get_job_queue dependency not configured")


class CalculateRequest(BaseModel):
    """Calculator request model."""

    num1: float = Field(..., description="First number")
    num2: float = Field(..., description="Second number")
    operator: str = Field(..., description="Operator (add, subtract, multiply, divide)")
    locale: str = Field(default="en-US", description="Locale for formatting (en-US, de-DE, fr-FR)")
    decimals: int = Field(default=2, description="Number of decimal places", ge=0, le=10)


class CalculateResponse(BaseModel):
    """Calculator response model."""

    job_id: str = Field(..., description="Job ID for tracking")
    status: str = Field(..., description="Job status")


class JobStatusResponse(BaseModel):
    """Job status response model."""

    job_id: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status (pending, running, done, failed)")
    result: str | None = Field(None, description="Formatted calculation result")
    error: str | None = Field(None, description="Error message if failed")


@router.post("", response_model=CalculateResponse, status_code=status.HTTP_202_ACCEPTED)
async def calculate(
    request: CalculateRequest,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> CalculateResponse:
    """Create a calculation job.

    Args:
        request: Calculation request
        job_queue: JobQueue instance (injected)

    Returns:
        Job ID and status

    Raises:
        HTTPException: If job creation fails
    """
    try:
        # Create empty task graph (coordinator will handle the flow)
        task_graph = TaskGraph()

        # Create job with calculation parameters in metadata
        job = Job(
            intent="calculate",
            task_graph=task_graph,
            max_retries=3,
        )

        # Store calculation parameters in job result (will be used by coordinator)
        job.result = {
            "num1": request.num1,
            "num2": request.num2,
            "operator": request.operator,
            "locale": request.locale,
            "decimals": request.decimals,
        }

        # Enqueue job
        await job_queue.enqueue(job)

        logger.info(
            "calculation_job_created",
            job_id=job.id,
            num1=request.num1,
            num2=request.num2,
            operator=request.operator,
        )

        return CalculateResponse(
            job_id=job.id,
            status=job.status.value,
        )

    except Exception as e:
        logger.error("calculation_job_creation_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create calculation job",
        ) from e


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> JobStatusResponse:
    """Get calculation job status.

    Args:
        job_id: Job ID
        job_queue: JobQueue instance (injected)

    Returns:
        Job status and result

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

        # Extract result if job is done
        result = None
        if job.status.value == "done" and job.result:
            result = job.result.get("formatted_result")

        logger.info("job_status_retrieved", job_id=job_id, status=job.status.value)

        return JobStatusResponse(
            job_id=job.id,
            status=job.status.value,
            result=result,
            error=job.error,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("job_status_retrieval_failed", job_id=job_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status",
        ) from e

