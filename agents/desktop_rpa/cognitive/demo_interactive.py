"""Interactive Demo - Watch the Cognitive Executor in action!"""

import asyncio
import logging
import time

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor

# Disable all logging for clean output
logging.basicConfig(level=logging.CRITICAL)


async def countdown(seconds: int):
    """Show countdown before starting."""
    for i in range(seconds, 0, -1):
        print(f"\r⏰ Starting in {i} seconds... (Move your mouse to cancel)", end="", flush=True)
        await asyncio.sleep(1)
    print("\r" + " " * 80 + "\r", end="", flush=True)  # Clear line


async def main():
    """Run interactive demo."""
    print("\n" + "=" * 80)
    print("🎬 INTERACTIVE DEMO - Cognitive RPA Agent")
    print("=" * 80)
    print("\n⚠️  WARNING: This demo will control your mouse and keyboard!")
    print("📺 Watch your screen to see the agent in action.")
    print("🛑 Move your mouse to the top-left corner to emergency stop.\n")
    
    # Countdown
    await countdown(5)
    
    print("\n🚀 Starting demo...\n")
    
    # Create executor with slower execution
    executor = CognitiveExecutor()
    executor.max_steps = 3  # Only 3 steps for demo
    
    # Simple task
    task = {
        "goal": "Open the Windows Start Menu by clicking the Start button",
    }
    
    print("🎯 TASK: Open the Windows Start Menu")
    print("👀 Watch your screen now!\n")
    
    # Small delay so user can focus on screen
    await asyncio.sleep(2)
    
    # Execute
    result = await executor.execute(task)
    
    # Show result
    print("\n" + "=" * 80)
    print("📊 DEMO COMPLETE!")
    print("=" * 80)
    print(f"\n✅ Status: {result['status']}")
    print(f"📈 Steps: {result['steps']}")
    print(f"🎯 Final State: {result['final_state']}")
    
    if result.get('actions'):
        print(f"\n📝 Actions performed:")
        for i, action in enumerate(result['actions'], 1):
            print(f"  {i}. {action['action_type'].upper()}")
            print(f"     💭 {action['reasoning']}")
            print(f"     📊 Confidence: {action['confidence']:.2f}")
            print()
    
    print("=" * 80)
    print("🎬 Demo finished! Check the screenshots in: screenshots/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Demo cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

