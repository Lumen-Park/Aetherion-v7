import os
import shutil
import tempfile
from unittest.mock import patch

import pytest


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
def patch_knowledge_graph_init(temp_chromadb_path):
    """
    Monkey-patch KnowledgeGraph.__init__ to always use the temporary directory.
    This ensures all tests use an isolated ChromaDB.
    """
    from core import memory

    original_init = memory.KnowledgeGraph.__init__

    def patched_init(self, persist_dir=None):
        # Force the temporary directory, ignoring any passed value
        original_init(self, persist_dir=temp_chromadb_path)

    memory.KnowledgeGraph.__init__ = patched_init
    yield
    # Restore original after tests
    memory.KnowledgeGraph.__init__ = original_init


# Now import the rest – the patched __init__ will be used
from agents.governance.meta_orchestrator import (
    BudgetExceededError,
    MetaOrchestrator,
)
from core.task_state import TaskContext, TaskState


def test_human_override_accepts_rejected_task():
    orch = MetaOrchestrator()
    orch.current_context = TaskContext(
        task_id="test-override",
        state=TaskState.HUMAN_REVIEW,
        goal="Test override",
        council_verdict={"verdict": "REJECTED", "score": 0.0},
    )
    orch.state_manager.current_context = orch.current_context

    result = orch.accept_override(
        "test-override", "examiner", "Valid override"
    )
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
