"""State Tracker - Track current state and state history."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agents.desktop_rpa.state_graph.graph import StateGraph

logger = logging.getLogger(__name__)


@dataclass
class StateHistoryEntry:
    """Represents a state in the history."""
    
    state: str
    timestamp: datetime
    action_taken: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state": self.state,
            "timestamp": self.timestamp.isoformat(),
            "action_taken": self.action_taken,
            "metadata": self.metadata,
        }


class StateTracker:
    """Tracks current state and maintains state history."""
    
    def __init__(self, graph: StateGraph, initial_state: str = "desktop_visible"):
        """Initialize state tracker.
        
        Args:
            graph: State graph
            initial_state: Initial state
        """
        self.graph = graph
        self.current_state = initial_state
        self.history: list[StateHistoryEntry] = []
        
        # Add initial state to history
        self._add_to_history(initial_state, action_taken=None)
        
        logger.info(f"State Tracker initialized with state: {initial_state}")
    
    def _add_to_history(self, state: str, action_taken: str | None = None, metadata: dict[str, Any] | None = None):
        """Add state to history."""
        entry = StateHistoryEntry(
            state=state,
            timestamp=datetime.now(),
            action_taken=action_taken,
            metadata=metadata or {},
        )
        self.history.append(entry)
        logger.debug(f"Added to history: {state} (action: {action_taken})")
    
    def update_state(self, new_state: str, action_taken: str | None = None, metadata: dict[str, Any] | None = None):
        """Update current state.
        
        Args:
            new_state: New state
            action_taken: Action that led to this state
            metadata: Additional metadata
        """
        old_state = self.current_state
        self.current_state = new_state
        
        # Add to history
        self._add_to_history(new_state, action_taken, metadata)
        
        logger.info(f"State updated: {old_state} -> {new_state} (action: {action_taken})")
    
    def get_current_state(self) -> str:
        """Get current state."""
        return self.current_state
    
    def get_history(self, limit: int | None = None) -> list[StateHistoryEntry]:
        """Get state history.
        
        Args:
            limit: Maximum number of entries to return (most recent first)
        
        Returns:
            List of history entries
        """
        if limit is None:
            return self.history.copy()
        
        return self.history[-limit:]
    
    def get_last_action(self) -> str | None:
        """Get the last action taken."""
        if len(self.history) < 2:
            return None
        
        return self.history[-1].action_taken
    
    def get_state_count(self, state: str) -> int:
        """Count how many times a state has been visited.
        
        Args:
            state: State name
        
        Returns:
            Number of times visited
        """
        return sum(1 for entry in self.history if entry.state == state)
    
    def is_looping(self, window_size: int = 5) -> bool:
        """Check if we're stuck in a loop.
        
        Args:
            window_size: Number of recent states to check
        
        Returns:
            True if we're looping
        """
        if len(self.history) < window_size:
            return False
        
        recent_states = [entry.state for entry in self.history[-window_size:]]
        
        # Check if all states are the same
        if len(set(recent_states)) == 1:
            logger.warning(f"Detected loop: stuck in state {recent_states[0]}")
            return True
        
        # Check if we're alternating between two states
        if len(set(recent_states)) == 2 and window_size >= 4:
            # Check for pattern like [A, B, A, B]
            if all(recent_states[i] == recent_states[i % 2] for i in range(len(recent_states))):
                logger.warning(f"Detected loop: alternating between {set(recent_states)}")
                return True
        
        return False
    
    def get_path_taken(self) -> list[str]:
        """Get the path taken (list of states).
        
        Returns:
            List of state names in order
        """
        return [entry.state for entry in self.history]
    
    def get_actions_taken(self) -> list[str]:
        """Get the actions taken.
        
        Returns:
            List of actions in order (excluding None)
        """
        return [entry.action_taken for entry in self.history if entry.action_taken is not None]
    
    def reset(self, initial_state: str = "desktop_visible"):
        """Reset tracker to initial state.
        
        Args:
            initial_state: State to reset to
        """
        self.current_state = initial_state
        self.history.clear()
        self._add_to_history(initial_state, action_taken=None)
        logger.info(f"State Tracker reset to: {initial_state}")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_state": self.current_state,
            "history": [entry.to_dict() for entry in self.history],
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics.
        
        Returns:
            Dictionary with summary stats
        """
        states_visited = set(entry.state for entry in self.history)
        actions_taken = [entry.action_taken for entry in self.history if entry.action_taken]
        
        return {
            "current_state": self.current_state,
            "total_steps": len(self.history) - 1,  # Exclude initial state
            "unique_states": len(states_visited),
            "states_visited": list(states_visited),
            "total_actions": len(actions_taken),
            "is_looping": self.is_looping(),
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"StateTracker(current={self.current_state}, steps={len(self.history)-1})"

