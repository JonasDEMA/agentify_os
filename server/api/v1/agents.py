"""Agent management endpoints."""
import secrets
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.desktop_rpa.server_comm.models import (
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    AgentHeartbeatRequest,
    AgentHeartbeatResponse,
)
from server.core.config import settings
from server.db.database import get_db
from server.db.models import Agent

router = APIRouter()


def generate_agent_id() -> str:
    """Generate unique agent ID."""
    return f"agent_{secrets.token_hex(16)}"


def generate_api_key() -> str:
    """Generate API key."""
    return secrets.token_urlsafe(settings.API_KEY_LENGTH)


@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(
    request: AgentRegistrationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new agent.
    
    Args:
        request: Agent registration request
        db: Database session
        
    Returns:
        Registration response with agent ID and API key
    """
    # Generate agent ID and API key
    agent_id = generate_agent_id()
    api_key = generate_api_key()
    
    # Create agent record
    agent = Agent(
        id=agent_id,
        api_key=api_key,
        os_name=request.agent_info.os_name,
        os_version=request.agent_info.os_version,
        os_build=request.agent_info.os_build,
        os_locale=request.agent_info.os_locale,
        hostname=request.agent_info.hostname,
        cpu_count=request.agent_info.cpu_count,
        memory_total_gb=request.agent_info.memory_total_gb,
        screen_resolution=request.agent_info.screen_resolution,
        dpi_scaling=request.agent_info.dpi_scaling,
        ip_address=request.agent_info.ip_address,
        mac_address=request.agent_info.mac_address,
        port=request.agent_info.port,
        python_version=request.agent_info.python_version,
        agent_version=request.agent_info.agent_version,
        has_vision=request.agent_info.has_vision,
        has_ocr=request.agent_info.has_ocr,
        has_ui_automation=request.agent_info.has_ui_automation,
        phone_number=request.phone_number,
        is_active=True,
    )
    
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Return registration response
    return AgentRegistrationResponse(
        agent_id=agent_id,
        api_key=api_key,
        server_url=f"http://{settings.HOST}:{settings.PORT}",
        websocket_url=f"ws://{settings.HOST}:{settings.PORT}/ws",
        registered_at=agent.registered_at,
    )


@router.get("/")
async def list_agents(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all registered agents.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of agents
    """
    result = await db.execute(
        select(Agent).offset(skip).limit(limit).order_by(Agent.registered_at.desc())
    )
    agents = result.scalars().all()
    
    return [
        {
            "id": agent.id,
            "hostname": agent.hostname,
            "os_name": agent.os_name,
            "os_version": agent.os_version,
            "ip_address": agent.ip_address,
            "port": agent.port,
            "registered_at": agent.registered_at,
            "last_seen_at": agent.last_seen_at,
            "is_active": agent.is_active,
            "current_task": agent.current_task,
        }
        for agent in agents
    ]


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get agent details.
    
    Args:
        agent_id: Agent ID
        db: Database session
        
    Returns:
        Agent details
    """
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "id": agent.id,
        "hostname": agent.hostname,
        "os_name": agent.os_name,
        "os_version": agent.os_version,
        "os_build": agent.os_build,
        "os_locale": agent.os_locale,
        "cpu_count": agent.cpu_count,
        "memory_total_gb": agent.memory_total_gb,
        "screen_resolution": agent.screen_resolution,
        "dpi_scaling": agent.dpi_scaling,
        "ip_address": agent.ip_address,
        "mac_address": agent.mac_address,
        "port": agent.port,
        "python_version": agent.python_version,
        "agent_version": agent.agent_version,
        "has_vision": agent.has_vision,
        "has_ocr": agent.has_ocr,
        "has_ui_automation": agent.has_ui_automation,
        "phone_number": agent.phone_number,
        "registered_at": agent.registered_at,
        "last_seen_at": agent.last_seen_at,
        "is_active": agent.is_active,
        "current_task": agent.current_task,
    }


@router.post("/{agent_id}/heartbeat", response_model=AgentHeartbeatResponse)
async def agent_heartbeat(
    agent_id: str,
    request: AgentHeartbeatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update agent heartbeat and status.
    
    Args:
        agent_id: Agent ID
        request: Heartbeat request
        db: Database session
        
    Returns:
        Heartbeat response
    """
    if agent_id != request.agent_id:
        raise HTTPException(status_code=400, detail="Agent ID mismatch")
        
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status
    agent.is_active = request.status == "active"
    agent.current_task = request.current_task
    agent.last_seen_at = datetime.now()
    
    await db.commit()
    
    return AgentHeartbeatResponse(
        status="ok",
        next_check_in=30
    )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an agent registration.
    
    Args:
        agent_id: Agent ID
        db: Database session
        
    Returns:
        Success message
    """
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db.delete(agent)
    await db.commit()
    
    return {"status": "ok", "message": f"Agent {agent_id} deleted"}

