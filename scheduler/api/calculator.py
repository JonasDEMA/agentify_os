"""Calculator API endpoints."""
from typing import Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import asyncio

from scheduler.queue.job_queue import JobQueue, Job, JobStatus
from scheduler.core.task_graph import TaskGraph, ToDo, ActionType

router = APIRouter()

def get_job_queue() -> JobQueue:
    """Dependency placeholder - will be overridden in main.py."""
    raise NotImplementedError()

class CalculateRequest(BaseModel):
    """Calculate request model."""
    num1: float
    num2: float
    operator: str
    locale: str = "en-US"
    decimals: int = 2

class CalculateResponse(BaseModel):
    """Calculate response model."""
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    """Job status response model."""
    job_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None

@router.post("/calculate", response_model=CalculateResponse, status_code=202)
async def create_calculation(
    request: CalculateRequest,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)]
):
    """Create a new calculation job."""
    # Create a simple task graph with one calculator task  
    task_graph = TaskGraph()
    task_id = task_graph.add_task(
        ToDo(
            action=ActionType.TOOL,
            selector=f"calculator:{request.operator}:{request.num1}:{request.num2}:{request.locale}:{request.decimals}",
            text=f"{request.num1} {request.operator} {request.num2}",
            timeout=30.0,
            depends_on=[]
        )
    )
    
    # Create job with proper fields
    job = Job(
        intent="calculate",
        task_graph=task_graph,
        status=JobStatus.PENDING
    )
    
    # Add to queue
    await job_queue.enqueue(job)
    
    return CalculateResponse(
        job_id=job.id,
        status=job.status.value
    )

@router.get("/calculate/{job_id}", response_model=JobStatusResponse)
async def get_calculation_status(
    job_id: str,
    job_queue: Annotated[JobQueue, Depends(get_job_queue)]
):
    """Get status of a calculation job."""
    job = await job_queue.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Extract result from Redis if available
    result = None
    if job.status == JobStatus.DONE:
        # Get the full job data from Redis which includes the result
        import json
        job_key = job_queue._get_job_key(job_id)
        job_data_bytes = await job_queue.redis.get(job_key)
        if job_data_bytes:
            job_data = job_data_bytes.decode() if isinstance(job_data_bytes, bytes) else job_data_bytes
            job_dict = json.loads(job_data)
            result = job_dict.get("result")
    
    return JobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        result=result,
        error=job.error
    )
