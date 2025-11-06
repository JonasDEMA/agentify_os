"""Demo for Window Manager - Intelligent Window Detection and Reuse.

This demo shows:
1. Detecting already open windows
2. Reusing existing windows instead of opening new ones
3. Bringing windows to foreground
4. User prompts for critical actions
"""

import asyncio
import logging

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def demo_with_window_manager():
    """Demo: Execute task WITH Window Manager."""
    print("\n" + "=" * 60)
    print("🧪 DEMO 1: Execute Task WITH Window Manager")
    print("=" * 60)
    print("\n📝 This demo will:")
    print("   1. Check if Notepad is already open")
    print("   2. If open: Bring to foreground (reuse)")
    print("   3. If not open: Open new instance")
    print("\n🎯 Task: Open Notepad application")
    print("\n" + "=" * 60)

    # Create executor WITH Window Manager
    executor = CognitiveExecutor(
        use_vision=True,
        use_state_graph=True,
        use_window_manager=True,  # ✅ Window Manager enabled
    )

    # Execute task
    task = {"goal": "Open Notepad application from the Start Menu"}

    print("\n🚀 Starting execution...\n")
    result = await executor.execute(task)

    print("\n" + "=" * 60)
    print("📊 RESULT:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Steps: {result.get('steps_taken', 0)}")
    if result.get("error"):
        print(f"   Error: {result['error']}")
    print("=" * 60)


async def demo_without_window_manager():
    """Demo: Execute task WITHOUT Window Manager."""
    print("\n" + "=" * 60)
    print("🧪 DEMO 2: Execute Task WITHOUT Window Manager")
    print("=" * 60)
    print("\n📝 This demo will:")
    print("   1. NOT check if Calculator is already open")
    print("   2. Always try to open new instance")
    print("   3. May result in multiple instances")
    print("\n🎯 Task: Open Calculator application")
    print("\n" + "=" * 60)

    # Create executor WITHOUT Window Manager
    executor = CognitiveExecutor(
        use_vision=True,
        use_state_graph=True,
        use_window_manager=False,  # ❌ Window Manager disabled
    )

    # Execute task
    task = {"goal": "Open Calculator application from the Start Menu"}

    print("\n🚀 Starting execution...\n")
    result = await executor.execute(task)

    print("\n" + "=" * 60)
    print("📊 RESULT:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Steps: {result.get('steps_taken', 0)}")
    if result.get("error"):
        print(f"   Error: {result['error']}")
    print("=" * 60)


async def demo_window_detection():
    """Demo: Window Detection Features."""
    print("\n" + "=" * 60)
    print("🧪 DEMO 3: Window Detection Features")
    print("=" * 60)

    from agents.desktop_rpa.window_manager import WindowManager

    wm = WindowManager()

    # 1. Detect all open windows
    print("\n1️⃣  Detecting all open windows...")
    windows = wm.detect_open_windows()
    print(f"   ✅ Found {len(windows)} open windows")
    for window in windows[:5]:  # Show first 5
        print(f"      • {window.app_name} - {window.title[:50]}")

    # 2. Check for specific apps
    print("\n2️⃣  Checking for specific applications...")
    apps = ["Notepad", "Calculator", "Outlook", "Chrome"]
    for app in apps:
        window = wm.is_app_open(app)
        if window:
            print(f"   ✅ {app} is OPEN: {window.title}")
        else:
            print(f"   ❌ {app} is NOT open")

    # 3. Window summary
    print("\n3️⃣  Window Summary...")
    summary = wm.get_window_summary()
    print(f"   Total Windows: {summary['total_windows']}")
    print(f"   Applications: {', '.join(summary['applications'][:5])}")
    if summary['active_window']:
        print(f"   Active Window: {summary['active_window'].app_name}")

    # 4. User prompts
    if windows:
        print("\n4️⃣  Creating user prompts...")
        window = windows[0]

        # Close prompt
        close_prompt = wm.create_close_prompt(
            window, reason="Need to open a different application"
        )
        print(f"\n   📝 Close Prompt:")
        print(f"      Type: {close_prompt.prompt_type}")
        print(f"      Message: {close_prompt.message[:80]}...")
        print(f"      Options: {', '.join(close_prompt.options)}")
        print(f"      Requires SMS: {close_prompt.requires_sms}")

        # Save prompt
        save_prompt = wm.create_save_prompt(window)
        print(f"\n   📝 Save Prompt:")
        print(f"      Type: {save_prompt.prompt_type}")
        print(f"      Message: {save_prompt.message[:80]}...")
        print(f"      Options: {', '.join(save_prompt.options)}")
        print(f"      Requires SMS: {save_prompt.requires_sms}")

    print("\n" + "=" * 60)


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("🚀 WINDOW MANAGER DEMO SUITE")
    print("=" * 60)
    print("\nThis demo showcases the Window Manager features:")
    print("  • Intelligent window detection")
    print("  • Reusing existing windows")
    print("  • Bringing windows to foreground")
    print("  • User prompts for critical actions")
    print("\n" + "=" * 60)

    while True:
        print("\n📋 Select a demo:")
        print("  1. Execute task WITH Window Manager (Notepad)")
        print("  2. Execute task WITHOUT Window Manager (Calculator)")
        print("  3. Window Detection Features (no execution)")
        print("  4. Run all demos")
        print("  5. Exit")

        choice = input("\n👉 Enter choice (1-5): ").strip()

        if choice == "1":
            await demo_with_window_manager()
        elif choice == "2":
            await demo_without_window_manager()
        elif choice == "3":
            await demo_window_detection()
        elif choice == "4":
            await demo_with_window_manager()
            await asyncio.sleep(2)
            await demo_without_window_manager()
            await asyncio.sleep(2)
            await demo_window_detection()
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")

        input("\n⏸️  Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())

