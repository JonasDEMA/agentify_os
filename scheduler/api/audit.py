"""Audit API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
import os

from scheduler.audit.audit_log import AuditLogService, AuditEntry
from scheduler.repository.sqlite_repository import SQLiteAuditRepository
from scheduler.config.settings import settings

router = APIRouter()

# Dependency for AuditLogService
async def get_audit_service() -> AuditLogService:
    # In a real app, this would use a proper session factory
    # For now, we'll use a placeholder or the one from database setup
    # Note: TestingSessionLocal is just for demo, we'd normally use AsyncSessionLocal
    from scheduler.repository.sqlite_repository import sessionmaker, AsyncSession, create_async_engine
    engine = create_async_engine(settings.database_url)
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    repo = SQLiteAuditRepository(factory)
    return AuditLogService(repo, screenshot_dir=os.path.join(settings.UPLOAD_DIR, "screenshots"))

@router.get("/{job_id}", response_model=List[AuditEntry])
async def get_job_audit_logs(
    job_id: str,
    service: AuditLogService = Depends(get_audit_service)
):
    """Get audit logs for a specific job."""
    logs = await service.get_job_logs(job_id)
    if not logs:
        # Check if job exists at least (optional)
        return []
    return logs

@router.get("/screenshots/{job_id}/{filename}")
async def get_audit_screenshot(
    job_id: str,
    filename: str
):
    """Retrieve a specific screenshot."""
    screenshot_path = os.path.join(settings.UPLOAD_DIR, "screenshots", job_id, filename)
    if not os.path.exists(screenshot_path):
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(screenshot_path)
