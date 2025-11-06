"""Task Decomposer - Hierarchical task decomposition with knowledge reuse.

This module provides:
- Decomposition of complex tasks into sub-tasks
- Reuse of learned sub-task graphs
- Dynamic linking between state graphs
- Meta-graph management
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agents.desktop_rpa.state_graph.graph import StateGraph

logger = logging.getLogger(__name__)


@dataclass
class SubTask:
    """Represents a sub-task in a hierarchical task."""
    
    name: str
    description: str
    graph_id: str | None = None  # ID of learned graph, if available
    is_learned: bool = False
    dependencies: list[str] = field(default_factory=list)  # List of sub-task names this depends on
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskDecomposition:
    """Represents a hierarchical task decomposition."""
    
    task_name: str
    description: str
    sub_tasks: list[SubTask] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class TaskDecomposer:
    """Decomposes complex tasks into sub-tasks and manages knowledge reuse."""
    
    def __init__(self, graph_storage_dir: Path | None = None):
        """Initialize task decomposer.
        
        Args:
            graph_storage_dir: Directory where state graphs are stored
        """
        self.graph_storage_dir = graph_storage_dir or Path("data/state_graphs")
        self.graph_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache of learned graphs
        self.learned_graphs: dict[str, StateGraph] = {}
        
        # Load existing graphs
        self._load_learned_graphs()
    
    def _load_learned_graphs(self):
        """Load all learned state graphs from storage."""
        if not self.graph_storage_dir.exists():
            return
        
        for graph_file in self.graph_storage_dir.glob("*.json"):
            try:
                graph = StateGraph.load(graph_file)
                # Use task name as key (normalized)
                task_name = graph_file.stem.replace("_", " ").lower()
                self.learned_graphs[task_name] = graph
                logger.info(f"Loaded learned graph: {task_name}")
            except Exception as e:
                logger.warning(f"Failed to load graph {graph_file}: {e}")
    
    def decompose_task(self, task_description: str) -> TaskDecomposition:
        """Decompose a task into sub-tasks.
        
        This uses heuristics and patterns to break down complex tasks.
        In the future, this could use LLM for intelligent decomposition.
        
        Args:
            task_description: Description of the task to decompose
            
        Returns:
            TaskDecomposition with sub-tasks
        """
        task_lower = task_description.lower()
        
        # Pattern: "Activate Ransomware Protection in Windows"
        if "ransomware" in task_lower and "windows" in task_lower:
            return self._decompose_ransomware_protection(task_description)
        
        # Pattern: "Install X application"
        if "install" in task_lower:
            return self._decompose_installation(task_description)
        
        # Pattern: "Configure X in Y"
        if "configure" in task_lower or "settings" in task_lower:
            return self._decompose_configuration(task_description)
        
        # Default: Single task (no decomposition)
        return TaskDecomposition(
            task_name=task_description,
            description=task_description,
            sub_tasks=[
                SubTask(
                    name=task_description,
                    description=task_description,
                )
            ]
        )
    
    def _decompose_ransomware_protection(self, task_description: str) -> TaskDecomposition:
        """Decompose ransomware protection activation task."""
        sub_tasks = [
            SubTask(
                name="Get Windows Version",
                description="Determine the Windows version of the system",
                graph_id=self._find_learned_graph("get windows version"),
            ),
            SubTask(
                name="Open Windows Security",
                description="Open Windows Security settings",
                dependencies=["Get Windows Version"],
                graph_id=self._find_learned_graph("open windows security"),
            ),
            SubTask(
                name="Navigate to Virus & Threat Protection",
                description="Navigate to Virus & threat protection settings",
                dependencies=["Open Windows Security"],
                graph_id=self._find_learned_graph("navigate virus threat protection"),
            ),
            SubTask(
                name="Enable Ransomware Protection",
                description="Enable Controlled folder access (Ransomware protection)",
                dependencies=["Navigate to Virus & Threat Protection"],
                graph_id=self._find_learned_graph("enable ransomware protection"),
            ),
        ]
        
        # Mark sub-tasks as learned if graph exists
        for sub_task in sub_tasks:
            sub_task.is_learned = sub_task.graph_id is not None
        
        return TaskDecomposition(
            task_name="Activate Ransomware Protection",
            description=task_description,
            sub_tasks=sub_tasks,
            metadata={
                "requires_admin": True,
                "windows_version_min": "10",
            }
        )
    
    def _decompose_installation(self, task_description: str) -> TaskDecomposition:
        """Decompose software installation task."""
        # Extract app name (simple heuristic)
        app_name = task_description.replace("install", "").strip()
        
        sub_tasks = [
            SubTask(
                name="Open Browser",
                description="Open web browser to download installer",
                graph_id=self._find_learned_graph("open browser"),
            ),
            SubTask(
                name=f"Download {app_name}",
                description=f"Download {app_name} installer",
                dependencies=["Open Browser"],
            ),
            SubTask(
                name=f"Run Installer",
                description=f"Run the {app_name} installer",
                dependencies=[f"Download {app_name}"],
            ),
            SubTask(
                name="Complete Installation",
                description="Follow installation wizard and complete setup",
                dependencies=["Run Installer"],
            ),
        ]
        
        for sub_task in sub_tasks:
            sub_task.is_learned = sub_task.graph_id is not None
        
        return TaskDecomposition(
            task_name=f"Install {app_name}",
            description=task_description,
            sub_tasks=sub_tasks,
        )
    
    def _decompose_configuration(self, task_description: str) -> TaskDecomposition:
        """Decompose configuration task."""
        sub_tasks = [
            SubTask(
                name="Open Settings",
                description="Open system settings",
                graph_id=self._find_learned_graph("open settings"),
            ),
            SubTask(
                name="Navigate to Setting",
                description="Navigate to the specific setting",
                dependencies=["Open Settings"],
            ),
            SubTask(
                name="Apply Configuration",
                description="Apply the configuration changes",
                dependencies=["Navigate to Setting"],
            ),
        ]
        
        for sub_task in sub_tasks:
            sub_task.is_learned = sub_task.graph_id is not None
        
        return TaskDecomposition(
            task_name="Configure Setting",
            description=task_description,
            sub_tasks=sub_tasks,
        )
    
    def _find_learned_graph(self, task_name: str) -> str | None:
        """Find a learned graph for a task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Graph ID if found, None otherwise
        """
        task_normalized = task_name.lower().strip()
        
        # Exact match
        if task_normalized in self.learned_graphs:
            return task_normalized
        
        # Fuzzy match (contains)
        for learned_task in self.learned_graphs.keys():
            if task_normalized in learned_task or learned_task in task_normalized:
                return learned_task
        
        return None
    
    def get_learned_graph(self, graph_id: str) -> StateGraph | None:
        """Get a learned graph by ID.
        
        Args:
            graph_id: Graph ID
            
        Returns:
            StateGraph if found, None otherwise
        """
        return self.learned_graphs.get(graph_id)
    
    def save_learned_graph(self, task_name: str, graph: StateGraph):
        """Save a learned graph for future reuse.
        
        Args:
            task_name: Name of the task
            graph: State graph to save
        """
        task_normalized = task_name.lower().strip().replace(" ", "_")
        graph_file = self.graph_storage_dir / f"{task_normalized}.json"
        
        graph.save(graph_file)
        self.learned_graphs[task_name.lower().strip()] = graph
        
        logger.info(f"Saved learned graph: {task_name} -> {graph_file}")
    
    def get_execution_order(self, decomposition: TaskDecomposition) -> list[SubTask]:
        """Get the execution order of sub-tasks based on dependencies.
        
        Args:
            decomposition: Task decomposition
            
        Returns:
            List of sub-tasks in execution order
        """
        # Topological sort
        executed = set()
        result = []
        
        def can_execute(sub_task: SubTask) -> bool:
            """Check if all dependencies are executed."""
            return all(dep in executed for dep in sub_task.dependencies)
        
        remaining = list(decomposition.sub_tasks)
        
        while remaining:
            # Find tasks that can be executed
            ready = [t for t in remaining if can_execute(t)]
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning("Cannot resolve dependencies, executing remaining tasks in order")
                result.extend(remaining)
                break
            
            # Execute first ready task
            task = ready[0]
            result.append(task)
            executed.add(task.name)
            remaining.remove(task)
        
        return result

