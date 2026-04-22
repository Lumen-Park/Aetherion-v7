import pytest
from unittest.mock import patch, MagicMock

# Patch KnowledgeGraph BEFORE importing MetaOrchestrator
with patch('core.memory.KnowledgeGraph', return_value=MagicMock()):
    from agents.governance.meta_orchestrator import MetaOrchestrator, BudgetExceededError
    from core.task_state import TaskState, TaskContext


def test_human_override_accepts_rejected_task():
    orch = MetaOrchestrator()
    orch.current_context = TaskContext(
        task_id="test-override",
        state=TaskState.HUMAN_REVIEW,
        goal="Test override",
        council_verdict={"verdict": "REJECTED", "score": 0.0}
    )
    orch.state_manager.current_context = orch.current_context

    result = orch.accept_override("test-override", "examiner", "Valid override")
    assert result is True
    assert orch.current_context.state == TaskState.DONE
    assert orch.current_context.override is True
    assert orch.current_context.override_operator == "examiner"


def test_override_fails_on_wrong_state():
    orch = MetaOrchestrator()
    orch.current_context = TaskContext(
        task_id="test", state=TaskState.QUEUED, goal="Test"
    )
    orch.state_manager.current_context = orch.current_context
    result = orch.accept_override("test", "examiner", "reason")
    assert result is False


def test_budget_enforcement_raises():
    orch = MetaOrchestrator()
    orch.call_count = 50
    with pytest.raises(BudgetExceededError):
        orch._check_budget()
