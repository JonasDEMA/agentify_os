"""Tests for Task Graph and ToDo Schema."""

import pytest
from scheduler.core.task_graph import (
    ActionType,
    ExecutionResult,
    TaskGraph,
    ToDo,
)


class TestToDo:
    """Tests for ToDo model."""

    def test_create_minimal_todo(self) -> None:
        """Test creating a minimal ToDo."""
        todo = ToDo(
            action=ActionType.CLICK,
            selector="button#submit",
        )
        assert todo.action == ActionType.CLICK
        assert todo.selector == "button#submit"
        assert todo.text is None
        assert todo.timeout == 30.0
        assert todo.depends_on == []

    def test_create_full_todo(self) -> None:
        """Test creating a full ToDo with all fields."""
        todo = ToDo(
            action=ActionType.TYPE,
            selector="input#email",
            text="test@example.com",
            timeout=10.0,
            depends_on=["task-1", "task-2"],
        )
        assert todo.action == ActionType.TYPE
        assert todo.selector == "input#email"
        assert todo.text == "test@example.com"
        assert todo.timeout == 10.0
        assert todo.depends_on == ["task-1", "task-2"]

    def test_todo_serialization(self) -> None:
        """Test ToDo serialization."""
        todo = ToDo(
            action=ActionType.SEND_MAIL,
            selector="recipient@example.com",
            text="Hello World",
        )
        data = todo.model_dump()
        assert data["action"] == "send_mail"
        assert data["selector"] == "recipient@example.com"
        assert data["text"] == "Hello World"


class TestExecutionResult:
    """Tests for ExecutionResult model."""

    def test_create_success_result(self) -> None:
        """Test creating a successful execution result."""
        result = ExecutionResult(
            success=True,
            result={"status": "ok"},
            duration=1.5,
        )
        assert result.success is True
        assert result.result == {"status": "ok"}
        assert result.error is None
        assert result.duration == 1.5

    def test_create_failure_result(self) -> None:
        """Test creating a failed execution result."""
        result = ExecutionResult(
            success=False,
            error="Element not found",
            duration=0.5,
        )
        assert result.success is False
        assert result.result is None
        assert result.error == "Element not found"
        assert result.duration == 0.5


