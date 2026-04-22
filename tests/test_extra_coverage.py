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


def test_task_state_manager_loop_force_fail():
    tsm = TaskStateManager()
    tsm.start_task("task-loop", "goal")
    # Manually increment counter to trigger loop detection
    for _ in range(3):
        tsm.state_counter[TaskState.REFINING] = tsm.state_counter.get(TaskState.REFINING, 0) + 1
    assert tsm.detect_loop(TaskState.REFINING)
    # Transition should be forced to FAILED due to loop detection
    ctx = tsm.transition(TaskState.REFINING, {"refined_goal": "test"})
    assert ctx.state == TaskState.FAILED
    assert ctx.error is not None


def test_priority_enum_from_string():
    assert Priority("high") == Priority.HIGH
    assert Priority("critical") == Priority.CRITICAL


def test_verdict_enum_values():
    assert Verdict.APPROVE.value == "approve"
    assert Verdict.REJECT.value == "reject"
