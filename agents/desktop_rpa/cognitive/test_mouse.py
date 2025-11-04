"""Simple test to see if mouse movement works."""

import time
import pyautogui

print("\n" + "=" * 80)
print("🖱️  MOUSE MOVEMENT TEST")
print("=" * 80)
print("\n⚠️  WARNING: Your mouse will move in 3 seconds!")
print("👀 Watch your screen!\n")

# Countdown
for i in range(3, 0, -1):
    print(f"⏰ Starting in {i}...")
    time.sleep(1)

print("\n🚀 Moving mouse NOW!\n")

# Get current position
current_x, current_y = pyautogui.position()
print(f"📍 Current mouse position: ({current_x}, {current_y})")

# Move mouse SLOWLY to center of screen
screen_width, screen_height = pyautogui.size()
center_x = screen_width // 2
center_y = screen_height // 2

print(f"📺 Screen size: {screen_width} x {screen_height}")
print(f"🎯 Moving to center: ({center_x}, {center_y})")
print("\n👀 WATCH YOUR MOUSE NOW!\n")

# Move SLOWLY (duration=2 seconds)
pyautogui.moveTo(center_x, center_y, duration=2.0)

print("✅ Mouse moved to center!")
time.sleep(1)

# Move to top-left corner SLOWLY
print("\n🎯 Moving to top-left corner (100, 100)...")
pyautogui.moveTo(100, 100, duration=2.0)

print("✅ Mouse moved to top-left!")
time.sleep(1)

# Move to bottom-right SLOWLY
print("\n🎯 Moving to bottom-right corner...")
pyautogui.moveTo(screen_width - 100, screen_height - 100, duration=2.0)

print("✅ Mouse moved to bottom-right!")
time.sleep(1)

# Move back to original position
print(f"\n🎯 Moving back to original position ({current_x}, {current_y})...")
pyautogui.moveTo(current_x, current_y, duration=2.0)

print("\n✅ Test complete!")
print("=" * 80)
print("\nDid you see the mouse moving? (Yes/No)")
print("=" * 80 + "\n")

