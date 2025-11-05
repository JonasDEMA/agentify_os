"""State Graph - Directed graph of states and transitions."""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class StateNode:
    """Represents a state in the graph."""
    
    name: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self) -> int:
        """Make hashable for use in sets/dicts."""
        return hash(self.name)
    
    def __eq__(self, other: object) -> bool:
        """Equality based on name."""
        if not isinstance(other, StateNode):
            return False
        return self.name == other.name
    
    def __repr__(self) -> str:
        """String representation."""
        return f"StateNode(name='{self.name}')"


@dataclass
class StateTransition:
    """Represents a transition between states."""
    
    from_state: str
    to_state: str
    action: str
    confidence: float = 1.0
    cost: float = 1.0  # Cost of this transition (for path finding)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"StateTransition({self.from_state} --[{self.action}]--> {self.to_state})"


class StateGraph:
    """Directed graph of states and transitions."""
    
    def __init__(self):
        """Initialize empty state graph."""
        self.nodes: dict[str, StateNode] = {}
        self.transitions: list[StateTransition] = []
        logger.info("State Graph initialized")
    
    def add_node(self, name: str, description: str = "", metadata: dict[str, Any] | None = None) -> StateNode:
        """Add a state node to the graph."""
        if name in self.nodes:
            logger.debug(f"Node already exists: {name}")
            return self.nodes[name]
        
        node = StateNode(name=name, description=description, metadata=metadata or {})
        self.nodes[name] = node
        logger.debug(f"Added node: {node}")
        return node
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        action: str,
        confidence: float = 1.0,
        cost: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> StateTransition:
        """Add a transition between states."""
        # Ensure nodes exist
        if from_state not in self.nodes:
            self.add_node(from_state)
        if to_state not in self.nodes:
            self.add_node(to_state)
        
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            action=action,
            confidence=confidence,
            cost=cost,
            metadata=metadata or {},
        )
        
        self.transitions.append(transition)
        logger.debug(f"Added transition: {transition}")
        return transition
    
    def get_node(self, name: str) -> StateNode | None:
        """Get a node by name."""
        return self.nodes.get(name)
    
    def get_transitions_from(self, state: str) -> list[StateTransition]:
        """Get all transitions from a state."""
        return [t for t in self.transitions if t.from_state == state]
    
    def get_transitions_to(self, state: str) -> list[StateTransition]:
        """Get all transitions to a state."""
        return [t for t in self.transitions if t.to_state == state]
    
    def get_neighbors(self, state: str) -> list[str]:
        """Get all neighboring states (states reachable in one step)."""
        transitions = self.get_transitions_from(state)
        return [t.to_state for t in transitions]
    
    def has_path(self, from_state: str, to_state: str) -> bool:
        """Check if there's a path between two states (BFS)."""
        if from_state not in self.nodes or to_state not in self.nodes:
            return False
        
        if from_state == to_state:
            return True
        
        visited = set()
        queue = [from_state]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == to_state:
                return True
            
            neighbors = self.get_neighbors(current)
            queue.extend(neighbors)
        
        return False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert graph to dictionary."""
        return {
            "nodes": [
                {
                    "name": node.name,
                    "description": node.description,
                    "metadata": node.metadata,
                }
                for node in self.nodes.values()
            ],
            "transitions": [
                {
                    "from_state": t.from_state,
                    "to_state": t.to_state,
                    "action": t.action,
                    "confidence": t.confidence,
                    "cost": t.cost,
                    "metadata": t.metadata,
                }
                for t in self.transitions
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StateGraph":
        """Create graph from dictionary."""
        graph = cls()
        
        # Add nodes
        for node_data in data.get("nodes", []):
            graph.add_node(
                name=node_data["name"],
                description=node_data.get("description", ""),
                metadata=node_data.get("metadata", {}),
            )
        
        # Add transitions
        for trans_data in data.get("transitions", []):
            graph.add_transition(
                from_state=trans_data["from_state"],
                to_state=trans_data["to_state"],
                action=trans_data["action"],
                confidence=trans_data.get("confidence", 1.0),
                cost=trans_data.get("cost", 1.0),
                metadata=trans_data.get("metadata", {}),
            )
        
        return graph
    
    def __repr__(self) -> str:
        """String representation."""
        return f"StateGraph(nodes={len(self.nodes)}, transitions={len(self.transitions)})"

