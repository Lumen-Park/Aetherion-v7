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
        tsm.state_counter[TaskState.REFINING] = tsm.state_counter.get(TaskState.REFINING, 0) + 1
    assert tsm.detect_loop(TaskState.REFINING)


def test_loop_detection_enforcement():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    for _ in range(3):
        tsm.state_counter[TaskState.REFINING] = tsm.state_counter.get(TaskState.REFINING, 0) + 1
    assert tsm.detect_loop(TaskState.REFINING)
    with pytest.raises(ValueError, match="Invalid transition"):
        tsm.transition(TaskState.REFINING, {"refined_goal": "x"})


def test_agent_call_budget_exceeded():
    config = OrchestratorConfig(max_agent_calls=2, max_time_seconds=999)
    orch = MetaOrchestrator(config=config)
    orch.call_count = 2
    with pytest.raises(BudgetExceededError, match="Agent call budget exceeded"):
        orch._check_budget()


def test_task_timeout_raises():
    config = OrchestratorConfig(max_agent_calls=999, max_time_seconds=1)
    orch = MetaOrchestrator(config=config)
    orch.start_time = 1000.0   # start time in the past
    with patch('time.time', return_value=1002.0):   # now > start_time + max_time
        with pytest.raises(TimeoutError, match="Task timeout"):
            orch._check_budget()


def test_required_outputs_enforced():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    with pytest.raises(ValueError, match="requires field 'refined_goal'"):
        tsm.transition(TaskState.REFINING, {})


def test_failed_state_is_terminal():
    tsm = TaskStateManager()
    tsm.start_task("test", "goal")
    # Move to a state that allows FAILED (HUMAN_REVIEW)
    tsm.transition(TaskState.REFINING, {"refined_goal": "x"})
    tsm.transition(TaskState.CURATING, {"expert_panel": []})
    tsm.transition(TaskState.RESEARCHING, {"research_findings": "findings"})
    tsm.transition(TaskState.DEVELOPING, {"code_output": "code"})
    tsm.transition(TaskState.REVIEWING, {})
    tsm.transition(TaskState.TESTING, {"test_results": {}})
    tsm.transition(TaskState.SANITIZING, {})
    tsm.transition(TaskState.FORENSICS, {})
    tsm.transition(TaskState.EDGE_CASES, {})
    tsm.transition(TaskState.EVALUATING, {})
    tsm.transition(TaskState.COUNCIL, {"council_verdict": {"verdict": "APPROVED"}})
    tsm.transition(TaskState.HUMAN_REVIEW, {})
    ctx = tsm.transition(TaskState.FAILED, {"error": "something"})
    assert ctx.state == TaskState.FAILED
    with pytest.raises(ValueError):
        tsm.transition(TaskState.DONE, {})
