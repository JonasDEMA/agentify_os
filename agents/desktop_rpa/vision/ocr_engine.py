"""OCR Engine - Text recognition from screenshots using Tesseract."""

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class TextRegion:
    """Represents a text region found by OCR."""
    
    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        confidence: float,
    ):
        """Initialize text region."""
        self.text = text.strip()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.confidence = confidence
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "confidence": self.confidence,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"TextRegion(text='{self.text}', pos=({self.center_x}, {self.center_y}), conf={self.confidence:.2f})"


class OCREngine:
    """OCR Engine using Tesseract."""
    
    def __init__(self):
        """Initialize OCR engine."""
        # Try to configure Tesseract path (Windows)
        try:
            # Common Tesseract installation paths on Windows
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            
            for path in tesseract_paths:
                if Path(path).exists():
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    break
        except Exception as e:
            logger.warning(f"Could not configure Tesseract path: {e}")
        
        logger.info("OCR Engine initialized")
    
    def extract_text(self, image_path: Path | str) -> str:
        """Extract all text from image."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            logger.info(f"Extracted {len(text)} characters from image")
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def find_text_regions(self, image_path: Path | str, min_confidence: float = 60.0) -> list[TextRegion]:
        """Find all text regions in image with bounding boxes."""
        regions = []
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text regions
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                # Get confidence
                conf = float(data['conf'][i])
                
                # Skip low confidence or empty text
                if conf < min_confidence:
                    continue
                
                text = data['text'][i].strip()
                if not text:
                    continue
                
                # Get bounding box
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                region = TextRegion(
                    text=text,
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    confidence=conf,
                )
                
                regions.append(region)
            
            logger.info(f"Found {len(regions)} text regions")
            
        except Exception as e:
            logger.error(f"Error finding text regions: {e}")
        
        return regions
    
    def find_text(self, image_path: Path | str, search_text: str, min_confidence: float = 60.0) -> list[TextRegion]:
        """Find specific text in image."""
        regions = self.find_text_regions(image_path, min_confidence)
        
        # Filter by search text (case-insensitive)
        search_lower = search_text.lower()
        matches = [
            region for region in regions
            if search_lower in region.text.lower()
        ]
        
        logger.info(f"Found {len(matches)} matches for '{search_text}'")
        return matches
    
    def preprocess_image(self, image_path: Path | str, output_path: Path | str | None = None) -> Path:
        """Preprocess image for better OCR results."""
        try:
            # Read image
            img = cv2.imread(str(image_path))
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            
            # Save preprocessed image
            if output_path is None:
                output_path = Path(str(image_path).replace('.png', '_preprocessed.png'))
            
            cv2.imwrite(str(output_path), denoised)
            logger.info(f"Preprocessed image saved to: {output_path}")
            
            return Path(output_path)
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return Path(image_path)
    
    def extract_text_with_preprocessing(self, image_path: Path | str) -> str:
        """Extract text with image preprocessing for better results."""
        try:
            # Preprocess image
            preprocessed = self.preprocess_image(image_path)
            
            # Extract text
            text = self.extract_text(preprocessed)
            
            # Clean up preprocessed image
            try:
                preprocessed.unlink()
            except Exception:
                pass
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text with preprocessing: {e}")
            return ""

