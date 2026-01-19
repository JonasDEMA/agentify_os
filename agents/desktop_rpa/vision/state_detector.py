"""State Detector - Identifies the current application state based on rules."""
import logging
from typing import Any, Dict, List, Optional

from PIL import Image
from agents.desktop_rpa.vision.screen_analyzer import ScreenAnalyzer

logger = logging.getLogger(__name__)

class StateDetector:
    """Detects the current state of the desktop/application based on visual and system cues."""

    def __init__(self, screen_analyzer: ScreenAnalyzer):
        """Initialize State Detector.

        Args:
            screen_analyzer: Screen analyzer instance for OCR/CV
        """
        self.screen_analyzer = screen_analyzer
        self.states: Dict[str, Dict[str, Any]] = {}

    def register_state(self, name: str, rules: Dict[str, Any]):
        """Register a state with its detection rules.

        Args:
            name: Name of the state (e.g., 'outlook_open')
            rules: Dictionary of rules (e.g., {'window_title': 'Outlook', 'text_present': ['Inbox']})
        """
        self.states[name] = rules
        logger.info(f"Registered state: {name}")

    def detect_state(self, image: Image.Image, window_title: Optional[str] = None) -> str:
        """Detect the current state based on registered rules.

        Args:
            image: Current screenshot
            window_title: Currently active window title

        Returns:
            Name of the detected state or 'unknown'
        """
        for state_name, rules in self.states.items():
            if self._check_rules(state_name, rules, image, window_title):
                logger.info(f"Detected state: {state_name}")
                return state_name
        
        return "unknown"

    def _check_rules(self, name: str, rules: Dict[str, Any], image: Image.Image, window_title: Optional[str]) -> bool:
        """Check if all rules for a state are met."""
        # 1. Check window title (substring match)
        if "window_title" in rules:
            target = rules["window_title"]
            if not window_title or target.lower() not in window_title.lower():
                return False

        # 2. Check for presence of specific text (OCR)
        if "text_present" in rules:
            targets = rules["text_present"]
            if isinstance(targets, str):
                targets = [targets]
            
            for target in targets:
                matches = self.screen_analyzer.find_text(image, target)
                if not matches:
                    return False

        # 3. Check for absence of specific text
        if "text_absent" in rules:
            targets = rules["text_absent"]
            if isinstance(targets, str):
                targets = [targets]
            
            for target in targets:
                matches = self.screen_analyzer.find_text(image, target)
                if matches:
                    return False

        return True
