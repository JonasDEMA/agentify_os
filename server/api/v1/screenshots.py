"""Screenshot management endpoints."""
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.desktop_rpa.server_comm.models import ScreenshotUpload
from server.api.v1.logs import verify_api_key
from server.core.config import settings
from server.db.database import get_db
from server.db.models import Screenshot

router = APIRouter()


@router.post("/")
async def upload_screenshot(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    db: AsyncSession = Depends(get_db),
    agent_id: str = Depends(verify_api_key),
):
    """Upload a screenshot.
    
    Args:
        file: Screenshot file
        metadata: Screenshot metadata (JSON)
        db: Database session
        agent_id: Agent ID (from API key)
        
    Returns:
        Upload confirmation
    """
    # Parse metadata
    screenshot_meta = ScreenshotUpload.model_validate_json(metadata)
    
    # Verify agent ID matches
    if screenshot_meta.agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Agent ID mismatch")
    
    # Save file
    screenshot_dir = Path(settings.SCREENSHOT_DIR) / agent_id
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = screenshot_dir / screenshot_meta.filename
    
    with file_path.open("wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create database record
    screenshot = Screenshot(
        agent_id=screenshot_meta.agent_id,
        timestamp=screenshot_meta.timestamp,
        action_type=screenshot_meta.action_type,
        mouse_x=screenshot_meta.mouse_x,
        mouse_y=screenshot_meta.mouse_y,
        task_goal=screenshot_meta.task_goal,
        filename=screenshot_meta.filename,
        file_path=str(file_path),
        file_size_bytes=screenshot_meta.file_size_bytes,
    )
    
    db.add(screenshot)
    await db.commit()
    await db.refresh(screenshot)
    
    return {
        "id": screenshot.id,
        "status": "uploaded",
        "url": f"/screenshots/{agent_id}/{screenshot_meta.filename}",
    }


@router.get("/")
async def list_screenshots(
    db: AsyncSession = Depends(get_db),
    agent_id: str | None = None,
    action_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    """List screenshots.
    
    Args:
        db: Database session
        agent_id: Filter by agent ID
        action_type: Filter by action type
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of screenshots
    """
    query = select(Screenshot)
    
    if agent_id:
        query = query.where(Screenshot.agent_id == agent_id)
    
    if action_type:
        query = query.where(Screenshot.action_type == action_type)
    
    query = query.offset(skip).limit(limit).order_by(Screenshot.timestamp.desc())
    
    result = await db.execute(query)
    screenshots = result.scalars().all()
    
    return [
        {
            "id": screenshot.id,
            "agent_id": screenshot.agent_id,
            "timestamp": screenshot.timestamp,
            "action_type": screenshot.action_type,
            "mouse_x": screenshot.mouse_x,
            "mouse_y": screenshot.mouse_y,
            "task_goal": screenshot.task_goal,
            "filename": screenshot.filename,
            "file_size_bytes": screenshot.file_size_bytes,
            "url": f"/screenshots/{screenshot.agent_id}/{screenshot.filename}",
        }
        for screenshot in screenshots
    ]


@router.get("/{agent_id}/latest")
async def get_latest_screenshots(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
):
    """Get latest screenshots for an agent.
    
    Args:
        agent_id: Agent ID
        db: Database session
        limit: Maximum number of screenshots to return
        
    Returns:
        List of latest screenshots
    """
    result = await db.execute(
        select(Screenshot)
        .where(Screenshot.agent_id == agent_id)
        .order_by(Screenshot.timestamp.desc())
        .limit(limit)
    )
    screenshots = result.scalars().all()
    
    return [
        {
            "id": screenshot.id,
            "timestamp": screenshot.timestamp,
            "action_type": screenshot.action_type,
            "mouse_x": screenshot.mouse_x,
            "mouse_y": screenshot.mouse_y,
            "task_goal": screenshot.task_goal,
            "filename": screenshot.filename,
            "url": f"/screenshots/{agent_id}/{screenshot.filename}",
        }
        for screenshot in screenshots
    ]

