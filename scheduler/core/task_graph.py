"""Task Graph and ToDo Schema.

Manages task dependencies and execution order.
"""

from collections import defaultdict, deque
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Task action types."""

    OPEN_APP = "open_app"  # Open application
    CLICK = "click"  # Click element
    TYPE = "type"  # Type text
    WAIT_FOR = "wait_for"  # Wait for element
    PLAYWRIGHT = "playwright"  # Playwright script
    UIA = "uia"  # UI Automation
    SEND_MAIL = "send_mail"  # Send email


class ToDo(BaseModel):
    """Task definition model.

    Represents a single task to be executed.
    """

    action: ActionType = Field(..., description="Action type")
    selector: str = Field(..., description="Element selector or target")
    text: str | None = Field(None, description="Text to type or email body")
    timeout: float = Field(30.0, description="Timeout in seconds")
    depends_on: list[str] = Field(default_factory=list, description="Task IDs this task depends on")


class ExecutionResult(BaseModel):
    """Execution result model."""

    success: bool = Field(..., description="Whether execution was successful")
    result: dict[str, Any] | None = Field(None, description="Execution result data")
    error: str | None = Field(None, description="Error message if failed")
    duration: float = Field(..., description="Execution duration in seconds")


class TaskGraph:
    """Task graph for managing task dependencies and execution order.

    Supports:
    - Adding tasks with dependencies
    - Topological sorting for execution order
    - Parallel batch detection
    - Cycle detection
    """

    def __init__(self) -> None:
        """Initialize empty task graph."""
        self.tasks: dict[str, ToDo] = {}

    def add_task(self, todo: ToDo) -> str:
        """Add a task to the graph.

        Args:
            todo: Task to add

        Returns:
            Task ID

        Raises:
            ValueError: If dependency not found
        """
        # Validate dependencies exist
        for dep_id in todo.depends_on:
            if dep_id not in self.tasks:
                msg = f"Dependency {dep_id} not found in task graph"
                raise ValueError(msg)

        # Generate task ID
        task_id = str(uuid4())

        # Add task
        self.tasks[task_id] = todo

        return task_id

    def get_task(self, task_id: str) -> ToDo | None:
        """Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        return self.tasks.get(task_id)

    def topological_sort(self) -> list[str]:
        """Perform topological sort on task graph.

        Returns:
            List of task IDs in execution order

        Raises:
            ValueError: If cycle detected
        """
        if not self.tasks:
            return []

        # Build adjacency list and in-degree count
        in_degree: dict[str, int] = defaultdict(int)
        adj_list: dict[str, list[str]] = defaultdict(list)

        # Initialize all tasks with in-degree 0
        for task_id in self.tasks:
            in_degree[task_id] = 0

        # Build graph
        for task_id, task in self.tasks.items():
            for dep_id in task.depends_on:
                adj_list[dep_id].append(task_id)
                in_degree[task_id] += 1

        # Kahn's algorithm
        queue: deque[str] = deque()
        for task_id, degree in in_degree.items():
            if degree == 0:
                queue.append(task_id)

        result: list[str] = []
        while queue:
            task_id = queue.popleft()
            result.append(task_id)

            for neighbor in adj_list[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self.tasks):
            msg = "Cycle detected in task graph"
            raise ValueError(msg)

        return result

    def get_parallel_batches(self) -> list[list[str]]:
        """Get parallel execution batches.

        Groups tasks that can be executed in parallel.

        Returns:
            List of batches, where each batch contains task IDs that can run in parallel
        """
        if not self.tasks:
            return []

        # Build adjacency list and in-degree count
        in_degree: dict[str, int] = defaultdict(int)
        adj_list: dict[str, list[str]] = defaultdict(list)

        # Initialize all tasks with in-degree 0
        for task_id in self.tasks:
            in_degree[task_id] = 0

        # Build graph
        for task_id, task in self.tasks.items():
            for dep_id in task.depends_on:
                adj_list[dep_id].append(task_id)
                in_degree[task_id] += 1

        # Level-based BFS
        batches: list[list[str]] = []
        current_batch: list[str] = []

        # Start with tasks that have no dependencies
        for task_id, degree in in_degree.items():
            if degree == 0:
                current_batch.append(task_id)

        while current_batch:
            batches.append(current_batch)
            next_batch: list[str] = []

            for task_id in current_batch:
                for neighbor in adj_list[task_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_batch.append(neighbor)

            current_batch = next_batch

        return batches

    def detect_cycles(self) -> None:
        """Detect cycles in task graph.

        Raises:
            ValueError: If cycle detected
        """
        if not self.tasks:
            return

        # Use DFS with color marking
        # White (0): Not visited
        # Gray (1): Currently visiting
        # Black (2): Visited
        color: dict[str, int] = {task_id: 0 for task_id in self.tasks}

        def dfs(task_id: str) -> None:
            """DFS helper function."""
            color[task_id] = 1  # Mark as visiting

            task = self.tasks[task_id]
            for dep_id in task.depends_on:
                if color[dep_id] == 1:  # Back edge - cycle detected
                    msg = f"Cycle detected in task graph involving task {task_id}"
                    raise ValueError(msg)
                if color[dep_id] == 0:  # Not visited
                    dfs(dep_id)

            color[task_id] = 2  # Mark as visited

        # Visit all tasks
        for task_id in self.tasks:
            if color[task_id] == 0:
                dfs(task_id)

