"""Element Detector - Combines UI Automation and OCR for comprehensive element detection."""

import logging
from pathlib import Path
from typing import Any

from agents.desktop_rpa.vision.ocr_engine import OCREngine, TextRegion
from agents.desktop_rpa.vision.ui_automation import UIAutomation, UIElement

logger = logging.getLogger(__name__)


class DetectedElement:
    """Unified element representation combining UI Automation and OCR."""
    
    def __init__(
        self,
        name: str,
        element_type: str,
        x: int,
        y: int,
        width: int,
        height: int,
        source: str,  # "ui_automation" or "ocr"
        confidence: float = 1.0,
        text: str = "",
        is_clickable: bool = False,
    ):
        """Initialize detected element."""
        self.name = name
        self.element_type = element_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.source = source
        self.confidence = confidence
        self.text = text
        self.is_clickable = is_clickable
    
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
            "source": self.source,
            "confidence": self.confidence,
            "text": self.text,
            "is_clickable": self.is_clickable,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DetectedElement(name='{self.name}', type={self.element_type}, pos=({self.center_x}, {self.center_y}), source={self.source})"


class ElementDetector:
    """Combines UI Automation and OCR for comprehensive element detection."""
    
    def __init__(self):
        """Initialize element detector."""
        self.ui_automation = UIAutomation()
        self.ocr_engine = OCREngine()
        logger.info("Element Detector initialized")
    
    def detect_all_elements(
        self,
        screenshot_path: Path | str | None = None,
        window_title: str | None = None,
        use_ocr: bool = True,
    ) -> list[DetectedElement]:
        """Detect all elements using UI Automation and optionally OCR."""
        elements = []
        
        # 1. Get UI elements via UI Automation
        logger.info("Detecting UI elements via UI Automation...")
        ui_elements = self.ui_automation.get_window_elements(window_title)
        
        for ui_elem in ui_elements:
            elem = DetectedElement(
                name=ui_elem.name,
                element_type=ui_elem.element_type,
                x=ui_elem.x,
                y=ui_elem.y,
                width=ui_elem.width,
                height=ui_elem.height,
                source="ui_automation",
                confidence=1.0,
                text=ui_elem.text,
                is_clickable="Button" in ui_elem.element_type or "MenuItem" in ui_elem.element_type,
            )
            elements.append(elem)
        
        # 2. Get text regions via OCR (if screenshot provided)
        if use_ocr and screenshot_path:
            logger.info("Detecting text regions via OCR...")
            text_regions = self.ocr_engine.find_text_regions(screenshot_path)
            
            for text_region in text_regions:
                elem = DetectedElement(
                    name=text_region.text,
                    element_type="Text",
                    x=text_region.x,
                    y=text_region.y,
                    width=text_region.width,
                    height=text_region.height,
                    source="ocr",
                    confidence=text_region.confidence / 100.0,
                    text=text_region.text,
                    is_clickable=False,
                )
                elements.append(elem)
        
        logger.info(f"Detected {len(elements)} total elements ({len(ui_elements)} UI, {len(text_regions) if use_ocr and screenshot_path else 0} OCR)")
        return elements
    
    def find_element(
        self,
        search_text: str,
        screenshot_path: Path | str | None = None,
        window_title: str | None = None,
    ) -> DetectedElement | None:
        """Find element by text (searches both UI Automation and OCR)."""
        # Try UI Automation first
        ui_elem = self.ui_automation.find_element_by_name(search_text, window_title)
        if ui_elem:
            logger.info(f"Found element via UI Automation: {ui_elem}")
            return DetectedElement(
                name=ui_elem.name,
                element_type=ui_elem.element_type,
                x=ui_elem.x,
                y=ui_elem.y,
                width=ui_elem.width,
                height=ui_elem.height,
                source="ui_automation",
                confidence=1.0,
                text=ui_elem.text,
                is_clickable=True,
            )
        
        # Try OCR if screenshot provided
        if screenshot_path:
            text_regions = self.ocr_engine.find_text(screenshot_path, search_text)
            if text_regions:
                # Return first match with highest confidence
                best_match = max(text_regions, key=lambda r: r.confidence)
                logger.info(f"Found element via OCR: {best_match}")
                return DetectedElement(
                    name=best_match.text,
                    element_type="Text",
                    x=best_match.x,
                    y=best_match.y,
                    width=best_match.width,
                    height=best_match.height,
                    source="ocr",
                    confidence=best_match.confidence / 100.0,
                    text=best_match.text,
                    is_clickable=True,  # Assume text can be clicked
                )
        
        logger.warning(f"Element not found: {search_text}")
        return None
    
    def get_clickable_elements(
        self,
        screenshot_path: Path | str | None = None,
        window_title: str | None = None,
    ) -> list[DetectedElement]:
        """Get all clickable elements."""
        elements = []
        
        # Get clickable UI elements
        ui_clickable = self.ui_automation.find_clickable_elements(window_title)
        for ui_elem in ui_clickable:
            elem = DetectedElement(
                name=ui_elem.name,
                element_type=ui_elem.element_type,
                x=ui_elem.x,
                y=ui_elem.y,
                width=ui_elem.width,
                height=ui_elem.height,
                source="ui_automation",
                confidence=1.0,
                text=ui_elem.text,
                is_clickable=True,
            )
            elements.append(elem)
        
        logger.info(f"Found {len(elements)} clickable elements")
        return elements
    
    def format_elements_for_llm(self, elements: list[DetectedElement]) -> str:
        """Format elements as text for LLM prompt."""
        if not elements:
            return "No UI elements detected."
        
        # Group by type
        by_type: dict[str, list[DetectedElement]] = {}
        for elem in elements:
            if elem.element_type not in by_type:
                by_type[elem.element_type] = []
            by_type[elem.element_type].append(elem)
        
        # Format output
        lines = ["Available UI Elements:"]
        lines.append("=" * 50)
        
        for elem_type, elems in sorted(by_type.items()):
            lines.append(f"\n{elem_type}s ({len(elems)}):")
            for elem in elems[:10]:  # Limit to 10 per type
                text_info = f" - '{elem.text}'" if elem.text else ""
                lines.append(f"  • {elem.name}{text_info} at ({elem.center_x}, {elem.center_y})")
        
        return "\n".join(lines)

