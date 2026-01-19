"""State Graph - Manages application states and transitions between them."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class State(BaseModel):
    """Represents a discrete state of an application or desktop."""
    state_id: str
    name: str
    description: str
    detection_rules: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Transition(BaseModel):
    """Represents a move from one state to another via a set of actions."""
    transition_id: str
    from_state: str
    to_state: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    success_rate: float = 1.0
    execution_count: int = 0
    average_duration: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StateGraph(BaseModel):
    """A collection of states and transitions forming a graph."""
    graph_id: str
    name: str
    description: str
    states: Dict[str, State] = Field(default_factory=dict)
    transitions: List[Transition] = Field(default_factory=list)
    entry_state: Optional[str] = None
    goal_states: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    revision: int = 1

    def add_state(self, state: State):
        """Add a state to the graph."""
        self.states[state.state_id] = state
        self.updated_at = datetime.now()

    def add_transition(self, transition: Transition):
        """Add a transition to the graph."""
        # Validate states exist
        if transition.from_state not in self.states:
            raise ValueError(f"From-state {transition.from_state} not in graph")
        if transition.to_state not in self.states:
            raise ValueError(f"To-state {transition.to_state} not in graph")
        
        self.transitions.append(transition)
        self.updated_at = datetime.now()

    def find_path(self, from_state_id: str, to_state_id: str) -> Optional[List[Transition]]:
        """Find a sequence of transitions from one state to another using BFS.

        Args:
            from_state_id: Starting state ID
            to_state_id: Target state ID

        Returns:
            List of transitions or None if no path found
        """
        if from_state_id == to_state_id:
            return []

        # Simple BFS for pathfinding
        queue = [(from_state_id, [])]
        visited = {from_state_id}

        while queue:
            current_state, path = queue.pop(0)
            
            # Find all outgoing transitions
            for trans in self.transitions:
                if trans.from_state == current_state:
                    if trans.to_state == to_state_id:
                        return path + [trans]
                    
                    if trans.to_state not in visited:
                        visited.add(trans.to_state)
                        queue.append((trans.to_state, path + [trans]))
        
        return None

    def get_current_transitions(self, state_id: str) -> List[Transition]:
        """Get all available transitions from a specific state."""
        return [t for t in self.transitions if t.from_state == state_id]
