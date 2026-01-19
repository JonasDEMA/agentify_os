"""Integration test for end-to-end workflow."""
import pytest
import asyncio
from scheduler.core.task_graph import TaskGraph, ToDo, ActionType, TaskStatus
from scheduler.executors.executor_registry import ExecutorRegistry
from scheduler.executors.playwright_executor import PlaywrightExecutor
from scheduler.executors.mail_executor import MailExecutor

@pytest.mark.asyncio
async def test_e2e_workflow_simulation():
    """Test a full workflow simulation: Portal -> PDF -> Mail."""
    
    # 1. Setup registry and executors
    registry = ExecutorRegistry()
    registry.register(ActionType.PLAYWRIGHT, PlaywrightExecutor())
    registry.register(ActionType.SEND_MAIL, MailExecutor())
    
    # 2. Build task graph
    graph = TaskGraph()
    
    # Task 1: Open portal
    t1_id = graph.add_task(ToDo(
        action=ActionType.PLAYWRIGHT,
        selector="goto",
        text="https://portal.example.com"
    ))
    
    # Task 2: Click download (depends on t1)
    t2_id = graph.add_task(ToDo(
        action=ActionType.PLAYWRIGHT,
        selector="click",
        text="#download-pdf",
        depends_on=[t1_id]
    ))
    
    # Task 3: Send email (depends on t2)
    t3_id = graph.add_task(ToDo(
        action=ActionType.SEND_MAIL,
        selector="boss@example.com",
        text="Here is the report you requested.",
        depends_on=[t2_id]
    ))
    
    # 3. Simulate execution using parallel batches
    batches = graph.get_parallel_batches()
    assert len(batches) == 3 # Sequential workflow in this case
    
    results = {}
    for batch in batches:
        for task_id in batch:
            task = graph.get_task(task_id)
            result = await registry.execute(task)
            assert result.success is True
            results[task_id] = result
            
    # 4. Verify results
    assert t3_id in results
    assert "boss@example.com" in results[t3_id].result["output"]
    assert "https://portal.example.com" in results[t1_id].result["output"]
