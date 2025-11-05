"""Demo: Cognitive Executor with State Graph."""

import asyncio
import logging

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


async def demo_with_state_graph():
    """Demo: Execute task with State Graph enabled."""
    print("\n" + "=" * 70)
    print("🧪 DEMO: Cognitive Executor with State Graph")
    print("=" * 70)
    
    # Create executor with State Graph
    executor = CognitiveExecutor(use_vision=True, use_state_graph=True)
    
    print("\n✅ Executor created with:")
    print("   - Vision Layer: ENABLED")
    print("   - State Graph: ENABLED")
    
    # Show state graph info
    if executor.state_graph:
        print(f"\n📊 State Graph:")
        print(f"   - Nodes: {len(executor.state_graph.nodes)}")
        print(f"   - Transitions: {len(executor.state_graph.transitions)}")
        print(f"   - States: {list(executor.state_graph.nodes.keys())}")
    
    # Execute task
    task = {"goal": "Open Notepad application from the Start Menu"}
    
    print(f"\n🎯 Task: {task['goal']}")
    print("\n" + "-" * 70)
    
    result = await executor.execute(task)
    
    print("\n" + "-" * 70)
    print(f"\n📊 Result:")
    print(f"   - Status: {result['status']}")
    print(f"   - Steps: {result['steps']}")
    print(f"   - Final State: {result['final_state']}")
    
    if "state_summary" in result and result["state_summary"]:
        summary = result["state_summary"]
        print(f"\n📈 State Graph Summary:")
        print(f"   - Current State: {summary['current_state']}")
        print(f"   - Total Steps: {summary['total_steps']}")
        print(f"   - Unique States: {summary['unique_states']}")
        print(f"   - States Visited: {summary['states_visited']}")
        print(f"   - Total Actions: {summary['total_actions']}")
        print(f"   - Loop Detected: {summary['is_looping']}")


async def demo_without_state_graph():
    """Demo: Execute task without State Graph."""
    print("\n" + "=" * 70)
    print("🧪 DEMO: Cognitive Executor WITHOUT State Graph")
    print("=" * 70)
    
    # Create executor without State Graph
    executor = CognitiveExecutor(use_vision=True, use_state_graph=False)
    
    print("\n✅ Executor created with:")
    print("   - Vision Layer: ENABLED")
    print("   - State Graph: DISABLED")
    
    # Execute task
    task = {"goal": "Open Calculator application from the Start Menu"}
    
    print(f"\n🎯 Task: {task['goal']}")
    print("\n" + "-" * 70)
    
    result = await executor.execute(task)
    
    print("\n" + "-" * 70)
    print(f"\n📊 Result:")
    print(f"   - Status: {result['status']}")
    print(f"   - Steps: {result['steps']}")
    print(f"   - Final State: {result['final_state']}")


async def demo_state_graph_features():
    """Demo: State Graph features."""
    print("\n" + "=" * 70)
    print("🧪 DEMO: State Graph Features")
    print("=" * 70)
    
    # Create executor
    executor = CognitiveExecutor(use_vision=False, use_state_graph=True)
    
    # Access state graph components
    graph = executor.state_graph
    tracker = executor.state_tracker
    finder = executor.path_finder
    
    print("\n📊 State Graph Info:")
    print(f"   - Nodes: {len(graph.nodes)}")
    print(f"   - Transitions: {len(graph.transitions)}")
    
    # Show all states
    print("\n🔍 All States:")
    for name, node in graph.nodes.items():
        print(f"   - {name}: {node.description}")
    
    # Show transitions from desktop
    print("\n🔀 Transitions from 'desktop_visible':")
    transitions = graph.get_transitions_from("desktop_visible")
    for t in transitions:
        print(f"   - {t.action} -> {t.to_state} (cost: {t.cost}, confidence: {t.confidence})")
    
    # Find path
    print("\n🗺️  Path Finding:")
    path = finder.find_path("desktop_visible", "notepad_open")
    if path:
        print(f"   Found path with {len(path)} steps:")
        for i, transition in enumerate(path, 1):
            print(f"   {i}. {transition.action}: {transition.from_state} -> {transition.to_state}")
        
        cost = sum(t.cost for t in path)
        print(f"   Total cost: {cost}")
    
    # Get next action
    next_action = finder.get_next_action("desktop_visible", "calculator_open")
    print(f"\n🎯 Next action from 'desktop_visible' to 'calculator_open': {next_action}")
    
    # Reachable states
    reachable = finder.get_reachable_states("desktop_visible", max_steps=2)
    print(f"\n📍 Reachable states from 'desktop_visible' (2 steps): {reachable}")
    
    # State tracker
    print("\n📈 State Tracker:")
    print(f"   - Current state: {tracker.get_current_state()}")
    print(f"   - History length: {len(tracker.get_history())}")
    
    # Simulate state transitions
    print("\n🔄 Simulating state transitions:")
    tracker.update_state("start_menu_open", action_taken="click_start")
    print(f"   1. Updated to: {tracker.get_current_state()}")
    
    tracker.update_state("search_active", action_taken="start_typing")
    print(f"   2. Updated to: {tracker.get_current_state()}")
    
    tracker.update_state("notepad_open", action_taken="search_and_open_notepad")
    print(f"   3. Updated to: {tracker.get_current_state()}")
    
    # Show path taken
    path_taken = tracker.get_path_taken()
    print(f"\n🛤️  Path taken: {' -> '.join(path_taken)}")
    
    # Show actions taken
    actions_taken = tracker.get_actions_taken()
    print(f"   Actions: {actions_taken}")
    
    # Summary
    summary = tracker.get_summary()
    print(f"\n📊 Summary:")
    for key, value in summary.items():
        print(f"   - {key}: {value}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("🚀 STATE GRAPH DEMO SUITE")
    print("=" * 70)
    
    # Menu
    print("\nSelect demo:")
    print("1. Execute task WITH State Graph (Notepad)")
    print("2. Execute task WITHOUT State Graph (Calculator)")
    print("3. State Graph Features (no execution)")
    print("4. Run all demos")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        await demo_with_state_graph()
    elif choice == "2":
        await demo_without_state_graph()
    elif choice == "3":
        await demo_state_graph_features()
    elif choice == "4":
        await demo_state_graph_features()
        await demo_with_state_graph()
        await demo_without_state_graph()
    else:
        print("Invalid choice!")
        return
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETED!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

