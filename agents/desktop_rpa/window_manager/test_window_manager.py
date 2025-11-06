"""Test Window Manager functionality."""

import logging

from agents.desktop_rpa.window_manager import WindowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s"
)


def test_detect_windows():
    """Test window detection."""
    print("\n" + "=" * 60)
    print("🧪 TEST 1: Detect Open Windows")
    print("=" * 60)

    wm = WindowManager()

    # Detect all open windows
    windows = wm.detect_open_windows()

    print(f"\n✅ Detected {len(windows)} open windows:\n")
    for i, window in enumerate(windows, 1):
        active = "🟢 ACTIVE" if window.is_active else ""
        print(f"  {i}. {window.app_name} {active}")
        print(f"     Title: {window.title[:60]}")
        print(f"     Class: {window.class_name}")
        print(f"     Position: ({window.x}, {window.y})")
        print(f"     Size: {window.width}x{window.height}")
        print()


def test_is_app_open():
    """Test checking if specific apps are open."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Check if Apps are Open")
    print("=" * 60)

    wm = WindowManager()

    # Test common applications
    apps_to_check = [
        "Notepad",
        "Calculator",
        "Outlook",
        "Excel",
        "Chrome",
        "Firefox",
        "Edge",
        "File Explorer",
    ]

    print("\n📊 Checking for open applications:\n")
    for app in apps_to_check:
        window = wm.is_app_open(app)
        if window:
            print(f"  ✅ {app} is OPEN")
            print(f"     Title: {window.title}")
        else:
            print(f"  ❌ {app} is NOT open")


def test_bring_to_foreground():
    """Test bringing window to foreground."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Bring Window to Foreground")
    print("=" * 60)

    wm = WindowManager()

    # Find any open window
    windows = wm.detect_open_windows()
    if not windows:
        print("\n⚠️  No windows open to test")
        return

    # Try to bring first window to foreground
    window = windows[0]
    print(f"\n🎯 Attempting to bring to foreground: {window.app_name}")
    print(f"   Title: {window.title}")

    success = wm.bring_to_foreground(window)

    if success:
        print(f"\n✅ Successfully brought window to foreground!")
    else:
        print(f"\n❌ Failed to bring window to foreground")


def test_find_window_by_app():
    """Test finding window by application name."""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Find Window by App Name")
    print("=" * 60)

    wm = WindowManager()

    # Test finding specific apps
    apps = ["Notepad", "Calculator", "Chrome"]

    print("\n🔍 Searching for applications:\n")
    for app in apps:
        window = wm.find_window_by_app(app)
        if window:
            print(f"  ✅ Found {app}:")
            print(f"     Title: {window.title}")
            print(f"     Position: ({window.x}, {window.y})")
        else:
            print(f"  ❌ {app} not found")


def test_user_prompts():
    """Test user prompt creation."""
    print("\n" + "=" * 60)
    print("🧪 TEST 5: User Prompts")
    print("=" * 60)

    wm = WindowManager()

    # Find a window to test with
    windows = wm.detect_open_windows()
    if not windows:
        print("\n⚠️  No windows open to test")
        return

    window = windows[0]

    # Test close prompt
    print(f"\n📝 Creating close prompt for: {window.app_name}")
    close_prompt = wm.create_close_prompt(
        window, reason="Need to open a different application"
    )

    print(f"\n✅ Close Prompt Created:")
    print(f"   Type: {close_prompt.prompt_type}")
    print(f"   Message: {close_prompt.message}")
    print(f"   Options: {', '.join(close_prompt.options)}")
    print(f"   Default: {close_prompt.default_option}")
    print(f"   Requires SMS: {close_prompt.requires_sms}")

    # Test save prompt
    print(f"\n📝 Creating save prompt for: {window.app_name}")
    save_prompt = wm.create_save_prompt(window)

    print(f"\n✅ Save Prompt Created:")
    print(f"   Type: {save_prompt.prompt_type}")
    print(f"   Message: {save_prompt.message}")
    print(f"   Options: {', '.join(save_prompt.options)}")
    print(f"   Default: {save_prompt.default_option}")
    print(f"   Requires SMS: {save_prompt.requires_sms}")


def test_window_summary():
    """Test window summary."""
    print("\n" + "=" * 60)
    print("🧪 TEST 6: Window Summary")
    print("=" * 60)

    wm = WindowManager()

    summary = wm.get_window_summary()

    print(f"\n📊 Window Summary:")
    print(f"   Total Windows: {summary['total_windows']}")
    print(f"   Applications: {', '.join(summary['applications'][:5])}")
    if len(summary['applications']) > 5:
        print(f"                 ... and {len(summary['applications']) - 5} more")

    if summary['active_window']:
        print(f"   Active Window: {summary['active_window'].app_name}")
    else:
        print(f"   Active Window: None")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 WINDOW MANAGER TEST SUITE")
    print("=" * 60)

    try:
        test_detect_windows()
        test_is_app_open()
        test_bring_to_foreground()
        test_find_window_by_app()
        test_user_prompts()
        test_window_summary()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

