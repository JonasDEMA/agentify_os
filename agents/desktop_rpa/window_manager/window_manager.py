"""Window Manager for intelligent window detection and management.

This module provides:
- Detection of already open windows
- Reusing existing windows instead of opening new ones
- Bringing windows to foreground
- User prompts for critical actions (close, save, etc.)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class OpenWindow:
    """Represents an open window."""

    title: str
    class_name: str
    process_id: int
    x: int
    y: int
    width: int
    height: int
    is_visible: bool = True
    is_active: bool = False
    detected_at: datetime = field(default_factory=datetime.now)

    @property
    def app_name(self) -> str:
        """Extract application name from title or class name."""
        # Common patterns
        if "notepad" in self.title.lower() or "notepad" in self.class_name.lower():
            return "Notepad"
        elif "calculator" in self.title.lower() or "calculator" in self.class_name.lower():
            return "Calculator"
        elif "outlook" in self.title.lower() or "outlook" in self.class_name.lower():
            return "Outlook"
        elif "excel" in self.title.lower() or "excel" in self.class_name.lower():
            return "Excel"
        elif "word" in self.title.lower() or "word" in self.class_name.lower():
            return "Word"
        elif "powerpoint" in self.title.lower() or "powerpoint" in self.class_name.lower():
            return "PowerPoint"
        elif "chrome" in self.title.lower() or "chrome" in self.class_name.lower():
            return "Chrome"
        elif "firefox" in self.title.lower() or "firefox" in self.class_name.lower():
            return "Firefox"
        elif "edge" in self.title.lower() or "edge" in self.class_name.lower():
            return "Edge"
        elif "explorer" in self.title.lower() or "explorer" in self.class_name.lower():
            return "File Explorer"
        else:
            # Extract from title (before " - ")
            if " - " in self.title:
                return self.title.split(" - ")[-1]
            return self.title or self.class_name


@dataclass
class UserPrompt:
    """Represents a user prompt for critical actions."""

    prompt_type: str  # "close_window", "save_document", "confirm_action"
    message: str
    window: OpenWindow | None = None
    options: list[str] = field(default_factory=lambda: ["Yes", "No", "Cancel"])
    default_option: str = "Cancel"
    requires_sms: bool = False  # Whether to send SMS notification


class WindowManager:
    """Manages window detection, reuse, and user prompts."""

    def __init__(self):
        """Initialize Window Manager."""
        self.desktop = Desktop(backend="uia")
        self.open_windows: dict[str, OpenWindow] = {}
        self.pending_prompts: list[UserPrompt] = []
        logger.info("Window Manager initialized")

    def detect_open_windows(self) -> list[OpenWindow]:
        """Detect all currently open windows.

        Returns:
            List of OpenWindow objects
        """
        windows = []
        try:
            for window in self.desktop.windows():
                try:
                    if window.is_visible():
                        rect = window.rectangle()
                        process_id = window.process_id()

                        open_window = OpenWindow(
                            title=window.window_text(),
                            class_name=window.class_name(),
                            process_id=process_id,
                            x=rect.left,
                            y=rect.top,
                            width=rect.width(),
                            height=rect.height(),
                            is_visible=True,
                            is_active=window.has_focus(),
                        )

                        windows.append(open_window)

                        # Store in cache
                        self.open_windows[open_window.app_name] = open_window

                except Exception as e:
                    logger.debug(f"Error getting window info: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error detecting windows: {e}")

        logger.info(f"Detected {len(windows)} open windows")
        return windows

    def is_app_open(self, app_name: str) -> OpenWindow | None:
        """Check if an application is already open.

        Args:
            app_name: Application name (e.g., "Notepad", "Outlook")

        Returns:
            OpenWindow if found, None otherwise
        """
        # Refresh window list
        self.detect_open_windows()

        # Check cache
        for name, window in self.open_windows.items():
            if app_name.lower() in name.lower():
                logger.info(f"Found open window: {name} (title: {window.title})")
                return window

        logger.info(f"Application not open: {app_name}")
        return None

    def bring_to_foreground(self, window: OpenWindow) -> bool:
        """Bring a window to the foreground.

        Args:
            window: OpenWindow to bring to foreground

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find window by title
            pywin_window = self.desktop.window(title_re=f".*{window.title}.*")

            if pywin_window:
                # Set focus
                pywin_window.set_focus()
                logger.info(f"Brought window to foreground: {window.title}")
                return True

        except ElementNotFoundError:
            logger.warning(f"Window not found: {window.title}")
        except Exception as e:
            logger.error(f"Error bringing window to foreground: {e}")

        return False

    def find_window_by_app(self, app_name: str) -> OpenWindow | None:
        """Find window by application name.

        Args:
            app_name: Application name (e.g., "Notepad", "Outlook")

        Returns:
            OpenWindow if found, None otherwise
        """
        # Common title patterns
        patterns = {
            "notepad": ["Notepad", "Untitled - Notepad"],
            "calculator": ["Calculator"],
            "outlook": ["Outlook", "Microsoft Outlook"],
            "excel": ["Excel", "Microsoft Excel"],
            "word": ["Word", "Microsoft Word"],
            "powerpoint": ["PowerPoint", "Microsoft PowerPoint"],
            "chrome": ["Chrome", "Google Chrome"],
            "firefox": ["Firefox", "Mozilla Firefox"],
            "edge": ["Edge", "Microsoft Edge"],
            "explorer": ["File Explorer", "Windows Explorer"],
        }

        app_lower = app_name.lower()
        search_patterns = patterns.get(app_lower, [app_name])

        try:
            for pattern in search_patterns:
                try:
                    window = self.desktop.window(title_re=f".*{pattern}.*")
                    if window and window.is_visible():
                        rect = window.rectangle()
                        return OpenWindow(
                            title=window.window_text(),
                            class_name=window.class_name(),
                            process_id=window.process_id(),
                            x=rect.left,
                            y=rect.top,
                            width=rect.width(),
                            height=rect.height(),
                            is_visible=True,
                            is_active=window.has_focus(),
                        )
                except ElementNotFoundError:
                    continue

        except Exception as e:
            logger.error(f"Error finding window: {e}")

        return None

    def create_close_prompt(self, window: OpenWindow, reason: str = "") -> UserPrompt:
        """Create a user prompt for closing a window.

        Args:
            window: Window to close
            reason: Reason for closing

        Returns:
            UserPrompt object
        """
        message = f"The application '{window.app_name}' is currently open."
        if reason:
            message += f"\n\nReason: {reason}"
        message += "\n\nWhat would you like to do?"

        return UserPrompt(
            prompt_type="close_window",
            message=message,
            window=window,
            options=["Save and Close", "Close without Saving", "Keep Open", "Cancel"],
            default_option="Cancel",
            requires_sms=True,  # Send SMS for critical action
        )

    def create_save_prompt(self, window: OpenWindow) -> UserPrompt:
        """Create a user prompt for saving a document.

        Args:
            window: Window with unsaved changes

        Returns:
            UserPrompt object
        """
        message = f"The document in '{window.app_name}' may have unsaved changes.\n\n"
        message += "Would you like to save before continuing?"

        return UserPrompt(
            prompt_type="save_document",
            message=message,
            window=window,
            options=["Save", "Don't Save", "Cancel"],
            default_option="Cancel",
            requires_sms=True,
        )

    def get_window_summary(self) -> dict[str, Any]:
        """Get summary of all open windows.

        Returns:
            Dictionary with window statistics
        """
        windows = self.detect_open_windows()

        return {
            "total_windows": len(windows),
            "applications": [w.app_name for w in windows],
            "visible_windows": [w for w in windows if w.is_visible],
            "active_window": next((w for w in windows if w.is_active), None),
        }

