"""CPA Server - FastAPI application for agent monitoring."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.api.v1 import agents, logs, screenshots
from server.core.config import settings
from server.db.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CPA Server...")
    
    # Initialize database
    await init_db()
    
    # Create upload directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
    
    logger.info("CPA Server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CPA Server...")


# Create FastAPI app
app = FastAPI(
    title="CPA Server",
    description="Agent monitoring and management server for Agentify CPA",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(screenshots.router, prefix="/api/v1/screenshots", tags=["screenshots"])

# Static files (for web UI)
if Path("server/static").exists():
    app.mount("/static", StaticFiles(directory="server/static"), name="static")

# Screenshots (for viewing)
if Path(settings.SCREENSHOT_DIR).exists():
    app.mount("/screenshots", StaticFiles(directory=settings.SCREENSHOT_DIR), name="screenshots")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CPA Server",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

