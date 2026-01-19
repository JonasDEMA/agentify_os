"""Windows API Integration - UI Automation for Windows applications."""
import logging
import platform
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Conditional imports for Windows
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    try:
        from pywinauto import Desktop, Application
    except ImportError:
        logger.warning("pywinauto not installed. Windows UI Automation will be unavailable.")
        Desktop = None
        Application = None
else:
    Desktop = None
    Application = None

class WindowsAPI:
    """Wrapper for Windows UI Automation using pywinauto."""

    def __init__(self):
        """Initialize Windows API."""
        self.enabled = IS_WINDOWS and Desktop is not None
        if not self.enabled:
            logger.info("Windows API disabled (not on Windows or pywinauto missing)")

    def get_visible_windows(self) -> List[Dict[str, Any]]:
        """Get a list of all visible windows and their titles.

        Returns:
            List of window info dictionaries
        """
        if not self.enabled:
            return []

        try:
            windows = Desktop(backend="uia").windows()
            return [
                {
                    "title": w.window_text(),
                    "class_name": w.class_name(),
                    "handle": w.handle,
                    "is_visible": w.is_visible(),
                }
                for w in windows if w.window_text()
            ]
        except Exception as e:
            logger.error(f"Failed to get visible windows: {e}")
            return []

    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get the currently active (foreground) window.

        Returns:
            Window info dictionary or None
        """
        if not self.enabled:
            return None

        try:
            # Note: pywinauto doesn't have a direct "get foreground" in Desktop
            # but we can try to find the one with focus
            windows = Desktop(backend="uia").windows()
            for w in windows:
                if w.has_focus():
                    return {
                        "title": w.window_text(),
                        "class_name": w.class_name(),
                        "handle": w.handle,
                    }
            return None
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None

    def find_elements(self, window_title: str, control_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find GUI elements in a specific window.

        Args:
            window_title: Title of the window to search in
            control_type: Optional filter for control type (e.g., 'Button', 'Edit')

        Returns:
            List of element info dictionaries
        """
        if not self.enabled:
            return []

        try:
            app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=5)
            win = app.window(title_re=f".*{window_title}.*")
            
            elements = []
            # This is a bit simplified; real pywinauto usage for finding all elements 
            # can be complex depending on depth.
            descendants = win.descendants(control_type=control_type) if control_type else win.descendants()
            
            for el in descendants:
                try:
                    rect = el.rectangle()
                    elements.append({
                        "name": el.window_text(),
                        "control_type": el.control_type(),
                        "x": rect.left,
                        "y": rect.top,
                        "width": rect.width(),
                        "height": rect.height(),
                        "is_enabled": el.is_enabled(),
                        "is_visible": el.is_visible(),
                    })
                except Exception:
                    continue
            
            return elements
        except Exception as e:
            logger.error(f"Failed to find elements in window '{window_title}': {e}")
            return []
