"""Screenshot Manager with mouse cursor overlay and before/after capture."""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

import pyautogui
from PIL import Image, ImageDraw
from pynput import mouse

from agents.desktop_rpa.config.settings import settings

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Manage screenshots with mouse cursor overlay and before/after capture."""
    
    def __init__(self, screenshot_dir: Path | None = None):
        """Initialize screenshot manager.
        
        Args:
            screenshot_dir: Directory to save screenshots (uses settings if None)
        """
        self.screenshot_dir = screenshot_dir or Path(settings.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Mouse controller
        self.mouse_controller = mouse.Controller()
        
        # Last screenshot info
        self.last_screenshot_path: Path | None = None
        self.last_action_type: str | None = None
    
    def get_mouse_position(self) -> tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return self.mouse_controller.position
    
    def capture_screenshot_with_cursor(
        self,
        action_type: Literal["before_click", "after_click", "before_type", "after_type", "general"] = "general",
        cursor_color: str = "red",
        cursor_size: int = 20,
    ) -> Path:
        """Capture screenshot with mouse cursor overlay.
        
        Args:
            action_type: Type of action (for filename)
            cursor_color: Color of cursor overlay (red, blue, green, yellow)
            cursor_size: Size of cursor overlay in pixels
            
        Returns:
            Path to saved screenshot
        """
        # Get mouse position
        mouse_x, mouse_y = self.get_mouse_position()
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Draw cursor overlay
        draw = ImageDraw.Draw(screenshot)
        
        # Color mapping
        color_map = {
            "red": "#FF0000",
            "blue": "#0000FF",
            "green": "#00FF00",
            "yellow": "#FFFF00",
            "orange": "#FF9800",
            "purple": "#9C27B0",
        }
        
        color = color_map.get(cursor_color, "#FF0000")
        
        # Draw crosshair cursor
        half_size = cursor_size // 2
        
        # Horizontal line
        draw.line(
            [(mouse_x - half_size, mouse_y), (mouse_x + half_size, mouse_y)],
            fill=color,
            width=3,
        )
        
        # Vertical line
        draw.line(
            [(mouse_x, mouse_y - half_size), (mouse_x, mouse_y + half_size)],
            fill=color,
            width=3,
        )
        
        # Draw circle around cursor
        draw.ellipse(
            [
                (mouse_x - half_size, mouse_y - half_size),
                (mouse_x + half_size, mouse_y + half_size),
            ],
            outline=color,
            width=2,
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds
        filename = f"screenshot_{action_type}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        # Save screenshot
        screenshot.save(filepath)
        
        # Update last screenshot info
        self.last_screenshot_path = filepath
        self.last_action_type = action_type
        
        logger.info(f"Screenshot saved: {filepath} (cursor at {mouse_x}, {mouse_y})")
        
        return filepath
    
    async def capture_before_action(
        self,
        action_type: Literal["click", "type"],
    ) -> Path:
        """Capture screenshot before an action.
        
        Args:
            action_type: Type of action (click or type)
            
        Returns:
            Path to saved screenshot
        """
        screenshot_type = f"before_{action_type}"
        return self.capture_screenshot_with_cursor(
            action_type=screenshot_type,
            cursor_color="blue",  # Blue for "before"
        )
    
    async def capture_after_action(
        self,
        action_type: Literal["click", "type"],
        delay_seconds: float = 3.0,
    ) -> Path:
        """Capture screenshot after an action with delay.
        
        Args:
            action_type: Type of action (click or type)
            delay_seconds: Delay in seconds before capturing (default: 3.0)
            
        Returns:
            Path to saved screenshot
        """
        # Wait for UI to update
        await asyncio.sleep(delay_seconds)
        
        screenshot_type = f"after_{action_type}"
        return self.capture_screenshot_with_cursor(
            action_type=screenshot_type,
            cursor_color="green",  # Green for "after"
        )
    
    async def capture_action_sequence(
        self,
        action_type: Literal["click", "type"],
        action_func,
        *action_args,
        after_delay: float = 3.0,
        **action_kwargs,
    ) -> tuple[Path, Path]:
        """Capture before and after screenshots for an action.
        
        Args:
            action_type: Type of action (click or type)
            action_func: Function to execute (e.g., pyautogui.click)
            *action_args: Positional arguments for action function
            after_delay: Delay in seconds after action (default: 3.0)
            **action_kwargs: Keyword arguments for action function
            
        Returns:
            Tuple of (before_screenshot_path, after_screenshot_path)
        """
        # Capture before
        before_path = await self.capture_before_action(action_type)
        
        # Execute action
        if asyncio.iscoroutinefunction(action_func):
            await action_func(*action_args, **action_kwargs)
        else:
            action_func(*action_args, **action_kwargs)
        
        # Capture after
        after_path = await self.capture_after_action(action_type, delay_seconds=after_delay)
        
        logger.info(f"Action sequence captured: {action_type}")
        logger.info(f"  Before: {before_path}")
        logger.info(f"  After: {after_path}")
        
        return before_path, after_path
    
    def get_recent_screenshots(self, limit: int = 10) -> list[Path]:
        """Get most recent screenshots.
        
        Args:
            limit: Maximum number of screenshots to return
            
        Returns:
            List of screenshot paths, sorted by modification time (newest first)
        """
        screenshots = sorted(
            self.screenshot_dir.glob("screenshot_*.png"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        
        return screenshots[:limit]
    
    def cleanup_old_screenshots(self, keep_count: int = 100):
        """Delete old screenshots, keeping only the most recent ones.
        
        Args:
            keep_count: Number of screenshots to keep
        """
        screenshots = sorted(
            self.screenshot_dir.glob("screenshot_*.png"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        
        # Delete old screenshots
        for screenshot in screenshots[keep_count:]:
            try:
                screenshot.unlink()
                logger.debug(f"Deleted old screenshot: {screenshot}")
            except Exception as e:
                logger.warning(f"Failed to delete screenshot {screenshot}: {e}")
        
        if len(screenshots) > keep_count:
            logger.info(f"Cleaned up {len(screenshots) - keep_count} old screenshots")


# Global instance
_screenshot_manager: ScreenshotManager | None = None


def get_screenshot_manager() -> ScreenshotManager:
    """Get global screenshot manager instance."""
    global _screenshot_manager
    
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    
    return _screenshot_manager

