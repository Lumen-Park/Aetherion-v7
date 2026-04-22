import pytest

from core.protocol import AgentMessage, LLMWrapper, Priority, Verdict
from core.task_state import TaskState, TaskStateManager


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


def test_task_context_defaults():
    from core.task_state import TaskContext, TaskState

    ctx = TaskContext(task_id="x", state=TaskState.QUEUED, goal="g")
    assert ctx.refined_goal is None
    assert ctx.expert_panel == []


def test_message_validator():
    from core.protocol import MessageValidator

    msg = AgentMessage(from_agent="A", to_agent="B", task_id="t1")
    assert MessageValidator.validate(msg) is True
    msg.from_agent = ""
    assert MessageValidator.validate(msg) is False


def test_protocol_registry():
    from core.protocol import ProtocolRegistry

    reg = ProtocolRegistry()
    reg.register("test", lambda x: {"status": "ok"})
    msg = AgentMessage(from_agent="A", to_agent="test", task_id="t1")
    result = reg.route(msg)
    assert result == {"status": "ok"}


def test_tool_enabled_llm_wrapper_registration():
    from core.protocol import ToolEnabledLLMWrapper

    wrapper = ToolEnabledLLMWrapper()
    wrapper.register_tool("test", lambda x: x, "desc", {"type": "object"})
    assert "test" in wrapper.tools


# Extra coverage: test TaskContext override fields
def test_task_context_override_fields():
    import time

    from core.task_state import TaskContext, TaskState

    ctx = TaskContext(
        task_id="t1",
        state=TaskState.DONE,
        goal="g",
        override=True,
        override_operator="op",
        override_reason="because",
        override_timestamp=time.time(),
    )
    assert ctx.override is True
    assert ctx.override_operator == "op"
    assert ctx.override_reason == "because"
    assert ctx.override_timestamp is not None
