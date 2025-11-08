"""Log management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.desktop_rpa.server_comm.models import LogEntry as LogEntryModel
from server.db.database import get_db
from server.db.models import Agent, LogEntry

router = APIRouter()


async def verify_api_key(authorization: str = Header(...), db: AsyncSession = Depends(get_db)) -> str:
    """Verify API key and return agent ID.
    
    Args:
        authorization: Authorization header (Bearer token)
        db: Database session
        
    Returns:
        Agent ID
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    result = await db.execute(select(Agent).where(Agent.api_key == api_key))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Update last seen
    agent.last_seen_at = LogEntry.timestamp
    await db.commit()
    
    return agent.id


@router.post("/")
async def create_log(
    log: LogEntryModel,
    db: AsyncSession = Depends(get_db),
    agent_id: str = Depends(verify_api_key),
):
    """Create a new log entry.
    
    Args:
        log: Log entry data
        db: Database session
        agent_id: Agent ID (from API key)
        
    Returns:
        Created log entry
    """
    # Verify agent ID matches
    if log.agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Agent ID mismatch")
    
    # Create log entry
    log_entry = LogEntry(
        agent_id=log.agent_id,
        timestamp=log.timestamp,
        level=log.level,
        message=log.message,
        task_goal=log.task_goal,
        extra_data=log.metadata,  # Renamed from 'metadata'
    )
    
    db.add(log_entry)
    
    # Update agent's current task
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent and log.task_goal:
        agent.current_task = log.task_goal
    
    await db.commit()
    await db.refresh(log_entry)
    
    return {"id": log_entry.id, "status": "created"}


@router.get("/")
async def list_logs(
    db: AsyncSession = Depends(get_db),
    agent_id: str | None = None,
    level: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    """List log entries.
    
    Args:
        db: Database session
        agent_id: Filter by agent ID
        level: Filter by log level
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of log entries
    """
    query = select(LogEntry)
    
    if agent_id:
        query = query.where(LogEntry.agent_id == agent_id)
    
    if level:
        query = query.where(LogEntry.level == level)
    
    query = query.offset(skip).limit(limit).order_by(LogEntry.timestamp.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "agent_id": log.agent_id,
            "timestamp": log.timestamp,
            "level": log.level,
            "message": log.message,
            "task_goal": log.task_goal,
            "metadata": log.extra_data,  # Renamed from 'metadata'
        }
        for log in logs
    ]


@router.get("/{agent_id}/stream")
async def stream_logs(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    since_id: int = 0,
):
    """Stream logs for an agent since a specific ID.
    
    Args:
        agent_id: Agent ID
        db: Database session
        since_id: Return logs with ID greater than this
        
    Returns:
        List of new log entries
    """
    result = await db.execute(
        select(LogEntry)
        .where(LogEntry.agent_id == agent_id)
        .where(LogEntry.id > since_id)
        .order_by(LogEntry.timestamp.asc())
    )
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp,
            "level": log.level,
            "message": log.message,
            "task_goal": log.task_goal,
            "metadata": log.extra_data,  # Renamed from 'metadata'
        }
        for log in logs
    ]

