"""UI Automation - Windows UI element detection using pywinauto."""

import logging
from typing import Any

from pywinauto import Desktop
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError

logger = logging.getLogger(__name__)


class UIElement:
    """Represents a UI element with its properties."""
    
    def __init__(
        self,
        name: str,
        element_type: str,
        x: int,
        y: int,
        width: int,
        height: int,
        is_visible: bool = True,
        is_enabled: bool = True,
        text: str = "",
    ):
        """Initialize UI element."""
        self.name = name
        self.element_type = element_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.is_visible = is_visible
        self.is_enabled = is_enabled
        self.text = text
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.element_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "is_visible": self.is_visible,
            "is_enabled": self.is_enabled,
            "text": self.text,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"UIElement(name={self.name}, type={self.element_type}, pos=({self.center_x}, {self.center_y}), text={self.text})"


class UIAutomation:
    """Windows UI Automation using pywinauto."""
    
    def __init__(self):
        """Initialize UI Automation."""
        self.desktop = Desktop(backend="uia")
        logger.info("UI Automation initialized")
    
    def get_all_windows(self) -> list[dict[str, Any]]:
        """Get all visible windows."""
        windows = []
        try:
            for window in self.desktop.windows():
                try:
                    if window.is_visible():
                        rect = window.rectangle()
                        windows.append({
                            "title": window.window_text(),
                            "class_name": window.class_name(),
                            "x": rect.left,
                            "y": rect.top,
                            "width": rect.width(),
                            "height": rect.height(),
                        })
                except Exception as e:
                    logger.debug(f"Error getting window info: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting windows: {e}")
        
        return windows
    
    def find_window(self, title: str | None = None, class_name: str | None = None) -> Any | None:
        """Find window by title or class name."""
        try:
            if title:
                return self.desktop.window(title_re=f".*{title}.*")
            elif class_name:
                return self.desktop.window(class_name=class_name)
        except ElementNotFoundError:
            logger.debug(f"Window not found: title={title}, class={class_name}")
            return None
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return None
    
    def get_window_elements(self, window_title: str | None = None) -> list[UIElement]:
        """Get all UI elements from a window."""
        elements = []

        try:
            # Get window
            if window_title:
                window = self.find_window(title=window_title)
                if not window:
                    logger.warning(f"Window not found: {window_title}")
                    return elements
            else:
                # Get all windows and use the first visible one
                windows = self.desktop.windows()
                if not windows:
                    logger.warning("No windows found")
                    return elements

                # Find first visible window
                window = None
                for w in windows:
                    try:
                        if w.is_visible():
                            window = w
                            break
                    except Exception:
                        continue

                if not window:
                    logger.warning("No visible window found")
                    return elements
            
            # Get all descendants
            try:
                descendants = window.descendants()
            except Exception as e:
                logger.error(f"Error getting descendants: {e}")
                return elements
            
            for elem in descendants:
                try:
                    # Get element info
                    rect = elem.rectangle()
                    
                    # Skip invisible or zero-size elements
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    # Get element properties
                    name = elem.window_text() or elem.class_name()
                    element_type = elem.element_info.control_type
                    
                    ui_elem = UIElement(
                        name=name,
                        element_type=element_type,
                        x=rect.left,
                        y=rect.top,
                        width=rect.width(),
                        height=rect.height(),
                        is_visible=elem.is_visible(),
                        is_enabled=elem.is_enabled(),
                        text=elem.window_text(),
                    )
                    
                    elements.append(ui_elem)
                    
                except Exception as e:
                    logger.debug(f"Error processing element: {e}")
                    continue
            
            logger.info(f"Found {len(elements)} UI elements in window: {window_title or 'foreground'}")
            
        except Exception as e:
            logger.error(f"Error getting window elements: {e}")
        
        return elements
    
    def find_element_by_name(self, name: str, window_title: str | None = None) -> UIElement | None:
        """Find UI element by name."""
        elements = self.get_window_elements(window_title)
        
        for elem in elements:
            if name.lower() in elem.name.lower() or name.lower() in elem.text.lower():
                return elem
        
        return None
    
    def find_clickable_elements(self, window_title: str | None = None) -> list[UIElement]:
        """Find all clickable elements (buttons, menu items, etc.)."""
        elements = self.get_window_elements(window_title)
        
        clickable_types = [
            "Button",
            "MenuItem",
            "ListItem",
            "TreeItem",
            "TabItem",
            "Hyperlink",
        ]
        
        clickable = [
            elem for elem in elements
            if any(ct in elem.element_type for ct in clickable_types)
            and elem.is_visible
            and elem.is_enabled
        ]
        
        logger.info(f"Found {len(clickable)} clickable elements")
        return clickable
    
    def get_start_button(self) -> UIElement | None:
        """Find Windows Start button."""
        try:
            # Try to find Start button
            elements = self.get_window_elements()
            
            for elem in elements:
                if "start" in elem.name.lower() or "start" in elem.text.lower():
                    if elem.element_type == "Button":
                        logger.info(f"Found Start button: {elem}")
                        return elem
            
            # Fallback: Start button is typically at bottom-left
            # Return a UIElement with estimated position
            logger.warning("Start button not found via UI Automation, using fallback position")
            return UIElement(
                name="Start",
                element_type="Button",
                x=0,
                y=1060,  # Typical position on 1920x1080
                width=40,
                height=40,
                text="Start",
            )
            
        except Exception as e:
            logger.error(f"Error finding Start button: {e}")
            return None
    
    def click_element(self, element: UIElement) -> bool:
        """Click on a UI element at its center position."""
        try:
            import pyautogui
            
            # Move mouse slowly to element center
            pyautogui.moveTo(element.center_x, element.center_y, duration=0.5)
            
            # Click
            pyautogui.click()
            
            logger.info(f"Clicked element: {element.name} at ({element.center_x}, {element.center_y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False

