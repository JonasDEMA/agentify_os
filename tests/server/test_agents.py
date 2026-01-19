"""Tests for Agent management API endpoints."""
import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import httpx
from server.main import app
from server.db.database import get_db, Base
from server.db.models import Agent

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def test_db():
    """Create a fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db):
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    
    # Use ASGITransport for modern httpx versions
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def sample_agent_info():
    """Sample agent info for registration."""
    return {
        "os_name": "Windows",
        "os_version": "11",
        "os_build": "22621",
        "os_locale": "en-US",
        "hostname": "test-host",
        "cpu_count": 8,
        "memory_total_gb": 16.0,
        "screen_resolution": "1920x1080",
        "dpi_scaling": 1.0,
        "ip_address": "127.0.0.1",
        "mac_address": "00:00:00:00:00:00",
        "python_version": "3.12.0",
        "agent_version": "0.1.0",
        "has_vision": True,
        "has_ocr": True,
        "has_ui_automation": True,
    }


@pytest.mark.asyncio
async def test_register_agent(client, sample_agent_info):
    """Test successful agent registration."""
    response = await client.post(
        "/api/v1/agents/register",
        json={
            "agent_info": sample_agent_info,
            "phone_number": "+1234567890"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "agent_id" in data
    assert "api_key" in data
    assert "registered_at" in data
    assert data["agent_id"].startswith("agent_")


@pytest.mark.asyncio
async def test_list_agents(client, sample_agent_info):
    """Test listing agents."""
    # Register an agent first
    await client.post(
        "/api/v1/agents/register",
        json={"agent_info": sample_agent_info}
    )
    
    response = await client.get("/api/v1/agents/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["hostname"] == "test-host"


@pytest.mark.asyncio
async def test_get_agent(client, sample_agent_info):
    """Test getting agent details."""
    # Register an agent first
    reg_resp = (await client.post(
        "/api/v1/agents/register",
        json={"agent_info": sample_agent_info}
    )).json()
    agent_id = reg_resp["agent_id"]
    
    response = await client.get(f"/api/v1/agents/{agent_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == agent_id
    assert data["hostname"] == "test-host"


@pytest.mark.asyncio
async def test_get_agent_not_found(client):
    """Test getting non-existent agent."""
    response = await client.get("/api/v1/agents/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_agent_heartbeat(client, sample_agent_info):
    """Test agent heartbeat."""
    # Register an agent first
    reg_resp = (await client.post(
        "/api/v1/agents/register",
        json={"agent_info": sample_agent_info}
    )).json()
    agent_id = reg_resp["agent_id"]
    
    response = await client.post(
        f"/api/v1/agents/{agent_id}/heartbeat",
        json={
            "agent_id": agent_id,
            "status": "active",
            "current_task": "testing"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    
    # Verify update
    agent_resp = (await client.get(f"/api/v1/agents/{agent_id}")).json()
    assert agent_resp["current_task"] == "testing"
    assert agent_resp["is_active"] is True


@pytest.mark.asyncio
async def test_delete_agent(client, sample_agent_info):
    """Test deleting an agent."""
    # Register an agent first
    reg_resp = (await client.post(
        "/api/v1/agents/register",
        json={"agent_info": sample_agent_info}
    )).json()
    agent_id = reg_resp["agent_id"]
    
    # Delete agent
    response = await client.delete(f"/api/v1/agents/{agent_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify deletion
    response = await client.get(f"/api/v1/agents/{agent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
