import pytest
from core.protocol import LLMWrapper, AgentMessage, Priority, Verdict
from core.task_state import TaskStateManager, TaskState


def test_llm_wrapper_initialization():
    wrapper = LLMWrapper(model="test-model", temperature=0.5)
    assert wrapper.model == "test-model"
    assert wrapper.temperature == 0.5


def test_agent_message_trace():
    msg = AgentMessage(from_agent="A", to_agent="B", task_id="t1")
    msg.add_to_trace("C")
    assert "C" in msg.trace


def test_agent_message_create_reply():
    msg = AgentMessage(from_agent="A", to_agent="B", task_id="t1")
    reply = msg.create_reply("B", {"status": "ok"})
    assert reply.from_agent == "B"
    assert reply.to_agent == "A"
    assert reply.payload["status"] == "ok"
    assert "A" in reply.trace


def test_task_state_manager_initial_state():
    tsm = TaskStateManager()
    ctx = tsm.start_task("task-1", "goal")
    assert ctx.state == TaskState.QUEUED
    assert ctx.goal == "goal"


def test_priority_enum_from_string():
    assert Priority("high") == Priority.HIGH
    assert Priority("critical") == Priority.CRITICAL


def test_verdict_enum_values():
    assert Verdict.APPROVE.value == "approve"
    assert Verdict.REJECT.value == "reject"


def test_orchestrator_config_defaults():
    from agents.governance.meta_orchestrator import OrchestratorConfig
    config = OrchestratorConfig()
    assert config.max_agent_calls == 50
    assert config.max_time_seconds == 420
    assert config.confidence_gate == 0.45


def test_llm_wrapper_mock_response():
    wrapper = LLMWrapper()
    wrapper._available = False
    resp = wrapper.generate("hello")
    assert "[MOCK]" in resp["content"]
