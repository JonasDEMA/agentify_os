"""Screen Analyzer - OCR and visual element detection."""
import logging
from typing import Any, Dict, List, Optional

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class ScreenAnalyzer:
    """Analyzes screenshots using OCR and other techniques to identify elements."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """Initialize Screen Analyzer.

        Args:
            tesseract_cmd: Optional path to tesseract executable
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image: Image.Image) -> str:
        """Extract all text from an image.

        Args:
            image: PIL Image object

        Returns:
            Extracted text string
        """
        try:
            return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    def find_text(self, image: Image.Image, query: str) -> List[Dict[str, Any]]:
        """Find occurrences of specific text in the image.

        Args:
            image: PIL Image object
            query: Text to search for

        Returns:
            List of matches with coordinates and confidence
        """
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            matches = []
            
            for i, text in enumerate(data['text']):
                if not text.strip():
                    continue
                    
                if query.lower() in text.lower():
                    matches.append({
                        "text": text,
                        "x": data['left'][i],
                        "y": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i],
                        "confidence": float(data['conf'][i])
                    })
            
            return matches
        except Exception as e:
            logger.error(f"OCR text search failed: {e}")
            return []

    def get_element_at(self, image: Image.Image, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Identify what is at a specific coordinate (experimental).

        Args:
            image: PIL Image object
            x: X coordinate
            y: Y coordinate

        Returns:
            Information about the element at the coordinate or None
        """
        # This could be implemented with template matching or more advanced CV
        # For now, let's see if there's text at that location
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            for i, text in enumerate(data['text']):
                if not text.strip():
                    continue
                
                left, top = data['left'][i], data['top'][i]
                width, height = data['width'][i], data['height'][i]
                
                if left <= x <= left + width and top <= y <= top + height:
                    return {
                        "type": "text",
                        "text": text,
                        "x": left,
                        "y": top,
                        "width": width,
                        "height": height,
                        "confidence": float(data['conf'][i])
                    }
            return None
        except Exception as e:
            logger.error(f"OCR element lookup failed: {e}")
            return None
