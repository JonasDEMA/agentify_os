"""Test State Graph components."""

import logging

from agents.desktop_rpa.state_graph import PathFinder, StateGraph, StateTracker

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_state_graph():
    """Test State Graph creation and operations."""
    print("\n" + "=" * 60)
    print("🧪 TEST 1: State Graph")
    print("=" * 60)
    
    # Create graph
    graph = StateGraph()
    
    # Add nodes
    graph.add_node("desktop_visible", "Desktop is visible")
    graph.add_node("start_menu_open", "Start menu is open")
    graph.add_node("notepad_open", "Notepad is open")
    graph.add_node("calculator_open", "Calculator is open")
    
    # Add transitions
    graph.add_transition("desktop_visible", "start_menu_open", "click_start", confidence=0.95, cost=1.0)
    graph.add_transition("start_menu_open", "notepad_open", "click_notepad", confidence=0.90, cost=1.5)
    graph.add_transition("start_menu_open", "calculator_open", "click_calculator", confidence=0.90, cost=1.5)
    graph.add_transition("notepad_open", "desktop_visible", "close_notepad", confidence=0.95, cost=1.0)
    graph.add_transition("calculator_open", "desktop_visible", "close_calculator", confidence=0.95, cost=1.0)
    
    print(f"\n✅ Created graph: {graph}")
    print(f"   Nodes: {list(graph.nodes.keys())}")
    print(f"   Transitions: {len(graph.transitions)}")
    
    # Test neighbors
    neighbors = graph.get_neighbors("start_menu_open")
    print(f"\n✅ Neighbors of 'start_menu_open': {neighbors}")
    
    # Test path existence
    has_path = graph.has_path("desktop_visible", "notepad_open")
    print(f"\n✅ Path exists from 'desktop_visible' to 'notepad_open': {has_path}")
    
    # Test serialization
    graph_dict = graph.to_dict()
    print(f"\n✅ Serialized graph: {len(graph_dict['nodes'])} nodes, {len(graph_dict['transitions'])} transitions")
    
    # Test deserialization
    graph2 = StateGraph.from_dict(graph_dict)
    print(f"✅ Deserialized graph: {graph2}")
    
    return graph


def test_path_finder(graph: StateGraph):
    """Test Path Finder."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Path Finder")
    print("=" * 60)
    
    finder = PathFinder(graph)
    
    # Find path
    path = finder.find_path("desktop_visible", "notepad_open")
    
    if path:
        print(f"\n✅ Found path from 'desktop_visible' to 'notepad_open':")
        for i, transition in enumerate(path, 1):
            print(f"   {i}. {transition}")
        
        # Estimate cost
        cost = sum(t.cost for t in path)
        print(f"\n✅ Total cost: {cost}")
    else:
        print("\n❌ No path found")
    
    # Find all paths
    all_paths = finder.find_all_paths("desktop_visible", "notepad_open", max_depth=5)
    print(f"\n✅ Found {len(all_paths)} total paths")
    
    # Get next action
    next_action = finder.get_next_action("desktop_visible", "notepad_open")
    print(f"\n✅ Next action from 'desktop_visible' to 'notepad_open': {next_action}")
    
    # Get reachable states
    reachable = finder.get_reachable_states("desktop_visible", max_steps=2)
    print(f"\n✅ Reachable states from 'desktop_visible' (2 steps): {reachable}")
    
    return finder


def test_state_tracker(graph: StateGraph):
    """Test State Tracker."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: State Tracker")
    print("=" * 60)
    
    tracker = StateTracker(graph, initial_state="desktop_visible")
    
    print(f"\n✅ Initial state: {tracker.get_current_state()}")
    
    # Simulate state transitions
    tracker.update_state("start_menu_open", action_taken="click_start")
    print(f"✅ Updated to: {tracker.get_current_state()}")
    
    tracker.update_state("notepad_open", action_taken="click_notepad")
    print(f"✅ Updated to: {tracker.get_current_state()}")
    
    # Get history
    history = tracker.get_history()
    print(f"\n✅ History ({len(history)} entries):")
    for entry in history:
        print(f"   - {entry.state} (action: {entry.action_taken})")
    
    # Get path taken
    path = tracker.get_path_taken()
    print(f"\n✅ Path taken: {' -> '.join(path)}")
    
    # Get actions taken
    actions = tracker.get_actions_taken()
    print(f"✅ Actions taken: {actions}")
    
    # Test loop detection
    tracker.update_state("desktop_visible", action_taken="close_notepad")
    tracker.update_state("start_menu_open", action_taken="click_start")
    tracker.update_state("desktop_visible", action_taken="escape")
    tracker.update_state("start_menu_open", action_taken="click_start")
    
    is_looping = tracker.is_looping(window_size=4)
    print(f"\n✅ Is looping: {is_looping}")
    
    # Get summary
    summary = tracker.get_summary()
    print(f"\n✅ Summary:")
    for key, value in summary.items():
        print(f"   - {key}: {value}")
    
    return tracker


def test_integration(graph: StateGraph, finder: PathFinder, tracker: StateTracker):
    """Test integration of all components."""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Integration")
    print("=" * 60)
    
    # Reset tracker
    tracker.reset("desktop_visible")
    
    # Goal: Open Calculator
    goal = "calculator_open"
    print(f"\n🎯 Goal: {goal}")
    print(f"📍 Current state: {tracker.get_current_state()}")
    
    # Find path
    path = finder.find_path(tracker.get_current_state(), goal)
    
    if path:
        print(f"\n✅ Found path with {len(path)} steps:")
        
        # Execute path
        for i, transition in enumerate(path, 1):
            print(f"\n   Step {i}: {transition.action}")
            print(f"      {transition.from_state} -> {transition.to_state}")
            
            # Update tracker
            tracker.update_state(transition.to_state, action_taken=transition.action)
            print(f"      ✅ State updated to: {tracker.get_current_state()}")
        
        print(f"\n🎉 Goal reached! Current state: {tracker.get_current_state()}")
        
        # Show summary
        summary = tracker.get_summary()
        print(f"\n📊 Summary:")
        print(f"   - Total steps: {summary['total_steps']}")
        print(f"   - Unique states: {summary['unique_states']}")
        print(f"   - Path: {' -> '.join(tracker.get_path_taken())}")
    else:
        print("\n❌ No path found to goal")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 STATE GRAPH TEST SUITE")
    print("=" * 60)
    
    # Test 1: State Graph
    graph = test_state_graph()
    
    # Test 2: Path Finder
    finder = test_path_finder(graph)
    
    # Test 3: State Tracker
    tracker = test_state_tracker(graph)
    
    # Test 4: Integration
    test_integration(graph, finder, tracker)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()

