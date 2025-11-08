"""Agent Client for server communication."""
import asyncio
import logging
import platform
import socket
from pathlib import Path
from typing import Any
from uuid import getnode

import httpx
from pydantic import BaseModel

from agents.desktop_rpa.server_comm.models import (
    AgentInfo,
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    LogEntry,
    ScreenshotUpload,
)

logger = logging.getLogger(__name__)


class AgentCredentials(BaseModel):
    """Stored agent credentials."""
    
    agent_id: str
    api_key: str
    server_url: str
    websocket_url: str


class AgentClient:
    """Client for communicating with CPA Server."""
    
    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        credentials_file: Path | None = None,
        timeout: float = 30.0,
    ):
        """Initialize agent client.
        
        Args:
            server_url: Base URL of CPA server
            credentials_file: Path to credentials file (default: .agent_credentials.json)
            timeout: HTTP request timeout in seconds
        """
        self.server_url = server_url.rstrip("/")
        self.credentials_file = credentials_file or Path(".agent_credentials.json")
        self.timeout = timeout
        
        # Credentials
        self.credentials: AgentCredentials | None = None
        self._load_credentials()
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=timeout)
    
    def _load_credentials(self):
        """Load credentials from file."""
        if self.credentials_file.exists():
            try:
                data = self.credentials_file.read_text()
                self.credentials = AgentCredentials.model_validate_json(data)
                logger.info(f"Loaded credentials for agent {self.credentials.agent_id}")
            except Exception as e:
                logger.warning(f"Failed to load credentials: {e}")
                self.credentials = None
    
    def _save_credentials(self, credentials: AgentCredentials):
        """Save credentials to file."""
        try:
            self.credentials_file.write_text(credentials.model_dump_json(indent=2))
            self.credentials = credentials
            logger.info(f"Saved credentials for agent {credentials.agent_id}")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def _get_system_info(self) -> AgentInfo:
        """Collect system information."""
        import psutil
        import screeninfo
        
        # OS info
        os_name = platform.system()
        os_version = platform.version()
        os_build = platform.release()
        os_locale = "de-DE"  # TODO: Get from system
        
        # Hardware
        hostname = socket.gethostname()
        cpu_count = psutil.cpu_count()
        memory_total_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        
        # Screen info
        try:
            monitors = screeninfo.get_monitors()
            primary = monitors[0] if monitors else None
            if primary:
                screen_resolution = f"{primary.width}x{primary.height}"
            else:
                screen_resolution = "unknown"
        except Exception:
            screen_resolution = "unknown"
        
        dpi_scaling = 1.0  # TODO: Get actual DPI scaling
        
        # Network
        try:
            ip_address = socket.gethostbyname(hostname)
        except Exception:
            ip_address = "unknown"
        
        mac_address = ":".join([f"{(getnode() >> i) & 0xff:02x}" for i in range(0, 48, 8)][::-1])
        
        # Software
        python_version = platform.python_version()
        agent_version = "0.1.0"  # TODO: Get from package
        
        return AgentInfo(
            os_name=os_name,
            os_version=os_version,
            os_build=os_build,
            os_locale=os_locale,
            hostname=hostname,
            cpu_count=cpu_count,
            memory_total_gb=memory_total_gb,
            screen_resolution=screen_resolution,
            dpi_scaling=dpi_scaling,
            ip_address=ip_address,
            mac_address=mac_address,
            python_version=python_version,
            agent_version=agent_version,
            has_vision=True,
            has_ocr=True,
            has_ui_automation=True,
        )
    
    async def register(self, phone_number: str | None = None) -> AgentRegistrationResponse:
        """Register agent with server.
        
        Args:
            phone_number: User's phone number for SMS
            
        Returns:
            Registration response with agent ID and API key
        """
        # Collect system info
        agent_info = self._get_system_info()
        
        # Create registration request
        request = AgentRegistrationRequest(
            agent_info=agent_info,
            phone_number=phone_number,
        )
        
        # Send registration request
        try:
            response = await self.client.post(
                f"{self.server_url}/api/v1/agents/register",
                json=request.model_dump(mode="json"),
            )
            response.raise_for_status()
            
            # Parse response
            registration = AgentRegistrationResponse.model_validate(response.json())
            
            # Save credentials
            credentials = AgentCredentials(
                agent_id=registration.agent_id,
                api_key=registration.api_key,
                server_url=registration.server_url,
                websocket_url=registration.websocket_url,
            )
            self._save_credentials(credentials)
            
            logger.info(f"Agent registered successfully: {registration.agent_id}")
            
            return registration
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to register agent: {e}")
            raise
    
    async def send_log(self, level: str, message: str, task_goal: str | None = None, metadata: dict[str, Any] | None = None):
        """Send log entry to server.
        
        Args:
            level: Log level (info, warning, error, success, thinking)
            message: Log message
            task_goal: Current task goal
            metadata: Additional metadata
        """
        if not self.credentials:
            logger.warning("No credentials available, skipping log send")
            return
        
        log_entry = LogEntry(
            agent_id=self.credentials.agent_id,
            level=level,
            message=message,
            task_goal=task_goal,
            metadata=metadata or {},
        )
        
        try:
            response = await self.client.post(
                f"{self.server_url}/api/v1/logs",
                json=log_entry.model_dump(mode="json"),
                headers={"Authorization": f"Bearer {self.credentials.api_key}"},
            )
            response.raise_for_status()
            
        except httpx.HTTPError as e:
            logger.debug(f"Failed to send log: {e}")
    
    async def upload_screenshot(
        self,
        screenshot_path: Path,
        action_type: str,
        mouse_x: int,
        mouse_y: int,
        task_goal: str | None = None,
    ):
        """Upload screenshot to server.
        
        Args:
            screenshot_path: Path to screenshot file
            action_type: Action type (before_click, after_click, etc.)
            mouse_x: Mouse X coordinate
            mouse_y: Mouse Y coordinate
            task_goal: Current task goal
        """
        if not self.credentials:
            logger.warning("No credentials available, skipping screenshot upload")
            return
        
        if not screenshot_path.exists():
            logger.error(f"Screenshot file not found: {screenshot_path}")
            return
        
        # Create metadata
        metadata = ScreenshotUpload(
            agent_id=self.credentials.agent_id,
            action_type=action_type,
            mouse_x=mouse_x,
            mouse_y=mouse_y,
            task_goal=task_goal,
            filename=screenshot_path.name,
            file_size_bytes=screenshot_path.stat().st_size,
        )
        
        try:
            # Upload file with metadata
            with screenshot_path.open("rb") as f:
                files = {"file": (screenshot_path.name, f, "image/png")}
                data = {"metadata": metadata.model_dump_json()}
                
                response = await self.client.post(
                    f"{self.server_url}/api/v1/screenshots",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {self.credentials.api_key}"},
                )
                response.raise_for_status()
            
            logger.info(f"Screenshot uploaded: {screenshot_path.name}")
            
        except httpx.HTTPError as e:
            logger.debug(f"Failed to upload screenshot: {e}")
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    @property
    def is_registered(self) -> bool:
        """Check if agent is registered."""
        return self.credentials is not None
    
    @property
    def agent_id(self) -> str | None:
        """Get agent ID."""
        return self.credentials.agent_id if self.credentials else None

