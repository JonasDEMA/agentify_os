"""Desktop RPA Agent - FastAPI Application."""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

import pyautogui
import structlog
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agents.desktop_rpa.config.settings import settings
from agents.desktop_rpa.executors import (
    ClickExecutor,
    ScreenshotExecutor,
    TypeExecutor,
    WaitExecutor,
)

# Configure PyAutoGUI
pyautogui.PAUSE = settings.pyautogui_pause
pyautogui.FAILSAFE = settings.pyautogui_failsafe

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# Request/Response Models
class TaskRequest(BaseModel):
    """Task request from scheduler."""

    task_id: str = Field(..., description="Unique task ID")
    action: str = Field(..., description="Action type (click, type, wait_for, screenshot)")
    selector: str = Field(..., description="Element selector or target")
    text: str | None = Field(None, description="Text to type")
    timeout: float = Field(default=30.0, description="Timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskResponse(BaseModel):
    """Task response to scheduler."""

    task_id: str = Field(..., description="Task ID")
    success: bool = Field(..., description="Whether task succeeded")
    message: str = Field(..., description="Result message")
    data: dict[str, Any] = Field(default_factory=dict, description="Result data")
    error: str | None = Field(None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Agent version")
    capabilities: list[str] = Field(..., description="Supported action types")


# Executor registry
executors: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Application lifespan manager."""
    # Startup
    logger.info(
        "desktop_rpa_agent_starting",
        agent_id=settings.agent_id,
        version=settings.agent_version,
    )

    # Initialize executors
    executors["click"] = ClickExecutor(timeout=settings.default_timeout)
    executors["type"] = TypeExecutor(timeout=settings.default_timeout)
    executors["wait_for"] = WaitExecutor(timeout=settings.default_timeout)
    executors["screenshot"] = ScreenshotExecutor(
        timeout=settings.default_timeout,
        screenshot_dir=settings.screenshot_dir,
    )

    logger.info(
        "executors_initialized",
        executors=list(executors.keys()),
    )

    yield

    # Shutdown
    logger.info("desktop_rpa_agent_stopping")


# Create FastAPI app
app = FastAPI(
    title="Desktop RPA Agent",
    description="Specialized agent for local desktop automation",
    version=settings.agent_version,
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent_id=settings.agent_id,
        agent_name=settings.agent_name,
        version=settings.agent_version,
        capabilities=list(executors.keys()),
    )


@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest) -> TaskResponse:
    """Execute a task.

    This endpoint receives task requests from the scheduler and executes them
    using the appropriate executor.

    Args:
        request: Task request with action, selector, text, etc.

    Returns:
        TaskResponse with execution result
    """
    logger.info(
        "task_received",
        task_id=request.task_id,
        action=request.action,
        selector=request.selector,
    )

    # Get executor for action type
    executor = executors.get(request.action)
    if not executor:
        logger.error(
            "unsupported_action",
            task_id=request.task_id,
            action=request.action,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported action type: {request.action}",
        )

    # Execute action
    try:
        result = await executor.execute(
            selector=request.selector,
            text=request.text,
            timeout=request.timeout,
        )

        logger.info(
            "task_completed",
            task_id=request.task_id,
            success=result.success,
            message=result.message,
        )

        return TaskResponse(
            task_id=request.task_id,
            success=result.success,
            message=result.message,
            data=result.data,
            error=result.error,
        )

    except Exception as e:
        logger.error(
            "task_failed",
            task_id=request.task_id,
            error=str(e),
        )
        return TaskResponse(
            task_id=request.task_id,
            success=False,
            message=f"Task execution failed: {e}",
            error=str(e),
        )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "agent": settings.agent_name,
        "version": settings.agent_version,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agents.desktop_rpa.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )

