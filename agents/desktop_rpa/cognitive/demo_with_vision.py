"""Demo: Cognitive Executor with Vision Layer (Phase 5.2)."""

import asyncio
import logging

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def countdown(seconds: int):
    """Countdown before starting."""
    for i in range(seconds, 0, -1):
        print(f"\r⏰ Starting in {i} seconds... (Move mouse to cancel)", end="", flush=True)
        await asyncio.sleep(1)
    print("\r" + " " * 60 + "\r", end="", flush=True)


async def demo_open_notepad():
    """Demo: Open Notepad using Vision Layer."""
    print("\n" + "=" * 70)
    print("🎯 DEMO 1: Open Notepad (with Vision Layer)")
    print("=" * 70)
    print("\n⚠️  This demo will:")
    print("   • Use Vision Layer to detect UI elements")
    print("   • Find and click the Start button")
    print("   • Search for 'Notepad' in Start Menu")
    print("   • Open Notepad")
    print("\n")
    
    await countdown(5)
    
    # Create executor with Vision Layer enabled
    executor = CognitiveExecutor(use_vision=True)
    executor.max_steps = 10
    
    # Execute task
    result = await executor.execute({
        "goal": "Open Notepad application"
    })
    
    print("\n" + "=" * 70)
    print(f"📊 Result: {result['status']}")
    print(f"📈 Steps taken: {result.get('steps', 'N/A')}")
    print("=" * 70)


async def demo_open_calculator():
    """Demo: Open Calculator using Vision Layer."""
    print("\n" + "=" * 70)
    print("🎯 DEMO 2: Open Calculator (with Vision Layer)")
    print("=" * 70)
    print("\n⚠️  This demo will:")
    print("   • Use Vision Layer to detect UI elements")
    print("   • Find and click the Start button")
    print("   • Search for 'Calculator' in Start Menu")
    print("   • Open Calculator")
    print("\n")
    
    await countdown(5)
    
    # Create executor with Vision Layer enabled
    executor = CognitiveExecutor(use_vision=True)
    executor.max_steps = 10
    
    # Execute task
    result = await executor.execute({
        "goal": "Open Calculator application"
    })
    
    print("\n" + "=" * 70)
    print(f"📊 Result: {result['status']}")
    print(f"📈 Steps taken: {result.get('steps', 'N/A')}")
    print("=" * 70)


async def demo_comparison():
    """Demo: Compare with and without Vision Layer."""
    print("\n" + "=" * 70)
    print("🎯 DEMO 3: Comparison - With vs Without Vision Layer")
    print("=" * 70)
    
    # Test 1: Without Vision Layer
    print("\n" + "-" * 70)
    print("📍 Test 1: WITHOUT Vision Layer (blind mode)")
    print("-" * 70)
    print("\n⚠️  This will use only screenshots (no element detection)")
    print("\n")
    
    await countdown(3)
    
    executor_blind = CognitiveExecutor(use_vision=False)
    executor_blind.max_steps = 5
    
    result_blind = await executor_blind.execute({
        "goal": "Click the Start button"
    })
    
    print(f"\n📊 Result (blind): {result_blind['status']} in {result_blind.get('steps', 'N/A')} steps")
    
    # Wait
    await asyncio.sleep(3)
    
    # Test 2: With Vision Layer
    print("\n" + "-" * 70)
    print("📍 Test 2: WITH Vision Layer (smart mode)")
    print("-" * 70)
    print("\n⚠️  This will use Vision Layer (UI Automation + OCR)")
    print("\n")
    
    await countdown(3)
    
    executor_smart = CognitiveExecutor(use_vision=True)
    executor_smart.max_steps = 5
    
    result_smart = await executor_smart.execute({
        "goal": "Click the Start button"
    })
    
    print(f"\n📊 Result (smart): {result_smart['status']} in {result_smart.get('steps', 'N/A')} steps")
    
    # Comparison
    print("\n" + "=" * 70)
    print("📊 COMPARISON")
    print("=" * 70)
    print(f"Without Vision: {result_blind['status']} in {result_blind.get('steps', 'N/A')} steps")
    print(f"With Vision:    {result_smart['status']} in {result_smart.get('steps', 'N/A')} steps")
    print("=" * 70)


async def main():
    """Run all demos."""
    print("\n" + "🚀" * 35)
    print("🎬 COGNITIVE EXECUTOR - VISION LAYER DEMOS (Phase 5.2)")
    print("🚀" * 35)
    
    demos = [
        ("1", "Open Notepad", demo_open_notepad),
        ("2", "Open Calculator", demo_open_calculator),
        ("3", "Comparison (With vs Without Vision)", demo_comparison),
    ]
    
    print("\n📋 Available Demos:")
    for num, name, _ in demos:
        print(f"   {num}. {name}")
    print("   0. Run all demos")
    print("   q. Quit")
    
    choice = input("\n👉 Select demo (0-3, q): ").strip().lower()
    
    if choice == "q":
        print("\n👋 Bye!")
        return
    elif choice == "0":
        # Run all demos
        for _, _, demo_func in demos:
            await demo_func()
            await asyncio.sleep(2)
    else:
        # Run selected demo
        for num, _, demo_func in demos:
            if choice == num:
                await demo_func()
                break
        else:
            print(f"\n❌ Invalid choice: {choice}")
    
    print("\n" + "🎉" * 35)
    print("✅ DEMOS COMPLETED!")
    print("🎉" * 35)


if __name__ == "__main__":
    asyncio.run(main())

