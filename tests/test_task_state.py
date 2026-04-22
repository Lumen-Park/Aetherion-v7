import pytest
from unittest.mock import patch
from core.task_state import TaskStateManager, TaskState, TaskContext
from agents.governance.meta_orchestrator import MetaOrchestrator, OrchestratorConfig, BudgetExceededError


def test_valid_transition():
    tsm = TaskStateManager()
    ctx = tsm.start_task("test-1", "Test goal")
    ctx = tsm.transition(TaskState.REFINING, {"refined_goal": "Refined"})
    assert ctx.state == TaskState.REFINING


def test_invalid_transition_raises():
    tsm = TaskStateManager()
    ctx = tsm.start_task("test-1", "Test goal")
    with pytest.raises(ValueError):
        tsm.transition(TaskState.APPROVED, {})


def test_confidence_gate():
    tsm = TaskStateManager(confidence_threshold=0.5)
    tsm.start_task("test-1", "Test")
    tsm.current_context.confidence = 0.3
    assert not tsm.should_store_to_memory()
    tsm.current_context.confidence = 0.6
    assert tsm.should_store_to_memory()


def test_confidence_gate_edge_cases():
    tsm = TaskStateManager(confidence_threshold=0.45)
    tsm.start_task("test", "goal")
    tsm.current_context.confidence = 0.449
    assert not tsm.should_store_to_memory()
    tsm.current_context.confidence = 0.451
    assert tsm.should_store_to_memory()


def test_loop_detection():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    for _ in range(3):
        tsm.transition(TaskState.REFINING, {"refined_goal": "x"})
    assert tsm.detect_loop(TaskState.REFINING)


def test_loop_detection_enforcement():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    for _ in range(3):
        tsm.transition(TaskState.REFINING, {"refined_goal": "x"})
    assert tsm.detect_loop(TaskState.REFINING)
    assert tsm.state_counter[TaskState.REFINING] == 3
    # TODO: When enforcement is added, assert that a 4th transition raises
    # or returns a different state. See ROADMAP.md.


def test_agent_call_budget_exceeded():
    config = OrchestratorConfig(max_agent_calls=2, max_time_seconds=999)
    orch = MetaOrchestrator(config=config)
    orch.call_count = 2
    with pytest.raises(BudgetExceededError, match="Agent call budget exceeded"):
        orch._check_budget()


def test_task_timeout_raises():
    config = OrchestratorConfig(max_agent_calls=999, max_time_seconds=1)
    orch = MetaOrchestrator(config=config)
    orch.start_time = 0.0
    with patch('time.time', return_value=1000.0):
        with pytest.raises(TimeoutError, match="Task timeout"):
            orch._check_budget()


def test_required_outputs_enforced():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    # REFINING requires 'refined_goal'
    with pytest.raises(ValueError, match="requires field 'refined_goal'"):
        tsm.transition(TaskState.REFINING, {})


def test_failed_state_is_terminal():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    ctx = tsm.transition(TaskState.FAILED, {"error": "something"})
    assert ctx.state == TaskState.FAILED
    with pytest.raises(ValueError):
        tsm.transition(TaskState.DONE, {})
