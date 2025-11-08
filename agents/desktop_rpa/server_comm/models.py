"""Data models for server communication."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    """Agent system information."""
    
    # Operating System
    os_name: str = Field(..., description="Operating system name (e.g., 'Windows', 'Linux', 'Darwin')")
    os_version: str = Field(..., description="OS version (e.g., '11', '10.0.22621')")
    os_build: str = Field(..., description="OS build number (e.g., '22621.2715')")
    os_locale: str = Field(..., description="OS locale (e.g., 'de-DE', 'en-US')")
    
    # Hardware
    hostname: str = Field(..., description="Computer hostname")
    cpu_count: int = Field(..., description="Number of CPU cores")
    memory_total_gb: float = Field(..., description="Total RAM in GB")
    screen_resolution: str = Field(..., description="Screen resolution (e.g., '1920x1080')")
    dpi_scaling: float = Field(..., description="DPI scaling factor (e.g., 1.0, 1.25, 1.5)")
    
    # Network
    ip_address: str = Field(..., description="Local IP address")
    mac_address: str = Field(..., description="MAC address")
    
    # Software
    python_version: str = Field(..., description="Python version (e.g., '3.12.0')")
    agent_version: str = Field(..., description="CPA Agent version")
    
    # Capabilities
    has_vision: bool = Field(default=True, description="Vision Layer available")
    has_ocr: bool = Field(default=True, description="OCR available")
    has_ui_automation: bool = Field(default=True, description="UI Automation available")


class AgentRegistrationRequest(BaseModel):
    """Agent registration request."""
    
    agent_info: AgentInfo = Field(..., description="Agent system information")
    phone_number: str | None = Field(None, description="User's phone number for SMS")


class AgentRegistrationResponse(BaseModel):
    """Agent registration response."""
    
    agent_id: str = Field(..., description="Unique agent ID assigned by server")
    api_key: str = Field(..., description="API key for authentication")
    server_url: str = Field(..., description="Server base URL")
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")
    registered_at: datetime = Field(..., description="Registration timestamp")


class LogEntry(BaseModel):
    """Log entry to send to server."""
    
    agent_id: str = Field(..., description="Agent ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    level: str = Field(..., description="Log level (info, warning, error, success, thinking)")
    message: str = Field(..., description="Log message")
    task_goal: str | None = Field(None, description="Current task goal")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ScreenshotUpload(BaseModel):
    """Screenshot upload metadata."""
    
    agent_id: str = Field(..., description="Agent ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Screenshot timestamp")
    action_type: str = Field(..., description="Action type (before_click, after_click, etc.)")
    mouse_x: int = Field(..., description="Mouse X coordinate")
    mouse_y: int = Field(..., description="Mouse Y coordinate")
    task_goal: str | None = Field(None, description="Current task goal")
    filename: str = Field(..., description="Screenshot filename")
    file_size_bytes: int = Field(..., description="File size in bytes")