class TestTaskGraph:
    """Tests for TaskGraph class."""

    def test_create_empty_graph(self) -> None:
        """Test creating an empty task graph."""
        graph = TaskGraph()
        assert len(graph.tasks) == 0

    def test_add_single_task(self) -> None:
        """Test adding a single task."""
        graph = TaskGraph()
        task_id = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="button#submit")
        )
        assert len(graph.tasks) == 1
        assert task_id in graph.tasks

    def test_add_multiple_tasks(self) -> None:
        """Test adding multiple tasks."""
        graph = TaskGraph()
        task1 = graph.add_task(ToDo(action=ActionType.OPEN_APP, selector="chrome"))
        task2 = graph.add_task(ToDo(action=ActionType.CLICK, selector="button"))
        task3 = graph.add_task(ToDo(action=ActionType.TYPE, selector="input", text="test"))

        assert len(graph.tasks) == 3
        assert task1 in graph.tasks
        assert task2 in graph.tasks
        assert task3 in graph.tasks

    def test_sequential_tasks(self) -> None:
        """Test sequential task execution order."""
        graph = TaskGraph()
        task1 = graph.add_task(ToDo(action=ActionType.OPEN_APP, selector="chrome"))
        task2 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="button", depends_on=[task1])
        )
        task3 = graph.add_task(
            ToDo(action=ActionType.TYPE, selector="input", text="test", depends_on=[task2])
        )

        order = graph.topological_sort()
        assert order == [task1, task2, task3]

    def test_parallel_tasks(self) -> None:
        """Test parallel task execution."""
        graph = TaskGraph()
        task1 = graph.add_task(ToDo(action=ActionType.OPEN_APP, selector="chrome"))
        task2 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="button1", depends_on=[task1])
        )
        task3 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="button2", depends_on=[task1])
        )
        task4 = graph.add_task(
            ToDo(action=ActionType.WAIT_FOR, selector="result", depends_on=[task2, task3])
        )

        batches = graph.get_parallel_batches()
        assert len(batches) == 3
        assert batches[0] == [task1]
        assert set(batches[1]) == {task2, task3}  # Parallel execution
        assert batches[2] == [task4]

    def test_mixed_dependencies(self) -> None:
        """Test mixed sequential and parallel dependencies."""
        graph = TaskGraph()
        # Task 1: Open app
        task1 = graph.add_task(ToDo(action=ActionType.OPEN_APP, selector="app"))

        # Tasks 2, 3, 4: Parallel (all depend on task1)
        task2 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="btn1", depends_on=[task1])
        )
        task3 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="btn2", depends_on=[task1])
        )
        task4 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="btn3", depends_on=[task1])
        )

        # Task 5: Depends on task2 and task3
        task5 = graph.add_task(
            ToDo(action=ActionType.WAIT_FOR, selector="result", depends_on=[task2, task3])
        )

        # Task 6: Depends on task4 and task5
        task6 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="submit", depends_on=[task4, task5])
        )

        batches = graph.get_parallel_batches()
        assert len(batches) == 4
        assert batches[0] == [task1]
        assert set(batches[1]) == {task2, task3, task4}
        assert batches[2] == [task5]
        assert batches[3] == [task6]

    def test_cycle_detection(self) -> None:
        """Test cycle detection in task graph."""
        graph = TaskGraph()
        task1 = graph.add_task(ToDo(action=ActionType.CLICK, selector="btn1"))
        task2 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="btn2", depends_on=[task1])
        )

        # Create a cycle: task1 depends on task2
        graph.tasks[task1].depends_on = [task2]

        with pytest.raises(ValueError, match="Cycle detected"):
            graph.detect_cycles()

    def test_self_dependency(self) -> None:
        """Test detection of self-dependency."""
        graph = TaskGraph()
        task1 = graph.add_task(ToDo(action=ActionType.CLICK, selector="btn"))

        # Create self-dependency
        graph.tasks[task1].depends_on = [task1]

        with pytest.raises(ValueError, match="Cycle detected"):
            graph.detect_cycles()

    def test_empty_graph_operations(self) -> None:
        """Test operations on empty graph."""
        graph = TaskGraph()
        assert graph.topological_sort() == []
        assert graph.get_parallel_batches() == []
        # Should not raise error
        graph.detect_cycles()

    def test_single_task_operations(self) -> None:
        """Test operations on graph with single task."""
        graph = TaskGraph()
        task1 = graph.add_task(ToDo(action=ActionType.CLICK, selector="btn"))

        assert graph.topological_sort() == [task1]
        assert graph.get_parallel_batches() == [[task1]]
        graph.detect_cycles()  # Should not raise error

    def test_invalid_dependency(self) -> None:
        """Test adding task with invalid dependency."""
        graph = TaskGraph()
        with pytest.raises(ValueError, match="Dependency .* not found"):
            graph.add_task(
                ToDo(action=ActionType.CLICK, selector="btn", depends_on=["invalid-id"])
            )

    def test_get_task(self) -> None:
        """Test getting a task by ID."""
        graph = TaskGraph()
        task_id = graph.add_task(ToDo(action=ActionType.CLICK, selector="btn"))
        task = graph.get_task(task_id)
        assert task is not None
        assert task.action == ActionType.CLICK
        assert task.selector == "btn"

    def test_get_nonexistent_task(self) -> None:
        """Test getting a non-existent task."""
        graph = TaskGraph()
        task = graph.get_task("invalid-id")
        assert task is None

    def test_complex_graph(self) -> None:
        """Test a complex task graph with multiple levels."""
        graph = TaskGraph()

        # Level 0
        t1 = graph.add_task(ToDo(action=ActionType.OPEN_APP, selector="app"))

        # Level 1
        t2 = graph.add_task(ToDo(action=ActionType.CLICK, selector="menu", depends_on=[t1]))

        # Level 2
        t3 = graph.add_task(ToDo(action=ActionType.CLICK, selector="item1", depends_on=[t2]))
        t4 = graph.add_task(ToDo(action=ActionType.CLICK, selector="item2", depends_on=[t2]))

        # Level 3
        t5 = graph.add_task(ToDo(action=ActionType.TYPE, selector="input1", text="a", depends_on=[t3]))
        t6 = graph.add_task(ToDo(action=ActionType.TYPE, selector="input2", text="b", depends_on=[t4]))

        # Level 4
        t7 = graph.add_task(
            ToDo(action=ActionType.CLICK, selector="submit", depends_on=[t5, t6])
        )

        batches = graph.get_parallel_batches()
        assert len(batches) == 5
        assert batches[0] == [t1]
        assert batches[1] == [t2]
        assert set(batches[2]) == {t3, t4}
        assert set(batches[3]) == {t5, t6}
        assert batches[4] == [t7]

