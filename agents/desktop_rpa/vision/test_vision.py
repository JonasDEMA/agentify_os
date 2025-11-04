"""Test Vision Layer - UI Automation and OCR."""

import asyncio
import time
from pathlib import Path

import pyautogui

from agents.desktop_rpa.vision.element_detector import ElementDetector
from agents.desktop_rpa.vision.ocr_engine import OCREngine
from agents.desktop_rpa.vision.ui_automation import UIAutomation


def test_ui_automation():
    """Test UI Automation."""
    print("\n" + "=" * 60)
    print("🧪 Testing UI Automation")
    print("=" * 60)
    
    ui = UIAutomation()
    
    # Get all windows
    print("\n📊 All Windows:")
    windows = ui.get_all_windows()
    for i, window in enumerate(windows[:5], 1):  # Show first 5
        print(f"  {i}. {window['title'][:50]} ({window['class_name']})")
    
    # Get foreground window elements
    print("\n🔍 Foreground Window Elements:")
    elements = ui.get_window_elements()
    print(f"  Found {len(elements)} elements")
    
    # Show clickable elements
    clickable = ui.find_clickable_elements()
    print(f"\n🖱️  Clickable Elements ({len(clickable)}):")
    for elem in clickable[:10]:  # Show first 10
        print(f"  • {elem.name} ({elem.element_type}) at ({elem.center_x}, {elem.center_y})")
    
    # Find Start button
    print("\n🔍 Searching for Start Button:")
    start_button = ui.get_start_button()
    if start_button:
        print(f"  ✅ Found: {start_button}")
    else:
        print(f"  ❌ Not found")


def test_ocr():
    """Test OCR Engine."""
    print("\n" + "=" * 60)
    print("🧪 Testing OCR Engine")
    print("=" * 60)
    
    ocr = OCREngine()
    
    # Take screenshot
    print("\n📸 Taking screenshot...")
    screenshot_path = Path("test_screenshot.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print(f"  Saved to: {screenshot_path}")
    
    # Extract text
    print("\n📝 Extracting text...")
    text = ocr.extract_text(screenshot_path)
    print(f"  Extracted {len(text)} characters")
    print(f"  Preview: {text[:200]}...")
    
    # Find text regions
    print("\n🔍 Finding text regions...")
    regions = ocr.find_text_regions(screenshot_path)
    print(f"  Found {len(regions)} text regions")
    
    # Show first 10 regions
    print("\n📍 Text Regions (first 10):")
    for region in regions[:10]:
        print(f"  • '{region.text}' at ({region.center_x}, {region.center_y}) - conf: {region.confidence:.0f}%")
    
    # Search for specific text
    search_terms = ["Start", "File", "Edit", "View"]
    for term in search_terms:
        matches = ocr.find_text(screenshot_path, term)
        if matches:
            print(f"\n🔍 Found '{term}': {len(matches)} matches")
            for match in matches[:3]:
                print(f"  • {match}")
    
    # Clean up
    screenshot_path.unlink()


def test_element_detector():
    """Test Element Detector (combined UI Automation + OCR)."""
    print("\n" + "=" * 60)
    print("🧪 Testing Element Detector")
    print("=" * 60)
    
    detector = ElementDetector()
    
    # Take screenshot
    print("\n📸 Taking screenshot...")
    screenshot_path = Path("test_screenshot.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    # Detect all elements
    print("\n🔍 Detecting all elements (UI Automation + OCR)...")
    elements = detector.detect_all_elements(screenshot_path=screenshot_path, use_ocr=True)
    print(f"  Found {len(elements)} total elements")
    
    # Count by source
    ui_count = sum(1 for e in elements if e.source == "ui_automation")
    ocr_count = sum(1 for e in elements if e.source == "ocr")
    print(f"  • UI Automation: {ui_count}")
    print(f"  • OCR: {ocr_count}")
    
    # Show clickable elements
    clickable = [e for e in elements if e.is_clickable]
    print(f"\n🖱️  Clickable Elements ({len(clickable)}):")
    for elem in clickable[:10]:
        print(f"  • {elem.name} ({elem.source}) at ({elem.center_x}, {elem.center_y})")
    
    # Format for LLM
    print("\n📋 LLM Format:")
    llm_text = detector.format_elements_for_llm(elements)
    print(llm_text[:500] + "...")
    
    # Search for specific elements
    search_terms = ["Start", "Notepad", "File", "Calculator"]
    for term in search_terms:
        print(f"\n🔍 Searching for '{term}':")
        element = detector.find_element(term, screenshot_path=screenshot_path)
        if element:
            print(f"  ✅ Found: {element}")
        else:
            print(f"  ❌ Not found")
    
    # Clean up
    screenshot_path.unlink()


def main():
    """Run all tests."""
    print("\n🚀 Vision Layer Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: UI Automation
        test_ui_automation()
        
        # Wait
        time.sleep(2)
        
        # Test 2: OCR
        test_ocr()
        
        # Wait
        time.sleep(2)
        
        # Test 3: Element Detector
        test_element_detector()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

