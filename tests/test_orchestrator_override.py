import pytest
from unittest.mock import patch, MagicMock

# Import the modules but patch KnowledgeGraph completely before any tests run
with patch('core.memory.KnowledgeGraph') as MockKnowledgeGraph:
    # Make the mock instance have necessary attributes
    mock_kg_instance = MagicMock()
    mock_kg_instance.reputation = MagicMock()
    mock_kg_instance.archivist = MagicMock()
    MockKnowledgeGraph.return_value = mock_kg_instance

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
