import pytest
from core.memory import KnowledgeGraph, AgentReputation, Archivist, MemoryEntry
from core.protocol import LLMWrapper, AgentMessage, Priority, Verdict
import json
import time
import os
import tempfile

def test_memory_entry_default_timestamp():
    entry1 = MemoryEntry(key="k1", value="v1", confidence=0.8, source="test")
    time.sleep(0.01)
    entry2 = MemoryEntry(key="k2", value="v2", confidence=0.9, source="test")
    assert entry1.timestamp != entry2.timestamp

def test_agent_reputation_weight():
    with tempfile.TemporaryDirectory() as tmpdir:
        rep = AgentReputation(tmpdir)
        assert rep.get_weight("unknown") == 1.0
        rep.update("agent1", True)
        rep.update("agent1", True)
        rep.update("agent1", False)
        rep.update("agent1", True)
        rep.update("agent1", True)
        # 4 correct out of 5 = 0.8 accuracy -> weight min(1.5, max(0.7, 0.8)) = 0.8
        assert rep.get_weight("agent1") == 0.8

def test_archivist_log_rejection():
    with tempfile.TemporaryDirectory() as tmpdir:
        arch = Archivist(tmpdir)
        arch.log_rejection("task123", "bad output", "patternA")
        patterns = arch.get_rejection_patterns(limit=1)
        assert len(patterns) == 1
        assert patterns[0]["task_id"] == "task123"

def test_llm_wrapper_mock_response():
    wrapper = LLMWrapper()
    # Force unavailable
    wrapper._available = False
    resp = wrapper.generate("test")
    assert "[MOCK RESPONSE]" in resp["content"]

def test_agent_message_serialization():
    msg = AgentMessage(from_agent="A", to_agent="B", task_id="t1", priority=Priority.HIGH,
                       payload={"data": 42})
    json_str = msg.to_json()
    msg2 = AgentMessage.from_json(json_str)
    assert msg2.priority == Priority.HIGH
    assert msg2.payload["data"] == 42

def test_verdict_enum():
    assert Verdict.APPROVE.value == "approve"
