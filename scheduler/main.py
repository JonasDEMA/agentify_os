"""FastAPI application entry point for CPA Scheduler."""

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from scheduler.api import jobs, lam_handler, audit, calculator
from scheduler.config.settings import settings
from scheduler.orchestrator.orchestrator import Orchestrator
from scheduler.queue.job_queue import JobQueue
from scheduler.telemetry.telemetry import TelemetryService

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

# Global state
job_queue: JobQueue | None = None
orchestrator: Orchestrator | None = None
telemetry: TelemetryService | None = None


def get_job_queue() -> JobQueue:
    """Dependency to get JobQueue instance.

    Returns:
        JobQueue instance

    Raises:
        HTTPException: If JobQueue is not initialized
    """
    if job_queue is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job queue not initialized",
        )
    return job_queue


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize Redis connection
    global job_queue, orchestrator, telemetry
    telemetry = TelemetryService()
    job_queue = JobQueue(redis_url=settings.redis_url)
    try:
        await job_queue.connect()
        logger.info("redis_connected", redis_url=settings.redis_url)

        # Initialize and start Orchestrator (unless disabled for calculator POC)
        disable_orch = os.getenv("DISABLE_ORCHESTRATOR", "").lower() in ("true", "1", "yes")
        if not disable_orch:
            orchestrator = Orchestrator(job_queue=job_queue, telemetry=telemetry)
            asyncio.create_task(orchestrator.start())
            logger.info("orchestrator_started")
        else:
            logger.info("orchestrator_disabled")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e), redis_url=settings.redis_url)
        # Don't fail startup, but log the error
        job_queue = None

    yield

    # Shutdown
    logger.info("application_shutdown")
    if orchestrator:
        await orchestrator.stop()
        logger.info("orchestrator_stopped")
    if job_queue:
        await job_queue.close()
        logger.info("redis_disconnected")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CPA Scheduler/Planner - Central orchestration component for Cognitive Process Automation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_methods_list,
    allow_headers=[settings.cors_allow_headers],
)

# Set dependency for jobs router
app.dependency_overrides[jobs.get_job_queue] = get_job_queue
app.dependency_overrides[calculator.get_job_queue] = get_job_queue

# Include routers
app.include_router(jobs.router)
app.include_router(lam_handler.router)
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(calculator.router, prefix="/api", tags=["Calculator"])


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        method=request.method,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status with component checks
    """
    health_status: dict[str, Any] = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "components": {},
    }

    # Check Redis connection
    redis_healthy = False
    redis_component: dict[str, Any] = {}

    if job_queue and job_queue.redis:
        try:
            await job_queue.redis.ping()
            redis_healthy = True
            redis_component = {
                "status": "healthy",
                "url": settings.redis_url,
            }
        except Exception as e:
            redis_component = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"
    else:
        redis_component = {
            "status": "not_connected",
        }
        health_status["status"] = "degraded"

    health_status["components"]["redis"] = redis_component

    logger.info(
        "health_check",
        status=health_status["status"],
        redis_healthy=redis_healthy,
    )

    return health_status


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

