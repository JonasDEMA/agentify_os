"""Path Finder - Find optimal paths through state graph."""

import heapq
import logging
from typing import Any

from agents.desktop_rpa.state_graph.graph import StateGraph, StateTransition

logger = logging.getLogger(__name__)


class PathFinder:
    """Finds optimal paths through state graph using A* algorithm."""
    
    def __init__(self, graph: StateGraph):
        """Initialize path finder.
        
        Args:
            graph: State graph to search
        """
        self.graph = graph
        logger.info("Path Finder initialized")
    
    def find_path(
        self,
        start_state: str,
        goal_state: str,
        heuristic: dict[str, float] | None = None,
    ) -> list[StateTransition] | None:
        """Find shortest path from start to goal using A* algorithm.
        
        Args:
            start_state: Starting state
            goal_state: Goal state
            heuristic: Optional heuristic function (state -> estimated cost to goal)
        
        Returns:
            List of transitions forming the path, or None if no path exists
        """
        if start_state not in self.graph.nodes:
            logger.warning(f"Start state not in graph: {start_state}")
            return None
        
        if goal_state not in self.graph.nodes:
            logger.warning(f"Goal state not in graph: {goal_state}")
            return None
        
        if start_state == goal_state:
            logger.info("Start and goal are the same")
            return []
        
        # A* algorithm
        # Priority queue: (f_score, state, path)
        # f_score = g_score + h_score
        # g_score = actual cost from start
        # h_score = estimated cost to goal (heuristic)
        
        heuristic = heuristic or {}
        
        # Initialize
        open_set = [(0, start_state, [])]  # (f_score, state, path)
        g_scores = {start_state: 0}  # Actual cost from start
        visited = set()
        
        while open_set:
            f_score, current_state, path = heapq.heappop(open_set)
            
            if current_state in visited:
                continue
            
            visited.add(current_state)
            
            # Check if we reached the goal
            if current_state == goal_state:
                logger.info(f"Found path from {start_state} to {goal_state} with {len(path)} steps")
                return path
            
            # Explore neighbors
            transitions = self.graph.get_transitions_from(current_state)
            
            for transition in transitions:
                neighbor = transition.to_state
                
                if neighbor in visited:
                    continue
                
                # Calculate g_score (actual cost from start)
                tentative_g_score = g_scores[current_state] + transition.cost
                
                # Check if this is a better path
                if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g_score
                    
                    # Calculate h_score (estimated cost to goal)
                    h_score = heuristic.get(neighbor, 0)
                    
                    # Calculate f_score
                    f_score = tentative_g_score + h_score
                    
                    # Add to open set
                    new_path = path + [transition]
                    heapq.heappush(open_set, (f_score, neighbor, new_path))
        
        logger.warning(f"No path found from {start_state} to {goal_state}")
        return None
    
    def find_all_paths(
        self,
        start_state: str,
        goal_state: str,
        max_depth: int = 10,
    ) -> list[list[StateTransition]]:
        """Find all paths from start to goal (DFS with depth limit).
        
        Args:
            start_state: Starting state
            goal_state: Goal state
            max_depth: Maximum path length
        
        Returns:
            List of all paths (each path is a list of transitions)
        """
        if start_state not in self.graph.nodes or goal_state not in self.graph.nodes:
            return []
        
        if start_state == goal_state:
            return [[]]
        
        all_paths = []
        
        def dfs(current: str, path: list[StateTransition], visited: set[str], depth: int):
            """Depth-first search for all paths."""
            if depth > max_depth:
                return
            
            if current == goal_state:
                all_paths.append(path.copy())
                return
            
            transitions = self.graph.get_transitions_from(current)
            
            for transition in transitions:
                neighbor = transition.to_state
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(transition)
                    
                    dfs(neighbor, path, visited, depth + 1)
                    
                    path.pop()
                    visited.remove(neighbor)
        
        dfs(start_state, [], {start_state}, 0)
        
        logger.info(f"Found {len(all_paths)} paths from {start_state} to {goal_state}")
        return all_paths
    
    def get_next_action(self, current_state: str, goal_state: str) -> str | None:
        """Get the next action to take from current state towards goal.
        
        Args:
            current_state: Current state
            goal_state: Goal state
        
        Returns:
            Action to take, or None if no path exists
        """
        path = self.find_path(current_state, goal_state)
        
        if not path:
            return None
        
        # Return first action in path
        return path[0].action
    
    def estimate_cost(self, start_state: str, goal_state: str) -> float | None:
        """Estimate cost of path from start to goal.
        
        Args:
            start_state: Starting state
            goal_state: Goal state
        
        Returns:
            Estimated cost, or None if no path exists
        """
        path = self.find_path(start_state, goal_state)
        
        if not path:
            return None
        
        # Sum costs of all transitions
        return sum(t.cost for t in path)
    
    def get_reachable_states(self, start_state: str, max_steps: int = 5) -> set[str]:
        """Get all states reachable from start within max_steps.
        
        Args:
            start_state: Starting state
            max_steps: Maximum number of steps
        
        Returns:
            Set of reachable state names
        """
        if start_state not in self.graph.nodes:
            return set()
        
        reachable = {start_state}
        frontier = {start_state}
        
        for _ in range(max_steps):
            new_frontier = set()
            
            for state in frontier:
                neighbors = self.graph.get_neighbors(state)
                for neighbor in neighbors:
                    if neighbor not in reachable:
                        reachable.add(neighbor)
                        new_frontier.add(neighbor)
            
            frontier = new_frontier
            
            if not frontier:
                break
        
        logger.debug(f"Found {len(reachable)} reachable states from {start_state} within {max_steps} steps")
        return reachable

