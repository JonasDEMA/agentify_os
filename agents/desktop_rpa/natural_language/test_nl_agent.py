"""Test script for natural language agent communication.

This script tests the complete flow:
1. User sends natural language command
2. Agent parses intent
3. Agent executes task with real-time updates
4. Agent returns final result
"""

import asyncio
from typing import Any

from agents.desktop_rpa.natural_language.nl_orchestrator import NaturalLanguageOrchestrator
from agents.desktop_rpa.natural_language.example_tasks import ExampleTasks


def print_message(message: dict[str, Any]):
    """Print message in a nice format."""
    message_type = message.get("message_type")
    msg_text = message.get("message", "")
    
    # Color codes
    RESET = "\033[0m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    
    if message_type == "user_command":
        print(f"\n{BLUE}👤 USER:{RESET} {message.get('command')}")
    
    elif message_type == "agent_thinking":
        print(f"{PURPLE}💭 THINKING:{RESET} {msg_text}")
    
    elif message_type == "agent_action":
        print(f"{CYAN}⚡ ACTION:{RESET} {msg_text}")
    
    elif message_type == "agent_progress":
        progress = message.get("progress_percent")
        if progress is not None:
            print(f"{YELLOW}📊 PROGRESS ({progress}%):{RESET} {msg_text}")
        else:
            print(f"{YELLOW}📊 PROGRESS:{RESET} {msg_text}")
    
    elif message_type == "agent_result":
        success = message.get("success", True)
        if success:
            print(f"{GREEN}✅ RESULT:{RESET} {msg_text}")
        else:
            print(f"{YELLOW}⚠️  RESULT:{RESET} {msg_text}")
    
    elif message_type == "agent_error":
        print(f"{RED}❌ ERROR:{RESET} {msg_text}")
    
    elif message_type == "agent_question":
        print(f"{CYAN}❓ QUESTION:{RESET} {msg_text}")
        options = message.get("options")
        if options:
            for i, option in enumerate(options, 1):
                print(f"   {i}. {option}")
    
    else:
        print(f"📨 {message_type}: {msg_text}")


async def test_command(command: str):
    """Test a single command."""
    print("\n" + "=" * 80)
    print(f"Testing command: {command}")
    print("=" * 80)
    
    # Create orchestrator with print callback
    orchestrator = NaturalLanguageOrchestrator(
        message_callback=print_message,
        use_vision=True,
        use_window_manager=True,
    )
    
    # Process command
    session = await orchestrator.process_command(command)
    
    # Print session summary
    print("\n" + "-" * 80)
    print(f"Session ID: {session.session_id}")
    print(f"Task Status: {session.task_status}")
    print(f"Total Messages: {len(session.messages)}")
    print("-" * 80)


async def test_interactive():
    """Interactive testing mode."""
    print("\n" + "=" * 80)
    print("🤖 CPA Agent - Natural Language Interactive Test")
    print("=" * 80)
    print("\nType your commands in natural language.")
    print("Type 'examples' to see example commands.")
    print("Type 'quit' to exit.\n")
    
    # Create orchestrator
    orchestrator = NaturalLanguageOrchestrator(
        message_callback=print_message,
        use_vision=True,
        use_window_manager=True,
    )
    
    while True:
        try:
            # Get user input
            command = input("\n👤 YOU: ").strip()
            
            if not command:
                continue
            
            if command.lower() == "quit":
                print("\n👋 Goodbye!")
                break
            
            if command.lower() == "examples":
                print("\n📚 Example Commands:")
                print("-" * 80)
                for i, task in enumerate(ExampleTasks.get_all_tasks()[:10], 1):
                    print(f"{i}. {task['command']}")
                    print(f"   → {task['description']}")
                print("-" * 80)
                continue
            
            # Process command
            await orchestrator.process_command(command)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def test_example_tasks():
    """Test all example tasks."""
    print("\n" + "=" * 80)
    print("🧪 Testing Example Tasks")
    print("=" * 80)
    
    tasks = ExampleTasks.get_all_tasks()[:5]  # Test first 5 tasks
    
    for i, task in enumerate(tasks, 1):
        print(f"\n\n{'#' * 80}")
        print(f"# Test {i}/{len(tasks)}: {task['description']}")
        print(f"{'#' * 80}")
        
        await test_command(task["command"])
        
        # Wait a bit between tests
        await asyncio.sleep(2)


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Test specific command from command line
        command = " ".join(sys.argv[1:])
        await test_command(command)
    else:
        # Interactive mode
        await test_interactive()


if __name__ == "__main__":
    asyncio.run(main())

