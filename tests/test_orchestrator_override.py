import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock

# ------------------------------------------------------------
# REAL CHROMADB FIXTURE – isolated temporary database per session
# ------------------------------------------------------------
@pytest.fixture(scope="session")
def temp_chromadb_path():
    """Create a temporary directory for ChromaDB that persists for the session."""
    temp_dir = tempfile.mkdtemp(prefix="aetherion_test_")
    yield temp_dir
    # Cleanup after all tests in session
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass


@pytest.fixture(scope="session", autouse=True)
def patch_knowledge_graph_persist_dir(temp_chromadb_path):
    """
    Automatically patch KnowledgeGraph to use the temporary directory.
    This ensures all tests that instantiate KnowledgeGraph use an isolated DB.
    """
    with patch('core.memory.KnowledgeGraph.__init__') as mock_init:
        # Make the real __init__ use our temp path
        def fake_init(self, persist_dir=None):
            # Call original but override persist_dir
            from core.memory import KnowledgeGraph as RealKG
            RealKG.__init__(self, persist_dir=temp_chromadb_path)
        mock_init.side_effect = fake_init
        yield


# Now we can import MetaOrchestrator safely – it will use the patched KnowledgeGraph
from agents.governance.meta_orchestrator import (
    MetaOrchestrator,
    BudgetExceededError,
)
from core.task_state import TaskState, TaskContext


def test_human_override_accepts_rejected_task():
    orch = MetaOrchestrator()
    orch.current_context = TaskContext(
        task_id="test-override",
        state=TaskState.HUMAN_REVIEW,
        goal="Test override",
        council_verdict={"verdict": "REJECTED", "score": 0.0},
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
