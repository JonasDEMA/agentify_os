"""Database models."""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, Boolean
from sqlalchemy.sql import func

from server.db.database import Base


class Agent(Base):
    """Agent model."""
    
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True, nullable=False)
    
    # System info
    os_name = Column(String, nullable=False)
    os_version = Column(String, nullable=False)
    os_build = Column(String, nullable=False)
    os_locale = Column(String, nullable=False)
    
    hostname = Column(String, nullable=False)
    cpu_count = Column(Integer, nullable=False)
    memory_total_gb = Column(Float, nullable=False)
    screen_resolution = Column(String, nullable=False)
    dpi_scaling = Column(Float, nullable=False)
    
    ip_address = Column(String, nullable=False)
    mac_address = Column(String, nullable=False)
    port = Column(Integer, nullable=True)  # Port the agent is listening on
    
    python_version = Column(String, nullable=False)
    agent_version = Column(String, nullable=False)
    
    has_vision = Column(Boolean, default=True)
    has_ocr = Column(Boolean, default=True)
    has_ui_automation = Column(Boolean, default=True)
    
    # Contact
    phone_number = Column(String, nullable=True)
    
    # Timestamps
    registered_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    current_task = Column(String, nullable=True)


class LogEntry(Base):
    """Log entry model."""

    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)

    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    task_goal = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved word)


class Screenshot(Base):
    """Screenshot model."""
    
    __tablename__ = "screenshots"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    action_type = Column(String, nullable=False)
    mouse_x = Column(Integer, nullable=False)
    mouse_y = Column(Integer, nullable=False)
    task_goal = Column(String, nullable=True)
    
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

